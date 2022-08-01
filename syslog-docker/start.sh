#!/usr/bin/env bash

if [ ! -f "${CAF_APP_CONFIG_FILE}" ]; then
    echo "The app configuration file is missing!"
    exit 1
fi

set -a                                      # Turn on automatic export
source <(grep = ${CAF_APP_CONFIG_FILE})     # Execute all commands in the file
set +a                                      # Turn off automatic export

# Ensures files in datadir are present
export CA_CERT_FILE=${CAF_APP_APPDATA_DIR}"/"${CA_CERT_FILE}
export CLIENT_CERT_FILE=${CAF_APP_APPDATA_DIR}"/"${CLIENT_CERT_FILE}
export CLIENT_KEY_FILE=${CAF_APP_APPDATA_DIR}"/"${CLIENT_KEY_FILE}

if [ ! -f "${CA_CERT_FILE}" ]; then
    echo "The CA certificate file is missing!"
    exit 1
fi

if [ ! -f "${CLIENT_CERT_FILE}" ]; then
    echo "The client certificate file is missing!"
    exit 1
fi

if [ ! -f "${CLIENT_KEY_FILE}" ]; then
    echo "The client key file is missing!"
    exit 1
fi


if ${DEBUG_MODE}; then
	RSYSLOG_DEBUG_FLAG="-d"
fi

exec /usr/sbin/rsyslogd -n $RSYSLOG_DEBUG_FLAG