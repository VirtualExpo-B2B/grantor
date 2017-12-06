#!/usr/bin/env python3
# coding: utf8

import os
from helpers.mappings import *
from helpers.common import *

def drop_user(conn, user, host, noop):

    noop_str = '[noop] ' if noop else ''
    log("%sremoving user %s@%s" % (noop_str, user, host))

    if not noop:
        cur = conn.cursor()
        cur.execute("DELETE FROM mysql.user WHERE User='%s' AND Host='%s'" % ( user, host ))
        cur.fetchall()

def revoke_db_privs(conn, user, host, db, noop):

    noop_str = '[noop] ' if noop else ''
    log("%srevoking database privileges from %s@%s on %s" % (noop_str, user, host, db))

    if not noop:
        cur = conn.cursor()
        cur.execute("DELETE FROM mysql.db WHERE User='%s' AND Host='%s' AND Db='%s'" % ( user, host, db ))
        cur.fetchall()

def check_global_users(conn,args, envtype, envid):
    cur = conn.cursor()

    if args.single_user != None:
        sql = "SELECT User, Host FROM mysql.user where user = '%s'" % (args.single_user)
    else:
        sql = "SELECT User, Host FROM mysql.user where user not in ('')"

    cur.execute(sql)

    for line in cur.fetchall():
        user = line[0]
        sql_host = line[1]

        # reverse lookup
        meta_host = get_meta_from_host(sql_host)

        # m = folx

        foundit = False
        for f in args.functions_list:
            if not os.path.isfile(makepath(args.permsdir, f,  user, 'hosts', envtype)):
                break
            else:
                r = quick_read(makepath(args.permsdir, f,  user, 'hosts', envtype))
                meta = r.split('\n')
                if meta_host in meta:
                    foundit = True
                    break

        if foundit == False:
                drop_user(conn, user, sql_host, args.noop)

        logv("user %s@%s is fine." % ( user, sql_host ) )

def check_db_privs(conn, args, envtype, envid):

    cur = conn.cursor()
    if args.single_user != None:
        sql="SELECT * FROM mysql.db WHERE User='%s'" % (args.single_user)
    else:
        sql="SELECT * FROM mysql.db"

    cur.execute(sql)

    for row in cur.fetchall():
        host = row[0]
        db = row[1]
        user = row[2]

        logv("checking database privileges %s@%s on %s" % ( user, host, db ) )
        # this is quite easy: if the file exists in permsdir,
        # then the proper perms will have been applied during
        # the previous stage. if the file is absent in permsdir,
        # it means the user no longer has any privs on the db.
        flag = False
        for f in args.functions_list:
            if os.path.isfile(makepath(args.permsdir, f, user, 'databases', db, 'perms')):
                flag = True

        if flag == False:
            revoke_db_privs(conn, user, host, db, args.noop)

def delete_table_priv(conn, host, db, user, table_name, noop):
    noop_str = '[noop] ' if noop else ''
    log("%srevoking tables privileges on %s.%s for %s@%s" % (noop_str, db, table_name, user, host))

    if not noop:
        cur = conn.cursor()
        cur.execute("DELETE FROM mysql.tables_priv WHERE User='%s' AND Db='%s' AND Host='%s' AND Table_name='%s'" % ( user, db, host, table_name ))
        cur.fetchall()

# iterates over each row of mysql.tables_priv
def check_tables_privs(conn, args, envtype, envid):
    cur = conn.cursor()

    if args.single_user != None:
        sql = "SELECT Host, Db, User, Table_name FROM mysql.tables_priv WHERE User='%s'" % (args.single_user)
    else:
        sql = "SELECT Host, Db, User, Table_name FROM mysql.tables_priv"

    cur.execute(sql)

    for host, db, user, table_name in cur.fetchall():
        logv("checking table permissions for %s@%s on db %s.%s" % ( user, host, db, table_name ) )
        found = False
        for f in args.functions_list:
            if os.path.isfile(makepath(args.permsdir, f, user, 'databases', db, 'tables', table_name)):
                found = True
                break
        if found == False:
            delete_table_priv(conn, host, db, user, table_name, args.noop)

def loop_from_db(conn, args, envtype, envid):
    logv('loop_from_db: working on global privs')
    check_global_users(conn, args, envtype, envid)
    logv('loop_from_db: working on db privs')
    check_db_privs(conn, args, envtype, envid)
    logv('loop_from_db: working on tables privs')
    check_tables_privs(conn, args, envtype, envid)
