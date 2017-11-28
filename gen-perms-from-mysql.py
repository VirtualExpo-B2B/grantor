#!/usr/bin/env python3
#coding: utf8

import argparse
import code
import time
import os, sys
import pymysql

# mysql -uroot -p$(cat /root/.mpwd) -B -N -e 'describe mysql.user' | grep _priv | awk '{ print $1 }'  | sed -e 's/^/"/' -e 's/$/", /' | tr -d '\n'
user_global_privs = [ "Select_priv", "Insert_priv", "Update_priv", "Delete_priv", "Create_priv", "Drop_priv", "Reload_priv", "Shutdown_priv", "Process_priv", "File_priv", "Grant_priv", "References_priv", "Index_priv", "Alter_priv", "Show_db_priv", "Super_priv", "Create_tmp_table_priv", "Lock_tables_priv", "Execute_priv", "Repl_slave_priv", "Repl_client_priv", "Create_view_priv", "Show_view_priv", "Create_routine_priv", "Alter_routine_priv", "Create_user_priv", "Event_priv", "Trigger_priv", "Create_tablespace_priv" ]

# mysql -uroot -p$(cat /root/.mpwd) -B -N -e 'describe mysql.db' | grep _priv | awk '{ print $1 }'  | sed -e 's/^/"/' -e 's/$/", /' |  '\n'
user_db_privs = [ "Select_priv", "Insert_priv", "Update_priv", "Delete_priv", "Create_priv", "Drop_priv", "Grant_priv", "References_priv", "Index_priv", "Alter_priv", "Create_tmp_table_priv", "Lock_tables_priv", "Create_view_priv", "Show_view_priv", "Create_routine_priv", "Alter_routine_priv", "Execute_priv", "Event_priv", "Trigger_priv" ]

#
# filesystem layout:
#
# - $dbtype
#   `- $user
#     `- perms
#     `- sources [select]
#     `- passwords -> $envtype
#     `- databases
#       `- perms
#       `- tables -> $table -> perms [select]

def quick_write(path, contents):
  of = open(path, 'w')
  of.write(contents)
  of.close()

def die(str):
  print(str + '\n')
  sys.exit(1)

def do_user_table_privs(d, conn, user):
  '''iterates over all permissions listed for a specific user in mysql.tables_priv'''
  safe_mkdir(d)

  cur = conn.cursor()

  # get the sources
  # FIXME: store everything in an array THEN flush to disk to avoid partial files?
  # DO WE RELAY NEED THIS : Cause, if we add a new server, or delete one, this list must be up to date
  of = open(d + '/_sources', 'w')
  cur.execute("SELECT DISTINCT Host FROM mysql.tables_priv WHERE User = '%s'" % user)
  for host in cur.fetchall():
    of.write("%s\n" % host)
  of.close()

  # since permissions are identical whatever the source Host is, we get the first one
  cur.execute("SELECT DISTINCT Host FROM mysql.tables_priv WHERE User = '%s' LIMIT 1" % user)
  h = cur.fetchall()[0][0]

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
        die("fatal: res.len=%i != 1 in do_user_db_privs for %s (priv: %s)" % ( len(res), user, priv ))
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
    if len(res) != 1 and user != 'app_batch_solr':
      die("fatal: res != 1 in do_user for %s (priv: %s)" % ( user, priv ))
    f.write(priv + ": " + res[0][0] + "\n")

  f.close()

  # fill sources?
  # todo hack some kind of reverse lookup

  do_user_db_privs(d + '/databases', conn, user)

  # then do per-table privileges
  do_user_table_privs(d + '/databases', conn, user)

def do_user_passwords(d, conn, user):
  '''stores the password of $user'''

  cur = conn.cursor()

  safe_mkdir(d + '/passwords')
  f = open(d + '/passwords/' + args.envtype)
  cur.execute("SELECT Password FROM mysql.user WHERE User='%s'" % ( user ))
  res = cur.fetchall()
  f.write(res[0])
  f.close()
    
def loop_users(d, conn):
  '''iterates over all users found in the mysql.tables_priv table'''
  global args

  logv("listing users...")

  cur = conn.cursor()
  cur_u = conn.cursor()

  cur.execute('SELECT DISTINCT User FROM mysql.tables_priv ORDER BY User')
  for user in cur.fetchall():
    logv("working on user %s" % user)
    du = d + '/' + user[0]
    safe_mkdir(du)

    #cur_u.execute("SELECT Password FROM mysql.user WHERE User='%s'" % user)
    #for p in cur_u.fetchall():
    #  quick_write(du + '/_password', p[0])
    if args.passwords:
      do_user_password(du, conn, user[0])
    else:
      do_user(du, conn, user[0])

  
def safe_mkdir(d):
  if not os.path.isdir(d):
    try: os.mkdir(d)
    except OSError as e:
      print ( "unable to create destdir %s: %s" % ( e.filename, e.strerror ) )
      sys.exit(1)

def logv(str):
  '''verbose logging using global crap'''
  global args 
  if args.verbose:
    print(str)

def main():
  parser = argparse.ArgumentParser(prog='perms-extractor', description='Generates a MySQL grants reference tree')
  parser.add_argument('-s', '--server', nargs=1, help='address of the MySQL server', required=True)
  parser.add_argument('-u', '--user', nargs=1, default=['root'], help='username to authenticate')
  parser.add_argument('-p', '--passwd', nargs=1, help='password of the user', required=True)
  parser.add_argument('-t', '--dbtype', nargs=1, required=True, help='type of database node (site/dwh/dmt/tech/...)')
  parser.add_argument('-d', '--destdir', nargs=1, default=['perms'], help='path to the output directory')
  parser.add_argument('-v', '--verbose', default=False, action='store_true', help='tell me whattya doin')
  parser.add_argument('-P', '--passwords', default=False, action='store_true', help='extract passwords from the remote server, requires --envtype')
  parser.add_argument('-T', '--envtype', nargs=1, help='specifies the environment type [dev/preprod/prod]')

  args = parser.parse_args()

  # put this shit back into the global scope for logv()
  global args

  logv("connecting to %s" % args.server[0])

  conn = pymysql.connect( host=args.server[0], user=args.user[0], passwd=args.passwd[0] )

  logv("connected to %s" % args.server[0])

  for d in args.destdir[0], args.destdir[0] + '/' + args.dbtype[0]:
    safe_mkdir(d)

  if args.password and not args.envtype:
    die("-P requires -T")

  loop_users(args.destdir[0] + '/' + args.dbtype[0], conn)


  conn.close()


if __name__ == "__main__":
  main()
