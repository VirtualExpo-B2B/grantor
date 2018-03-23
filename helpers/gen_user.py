#!/usr/bin/env python3
#coding: utf8

import argparse
import code
import time
import os, sys
import pymysql

from helpers.common import *

# mysql -B -N -e 'describe mysql.user' | grep _priv | awk '{ print $1 }'  | sed -e 's/^/"/' -e 's/$/", /' | tr -d '\n'
user_global_privs = [ "Select_priv", "Insert_priv", "Update_priv", "Delete_priv", "Create_priv", "Drop_priv", "Reload_priv", "Shutdown_priv", "Process_priv", "File_priv", "Grant_priv", "References_priv", "Index_priv", "Alter_priv", "Show_db_priv", "Super_priv", "Create_tmp_table_priv", "Lock_tables_priv", "Execute_priv", "Repl_slave_priv", "Repl_client_priv", "Create_view_priv", "Show_view_priv", "Create_routine_priv", "Alter_routine_priv", "Create_user_priv", "Event_priv", "Trigger_priv", "Create_tablespace_priv" ]

# mysql -B -N -e 'describe mysql.db' | grep _priv | awk '{ print $1 }'  | sed -e 's/^/"/' -e 's/$/", /' |  '\n'
user_db_privs = [ "Select_priv", "Insert_priv", "Update_priv", "Delete_priv", "Create_priv", "Drop_priv", "Grant_priv", "References_priv", "Index_priv", "Alter_priv", "Create_tmp_table_priv", "Lock_tables_priv", "Create_view_priv", "Show_view_priv", "Create_routine_priv", "Alter_routine_priv", "Execute_priv", "Event_priv", "Trigger_priv" ]


def gen_user_password(d, conn, user):
  '''stores the password of $user'''

  cur = conn.cursor()

  safe_mkdir(d + '/passwords')
  f = open(d + '/passwords/' + args.envtype[0], 'w')
  cur.execute("SELECT Password FROM mysql.user WHERE User='%s'" % ( user ))
  res = cur.fetchall()
  f.write(res[0][0] + "\n")
  f.close()
  
  
def do_user_table_privs(d, conn, user):
  '''iterates over all permissions listed for a specific user in mysql.tables_priv'''
  safe_mkdir(d)

  cur = conn.cursor()

  # since permissions are identical whatever the source Host is, we get the first one
  cur.execute("SELECT DISTINCT Host FROM mysql.tables_priv WHERE User = '%s' LIMIT 1" % user)
  res = cur.fetchall()
  if len(res) == 0:
    # user has no per-table permissions
    return
  h = res[0][0]

  # iterate over user's permissions
  cur.execute("SELECT * FROM mysql.tables_priv WHERE User = '%s' AND Host = '%s'" % (user, h))
  for host, db, user, table_name, grantor, ts,  table_priv, column_priv in cur.fetchall():
    safe_mkdir(d + '/' + db)
    safe_mkdir(d + '/' + db + '/tables')
    quick_write(d + '/' + db + '/tables/' + table_name, table_priv)

def do_user_db_privs(d, conn, user):
  '''stores database-level privileges'''
  cur = conn.cursor()
  safe_mkdir(d)
  res = cur.execute("SELECT DISTINCT Db FROM mysql.db WHERE User='%s'" % ( user ))
  dbs = cur.fetchall()
  for db in dbs:
    db = db[0]
    safe_mkdir(d + '/' + db)
    f = open(d + '/' + db + '/perms', 'w')
    for priv in user_db_privs:
      # FIXME: DISTINCT sucks, we should iterate with a specific Host
      cur.execute("SELECT DISTINCT %s FROM mysql.db WHERE User='%s' AND Db='%s'" % ( priv, user, db ))
      res = cur.fetchall()
      if len(res) != 1:
        log("CRIT: res.len=%i != 1 in do_user_db_privs for %s (priv: %s)" % ( len(res), user, priv ))
      f.write("%s: %s\n" % ( priv, res[0][0] ))
    f.close()

def do_user(d, conn, user):
    '''stores global user's settings'''
    # fill perms from mysql.user
    cur = conn.cursor()
    f = open(d + '/global_perms', 'w')
    for priv in user_global_privs:
        cur.execute("SELECT DISTINCT %s FROM mysql.user WHERE User='%s'" % ( priv, user ) )
        res = cur.fetchall()
        # FIXME: dirty hack for the specific Super_priv from 10.80.32.% granted to app_batch_solr
        if len(res) != 1:
            log("CRIT: res != 1 in do_user for %s (priv: %s)" % ( user, priv ))
        f.write(priv + ": " + res[0][0] + "\n")
  
    f.close()
  
    # fill sources?
    # todo hack some kind of reverse lookup
  
    do_user_db_privs(d + '/databases', conn, user)
  
    # then do per-table privileges
    do_user_table_privs(d + '/databases', conn, user)
