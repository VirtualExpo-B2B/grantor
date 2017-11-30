#!/usr/bin/env python3

import argparse
import socket
import os, re

from helpers.common import *
from helpers.loop_from_git import *

# 0. check version?
# 1. loop from git  ( conn, permsdir, list[functions], envtype, envid )
# 2. loop from db   ( conn, permsdir, list[functions], envtype, envid )



# FIXME: those routines need to support every database servers

def get_envid_prod(hostname):
  return "prod"

def get_envid_preprod(hostname):
  # veso2dblxN-M
  #            ^
  # veso2dwhlx01
  #           ^^
  # veso2ssolx01-1
  #           ^^
  s = re.search('veso2dblx01-([0-9])', hostname)
  if s:
    return "preprod" + s.group(1)
  else:
    return False

def get_envid_dev(hostname):
  # velo1ssolx01-1
  s = re.search('velo1dblx0([0-9])-[0-9]', hostname)
  if s:
    return "ndev" + s.group(1)
  else:
    return False

def get_envid_staging(hostname):
  s = re.search('velo6dblx0([0-9])-[0-9]', hostname)
  if s:
    return "stag" + s.group(1)
  else:
    return False

def main():
  parser = argparse.ArgumentParser(prog='update_mysql_users.py', description='Applies permissions to a MySQL instance')
  parser.add_argument('-s', '--server', nargs=1, help='address of the MySQL server', required=True, type=str)
  parser.add_argument('-u', '--user', nargs=1, default='root', help='username to authenticate', type=str)
  parser.add_argument('-p', '--passwd', nargs=1, help='password of the user', required=True, type=str)
  parser.add_argument('-P', '--permsdir', required=True, default='../perms', help='path to the perms directory', type=str)
  parser.add_argument('-v', '--verbose', default=False, action='store_true', help='tell me whattya doin')
  parser.add_argument('-f', '--function', nargs='*', required=True, help='function to restore [site/dwh/tech/dmt...]', type=str, dest='functions_list', action='store')

  args = parser.parse_args()

  logv_set(args.verbose)

  for f in args.functions_list:
    if not os.path.isdir(args.permsdir + '/' + f):
      die("function %s doesn't exist in %s\n" % (args.permsdir, f))

  logv("connecting to %s (user: %s)\n" % (args.server[0], args.user[0]))
  conn = pymysql.connect( host=args.server[0], user=args.user[0], passwd=args.passwd[0] )
  cur = conn.cursor()
  cur.execute("show variables like 'hostname'")
  res = cur.fetchall()
  hostname = res[0][1]

  logv("connected!")

  envs = { "1": "dev", "2": "preprod", "3": "prod", "6": "dev" }
  logv("hostname: %s" % hostname)
  s = re.search('ve[sl]o([0-9]).*', hostname)
  if s:
    envtype_n = s.group(1)
    envtype = envs[envtype_n]
    logv("envtype: %s" % envtype)
  else:
    die("unable to determine envtype from %s\n" % ( hostname ))

  fmap = { "1": get_envid_dev, "2": get_envid_preprod, "3": get_envid_prod, "6": get_envid_staging }
  envid = fmap[envtype_n](hostname) or die("unable to determine envid")

  loop_from_git(conn, str(args.permsdir), args.functions_list, envtype, envid)
  loop_from_db(conn, args.permsdir, args.functions_list, envtype, envid)


if __name__ == "__main__":
  main()
