#!/usr/bin/env python3

import argparse
import socket

import helpers

# 0. check version?
# 1. loop from git  ( conn, permsdir, list[functions], envtype, envid )
# 2. loop from db   ( conn, permsdir, list[functions], envtype, envid )

def get_envid_prod():
  True

def get_envid_preprod():
  True

def get_envid_dev():
  True

def get_endid_staging():
  True

def main():
  parser = argparse.ArgumentParser(prog='update_mysql_users.py', description='Applies permissions to a MySQL instance')
  parser.add_argument('-s', '--server', nargs=1, help='address of the MySQL server', required=True)
  parser.add_argument('-u', '--user', nargs=1, default=['root'], help='username to authenticate')
  parser.add_argument('-p', '--passwd', nargs=1, help='password of the user', required=True)
  parser.add_argument('-P', '--permsdir', nargs=1, required=True, default=['../perms'], help='path to the perms directory')
  parser.add_argument('-v', '--verbose', default=False, action='store_true', help='tell me whattya doin')
  parser.add_argument('-f', nargs='?', required=True, help='function to restore [site/dwh/tech/dmt...]')

  args = parser.parse_args()

  for f in args.f:
    if not os.path.isdir(args.P + '/' + f):
      die("function %s doesn't exist in %s\n" % (args.P, f))

  logv("connecting to %s (user: %s)\n" % (args.server[0], args.user[0]))
  conn = pymysql.connect( host=args.server[0], user=args.user[0], passwd=args.passwd[0] )
  logv("connected!")

  envs = { "1": "dev", "2": "preprod", "3": "prod", "6": "dev" }
  hostname = socket.gethostname()
  s = re.search('ve[sl]o([0-9]).*', hostname)
  if s:
    envtype = envs[s.group(1)]
  else:
    die("unable to determine envtype from %s\n" % ( hostname ))



  loop_from_git(conn, args.P, args.f, envtype, envid)
  loop_from_db(conn, args.P, args.f, envtype, envid)


if __name__ == "__main__":
  main()
