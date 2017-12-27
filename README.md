# Grantor

The MySQL Grantor is Virtual Expo's tool to apply user permissions to a running MySQL instance.

## Description

This program updates permissions on a MySQL instances from a repository listing all users and their grants.
The Virtual Expo's permission repository lies at http://gitlab.virtual-expo.com/sql/perms

The program can either work on a local copy of the git ```perms``` repository, or work from a freshly
cloned copy.

## Requirements
* Python 3
* PyMySQL (from the package ```python3-pymysql```, or using ```pip install PyMySQL```)

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
 -b BRANCH, --branc BRANCH | -b feature-24328 | branch to checkout after cloning the repository
 -u USER, --user USER | -u grantor | username to authenticate with
 -p PASSWD, --passwd PASSWD | -p MyPassword | password of the user to authenticate with
 -P PERMSDIR, --permsdir PERMSDIR | -P ../perms | path to the perms repo copy, or path to clone the repository to in case -R/-b is given
 -f FUNCTIONS_LIST, --function FUNCTIONS_LIST | -f common,site | list of functions of the mysql instance
 -U SINGLE_USER, --single-user SINGLE_USER | -U app_dealers_bt | update (or remove) a specific user
 -n, --noop | -n | noop mode: perform a dry-run and report non-compliant permissions
 -v, --verbose | -v | verbose mode
