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
        global_perms_content.append(line.split(':'))

    meta_hostlist = quick_read(makepath(permsdir,function,user,'hosts',envtype))
    if not meta_hostlist:
        logv("user %s does not exist on env %s" % (user, envtype))
    else:
        for meta_host in meta_hostlist:
            sql_hostlist = get_hosts_from_meta(envtype, envid, meta_host)
            for sql_host in sql_hostlist:
                if not check_global_perms_ok(conn, user, sql_host, global_perms_content):
                    apply_global_perms(conn, user, sql_host, global_perms_content)

                password = quick_read(makepath(permsdir, function, user, passwords, envtype))
                if not check_user_password(conn, user, sql_host, password):
                    apply_user_password(conn, user, sql_host, password)

def ensure_db_perms(conn, permsdir, function, user, db):
    logv("voila")

def ensure_table_perms(conn, permsdir, function, user, db):
    logv("voila")



def loop_from_git(conn, permsdir, functions, envtype, envid):
    global dry_run # FIXME check scope of the global shit across python modules

    for function in functions:
        logv("checking perms for function %s" % function)
        functiondir = makepath(permsdir, function)
        logv("functiondir: %s" % functiondir)

    dirs = os.listdir(functiondir)

    for user in dirs:
        if user == 'mysql_version':
            continue
        logv("user: %s" % user)

        if os.path.isfile(makepath(permsdir,function,user,'global_perms')):
            if not ensure_global_perms(conn, permsdir, function, user, envtype, envid):
                if not dry_run:
                    apply_global_perms(conn, permsdir, function, user)
                else:
                    logv("global perms not OK for %s" % (user))
            else:
                logv("global perms OK for %s" % (user))

        if os.path.isdir(makepath(permsdir, function, user, 'databases')):
            for db in os.listdir(makepath(permsdir, function, user, 'databases')):
                if not os.path.isfile(makepath(permsdir, function, user, 'databases', db, 'perms')):
                    continue
                else:
                    if not check_db_perms(conn, permsdir, function, user, db):
                       if not dry_run:
                           apply_global_perms(conn, permsdir, function, user)
                       else:
                           logv("db perms not OK for %s on %s" % (user, db))
                    else:
                        logv("db perms OK for %s on %s" % (user, db))

                     # now is the time to handle per-table privs! good luck :)
