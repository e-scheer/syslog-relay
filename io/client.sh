#!/usr/bin/env bash

echo "Log message content (CTRL+C to exit): "

while read input
do
    logger -n 127.0.0.1 -P 514 $input
    echo "Sent! Next log message content:"
done