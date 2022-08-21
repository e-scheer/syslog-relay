# Utilities and comments

Set of utilities and comments used during the deployment of this project.
In particular the python scripts used to study and analyse the received data (and dataset),
but also useful commands used during the tests.
A basic procedure for testing the environment is also provided.

## Testflow
I recommend the use of this testflow to avoid any problem or misunderstanding.

1. Start the server, ensure it is operational.
3. Activate the IOx application, configure it (set the parameters, statistics enabled or not, server's IP, ...), then start it.
2. Launch Kibana & Elasticsearch service (if the statistics module is enabled).
4. Configure the traffic controller (through advanced mode to isolate flow otherwise it might reset). Except for the bandwidth, only set configuration on one interface.
5. Connect to the Iox application using `ssh cisco@<ip>` followed by `app-hosting connect app <app-name> session`.
6. Ensure the traffic controller is working.
5. Run one of the two message generator.


### Fields inside Kibana

List of fields available inside Kibana (if the statistics module is enabled).
Please first isolate the data.name of interest (main queue, forwarding action ...) as fields attributes collide.


#### Input related (UDP)
- submitted - total number of messages submitted for processing since startup.
- disallowed - total number of messages discarded due to disallowed sender.
- called.recvmmsg - number of recvmmsg() OS calls done.
- msgs.received - number of actual messages received.

--------
#### Forwarding action
- processed - messages processed by this action.
- failed - number of messages this action failed to process.
- suspended - number of times this action was suspended.
- suspended_duration - amount of time this action has spent in a suspended state.
- resumed - number of times this action has resumed from a suspended state.

#### Main queue
- size - messages currently in queue.
- enqueued - total messages enqueued during lifetime of queue.
- full - number of times the queue was full.
- discarded_full - number of times messages were discarded due to the queue being full.
- discarded_not_full - number of times messages discarded but queue was not full.
- max_queue_size - maximum size the queue reached during its lifetime.

--------
### Resources related
- utime - user time used in microseconds.
- stime - system time used in microseconds.
- maxrss - maximum resident set size.
- minflt - total number of minor faults.
- majflt - total number of major faults.
- inblock - number of filesystem input operations.
- oublock - number of filesystem output operations.
- nvcsw - number of voluntary context switches.
- nivcsw - number of involuntary context switches.
