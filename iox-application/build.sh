#!/usr/bin/env bash

cd "$(dirname "$0")"

# variables
IOXCLIENT=./ioxclient
CONFIG_FILE=rsyslog.conf
EXTRA_CONFIG_FILE=rsyslog.conf.d/*.conf

# runs register script binfmt_misc entries (required)
sudo docker run --rm --privileged multiarch/qemu-user-static:register --reset

# builds image
if ! sudo docker-compose build --build-arg CONFIG_FILE=$CONFIG_FILE --build-arg EXTRA_CONFIG_FILE=$EXTRA_CONFIG_FILE; then
    echo "Docker build failed"
    exit
fi

# ensures ioxclient is present
if [ ! -f "$IOXCLIENT" ]; then
    echo "File '$IOXCLIENT' does not exist. Please install the latest version of ioxclient here: https://developer.cisco.com/docs/iox/#!iox-resource-downloads/downloads."
    exit 1
fi

# builds IOx application
sudo $IOXCLIENT docker package iox-syslog-relay . --name iox-syslog-relay -m