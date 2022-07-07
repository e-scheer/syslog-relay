# syslog-relay

Configuration steps:
1. Generate and drag certificates into docker /certs directory (ensure CN has the proper dnsName of the server, as defined by .conf AuthMode)
2. Configure docker-compose with elastic and central server address (propagate modification through .yml, .yaml, ... files)
3. Download ioxclient
4. Run syslog-docker/build.sh
5. Export .tar to IOx Management