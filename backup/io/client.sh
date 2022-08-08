#!/usr/bin/env bash

echo "Log message content (CTRL+C to exit): "

while read input
do
    logger -n 192.168.1.12 -P 54321 -d $input
    echo "Sent! Next log message content:"
done