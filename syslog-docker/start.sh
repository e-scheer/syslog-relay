#!/usr/bin/env bash

# Instructs the shell to exit if a command yields a non-zero exit status.
set -e

# Flush old logs
if ${AUTO_FLUSH_LOGS}; then
    rm ${CAF_APP_LOG_DIR}/* -f
fi

if [ ! -f "${CAF_APP_CONFIG_FILE}" ]; then
    echo "The app configuration file is missing!"
    exit 1
fi

# Might not be ideal, all variables' input should be validated.
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

# Check that the allocated structures are within the resources capabilities
# alpha=0.25
ALPHA_PERCENT=25
LOG_MEM_SIZE_KB=1

let "qmax = ((100 - $ALPHA_PERCENT) * (${CAF_APP_MEMORY_SIZE_KB})) / ($LOG_MEM_SIZE_KB * 100) "
let "qavail = $qmax - (${QUEUE_WORKER_THREADS} * ${QUEUE_DEQ_BATCH_SIZE})"

if [ "$qavail" -lt "${QUEUE_SIZE}" ]; then
    if [ "$qavail" -lt "0" ]; then
        echo "The maximum queue size ($qmax) is smaller than the dequeue batch size times the number of worker threads, please lower them. You can also increase the queue size AND the IOx memory's resources allocated."
    else
        echo "The maximum queue size with the current IOx memory's resources (${CAF_APP_MEMORY_SIZE_KB}KB) is $qavail and you have encoded ${QUEUE_SIZE}. Please lower the value. You can also increase the IOx memory's resources allocated."
    fi
    exit 1
fi

# Compute the queue discard mark based on the threshold (%)
let "mark = (${QUEUE_DISCARD_THRESHOLD::-1} * ${QUEUE_SIZE}) / 100"
export QUEUE_DISCARD_MARK=$mark

if ${DEBUG_MODE}; then
	RSYSLOG_DEBUG_FLAG="-d"
fi

export INPUT_TO_FILE_PATH="${CAF_APP_LOG_DIR}/input.log"

if [ "${INPUT_TO_FILE}" == "on" ]; then
	export INPUT_TO_REMOTE="off"

else
    export INPUT_TO_REMOTE="on"
fi

set +e

if ! ${USE_JSON_LOGS}; then
    # pipe stderr and stdout to a file
    STDOUT_LOG_PATH="${CAF_APP_LOG_DIR}/out.log"
    touch $STDOUT_LOG_PATH
    chmod 666 $STDOUT_LOG_PATH
    > $STDOUT_LOG_PATH

    STDERR_LOG_PATH="${CAF_APP_LOG_DIR}/err.log"
    touch $STDERR_LOG_PATH
    chmod 666 $STDERR_LOG_PATH
    > $STDERR_LOG_PATH

    exec /usr/sbin/rsyslogd -n $RSYSLOG_DEBUG_FLAG 2> $STDERR_LOG_PATH 1> $STDOUT_LOG_PATH
else
    exec /usr/sbin/rsyslogd -n $RSYSLOG_DEBUG_FLAG
fi