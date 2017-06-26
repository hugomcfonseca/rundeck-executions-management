# rundeck-executions-cleanup
Python script to remove old Rundeck executions and log files.

## Getting started
By default, this script runs without mandatory arguments - it takes predefined values. However, it is possible to pass following parameters:

```
**-h**, --help                          Show this help message and exit
**-c** File, **--config-file** _file_   JSON file with configurations
**--host** _host_                       IP address or domain of Rundeck
**--port** _port_                       Port of Rundeck
**--auth** _token_                      API token with correct permissions
**--api-version** _version_             API version of Rundeck
**--search-time** _seconds_             Time to expire search queries
**--delete-time** _seconds_             Time to expire delete queries
**--keeping-days** _days_               Number of days to keep logs
**--delete-size** _N_                   Number of executions to delete by cycle
**--over-ssl**                          Used when Rundeck is server over HTTPS
**--debug**                             Used to print executed operations
**--execs-by-project**                  Either delete defined range of executions by jobs or projects
```