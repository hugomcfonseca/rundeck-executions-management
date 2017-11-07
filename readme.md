# rundeck-executions-management

Python script to remove old Rundeck executions and log files. Altought, due with Rundeck API only does clean up of `base_report` and `execution1` tables, it was implemented cleanup of missing data from other tables of Rundeck database - `workflow`, `workflow_step` and `workflow_workflow_step`.

Also, it was implemented a feature to list Rundeck executions.

## Getting Started

By default, this script needs at least one parameter: a valid token. Others parameters are assumed by default and can be overriden. Next, it is showed all available parameters:

```sh
  -h, --help                        Show this help message and exit
  -a Token, --auth Token            Rundeck token
  -t Domain, --host Domain          Rundeck host or domain (default: localhost)
  -p Port, --port Port              Rundeck port (default: 4440)
  -m Mode, --execution-mode Mode    Select operation to run this project (default: cleanup)
  --db-host Host                    Rundeck database host (default: mysql-host)
  --db-port Port                    Rundeck database port (default: 3306)
  --db-name Database                Rundeck database name (default: rundeck)
  --db-user User                    Rundeck database user (default: rundeck)
  --db-pass Password                Rundeck database password
  --filtered-project Project        Filter by a given project
  --api-version Version             Rundeck API version (default: 19)
  --search-timeout Seconds          Timeout to expire HTTP GET requests (default: 60)
  --delete-timeout Seconds          Timeout to expire HTTP POST requests (default: 300)
  --keep-time Time                  Period of time to keep executions records (default: 30d)
  --chunk-size Size                 Size of each delete iteration (default: 200)
  --retries Number                  Number of retries when some error occur (default: 5)
  --retry-delay Seconds             Delay to start next retry (default: 5)
  --ssl-enabled                     Rundeck is served over SSL (default: false)
  --executions-by-project           Filter executions by project (default: true)
  --debug                           Print all operations (default: false)
```

## Usage

### **#1:** Cleanup old records with default arguments' values (local Rundeck server)

```sh
$ python executions_management.py --auth YOUR_TOKEN
```

### **#2:** Cleanup old records in a remote Rundeck server (available over SSL)

```sh
$ python executions_management.py --auth-token YOUR_TOKEN --host rundeck.domain.com --port 443 --ssl-enabled
```

### **#3:** Listing running executions on all projects (local Rundeck server)

```sh
$ python executions_management.py --auth YOUR_TOKEN --mode listing --only-running
```

### **#4:** Listing executions on by project and job name older than a given time amount (local Rundeck server)

```sh
$ python executions_management.py --auth YOUR_TOKEN --mode listing --filtered-project PROJECT_NAME --filtered-job JOB_NAME --keep-time TIME
```