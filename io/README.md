# Input & output related

Two folders containing the two message generators `logburst.py` and `loggen.py`, 
but also the central server `logserver.py`. Their features are listed below.
If in doubt, you can run the scripts with the `-h` argument to get more details.
## Message generators
Two scripts capable of generating logs are provided, the first one, logburst,
allows to generate a predefined number of messages per second. The second one,
loggen, proposes a message generation close to reality (uses distributions from
a study and a Linux log dataset).

### Logburst

The logburst script can generate a fixed number of messages per second, of a
customizable size per message, and for a predefined duration.
The messages can be assigned sequence numbers to test the quality of the order.
It is also possible to determine a ratio of important messages (low severity) to
classic messages. Finally, one can decide to gradually increase the rate in order
to evaluate the limits of the relay.

### Loggen
The loggen script creates a set of devices (threads) having their own clock and
which generate messages (for a given duration) according to probability distribution.
Several modes are possible, including alternating burst and standby periods.
It is also possible to determine the severity of important messages.
A seed is necessary to start the generation (it is split between each device
to eliminate the random effect introduced by the parallelism).

## Central syslog server
The central server can be quickly set up for testing via the logserver script.
Note that it does not parse nor analyse the received messages in order to offer
a promptness equivalent to a professional service deployed on Internet.

## Logserver
In terms of features, we will mainly note the retrieval of sequence numbers and 
the possibility to save messages in a file if a post-event analysis is required.