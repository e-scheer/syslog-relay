#!/usr/bin/env bash

cd "$(dirname "$0")"

sudo apt-get install --no-upgrade --yes gnutls-bin

## CA ##

# Generate a private key for the CA
sudo certtool --generate-privkey --outfile ca-key.pem

# Generate the (self-signed) CA certificate
sudo certtool --generate-self-signed --template ca.cfg --load-privkey ca-key.pem --outfile ca.pem

## SERVER ##

# Generate a private key for the server
sudo certtool --generate-privkey --outfile server-key.pem --bits 2048

# Generate a certificate request for the server 
sudo certtool --generate-request --load-privkey --template server.cfg server-key.pem --outfile server-request.pem

# Generate the certificate for the server and import trusted certificate authority keys into it
sudo certtool --generate-certificate --template server.cfg --load-request server-request.pem --outfile server-cert.pem --load-ca-certificate ca.pem --load-ca-privkey ca-key.pem

## CLIENT(S) ##

# Generate a private key for the client (device)
sudo certtool --generate-privkey --outfile client-key.pem --bits 2048

# Generate a private key for the client (device)
sudo certtool --generate-request --template client.cfg --load-privkey client-key.pem --outfile client-request.pem

# Generate a certificate for the client and import the certificate authority certificates inside
sudo certtool --generate-certificate --template client.cfg --load-request client-request.pem --outfile client-cert.pem --load-ca-certificate ca.pem --load-ca-privkey ca-key.pem