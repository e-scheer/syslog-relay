exit2shell

ifconfig eth0 down
ifconfig eth1 down

brctl addbr br0

brctl addif br0 eth0
brctl addif br0 eth1

ifconfig br0 up
ifconfig eth0 0.0.0.0 up
ifconfig eth1 0.0.0.0 up

dhclient br0 -v
