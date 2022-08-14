#!/usr/bin/env bash
sudo -H pip3 install pysyslog

cd "$(dirname "$0")"
pysyslog 0.0.0.0 10514 --cert ../../gen-certs/server-cert.pem --key ../../gen-certs/server-key.pem