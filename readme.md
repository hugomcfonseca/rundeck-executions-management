# rundeck-executions-management

Python script to remove Rundeck executions data using Rundeck API.

Rundeck API will clean up executions data from both database and filesystem. However, it does not remove all related executions' data from database - it only cleans up data from `base_report` and `execution` tables. This will maintain unnecessary data in database, specifically, in the following database tables: `workflow`, `workflow_step` and `workflow_workflow_step`. To overcome this issue, it was implemented on the script to connect to database and also cleaning up this data.

## Getting Started

By default, this script needs at least one parameter: a valid token. Others parameters are assumed by default and can be overriden. Next, it is showed all available parameters:

```sh
  -h, --help                      Show this help message and exit
  -a, --auth <token>              Rundeck token
  -t, --host <domain>             Rundeck host or domain (default: localhost)
  -p, --port <port>               Rundeck port (default: 4440)
  -m, --execution-mode <mode>     Select operation to run this project (default: cleanup)
  --db-host <host>                Rundeck database host (default: mysql-host)
  --db-port <port>                Rundeck database port (default: 3306)
  --db-name <database>            Rundeck database name (default: rundeck)
  --db-user <user>                Rundeck database user (default: rundeck)
  --db-pass <password>            Rundeck database password
  --filtered-project <project>    Filter by a given project
  --api-version <version>         Rundeck API version (default: 19)
  --search-timeout <seconds>      Timeout to expire HTTP GET requests (default: 60)
  --delete-timeout <seconds>      Timeout to expire HTTP POST requests (default: 300)
  --keep-time <time>              Period of time to keep executions records (default: 30d)
  --chunk-size <size>             Size of each delete iteration (default: 200)
  --retries <number>              Number of retries when some error occur (default: 5)
  --retry-delay <seconds>         Delay to start next retry (default: 5)
  --ssl-enabled                   Rundeck is served over SSL (default: false)
  --executions-by-project         Filter executions by project (default: true)
  --debug                         Print all operations (default: false)
```

## Tuning Rundeck database to speed up its cleaning

If you are experiencing some slowness in Rundeck cleanup, probably you are missing some changes you should do in Rundeck database.

```sql
-- Change columns type from base_report table
ALTER TABLE `base_report` MODIFY COLUMN `jc_exec_id` int(11) unsigned;
ALTER TABLE `base_report` MODIFY COLUMN `jc_job_id` int(11) unsigned;
 
-- Add indexes to `base_report` and `execution` tables
ALTER TABLE `base_report` ADD INDEX `BASE_REPORT_IDX_3` (`jc_exec_id`);
ALTER TABLE `base_report` ADD INDEX `BASE_REPORT_IDX_4` (`class`);
ALTER TABLE `base_report` ADD INDEX `BASE_REPORT_IDX_5` (`version`);
ALTER TABLE `execution` ADD INDEX `EXEC_IDX_0` (`version`);
ALTER TABLE `execution` ADD INDEX `EXEC_IDX_5` ( `retry_execution_id` );
 
-- Update existing foreign keys to have DELETE ON CASCADE
ALTER TABLE `workflow_step` DROP FOREIGN KEY `FK_8bbf05v4f6vo5o3cgp69awcue`;
ALTER TABLE `workflow_step` ADD CONSTRAINT `FK_8bbf05v4f6vo5o3cgp69awcue` FOREIGN KEY(`error_handler_id`) REFERENCES workflow_step(`id`) ON DELETE CASCADE;
ALTER TABLE `workflow_workflow_step` DROP FOREIGN KEY `FK_9pkey6k5fdo6worgquakkh7d1`;
ALTER TABLE `workflow_workflow_step` ADD CONSTRAINT `FK_9pkey6k5fdo6worgquakkh7d1` FOREIGN KEY(`workflow_step_id`) REFERENCES workflow_step(`id`) ON DELETE CASCADE;
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