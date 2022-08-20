#!/usr/bin/env python3

import argparse
import datetime
import signal
import socket
import threading
import time

FACILITY_MAX = 23
SEVERITY_MAX = 7

MSG_DEFAULT_PRI = 1 * 8 + 6 # user-level informational message

MSG_HOSTNAME="device"
MSG_TAG = 'prg00000'
MSG_PID = '1234'
MSG_CHARS = 'PAD'

class Counter:
    def __init__(self):
        self.value = 0

class CancellationToken:
    def __init__(self):
        self._cancelled = False

    def is_valid(self):
        return not self._cancelled

    def cancel(self, *args, **kwargs):
        print("Cancelling the token...")
        self._cancelled = True

class BucketRef:
    def __init__(self, bucket):
        self.bucket = bucket 

class TokenBucket:
    # Based on 'Alec Thomas' implementation:
    # https://code.activestate.com/recipes/511490-implementation-of-the-token-bucket-algorithm/

    def __init__(self, tokens, fill_rate):
        """ Regulates a flow to match the rate of the bucket (not thread-safe)

        Args:
            tokens (int): total tokens in the bucket
            fill_rate (int): tokens refill rate
        """
        self.capacity = float(tokens)
        self._tokens = float(tokens)
        self.fill_rate = float(fill_rate)
        self.timestamp = time.time()

    def consume(self, tokens):
        """Consume tokens from the bucket. Returns True if there were
        sufficient tokens otherwise False."""
        if tokens <= self.tokens:
            self._tokens -= tokens
            return True
        else:
            return False

    def get_tokens(self):
        now = time.time()
        if self._tokens < self.capacity:
            delta = self.fill_rate * (now - self.timestamp)
            self._tokens = min(self.capacity, self._tokens + delta)

        self.timestamp = now
        return self._tokens

    tokens = property(get_tokens)

def internal_counters(token, counter, impt_counter, msg_avg_size):
    while token.is_valid():
        prev_counter = counter.value
        time.sleep(1)
        delta = counter.value - prev_counter
        print(f"Statistics: count={counter.value}, impt-counter={impt_counter.value}, rate={str(delta)} msg/sec, throughput={round(delta * msg_avg_size / 1000000, 4)} MB/sec")

def inc_rate_gradually(bucket_ref, interval, init_rate, wait_dequeue, n):
    i = 0
    rate = init_rate

    while i != n:
        bucket_ref.bucket = TokenBucket(rate, rate)
        print(f"Gradual-rate: set rate to {rate} messages/s (next in {interval} seconds, {i}/{n})")

        time.sleep(interval)

        print(f"Gradual-rate: waiting for {wait_dequeue} seconds for the queue to empty")
        time.sleep(wait_dequeue)

        rate += init_rate
        i += 1

def main():
    parser = argparse.ArgumentParser(
        description='A syslog message generator.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-s', '--size',
        type=int,
        default=256,
        help="size of syslog messages in bytes")

    parser.add_argument(
        '-r', '--rate',
        type=int,
        default=5000,
        help="number of devices issuing messages")

    parser.add_argument(
        '-g', '--gradual-rate-interval',
        type=int,
        default=None,
        help="interval (s) between two rate increases, to be used in combination with the --timeout to create an evolving rate")

    parser.add_argument(
        '--gradual-rate-wait',
        type=int,
        default=30,
        help="waiting time to allow the queue to empty between two rate increases")

    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=120,
        help="generation's duration in seconds (0 for infinite)")

    parser.add_argument(
        '-a', '--affix-seq',
        action='store_true',
        help="affix a sequence number to messages")   

    parser.add_argument(
        '--impt-sev',
        type=int,
        default=3,
        choices=range(0, SEVERITY_MAX + 1),
        help="messages with severity below or equal to this value are considered important")

    parser.add_argument(
        '--impt-prob',
        type=float,
        default=0,
        help="probability that a message is an important one (between 0 and 1)")

    parser.add_argument("target", type=str)
    parser.add_argument("port", type=int)

    args = vars(parser.parse_args())

    if args['gradual_rate_interval'] and ((args['timeout'] % args['gradual_rate_interval']) != 0):
        parser.error('the gradual-rate-interval must be an integer divisor of the timeout')

    timestamp = time.strftime("%b %d %H:%M:%S", time.localtime())

    # precomputes the priority of the message
    MSG_IMPT_PRI = (0 * 8) + args['impt_sev'] # kernel messages

    # adds the sequence number (if required)
    message = f"<%d>{timestamp} {MSG_HOSTNAME} {MSG_TAG}[{MSG_PID}]:"
    if args['affix_seq']:
        message += "seq: {0}, impt-seq: {1}, "

    # build message with respect to the argument 'size'
    message += MSG_CHARS * int(
        max(0, (args['size'] - (len(message))))
        / len(MSG_CHARS))
    
    impt_message = message % MSG_IMPT_PRI
    message = message % MSG_DEFAULT_PRI

    # pre-encode if it does not requires the sequence number
    if not args['affix_seq']:
        message = message.encode()
        impt_message = impt_message.encode()

    token = CancellationToken()
    counter = Counter()
    impt_counter = Counter()

    print('Starting internal counters...')
    bg_task = threading.Thread(name='internal-counters', target=internal_counters, args=[token, counter, impt_counter, args['size']])
    bg_task.start()

    # creates a bucket to control burstiness (inside a reference if gradual rate is required)
    bucket_ref = BucketRef(TokenBucket(args['rate'], args['rate']))

    # set the evolving rate thread
    if args['gradual_rate_interval']:
        gradual_steps = int(args['timeout'] / args['gradual_rate_interval'])
        gradual_rate = int(args['rate'] / gradual_steps) # the loss of the remainder of the division is tolerable
        bucket_ref.bucket = TokenBucket(gradual_rate, gradual_rate)

        print(f'Starting gradual rate (max rate averaged to {gradual_rate*gradual_steps} messages/s)...')
        gr_task = threading.Thread(name='inc_rate_gradually', target=inc_rate_gradually, daemon=True, args=[
            bucket_ref,
            args['gradual_rate_interval'],
            gradual_rate,
            args['gradual_rate_wait'],
            gradual_steps])

        gr_task.start()

    # set a timeout if required
    if args['timeout'] > 0:
        signal.signal(signal.SIGALRM, token.cancel)
        signal.alarm(args['timeout'])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (args['target'], args['port'])
    print("Starting burst%s..." % (f" for {args['timeout']} second(s)" if args['timeout'] > 0 else ""))
    print("Starting time: %s" % str(datetime.datetime.now()))
    try:
        while token.is_valid():
            if bucket_ref.bucket.consume(1):
                msg = message
                is_impt = False

                if args['impt_prob'] > 0:
                    if 0 <= (counter.value  % (1 / args['impt_prob'])) < 1:
                        msg = impt_message
                        is_impt = True
                    else:
                        msg = message

                if args['affix_seq']:
                    msg = msg.format(counter.value, impt_counter.value).encode()
                
                sock.sendto(msg, addr)

                counter.value += 1
                if is_impt:
                    impt_counter.value += 1
                

    except:
        token.cancel()
        sock.close()

    bg_task.join()
    print("End time: %s" % str(datetime.datetime.now()))

if __name__ == "__main__":
    main()