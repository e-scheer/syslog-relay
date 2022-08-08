#!/usr/bin/env bash

export QUEUE_SIZE=50000
export QUEUE_DISCARD_THRESHOLD=80%

export CAF_APP_MEMORY_SIZE_KB=32000

export QUEUE_WORKER_THREADS=8
export QUEUE_DEQ_BATCH_SIZE=5024

#alpha=0.25
ALPHA_MULT_INV=4 
LOG_MEM_SIZE_KB=1

let "qmax = (($ALPHA_MULT_INV - 1) * (${CAF_APP_MEMORY_SIZE_KB})) / ($LOG_MEM_SIZE_KB * $ALPHA_MULT_INV) "
let "qavail = $qmax - (${QUEUE_WORKER_THREADS} * ${QUEUE_DEQ_BATCH_SIZE})"

if [ "$qavail" -lt "${QUEUE_SIZE}" ]; then
    if [ "$qavail" -lt "0" ]; then
        echo "The maximum queue size ($qmax) is smaller than the dequeue batch size times the number of worker threads, please lower them. You can also increase the queue size AND the IOx memory's resources allocated."
    else
        echo "The maximum queue size with the current IOx memory's resources (${CAF_APP_MEMORY_SIZE_KB}KB) is $qavail and you have encoded ${QUEUE_SIZE}. Please lower the value. You can also increase the IOx memory's resources allocated."
    fi
    exit 1
fi

let "mark = (${QUEUE_DISCARD_THRESHOLD::-1} * ${QUEUE_SIZE}) / 100"
export QUEUE_DISCARD_MARK=$mark