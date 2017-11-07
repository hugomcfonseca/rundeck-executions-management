FROM alpine:3.6

LABEL maintainer="Hugo Fonseca <https://github.com/hugomcfonseca>"

ENV \
    PKGS="python py-requests" \
    DEPS="curl mysql-dev gnupg file gcc python-dev musl-dev g++" \
    MYSQL_CONN_VERSION="2.1.7" \
    \
    RD_TOKEN="" \
    RD_HOST="localhost" \
    RD_PORT="4440" \
    RD_SSL=false \
    RD_API_VERSION="20" \
    RD_PROJECT="" \
    RD_DB_HOST="mysql-host" \
    RD_DB_PORT="3306" \
    RD_DB_NAME="rundeck" \
    RD_DB_USER="rundeck" \
    RD_DB_PASS="" \
    EXEC_MODE="cleanup" \
    SEARCH_TIMEOUT="60" \
    DELETE_TIMEOUT="300" \
    KEEP_TIME="30d" \
    RETRY_TIMES="5" \
    RETRY_BACKOFF="5" \
    CHUNK_SIZE="200" \
    DEBUG=false

RUN \
    apk add --update --no-cache ${PY_PKGS} && \
    apk add --update --no-cache --virtual .deps ${DEPS} && \
    curl -sSL http://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-${MYSQL_CONN_VERSION}.tar.gz -o /tmp/mysql-connector-python-${MYSQL_CONN_VERSION}.tar.gz && \
    tar xfz /tmp/mysql-connector-python-${MYSQL_CONN_VERSION}.tar.gz -C /tmp && \
    cd /tmp/mysql-connector-python-${MYSQL_CONN_VERSION} && \
    python /tmp/mysql-connector-python-${MYSQL_CONN_VERSION}/setup.py install --with-mysql-capi=$(which mysql_config) && \
    cd - && \
    rm -rf /tmp/mysql-connector-python-${MYSQL_CONN_VERSION}* && \
    apk del .deps && rm -rf /var/cache/apk/* /tmp/* /var/tmp/*

COPY app/ /app

WORKDIR /app

CMD \
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
        --ssl-enabled ${RD_SSL} \
        --debug ${DEBUG}