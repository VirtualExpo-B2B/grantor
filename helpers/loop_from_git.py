#!/usr/bin/env python3
#coding: utf8

import argparse
import os, sys
from helpers.common import *
from helpers.check_foo import *
from helpers.update_user_priv import *

dry_run = False

# returns an array of SQL hosts for a {function,user,envtype,envid} "couple"
def get_local_user_hosts(permsdir, function, user, envtype,envid):

    result=[]
    # FIXME: shit to prevent an error where the host file is not present for the environment
    try:
        meta_hostlist = quick_read(makepath(permsdir, function, user, 'hosts', envtype)).split('\n')
        for meta_host in meta_hostlist:
            list = get_hosts_from_meta(envtype, envid, meta_host)
            if len(list) > 1:
                for item in list:
                    result.append(item)
            else:
                result.append(list[0])
    except:
        logv("can't find the meta_host file %s" % makepath(permsdir, function, user, 'hosts', envtype))

    return result


def ensure_global_perms(conn, permsdir, function, user, envtype, envid):
    global_perms = quick_read(makepath(permsdir, function, user, 'global_perms'))
    global_perms_content = []
    for line in global_perms.strip().split("\n"):
        global_perms_content.append(line.split(': '))

    logv("checking perms for %s" % ( user ) )

    sql_hostlist = get_local_user_hosts(permsdir, function, user, envtype, envid)

    if len(sql_hostlist) == 0:
        logv("user %s does not exist on env %s" % (user, envtype))
    else:
        for host in sql_hostlist:
            logv("in-sql: working on %s@%s" % ( user, host ) )
            if not check_global_perms_ok(conn, user, host, global_perms_content):
                logv("%s@%s: fixing permissions" % ( user, host ))
                apply_global_perms(conn, user, host, global_perms_content)
            else:
                logv("%s@%s: perms OK, congrats" % ( user, host ) )

            password = quick_read(makepath(permsdir, function, user, 'passwords', envtype))
            if not check_user_password(conn, user, host, password):
                apply_user_password(conn, user, host, password)

def ensure_db_perms(conn, permsdir, function, user, host, db):
    logv('checking db %s permissions for user %s@%s' % (db, user, host))
    if not check_user_db_priv(conn, permsdir, function, user, host, db):
        logv('updating db privs for %s@%s on %s' % ( user, host, db ))
        apply_user_db_priv(conn, permsdir, function, user, host, db)

def ensure_table_perms(conn, permsdir, function, user, host, db, table):
    logv('checking table %s.%s permissions for user %s@%s' % ( db, table, user, host ))
    if not check_user_table_priv(conn, permsdir, function, user, host, db, table):
        logv('-> updating table %s.%s permissions for user %s@%s' % ( db, table, user, host ))
        apply_user_table_priv(conn, permsdir, function, user, host, db, table)


def loop_from_git(conn, permsdir, functions, envtype, envid):
    global dry_run # FIXME check scope of the global shit across python modules

    for function in functions:
        logv("checking perms for function %s" % function)
        functiondir = makepath(permsdir, function)
        logv("functiondir: %s" % functiondir)

        dirs = os.listdir(functiondir)

        for user in dirs:
            logv("(function: %s) working on user %s" % ( function, user ) )
            if user == 'mysql_version':
                continue

            # global privs
            if os.path.isfile(makepath(permsdir,function,user,'global_perms')):
                ensure_global_perms(conn, permsdir, function, user, envtype, envid)

            sql_hostlist = get_local_user_hosts(permsdir, function, user, envtype, envid)

            # db privs
            if os.path.isdir(makepath(permsdir, function, user, 'databases')):
                for db in os.listdir(makepath(permsdir, function, user, 'databases')):
                    if os.path.isfile(makepath(permsdir, function, user, 'databases', db, 'perms')):
                        for host in sql_hostlist:
                            ensure_db_perms(conn, permsdir, function, user, host, db)

                # tables privs
                    if os.path.isdir(makepath(permsdir, function, user, 'databases', db, 'tables')):
                        tables = os.listdir(makepath(permsdir, function, user, 'databases', db, 'tables'))
                        for table in tables:
                            for host in sql_hostlist:
                                ensure_table_perms(conn, permsdir, function, user, host, db, table)
