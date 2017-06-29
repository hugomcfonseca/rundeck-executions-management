# rundeck-executions-cleanup
Python script to remove old Rundeck executions and log files.

## Getting started
By default, this script needs at least one of two parameters: a configuration file or a valid token. Others parameters are assumed by default and can be overriden. Next, it is showed all available parameters:

```
-h, --help                          Show this help message and exit
-c or --config-file file            JSON file with configurations
--host host                         IP address or domain of Rundeck (default: localhost)
--port port                         Port of Rundeck (default: 4440)
--auth token                        API token with correct permissions
--api-version version               API version of Rundeck (default: 19)
--search-time seconds               Time to expire search queries (default: 60)
--delete-time seconds               Time to expire delete queries (default: 1200)
--keeping-days days                 Number of days to keep logs (default: 21)
--delete-size N                     Number of executions to delete by cycle (default: 1000)
--over-ssl                          Used when Rundeck is server over HTTPS (default: no)
--debug                             Used to print executed operations (default: no)
--execs-by-project                  Either delete defined range of executions by jobs or projects (default: no)
```

## Configuration file
The configuration file used by the script must follow JSON format and have, at least, the _token_ key. Next, it is presented its format and all available keys:

```json
{
    "hostname": <rundeck_host>,
    "port": <rundeck_port>,
    "token": <rundeck_token>,
    "api_version": <api_version>,
    "search_time": <max_time_to_read>,
    "delete_time": <max_time_to_delete>,
    "keeping_days": <days_to_keep>,
    "delete_size": <bulk_size>,
    "over_ssl": <boolean>,
    "debug": <boolean>,
    "execs_by_project": <boolean>
}
```

## Usage
**Executing script with a configuration file:**
```
$ python RundeckExecutionsCleanup.py -c my_confs.json
```

**Execution script without a configuration file and assuming all default values are correct:**
```
$ python RundeckExecutionsCleanup.py --auth-token MYTOKEN
```