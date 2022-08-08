#!/bin/sh
DEVICE=$(route | grep '^default' | grep -o '[^ ]*$')
tc qdisc del dev $DEVICE root
tc qdisc del dev ifb0 root