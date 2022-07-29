#!/bin/bash

: <<'END'
Cisco Device setup:
Enable HTTPS secure server connection on this device's IOS config.

Developer machine setup(laptop/PC):
a. Set environment variables,
   $ export DOCKER_HOST=<externally reachable cisco device IP>:443
   $ export DOCKER_TLS=1
   $ export DOCKER_API_VERSION=1.37 
b. Run below cmd to retrieve server ca cert and store it in dir $HOME/.docker/ for macOS/Linux (use dir %USERPROFILE%/.docker for Windows).  

   $ echo | openssl s_client  -connect $DOCKER_HOST 2>/dev/null | openssl x509 -text -out $HOME/.docker/ca.pem

c. Add HttpHeaders entry as below into docker config file at $HOME/.docker/config.json. If the file doesn't exist then create json file with just HttpHeaders entry.
   Base64 encode the cisco device username and password string using 
   $ echo -n 'device_username:device_passwd' | base64 - 
  and include the base64 encoded value as part of Basic Auth configuration in config.json.  
{
   ....
   "HttpHeaders": {
       "Authorization": "Basic YOUR_BASE64_ENCODED_VALUE"
   }
   ....
}
d. Now you can access docker engine on this device remotely from development machine, Try cmd: docker info 
e. To reset, unset env variables DOCKER_HOST, DOCKER_TLS and DOCKER_API_VERSION
END

export DOCKER_HOST=192.168.1.12:443
export DOCKER_TLS=1
export DOCKER_API_VERSION=1.37 

echo | openssl s_client  -connect $DOCKER_HOST 2>/dev/null | openssl x509 -text -out $HOME/.docker/ca.pem

echo -n 'cisco:cisco' | base64 - 