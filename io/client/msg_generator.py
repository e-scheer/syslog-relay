#!/usr/bin/env python3

import argparse
import signal
import time
import numpy as np
import threading



class CancellationToken:
    def __init__(self):
        self._cancelled = False

    def is_valid(self):
        return not self._cancelled

    def cancel(self, *args, **kwargs):
        self._cancelled = True

class MessageMetrics:
    def __init__(self, length_loc, length_scale, impt_prob, impt_sev, iat_scale):
        """ Provides metrics for message generation

        Args:
            length_loc (float): Message length mean (“centre”) of the distribution
            length_scale (float): Message length standard deviation (spread or “width”) of the distribution
            impt_prob (float): Probability for a message to be important
            impt_sev (int): Message below or equal to this severity are considered important
            iat_scale (float): Inter-arrival the scale parameter (exponential distribution)
        """
        self.length_loc = length_loc
        self.length_scale = length_scale
        self.impt_mean = impt_prob
        self.impt_sev = impt_sev
        self.iat_scale = iat_scale

class Device:
    def __init__(self, id, seed, metrics):
        self.id = id
        self.seed = seed
        self.metrics = metrics

def loggen(device, token):
    rng = np.random.default_rng(device.seed)


    while token.is_valid():
        rng.normal(loc=1, scale=2)

def main():
    parser = argparse.ArgumentParser(
        description='A syslog message generator.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-s', '--seed',
        type=int,
        default=2022,
        help="seed used for reproducibility")

    parser.add_argument(
        '-d', '--devices',
        type=int,
        default=1,
        help="number of devices issuing messages")

    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=10,
        help="generation's duration in seconds (0 for infinite)")

    parser.add_argument("target")
    parser.add_argument("port")

    args = vars(parser.parse_args())

    # instantiate independent rngs
    rng = np.random.default_rng(args['seed'])
    ss = rng.bit_generator._seed_seq
    device_seeds = ss.spawn(args['devices'])

    threads = []
    token = CancellationToken()

    # bind signal
    signal.signal(signal.SIGINT, token.cancel)

    # message metrics
    metrics = MessageMetrics(71.5, 30.2, 0.076, 3, 1.361)

    for i, seed in enumerate(device_seeds):
        d = Device(i, seed, metrics)
        t = threading.Thread(name="device-%d" % i, target=loggen, args=[d, token])
        threads.append(t)

    # start all threads
    for t in threads:
        t.start()

    # set a timeout if required
    if args['timeout'] > 0:
        signal.signal(signal.SIGALRM, token.cancel)
        signal.alarm(args['timeout'])

 
    # wait for all of them to finish
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()