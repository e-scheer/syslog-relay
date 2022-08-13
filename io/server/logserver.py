#!/usr/bin/env python3

import argparse
import signal
import threading
import time
import atomics
from socketserver import TCPServer, ThreadingMixIn, StreamRequestHandler
import ssl

IMPT_SEQ_TAG = "impt-seq:"

class InternalCounters:
    def __init__(self):
        self.msg_count = atomics.atomic(width=4, atype=atomics.UINT)
        self.impt_msg_count = atomics.atomic(width=4, atype=atomics.UINT)

class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    def __init__(self, counters, certfile, keyfile, *args, **kwargs):
        self.counters = counters
        TCPServer.__init__(self, *args, **kwargs)
        self.certfile = certfile
        self.keyfile = keyfile

    def get_request(self):
        sock, fromaddr = TCPServer.get_request(self)
        tls_sock = ssl.wrap_socket(
            sock,
            server_side=True,
            certfile = self.certfile,
            keyfile = self.keyfile)

        return tls_sock, fromaddr

    def finish_request(self, request, client_address):
        # forwards counters to the handler
        self.RequestHandlerClass(self.counters, request, client_address, self)

    def server_close(self):
        self.socket.close()
        self.shutdown()
        return TCPServer.server_close(self)

class LogHandler(StreamRequestHandler):
    def __init__(self, counters, *args, **kwargs):
        self.counters = counters
        StreamRequestHandler.__init__(self, *args, **kwargs)

    def handle(self):
        for line in self.rfile:
            # print(line)
            # counts arriving messages (do not process them)
            msg = line.decode()
            self.counters.msg_count.inc()
            if IMPT_SEQ_TAG in msg:
                self.counters.impt_msg_count.inc()

    def finish(self):
        self.request.close()

# task that runs at a fixed interval
def internal_counters(interval_sec, counters, timer):
    i = interval_sec
    while True:
        time.sleep(1)
        i -= 1

        if i == 0:
            dump_internal_counters(counters, timer)
            i = interval_sec

def dump_internal_counters(counters, timer):
    msg_count = counters.msg_count.load()
    t = int(time.perf_counter()) - timer
    print(f"Statistics: msg-count={msg_count}, impt-msg-count={counters.impt_msg_count.load()}, time={t} (sec), avg-rate={round(msg_count/t, 4)} msg/sec")

def main():
    parser = argparse.ArgumentParser(
        description='A syslog message generator.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-k', '--key',
        type=argparse.FileType('r', encoding='UTF-8'),
        required=True,
        help="server's private key (for TLS)")

    parser.add_argument(
        '-c', '--cert',
        type=argparse.FileType('r', encoding='UTF-8'),
        required=True,
        help="server's public certificate (for TLS)")

    parser.add_argument(
        '-s', '--stats',
        type=int,
        default=10,
        help="time interval between two internal (sec) counters feeds")

    parser.add_argument("target", type=str, default="0.0.0.0")
    parser.add_argument("port", type=int)

    args = vars(parser.parse_args())

    counters = InternalCounters()
    
    timer = int(time.perf_counter())
    server = ThreadedTCPServer(counters, args['cert'].name, args['key'].name, (args['target'], args['port']), LogHandler)

    print('Starting internal counters...')
    bg_task = threading.Thread(
        name='internal-counters',
        target=internal_counters,
        daemon=True,
        args=[args['stats'], counters, timer])
    bg_task.start()

    signal.signal(signal.SIGINT, signal.default_int_handler)
    try:
        # start server 
        print(f"Listening for logs on {args['target']} port {args['port']}...")
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        server.server_close()
        print("Server has been terminated.")

    dump_internal_counters(counters, timer)

if __name__ == "__main__":
    main()