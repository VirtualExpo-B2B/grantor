# Grantor

## MySQL Grants as Code


Grantor is a DevOps tool, developped in [VirtualExpo](http://www.virtual-expo.com/), to manage MySQL users. It enables a team to collaborate on MySQL grants: developpers can add users or modify permissions at will, and using a [Git workflow](https://www.atlassian.com/git/tutorials/comparing-workflows), their commits can be brought into the CI and finally up to production, using merge requests and code revues. Because the grants are managed just as code, traceability is not compromised and rollbacks are always permitted.

The principle consists in writing all the grants into an external Git repository, from which Gantor reads. Just like a Puppet code repo, a **runnning** MySQL instance can then be updated to match the permission described in our repo.

Also, in the case of replicated MySQL instances, Grantor only needs to be applied once. 

## Requirement
* A MySQL user to connect with, which has the [grant option](https://dev.mysql.com/doc/refman/5.5/en/privileges-provided.html#priv_grant-option) and [reload](https://dev.mysql.com/doc/refman/5.5/en/privileges-provided.html#priv_reload) privileges.

## Installation

### Bare metal

What you need:
* Python 3
* PyMySQL (from the package `python3-pymysql`, or using `pip install PyMySQL`)

Just clone the repository: `git clone https://github.com/mysql-grantor/grantor.git`

### Docker container

A Docker container is available on the Docker Hub:
```bash
docker pull virtualexpo/grantor:1.4.4
```

If you wish, you can also build it your self:
```bash
docker build -t grantor .
```

## Usage
### Bare metal

```
./grantor.py [OPTIONS]
```
### Docker container
```bash
docker run -v <permissions_dir>:/usr/src/perms virtualexpo/grantor:1.4.4 [OPTIONS]
```

`<permissions_dir>:` the path on your local filesystem where the MySQL grants are written. This directory is fully described in [a later section](#the-mysql-permissions-directory). It is often refered to as a repository, since the major advantage of Grantor is to use a Git workflow to manage MySQL grants.

## Options

### Authentication

Name | Description 
-- | --
`-s , --server` | **Required:** IP address or hostname of the MySQL server
`-u , --user` | **Required:** MySQL user to authenticate with
`-p , --passwd` | **Required:** password of the authentication user

### Permissions directory
*These options are available only for a bare metal installation.*

Name | Description 
-- | --
`-P , --permsdir` | Path to the [permissions directory](#the-mysql-permissions-directory), or path to clone the repository to if -R and optionnally -b are given
`-R , --repository` | Git clone url of your permissions repository. To yous this option, you need to be able to clone your repository without being prompted for a password, using [git-credential-store](https://git-scm.com/docs/git-credential-store) for example.
`-b , --branch` | Git branch to checkout to after cloning the repository

### Other
Name | Description 
-- | --
`-U , --single-user` | Create, update or remove a single user
`-f , --function` | List of [functions](#tree-description) (separated by a comma) of the MySQL instance
`-n, --noop` | Noop mode: perform a dry-run and report non-compliant permissions
`-v, --verbose` | Verbose
`-h, --help` | Show this help message and exit

## The MySQL permissions directory

This repository describes the MySQL permissions of the database servers you manage with Grantor.

### Tree Description
```
.
+-- function_example
    +-- user_example
        +-- global_perms
        +-- databases
        |   +-- database1
        |   |   +-- perms
        |   |   +-- tables
        |   |       +-- table1
        |   +-- database2
        |   |   +-- tables
        |   |       +-- table2
        |   |       +-- table3
        +-- hosts
        |   +-- dev
        |   +-- staging
        |   +-- preprod
        |   +-- prod
        +-- passwords
        |   +-- dev
        |   +-- staging
        |   +-- preprod
        |   +-- prod
```


1. At the first level lie what we call "functions": they describe the roles of your instances. Several functions can be applied on the same server. For example, if you define the same subset of users (backup, etc) on all your database servers, they can be described in a 'common' function, applied on each instance.

Functions can also be merged in case you restore several production MySQL instances on a single integration server for example.

2. Each function contains one directory per MySQL user.

3. Permissions are then desctibed on a per-user basis. There are three types of permissions:

  - Global permissions: `GRANT ... ON *.* TO ...`
    Those are stored in the `global_perms` file.
  - Per-database permissions: `GRANT ... ON db.* TO ...`
    Those are stored in `databases/$db_name/perms`
  - Per-table permissions: `GRANT ... ON db.table TO ...`
    Those are stored in `databases/$db_name/tables/$table_name`

The way permissions should be written is discussed [later](#writing-permissions).

4. Then, the `hosts` directory contains one file per environment type.
Each file contains a list of what we call `meta-hosts`, defining the allowed IP
sources for the user.

5. Finally, the `passwords` directory has the same layout as the `hosts` directory and contains hashes of
the passwords used to authenticate the user for each environment.


#### Writing permissions
Global permissions and per-database permissions are described using
one line per privilege, a semicolon, and a `Y` or a `N`.
```bash
Select_priv: Y
Insert_priv: Y
Update_priv: Y
Delete_priv: Y
Create_priv: Y
Drop_priv: Y
Reload_priv: N
Shutdown_priv: N
Process_priv: N
File_priv: Y
Grant_priv: N
References_priv: N
Index_priv: Y
Alter_priv: Y
Show_db_priv: Y
Super_priv: N
Create_tmp_table_priv: Y
Lock_tables_priv: Y
Execute_priv: N
Repl_slave_priv: N
Repl_client_priv: N
Create_view_priv: N
Show_view_priv: Y
Create_routine_priv: Y
Alter_routine_priv: Y
Create_user_priv: N
Event_priv: N
Trigger_priv: N
Create_tablespace_priv: N
```

Per-table permissions are stored as a one-per-line set of privileges:

```bash
Select
Insert
Update
Delete
Drop
Grant
References
Index
Alter
Create View
Show view
Trigger
```

#### Tree Version / changelog

  - 1.2: implement support for the `staging` environment using symlinks
  - 1.1: rewrite per-table permissions using one permission per line instead
         of comma-separated; `Create` is now added implicitely by Grantor.
  - 1.0: initial version

