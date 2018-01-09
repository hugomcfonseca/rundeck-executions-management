#!/bin/sh

scheduled_time=${SCHEDULE:-"* 0 * * *"}

if [ ${ONETIME_RUNNING} = true ]; then
    mode="/app/run.sh"
else
    echo -n "${scheduled_time}       /bin/bash /app/run.sh >> 2>&1 | tee /var/log/rundeck_cleanup.log" | crontab -
    mode="crond -f -d 7"
fi

exec $mode