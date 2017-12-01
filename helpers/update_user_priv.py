#!/usr/bin/env python3
#coding: utf8

from helpers.common import *

def create_new_mysql_user():
  True

def apply_global_perms(conn, user, sql_host, global_perms_content):
    cur = conn.cursor()
    log("updating permissions for %s@%s" % ( user, sql_host ))

    columns = [ 'Host', 'User' ]
    privs = [ ]
    for perm in global_perms_content:
        columns.append(perm[0])
        privs.append("'" + perm[1] + "'")

    cur.execute("REPLACE INTO mysql.user ( %s ) VALUES ( '%s', '%s', %s )" %  ( ','.join(columns), user, sql_host, ','.join(privs) ) )
