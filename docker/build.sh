#!/usr/bin/env bash

cd "$(dirname "$0")"

sudo apt-get install -y qemu-user-static

mkdir -p qemu
cp /usr/bin/qemu-aarch64-static qemu/

mkdir -p certs
cp ../certs/{ca-cert.pem,server-cert.pem,server-key.pem} certs/

sudo docker-compose build