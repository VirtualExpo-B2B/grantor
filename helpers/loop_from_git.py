#!/usr/bin/env python3
#coding: utf8

import argparse
import os, sys
from helpers.common import *
from helpers.check_foo import *
from helpers.update_user_priv import *

dry_run = False

def ensure_global_perms(conn, permsdir, function, user, envtype, envid):
    global_perms = quick_read(makepath(permsdir, function, user, 'global_perms'))
    global_perms_content = []
    for line in global_perms.strip().split("\n"):
        global_perms_content.append(line.split(': '))

    logv("checking perms for %s" % ( user ) )
    meta_hostlist = quick_read(makepath(permsdir,function,user,'hosts',envtype)).split('\n')
    if not meta_hostlist:
        logv("user %s does not exist on env %s" % (user, envtype))
    else:
        for meta_host in meta_hostlist:
            logv("in-meta: working on %s@%s" % ( user, meta_host ) )
            sql_hostlist = get_hosts_from_meta(envtype, envid, meta_host)
            for sql_host in sql_hostlist:
                logv("in-sql: working on %s@%s" % ( user, sql_host ) )
                if not check_global_perms_ok(conn, user, sql_host, global_perms_content):
                    logv("%s@%s: fixing permissions" % ( user, sql_host ))
                    apply_global_perms(conn, user, sql_host, global_perms_content)
                else:
                    logv("%s@%s: perms OK, congrats" % ( user, sql_host ) )

                password = quick_read(makepath(permsdir, function, user, 'passwords', envtype))
                if not check_user_password(conn, user, sql_host, password):
                    apply_user_password(conn, user, sql_host, password)

def ensure_db_perms(conn, permsdir, function, user, db):
    True

def ensure_table_perms(conn, permsdir, function, user, db):
    True



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

            # db privs
            if os.path.isdir(makepath(permsdir, function, user, 'databases')):
                for db in os.listdir(makepath(permsdir, function, user, 'databases')):
                    if os.path.isfile(makepath(permsdir, function, user, 'databases', db, 'perms')):
                        ensure_db_perms(conn, permsdir, function, user, db)

                # tables privs
                    if os.path.isdir(makepath(permsdir, function, user, db, "tables")):
                        tables = os.listdir(makepath(permsdir, function, user, db, "tables"))
                        for table in tables:
                            ensure_table_perms(conn, permsdir, function, user, db, table)
