#!/bin/sh
# Based on 'Super Linux Man' configuration:
# https://linux-man.org/2021/09/24/how-to-limit-ingress-bandwith-with-tc-command-in-linux/


UP_SPEED=30kbps
DOWN_SPEED=500kbps

DELAY=100ms
LOSS=0.2%

# Find the default network device in route table
DEVICE=$(route | grep '^default' | grep -o '[^ ]*$')

# Linux does not support shaping on ingress
# but we can redirect ingress taffic to ifb device, then do
# taffic shaping on egress queue of ifb device.

if test -z "$(lsmod | grep ifb)"; then
    modprobe ifb
fi

if test -z "$(ip link | grep ifb0)"; then
    ip link add name ifb0 type ifb
    ip link set dev ifb0 up
fi

tc qdisc add dev ifb0 root handle 1: htb r2q 1
tc class add dev ifb0 parent 1: classid 1:1 htb rate $UP_SPEED
tc filter add dev ifb0 parent 1: matchall flowid 1:1

tc qdisc add dev $DEVICE ingress
tc filter add dev $DEVICE ingress matchall action mirred egress redirect dev ifb0

tc qdisc add dev $DEVICE ingress
tc qdisc add dev $DEVICE root netem delay $DELAY rate $DOWN_SPEED loss $LOSS


# Note that "tc -p qdisc ls dev eth0" will list current defined rules