# rundeck-executions-management

Python script to execute remote operations on Rundeck. Available operations are: cleanup of old executions (both on database and filesystem) and executions listing.

## Getting Started

By default, this script needs at least one parameter: a valid token. Others parameters are assumed by default and can be overriden. Next, it is showed all available parameters:

```sh
  -h, --help                        Show this help message and exit
  -a Token, --auth Token            Rundeck token
  -t Domain, --host Domain          Rundeck host or domain (default: localhost)
  -p Port, --port Port              Rundeck port (default: 4440)
  -m Mode, --execution-mode Mode    Select operation to run this project (default: cleanup)
  --filtered-project Project        Filter by a given project
  --api-version Version             Rundeck API version (default: 19)
  --search-timeout Seconds          Timeout to expire HTTP GET requests (default: 60)
  --delete-timeout Seconds          Timeout to expire HTTP POST requests (default: 300)
  --keep-time Time                  Period of time to keep executions records (default: 30d)
  --retries Number                  Number of retries when some error occur (default: 5)
  --retry-delay Seconds             Delay to start next retry (default: 5)
  --chunk-size Size                 Size of each delete iteration (default: 200)
  --ssl-enabled status              Rundeck is served over SSL (default: false)
  --executions-by-project status    Filter executions by project (default: true)
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