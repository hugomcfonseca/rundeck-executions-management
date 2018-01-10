FROM alpine:3.7

LABEL maintainer='Hugo Fonseca <https://github.com/hugomcfonseca>'

WORKDIR /app

ENV \
    PKGS='python py-requests' \
    DEPS='mysql-dev gnupg file gcc py-pip musl-dev g++' \
    MYSQL_CONN_VERSION='2.1.7' \
    \
    RD_TOKEN='' \
    RD_HOST='localhost' \
    RD_PORT='4440' \
    RD_SSL=false \
    RD_API_VERSION='20' \
    RD_PROJECT='' \
    RD_DB_HOST='mysql-host' \
    RD_DB_PORT='3306' \
    RD_DB_NAME='rundeck' \
    RD_DB_USER='rundeck' \
    RD_DB_PASS='' \
    EXEC_MODE='cleanup' \
    SEARCH_TIMEOUT='60' \
    DELETE_TIMEOUT='300' \
    KEEP_TIME='30d' \
    RETRY_TIMES='5' \
    RETRY_BACKOFF='5' \
    CHUNK_SIZE='200' \
    DEBUG=false \
    \
    RD_DB_UNOPTIMIZED=false \
    ONETIME_RUNNING=false \
    SCHEDULE='* 0 * * *'

COPY app/ /app
COPY entrypoint.sh /

RUN \
    apk add --update --no-cache ${PKGS} && \
    apk add --update --no-cache --virtual .deps ${DEPS} && \
    pip install -U pip wheel && \
    pip install http://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-${MYSQL_CONN_VERSION}.tar.gz && \
    chmod +x /app/run.sh /entrypoint.sh && \
    apk del .deps && rm -rf /var/cache/apk/* /tmp/* /var/tmp/*

CMD /entrypoint.sh