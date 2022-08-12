#!/usr/bin/env python3

import argparse
import datetime
import signal
import socket
import time
import numpy as np
import threading
import atomics

FACILITY_MAX = 23
SEVERITY_MAX = 7

MSG_CHARS = 'PAD'
MSG_TAG = 'prg00000'
MSG_PID = '1234'

IN_BURST_MODE_AT_START=False

STATS_SLEEP=5

class InternalCounters:
    def __init__(self):
        self.seq = atomics.atomic(width=4, atype=atomics.UINT)
        self.impt_seq = atomics.atomic(width=4, atype=atomics.UINT)

class MessageMetrics:
    def __init__(self, length_loc, length_scale, impt_prob, impt_sev, iat_scale, in_burst_prob, out_burst_prob):
        """ Provides metrics for message generation

        Args:
            length_loc (float): Message's content length mean of the distribution
            length_scale (float): Message's content length standard deviation of the distribution
            impt_prob (float): Probability for a message to be important
            impt_sev (int): Message below or equal to this severity are considered important
            iat_scale (float): Inter-arrival the scale parameter (exponential distribution)
            in_burst_prob (float): Probability that the device enters burst mode (sends message)
            out_burst_prob (float): Probability that the devices leaves burst mode (stops sending message)
        """
        self.length_loc = length_loc
        self.length_scale = length_scale
        self.impt_mean = impt_prob
        self.impt_sev = impt_sev
        self.iat_scale = iat_scale
        self.in_burst_prob = in_burst_prob
        self.out_burst_prob = out_burst_prob

class Device:
    def __init__(self, id, seed, metrics, burst_mode, clock, timer):
        self.id = id
        self.rng = np.random.default_rng(seed)
        # can also be an IP or domain name
        self.hostname = "device-%d" % id
        self.metrics = metrics
        self.burst_mode = burst_mode
        self.bursty = IN_BURST_MODE_AT_START
        self._clock = clock
        self._timer = timer

    def __str__(self):
        return "<device-%d> [clock:%s]" % (self.hostname, str(self._clock))

    def burst_transition(self):
        if self.bursty:
            self.bursty = self.metrics.out_burst_prob > self.rng.random()
        else:
            self.bursty = self.metrics.in_burst_prob > self.rng.random()

    def waitfor(self):
        return self.rng.exponential(scale=self.metrics.iat_scale)

    def get_clock(self):
        t = self._clock + np.timedelta64(int(time.perf_counter())- self._timer, 's')
        return t.item().strftime("%b %d %H:%M:%S")

    def genlog(self, seq, impt_seq):
        facility = self.rng.integers(0, FACILITY_MAX + 1)

        # build attributes for statistics
        msg_bytes = int(self.rng.normal(self.metrics.length_loc, self.metrics.length_scale))
        attributes = f"seq: {seq.fetch_inc()}, thread: {self.id},"

        # is the message important or not
        if self.metrics.impt_mean > self.rng.random():
            severity = self.rng.integers(0, self.metrics.impt_sev + 1)
            attributes += f" impt-seq: {impt_seq.fetch_inc()},"
        else:
            severity = self.rng.integers(self.metrics.impt_sev, SEVERITY_MAX + 1)

        # compute priority
        priority =  facility * 8 + severity

        # build message's content
        message = f"{MSG_TAG}[{MSG_PID}]:{attributes} {MSG_CHARS * int(max(0,(msg_bytes-len(attributes)))/len(MSG_CHARS))}"

        # f-strings provides best performance
        return f"<{priority}>{str(self.get_clock())} {self.hostname} {message}"

def sendlogs(device, counters, address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # threads are running as daemon
    while True:
        next_time = time.time() + device.waitfor()

        if device.burst_mode:
            # attempts to transit to burst/standby
            device.burst_transition()
        
        if not device.burst_mode or device.bursty:
            sock.sendto(device.genlog(counters.seq, counters.impt_seq).encode(), address)

        # account for the computation time consumed before sleep
        time.sleep(max(0, next_time - time.time()))

def main():
    parser = argparse.ArgumentParser(
        description='A syslog message generator.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-s', '--seed',
        type=int,
        default=123456789,
        help="seed used for reproducibility")

    parser.add_argument(
        '-d', '--devices',
        type=int,
        default=1,
        help="number of devices issuing messages")

    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=120,
        help="generation's duration in seconds (0 for infinite)")

    parser.add_argument(
        '-b', '--bursty',
        action='store_true',
        help="sets the message generation in a bursty/standby model")

    parser.add_argument(
        '--impt-sev',
        type=int,
        default=3,
        choices=range(0, SEVERITY_MAX + 1),
        help="messages with severity below or equal to this value are considered important")

    parser.add_argument(
        '--no-random-clock',
        action='store_true',
        help="disable the random clock set on each device")

    parser.add_argument("target", type=str)
    parser.add_argument("port", type=int)

    args = vars(parser.parse_args())
    
    # instantiate independent rngs
    rng = np.random.default_rng(args['seed'])
    ss = rng.bit_generator._seed_seq
    device_seeds = ss.spawn(args['devices'])
    print("Seed used: %s" % args['seed'])

    threads = []
    devices = []

    # message metrics
    # server-like
    #metrics = MessageMetrics(71.5, 30.2, 0.076, args['impt_sev'], 1.361, 0.001757, 0.037)
    # linuxlogs-like
    metrics = MessageMetrics(71.5, 30.2, 0.076, args['impt_sev'], 57, 0.001757, 0.037)

    start_date = np.datetime64('1970', 's')
    end_date = np.datetime64('2022', 's')
    now_date = np.datetime64(datetime.datetime.now(), 's')
    timer = int(time.perf_counter())

    # message sequence number
    counters = InternalCounters()
    
    for i, seed in enumerate(device_seeds):
        # generate random clock
        if args['no_random_clock']:   
            clock = now_date
        else:
            clock = start_date + \
                np.timedelta64(rng.integers((end_date - start_date).astype(int)), 's')

        d = Device(i, seed, metrics, args['bursty'], clock, timer)
        
        t = threading.Thread(
            name="device-%d" % i,
            target=sendlogs,
            daemon=True,
            args=[d, counters, (args['target'], args['port'])])


        print("Configured device %d with clock %s" % (i, clock))

        threads.append(t)
        devices.append(d)

    print("Starting %d device(s)..." % args['devices'])

    # start all threads
    for t in threads:
        t.start()

    print("Done")

    # set a timeout if required
    if args['timeout'] > 0:
        signal.signal(signal.SIGALRM, signal.default_int_handler)
        signal.alarm(args['timeout'])

    signal.signal(signal.SIGINT, signal.default_int_handler)
    print("Statistics are displayed every %d second(s)..." % STATS_SLEEP)
    try:
        while True:
            time.sleep(STATS_SLEEP)
            
            seq = counters.seq.load()
            t = int(time.perf_counter()) - timer
            print(f"Statistics: last-seq={seq - 1}, last-impt-seq={counters.impt_seq.load()}, count={seq}, time={t} (sec), avg-rate={round(seq/t, 4)} msg/sec")
    except KeyboardInterrupt:
        pass

    seq = counters.seq.load()
    t = int(time.perf_counter()) - timer
    print(f"Statistics: last-seq={seq - 1}, last-impt-seq={counters.impt_seq.load()}, count={seq}, time={t} (sec), avg-rate={round(seq/t, 4)} msg/sec")

    print("Closing...")

if __name__ == "__main__":
    main()