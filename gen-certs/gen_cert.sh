#!/usr/bin/env bash

cd "$(dirname "$0")"
# Create a new self-signed CA certificate.
openssl genrsa -out ca-key.pem 2048
openssl req -new -x509 -sha256 -nodes -days 3600 -subj '/C=US/ST=LA/L=New Orleans/O=hdInternal/CN=192.168.1.55/emailAddress=admin@internal.com' -key ca-key.pem -out ca-cert.pem

# Create the request and sign it with our CA certificate
openssl req -newkey rsa:2048 -sha256 -days 3600 -nodes -subj '/C=US/ST=LA/L=New Orleans/O=hdInternal/CN=192.168.1.55/emailAddress=admin@internal.com' -keyout server-key.pem -out server-req.pem
openssl x509 -req -in server-req.pem -days 3600 -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem

# Certificate info
openssl x509 -text -in ca-cert.pem
openssl x509 -text -in server-cert.pem

while true; do
    read -p "Do you wish to copy certificates to the docker folder [Y/n] ? " yn
    case $yn in
        [Yy]* ) cp ./{ca-cert.pem,server-cert.pem,server-key.pem} ../syslog-docker/certs; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done