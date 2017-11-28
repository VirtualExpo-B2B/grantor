#!/usr/bin/env python3

import argparse
import code
import time
import os, sys
import pymysql

# - dbtype [arg]
#   `- user [select]
#      `- db [select]
#      |  `- table -> perms [select]
#      `- sources [select]

def list_user_perms(d, cur, user):
  '''iterates over all permissions listed for a specific user in mysql.tables_priv'''
  safe_mkdir(d)

  # get the sources
  # FIXME: store everything in an array THEN flush to disk to avoid partial files?
  of = open(d + '/sources', 'w')
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
    of = open(d + '/' + db + '/' + table_name, 'w')
    of.write(table_priv)
    of.close()
    

def list_users(d, cur):
  '''iterates over all users found in the mysql.tables_priv table'''
  logv("listing users...")
  cur.execute('SELECT DISTINCT User FROM mysql.tables_priv ORDER BY User')
  for user in cur.fetchall():
    logv("working on user %s" % user)
    du = d + '/' + user[0]
    list_user_perms(du, cur, user[0])

  
def safe_mkdir(d):
  if not os.path.isdir(d):
    logv("creating directory %s" % d)
    try: os.mkdir(d)
    except OSError as e:
      print ( "unable to create destdir %s: %s" % ( e.filename, e.strerror ) )
      sys.exit(1)
  else:
    logv("directory %s already exists" % d)

def logv(str):
  '''verbose logging using global crap'''
  global verbose
  if verbose:
    print(str)

def main():
  parser = argparse.ArgumentParser(prog='perms-extractor', description='Generates a MySQL grants reference tree')
  parser.add_argument('-s', '--server', nargs=1, help='address of the MySQL server', required=True)
  parser.add_argument('-u', '--user', nargs=1, default=['root'], help='username to authenticate')
  parser.add_argument('-p', '--passwd', nargs=1, help='password of the user', required=True)
  parser.add_argument('-t', '--dbtype', nargs=1, required=True, help='type of database node (site/dwh/dmt/tech/...)')
  parser.add_argument('-d', '--destdir', nargs=1, default=['perms'], help='path to the output directory')
  parser.add_argument('-v', '--verbose', default=False, action='store_true', help='tell me whattya doin')

  args = parser.parse_args()

  # put this shit back into the global scope for logv()
  global verbose
  verbose = args.verbose;

  logv("connecting to %s" % args.server[0])

  conn = pymysql.connect( host=args.server[0], user=args.user[0], passwd=args.passwd[0] )
  cur = conn.cursor()

  logv("connected to %s" % args.server[0])

  for d in args.destdir[0], args.destdir[0] + '/' + args.dbtype[0]:
    safe_mkdir(d)

  list_users(args.destdir[0] + '/' + args.dbtype[0], cur)

  conn.close()


if __name__ == "__main__":
  main()
