# Grantor

Make our athletic wrapped SebNin happy-to-work again!

## Description

This project enables one to read mysql permissions from the [perms repo](http://gitlab.virtual-expo.com/sql/perms) and update a chosen mysql instance.
A single user permissions can be applied, or all users can be updated as well.

**Be extremely careful to update the perms repo local copy before applying permissions!**

## Requirements
* Python 3
* Pymysql (from the package python3-pymysql or the pymysql pip module)

## Usage

```
grantor.py [-h] -s SERVER [-u USER] -p PASSWD -P PERMSDIR [-v] -f FUNCTIONS_LIST [-U SINGLE_USER] [-n]
```

## Options

 Name | Example | Description 
 -- | -- | --
 -h, --help | | show this help message and exit
 -s SERVER, --server SERVER | -s velo1dblx01 | address or hostname of the MySQL server
 -u USER, --user USER | -u grantor | username to authenticate with
 -p PASSWD, --passwd PASSWD | -p MyPassword | password of the user to authenticate with
 -P PERMSDIR, --permsdir PERMSDIR | -P ../perms | path to the perms repo copy
 -v, --verbose | -v | verbose mode
 -f FUNCTIONS_LIST, --function FUNCTIONS_LIST | -f common,site | list of functions of the mysql instance
 -U SINGLE_USER, --single-user SINGLE_USER | -U app_dealers_bt | upadte a single user
 -n, --noop | -n | noop mode: only show changes
