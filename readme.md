# rundeck-executions-management

Python tool to remove executions data from Rundeck using Rundeck API.

Rundeck API will clean up executions data from both database and filesystem. However, it does not remove all related executions' data from database - it only cleans up data from `base_report` and `execution` tables. This will maintain unnecessary data in database, specifically, in the following database tables: `workflow`, `workflow_step` and `workflow_workflow_step`. To overcome this issue, it was implemented on the script to connect to database and also cleaning up this data.

It is provided two different ways to run old data maintenance in Rundeck:

- **Standalone**: download latest code from `master` branch and execute it from where you may want, or
- **Docker**: launch container to run Rundeck maintenance and exit after finish it or periodically execute it in a cron job (check it in `master-docker` branch for stable version).

## Getting Started

### Standalone

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
  --filtered-job <job>            Filter by a given job UUID
  --api-version <version>         Rundeck API version (default: 20)
  --search-timeout <seconds>      Timeout to expire HTTP GET requests (default: 60)
  --delete-timeout <seconds>      Timeout to expire HTTP POST requests (default: 300)
  --keep-time <time>              Period of time to keep executions records (default: 30d)
  --chunk-size <size>             Size of each delete iteration (default: 200)
  --retries <number>              Number of retries when some error occur (default: 5)
  --retry-delay <seconds>         Delay to start next retry (default: 5)
  --ssl-enabled                   Rundeck is served over SSL (default: false)
  --executions-by-project         Filter executions by project (default: true)
  --unoptimized                   Run all queries in workflows tables (default: false)
  --running                       Filter by only running executions (default: false)
  --debug                         Print all operations (default: false)
```

### Docker

| Env variable | Default  | Required | Description |
| --- | --- | --- | --- |
| `RD_TOKEN` |  | Yes | Rundeck token to access its API |
| `RD_HOST` | `localhost` | Yes | Rundeck host or domain address |
| `RD_PORT` | `4440` | Yes | Rundeck port |
| `RD_SSL` | `false` | Yes | Flag to assign Rundeck is over SSL |
| `RD_DB_HOST` | `mysql-host` | Yes | Host of Rundeck database |
| `RD_DB_PORT` | `3306` | Yes | Port of Rundeck database |
| `RD_DB_NAME` | `rundeck` | Yes | Name of Rundeck database |
| `RD_DB_USER` | `rundeck` | Yes | User name of Rundeck database |
| `RD_DB_PASS` |  | Yes | User's password of Rundeck password |
| `KEEP_TIME` | `30d` | Yes | Period of time to keep executions records |
| `CHUNK_SIZE` | `200` | Yes | Size of each delete iteration |
| `RD_API_VERSION` | `20` | Yes | Rundeck API version |
| `RD_PROJECT` |  | No | Run cleanup to a given project |
| `SEARCH_TIMEOUT` | `60` | No | Timeout to expire HTTP GET requests (in _seconds_) |
| `DELETE_TIMEOUT` | `300` | No | Timeout to expire HTTP POST requests (in _seconds_) |
| `RETRY_TIMES` | `5` | No | Number of retries when some error occur |
| `RETRY_BACKOFF` | `5` | No | Delay to start next retry (in _seconds_) |
| `DEBUG` | `false` | No | Used to print all operations during clean up  |
| `RD_DB_UNOPTIMIZED` | `false` | No | Assign to true when database queries below were not run |
| `ONETIME_RUNNING` | `false` | No | Running mode of script (**run & exit** or by a **cron**) |
| `SCHEDULE` | `* 0 * * *` | No | Time schema which script may run (in cron mode) |

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

### Standalone

#### 1. Cleanup old records with default arguments' values (local Rundeck server)

```sh
$ python executions_management.py --auth YOUR_TOKEN
```

#### 2. Cleanup old records in a remote Rundeck server (available over SSL)

```sh
$ python executions_management.py --auth-token YOUR_TOKEN --host rundeck.domain.com --port 443 --ssl-enabled
```

### Docker

#### 1. Launch a container to run maintenance periodically

```sh
$ docker run -it -d --name rundeck-maintenance --link rundeck_db:mysql-host \
    -e RD_TOKEN="SECRET_TOKEN" \
    -e RD_DB_PASS="SECRET_DB_PASS" \
    hugomcfonseca/rundeck-executions-cleanup:latest
```

#### 2. Launch a container to run maintenance once

```sh
$ docker run -it -d --name rundeck-maintenance --link rundeck_db:mysql-host \
    -e RD_TOKEN="SECRET_TOKEN" \
    -e RD_DB_PASS="SECRET_DB_PASS" \
    -e ONETIME_RUNNING="true" \
    hugomcfonseca/rundeck-executions-cleanup:latest
```

Please notice, if you don't want to create a linked connection to Rundeck database, you are able to specify it using environment variables.