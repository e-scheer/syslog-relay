sudo apt install syslog-ng-core

# --rate <message/second> or -r <message/second>
# The number of messages generated per second for every active connection.

# --size <message-size> or -s <message-size>
# The size of a syslog message in bytes. Default value: 256. Minimum value: 127 bytes, maximum value: 8192 bytes.

# --interval <seconds> or -I <seconds>
# The number of seconds loggen will run. Default value: 10

loggen -i --dgram --size 256 --rate 50000 --interval 60 192.168.1.15 54321
