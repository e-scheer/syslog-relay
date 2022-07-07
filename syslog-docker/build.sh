#!/usr/bin/env bash

cd "$(dirname "$0")"

# variables
IOXCLIENT=./ioxclient
CERTS_DIR=certs
CERT_FILES='ca-cert.pem server-cert.pem server-key.pem'
CONFIG_FILE=rsyslog.conf
EXTRA_CONFIG_FILE=rsyslog.conf.d/*.conf

# ensures certificates are present
for file in $CERT_FILES; do
    if [[ ! -f $CERTS_DIR/$file ]]; then
        echo "At least one of the following files $CERTS_DIR/{$CERT_FILES} is missing"
        exit 1
    fi
done

# runs register script binfmt_misc entries (required)
sudo docker run --rm --privileged multiarch/qemu-user-static:register --reset

# builds image
sudo docker-compose build --build-arg CERTS_DIR=$CERTS_DIR --build-arg CONFIG_FILE=$CONFIG_FILE --build-arg EXTRA_CONFIG_FILE=$EXTRA_CONFIG_FILE

# ensures ioxclient is present
if [ ! -f "$IOXCLIENT" ]; then
    echo "File '$IOXCLIENT' does not exist. Please install the latest version of ioxclient here: https://developer.cisco.com/docs/iox/#!iox-resource-downloads/downloads."
    exit 1
fi

# builds IOx application
sudo $IOXCLIENT docker package iox-syslog-relay . --name iox-syslog-relay -m