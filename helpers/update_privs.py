#!/usr/bin/env python3
#coding: utf8

from helpers.common import *

def apply_global_perms(conn, user, sql_host, global_perms_content, noop):
    cur = conn.cursor()
    noop_str = '[noop] ' if noop else ''
    log("%supdating global permissions for %s@%s" % ( noop_str, user, sql_host ))

    columns = [ 'User', 'Host' ]
    privs = [ ]
    for perm in global_perms_content:
        columns.append(perm[0])
        privs.append("'" + perm[1] + "'")

    #FIXME :  quick shit in case, those mandatory columns are not present
    default_column=['ssl_cipher','x509_issuer','x509_subject']
    for dc in default_column:
        if dc not in columns:
            columns.append(dc)
            privs.append("''")

    if not noop:
        sql = "REPLACE INTO mysql.user ( %s ) VALUES ( '%s', '%s', %s )" %  ( ','.join(columns), user, sql_host, ','.join(privs) )
        cur.execute( sql )

def apply_user_db_priv(conn, permsdir, function, user, host, db, noop):

    noop_str = '[noop] ' if noop else ''
    log("%supdating database %s permissions for %s@%s" % (noop_str, db, user, host))

    local_db_priv = quick_read(makepath(permsdir, function, user, 'databases', db, 'perms')).split('\n')

    columns = ['User', 'Host', 'Db']
    privs = []
    for perm in local_db_priv:

        columns.append(perm.split(': ')[0])
        privs.append("'" + perm.split(': ')[1] + "'")

    if not noop:
        sql = "REPLACE INTO mysql.db ( %s ) VALUES ( '%s', '%s', '%s', %s )" % (','.join(columns), user, host, db, ','.join(privs))
        cur = conn.cursor()
        cur.execute(sql)

    return True


def apply_user_table_priv(conn, permsdir, function, user, host, db, table, noop):

    log("updating table privileges on %s.%s for %s@%s" % (db, table, user, host))
    cur = conn.cursor()

    target_privs = quick_read(makepath(permsdir, function, user, 'databases', db, 'tables', table))
    columns = [ 'Host', 'Db', 'User', 'Table_name', 'Grantor', 'Table_priv', 'Column_priv' ]

    if not noop:
        sql = "REPLACE INTO mysql.tables_priv ( %s ) VALUES ( '%s', '%s', '%s', '%s', '%s', '%s', '' )" % ( ','.join(columns), host, db, user, table, 'root@heaven', target_privs)
        cur.execute(sql)

    return True

