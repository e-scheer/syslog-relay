Central server features:
- Simulates downtime
- Create latency/packet loss
- Statistics:
  - Count number of syslog (by period ?)
  - Count by level of message (percent of sent vs received)

- Handle multiple clients:
  - - See if order guarenteed (using timestamp)


Client/IOT emulated features:
- Random GMT
- Loi de poisson pour les messages
- Taille des messages (rate/size/interval)
- taileldu cluster ?


client vs server comparator:
- compare values
- plots

3 "measures" (mostly counters):
- IOTs
- Central server
- cisco router: statistics of Internal Counters aka process statistics (https://www.rsyslog.com/doc/v8-stable/configuration/modules/impstats.html#impstats-statistic-counter): queue state (size, discarded messages, ...), 

Aim of tests:
- verifier si key objectives sont maintenu
- Determine router capacity
- Find best config for cisco (CPU & mem max value) and rsyslog (array vs linkedlist, discard threshold, discard severity)
- Variable tweaking of cisco config:  AND rsyslog config: 

Type of tests:
- lost packets (which ones)
- packet ordering