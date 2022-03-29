#!/usr/bin/env bash
sudo -H pip3 install pysyslog

cd "$(dirname "$0")"
pysyslog 0.0.0.0 10514 --cert ../certs/server-cert.pem --key ../certs/server-key.pem
