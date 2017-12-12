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
#   `- mysql_version
#   `- $user
#     `- global_perms
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
    if len(res) != 1 and ( user != 'app_batch_solr' and user != "replication" and user != "root" and user != "sys_maint" ):
      die("fatal: res != 1 in do_user for %s (priv: %s)" % ( user, priv ))
    f.write(priv + ": " + res[0][0] + "\n")

  f.close()

  # fill sources?
  # todo hack some kind of reverse lookup

  do_user_db_privs(d + '/databases', conn, user)

  # then do per-table privileges
  do_user_table_privs(d + '/databases', conn, user)

def do_user_password(d, conn, user):
  '''stores the password of $user'''

  cur = conn.cursor()

  safe_mkdir(d + '/passwords')
  f = open(d + '/passwords/' + args.envtype[0], 'w')
  cur.execute("SELECT Password FROM mysql.user WHERE User='%s'" % ( user ))
  res = cur.fetchall()
  f.write(res[0][0] + "\n")
  f.close()
   
def lookup_reverse_map(h):
  l = {
        "%": "any",
        "10.80.30.%": "folx",
        "10.80.31.%": "dblx",
        "10.80.32.%": "wklx",
        "10.80.34.%": "solx",
        "10.80.35.%": "ssolx",
        "10.80.31.12": "rdblx",
        "10.80.36.%": "rplx",
        "10.80.41.%": "admlx",
        "10.80.50.%": "applx", # bilx
        "10.80.0.0/255.255.0.0": "veso",
        "10.80.%.%": "veso",
        "127.0.0.1":  "localhost",
        "172.16.10.%": "net-priv",
        "172.16.11.%": "net-adm",
        "172.16.200.%": "net-vpn",
        "172.16.100.%": "net-vpn",
        "172.16.30.%":  "velo30",
        "172.16.40.%":  "velo40",
        "172.16.50.%":  "velo50",
        "::1":          "localhost",
        "localhost":    "localhost",
        "172.16.130.%": "folx",
        "172.16.131.%": "dblx",
        "172.16.132.%": "wklx",
        "172.16.133.%": "bolx",
        "172.16.134.%": "ssolx",
        "172.16.135.%": "rplx",
        "172.16.140.%": "folx",
        "172.16.141.%": "dblx",
        "172.16.142.%": "wklx",
        "172.16.143.%": "bolx",
        "172.16.144.%": "ssolx",
        "172.16.145.%": "rplx",
      }

  if h in l:
    return l[h]
  return False

def loop_users(d, conn):
  '''iterates over all users found in the mysql.tables_priv table'''
  global args

  logv("listing users...")

  cur = conn.cursor()
  cur_u = conn.cursor()

  # we assume users from EVERY sources have the same permissions
  cur.execute("SELECT DISTINCT User FROM mysql.user WHERE user not in ('') ORDER BY User")
  for user in cur.fetchall():
    user=user[0]
    logv("working on user %s" % user)
    du = d + '/' + user
    safe_mkdir(du)

    if args.passwords:
      do_user_password(du, conn, user)
    else:
      cur.execute('SELECT Host FROM mysql.user WHERE User="%s"' % ( user ) )
      res = cur.fetchall()
      safe_mkdir(du + '/hosts')
      f = open(du + '/hosts/' + args.envtype[0], 'w')
      for host in res:
        h = host[0]
        meta_host = lookup_reverse_map(h)
        if meta_host != False:
          f.write(meta_host + "\n")
        else:
          print("warning: unknown mapping %s [user=%s]" % ( h, user ))
          if user != "root":
            f.write(h + "\n")
      f.close()
      do_user(du, conn, user)

  
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

def store_mysql_version(d, conn):
  # we wrongfully assume that `d' has been created
  cur = conn.cursor()
  cur.execute('SHOW VARIABLES LIKE "version"')
  version = cur.fetchall()[0][1]
  f = open(d + '/mysql_version', 'w')
  f.write(version.split('-')[0] + "\n")
  f.close()

def main():
  # tell me it sucks if u got the balls to do so!
  global args

  parser = argparse.ArgumentParser(prog='perms-extractor', description='Generates a MySQL grants reference tree')
  parser.add_argument('-s', '--server', nargs=1, help='address of the MySQL server', required=True)
  parser.add_argument('-u', '--user', nargs=1, default=['root'], help='username to authenticate')
  parser.add_argument('-p', '--passwd', nargs=1, help='password of the user', required=True)
  parser.add_argument('-t', '--dbtype', nargs=1, required=True, help='type of database node (site/dwh/dmt/tech/...)')
  parser.add_argument('-d', '--destdir', nargs=1, default=['perms'], help='path to the output directory')
  parser.add_argument('-v', '--verbose', default=False, action='store_true', help='tell me whattya doin')
  parser.add_argument('-P', '--passwords', default=False, action='store_true', help='extract passwords from the remote server, requires --envtype')
  parser.add_argument('-T', '--envtype', nargs=1, required=True, help='specifies the environment type [dev/preprod/prod]')

  args = parser.parse_args()

  logv("connecting to %s" % args.server[0])
  conn = pymysql.connect( host=args.server[0], user=args.user[0], passwd=args.passwd[0] )
  logv("connected to %s" % args.server[0])

  for d in args.destdir[0], args.destdir[0] + '/' + args.dbtype[0]:
    safe_mkdir(d)

  if args.passwords and not args.envtype:
    die("-P requires -T")

  store_mysql_version(args.destdir[0] + '/' + args.dbtype[0], conn)

  loop_users(args.destdir[0] + '/' + args.dbtype[0], conn)

  conn.close()


if __name__ == "__main__":
  main()
