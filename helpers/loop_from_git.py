#!/usr/bin/env python3
#enccoding: utf8

import argparse
import os, sys
from helpers.common import *
from helpers.check_privs import *
from helpers.update_privs import *
from helpers.check_mysql_version import *

dry_run = False

# returns an array of SQL hosts for a {function,user,envtype,envid} "couple"
def get_local_user_hosts(permsdir, function, user, envtype,envid):

    result=[]
    meta_hostlist = None
    # FIXME: shit to prevent an error where the host file is not present for the environment
    try:
        meta_hostlist = quick_read(makepath(permsdir, function, user, 'hosts', envtype)).split('\n')
    except:
        logv("no hostlist for %s for f=%s,envtype=%s" % ( user, function, envtype ) )
        return None

    for meta_host in meta_hostlist:
        hostlist = get_hosts_from_meta(envtype, envid, meta_host)
        if hostlist == None:
            log("ERROR: %s has no mapping!" % ( meta_host ))
        for h in hostlist:
            result.append(h)

    logv("meta_host: %s   sql_host:%s" % ( ','.join(meta_hostlist), ','.join(result)))
    return result


def ensure_global_perms(conn, args, function, user, envtype, envid):
    global_perms = quick_read(makepath(args.permsdir, function, user, 'global_perms'))
    global_perms_content = []
    for line in global_perms.strip().split("\n"):
        global_perms_content.append(line.split(': '))

    logv("checking perms for %s" % ( user ) )

    sql_hostlist = get_local_user_hosts(args.permsdir, function, user, envtype, envid)

    if sql_hostlist == None:
        logv("user %s does not exist on env %s" % (user, envtype))
    else:
        for host in sql_hostlist:
            logv("in-sql: working on %s@%s" % ( user, host ) )
            if not check_global_perms_ok(conn, user, host, global_perms_content):
                logv("%s@%s: fixing permissions" % ( user, host ))
                apply_global_perms(conn, user, host, global_perms_content, args.noop)
            else:
                logv("%s@%s: perms OK, congrats" % ( user, host ) )

            password = quick_read(makepath(args.permsdir, function, user, 'passwords', envtype))
            if password == False:
              log("ERROR: no password file for user %s@%s [function=%s,envtype=%s]" % ( user, host, function, envtype ) )
            elif not check_user_password(conn, user, host, password):
                apply_user_password(conn, user, host, password, args.noop)

def ensure_db_perms(conn, args, function, user, host, db):
    logv('checking db %s permissions for user %s@%s' % (db, user, host))
    if not check_user_db_priv(conn, args.permsdir, function, user, host, db):
        apply_user_db_priv(conn, args.permsdir, function, user, host, db, args.noop)

def ensure_table_perms(conn, args, function, user, host, db, table):
    logv('checking table %s.%s permissions for user %s@%s' % ( db, table, user, host ))
    if not check_user_table_priv(conn, args.permsdir, function, user, host, db, table):
        apply_user_table_priv(conn, args.permsdir, function, user, host, db, table, args.noop)


def loop_from_git(conn, args, envtype, envid):
    permsdir = args.permsdir
    noop = args.noop
    single_user = args.single_user

    for function in args.functions_list:
        log("* working on function %s" % function)
        functiondir = makepath(permsdir, function)
        dirs = os.listdir(functiondir)

        logv("checking MySQL version....")
        if check_mysql_version(conn, makepath(permsdir, function, "mysql_version")) == False:
            log("WARNING: target MySQL version mismatches")
        else:
            logv("MySQL version OK")

        i = 0
        for user in dirs:
            if user == 'mysql_version':
                continue

            if args.single_user != None and not user == args.single_user:
                continue
            logv("working on user %s" % ( user ) )

            print("  working on: % 17s [%i/%i] [%i%%]\r" % ( user, i, len(dirs), i * 100 / len(dirs) ), end = '')
            i = i + 1  # come on, there's no i++ ?

            # global privs
            if os.path.isfile(makepath(permsdir,function,user,'global_perms')):
                ensure_global_perms(conn, args, function, user, envtype, envid)

            sql_hostlist = get_local_user_hosts(permsdir, function, user, envtype, envid)
            if sql_hostlist == None:
                log("WARNING: skipping user %s" % ( user ))
                continue

            # db privs
            if os.path.isdir(makepath(permsdir, function, user, 'databases')):
                for db in os.listdir(makepath(permsdir, function, user, 'databases')):
                    if os.path.isfile(makepath(permsdir, function, user, 'databases', db, 'perms')):
                        for host in sql_hostlist:
                            ensure_db_perms(conn, args, function, user, host, db)

                # tables privs
                    if os.path.isdir(makepath(permsdir, function, user, 'databases', db, 'tables')):
                        tables = os.listdir(makepath(permsdir, function, user, 'databases', db, 'tables'))
                        for table in tables:
                            for host in sql_hostlist:
                                ensure_table_perms(conn, args, function, user, host, db, table)

    print('\r', end='')
