#!/usr/bin/env python3

import argparse
import signal
import socket
import threading
import time
from xmlrpc.client import boolean

MSG_PRI = 1 * 8 + 6 # user-level informational message
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

def internal_counters(token, counter, msg_avg_size):
    while token.is_valid():
        prev_counter = counter.value
        time.sleep(1)
        delta = counter.value - prev_counter
        print(f"Statistics: count={counter.value}, rate={str(delta)} msg/sec, throughput={round(delta * msg_avg_size / 1000000, 4)} MB/sec")

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
        '-t', '--timeout',
        type=int,
        default=120,
        help="generation's duration in seconds (0 for infinite)")

    parser.add_argument(
        '-a', '--affix-seq',
        action='store_true',
        help="affix a sequence number to messages")   

    parser.add_argument("target", type=str)
    parser.add_argument("port", type=int)

    args = vars(parser.parse_args())
    
    timestamp = time.strftime("%b %d %H:%M:%S", time.localtime())

    # build message with respect to the argument 'size' 
    message = f"<{MSG_PRI}>{timestamp} {MSG_HOSTNAME} {MSG_TAG}[{MSG_PID}]: "
    if args['affix_seq']:
        message += "seq: %d, "

    message += MSG_CHARS * int(
        max(0, (args['size'] - (len(message))))
        / len(MSG_CHARS))

    # pre-encode if it does not requires the sequence number
    if not args['affix_seq']:    
        message = message.encode()

    token = CancellationToken()
    counter = Counter()

    print('Starting internal counters...')
    bg_task = threading.Thread(name='internal-counters', target=internal_counters, args=[token, counter, args['size']])
    bg_task.start()

    # creates a bucket to control burstiness
    bucket = TokenBucket(args['rate'], args['rate'])

    # set a timeout if required
    if args['timeout'] > 0:
        signal.signal(signal.SIGALRM, token.cancel)
        signal.alarm(args['timeout'])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (args['target'], args['port'])
    print("Starting burst%s..." % (f" for {args['timeout']} second(s)" if args['timeout'] > 0 else ""))

    try:
        while token.is_valid():
            if bucket.consume(1):
                # least work here to maximise throughput
                if args['affix_seq']:
                    sock.sendto((message % counter.value).encode(), addr)
                else:
                    sock.sendto(message, addr)
                counter.value += 1
    except:
        token.cancel()
        sock.close()

    bg_task.join()
 

if __name__ == "__main__":
    main()