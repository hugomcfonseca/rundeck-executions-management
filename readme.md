# rundeck-executions-cleanup
Python script to remove old Rundeck executions and log files.

## Getting started
By default, this script runs without mandatory arguments - it takes predefined values. However, it is possible to pass following parameters:

```
-h, --help                          Show this help message and exit
-c File, --config-file file   JSON file with configurations
--host host                       IP address or domain of Rundeck
--port port                       Port of Rundeck
--auth token                      API token with correct permissions
--api-version version             API version of Rundeck
--search-time seconds             Time to expire search queries
--delete-time seconds             Time to expire delete queries
--keeping-days days               Number of days to keep logs
--delete-size N                   Number of executions to delete by cycle
--over-ssl                          Used when Rundeck is server over HTTPS
--debug                             Used to print executed operations
--execs-by-project                  Either delete defined range of executions by jobs or projects
```