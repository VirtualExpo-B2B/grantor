# Grantor

## MySQL Grants as Code


Grantor is a DevOps tool, developped in [VirtualExpo](http://www.virtual-expo.com/), to manage MySQL users. It enables a team to collaborate on MySQL grants: developpers can add users or modify permissions at will, and using a [Git workflow](https://www.atlassian.com/git/tutorials/comparing-workflows), their commits can be brought into the CI and finally up to production, using merge requests and code revues. Because the grants are managed just as code, traceability is not compromised and rollbacks are always permitted.

The principle consists in writing all the grants into an external Git repository, from which Gantor reads. Just like a Puppet code repo, a **runnning** MySQL instance can then be updated to match the permission described in our repo.

Also, in the case of replicated MySQL instances, Grantor only needs to be applied once. 

## Requirement
* A MySQL user to connect with, which has the [grant option](https://dev.mysql.com/doc/refman/5.5/en/privileges-provided.html#priv_grant-option) and [reload](https://dev.mysql.com/doc/refman/5.5/en/privileges-provided.html#priv_reload) privileges

## Installation

### Bare metal

What you need:
* Python 3
* PyMySQL (from the package `python3-pymysql`, or using `pip install PyMySQL`)

Just clone the repository: `git clone https://github.com/mysql-grantor/grantor.git`

### Docker

A Docker container is available on the Docker Hub:
```bash
docker pull virtualexpo/grantor:1.4.4
```

### Building the container
You can also build it your self running:
```bash
docker build -t grantor .
```

## Usage

```
grantor.py [-h] -s SERVER [-u USER] -p PASSWD [-P PERMSDIR] [-R REPOSITORY] [-b BRANCH] -f FUNCTIONS_LIST [-U SINGLE_USER] [-n] [-v]
```

## Options

 Name | Example | Description 
 -- | -- | --
 -h, --help | | show this help message and exit
 -s SERVER, --server SERVER | -s velo1dblx01 | address or hostname of the MySQL server
 -R REPOSITORY, --repository REPOSITORY | -R http://gitlab.virtual-expo.com/sql/perms.git | path to the perms repository
 -b BRANCH, --branch BRANCH | -b feature-24328 | branch to checkout after cloning the repository
 -u USER, --user USER | -u grantor | username to authenticate with
 -p PASSWD, --passwd PASSWD | -p MyPassword | password of the user to authenticate with
 -P PERMSDIR, --permsdir PERMSDIR | -P ../perms | path to the perms repo copy, or path to clone the repository to in case -R/-b is given
 -f FUNCTIONS_LIST, --function FUNCTIONS_LIST | -f common,site | list of functions of the mysql instance
 -U SINGLE_USER, --single-user SINGLE_USER | -U app_dealers_bt | update (or remove) a specific user
 -n, --noop | -n | noop mode: perform a dry-run and report non-compliant permissions
 -v, --verbose | -v | verbose mode
