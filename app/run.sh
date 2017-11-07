#!/bin/sh

OPTS_PARAMS="" 

if [[ $DEBUG = true ]]; then 
    OPTS_PARAMS="$OPTS_PARAMS --debug"
fi

if [[ $RD_SSL = true ]]; then 
    OPTS_PARAMS="$OPTS_PARAMS --ssl-enabled"
fi

exec python /app/executions_management.py \
        --auth "${RD_TOKEN}" \
        --host "${RD_HOST}" \
        --port ${RD_PORT} \
        --execution-mode "${EXEC_MODE}" \
        --db-host "${RD_DB_HOST}" \
        --db-port ${RD_DB_PORT} \
        --db-name "${RD_DB_NAME}" \
        --db-user "${RD_DB_USER}" \
        --db-pass "${RD_DB_PASS}" \
        --filtered-project "${RD_PROJECT}" \
        --api-version ${RD_API_VERSION} \
        --search-timeout ${SEARCH_TIMEOUT} \
        --delete-timeout ${DELETE_TIMEOUT} \
        --keep-time ${KEEP_TIME} \
        --chunk-size ${CHUNK_SIZE} \
        --retries ${RETRY_TIMES} \
        --retry-delay ${RETRY_BACKOFF} \
        ${OPTS_PARAMS}