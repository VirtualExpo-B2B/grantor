#!/usr/bin/env python3

import argparse
import socket
import os, re

from helpers.common import *
from helpers.loop_from_git import *
from helpers.loop_from_db import *


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
  s = re.search('velo1dblx0([0-9])*', hostname)
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
  parser = argparse.ArgumentParser(prog='MySQL Grantor', description='Applies permissions to a MySQL instance')
  parser.add_argument('-s', '--server', nargs=1, help='address or hostname of the MySQL server', required=True, type=str)
  parser.add_argument('-u', '--user', nargs=1, default='root', help='username to authenticate with', type=str)
  parser.add_argument('-p', '--passwd', nargs=1, help='password of the user', required=True, type=str)
  parser.add_argument('-P', '--permsdir', required=True, default='../perms', help='path to the perms directory', type=str)
  parser.add_argument('-v', '--verbose', default=False, action='store_true', help='tell me whattya doin')
  parser.add_argument('-f', '--function', nargs='*', required=True, help='function to restore [site/dwh/tech/dmt...]', type=str, dest='functions_list', action='store')

  args = parser.parse_args()

  log("MySQL Grantor starting...")
  logv_set(args.verbose)

  for f in args.functions_list:
    if not os.path.isdir(args.permsdir + '/' + f):
      die("function %s doesn't exist in %s" % (args.permsdir, f))

  logv("connecting to %s (user: %s)... " % (args.server[0], args.user[0]))
  conn = pymysql.connect( host=args.server[0], user=args.user[0], passwd=args.passwd[0] )
  cur = conn.cursor()
  cur.execute("SHOW VARIABLES LIKE 'hostname'")
  res = cur.fetchall()
  hostname = res[0][1]

  logv("connected!\n")

  envs = { "1": "dev", "2": "preprod", "3": "prod", "6": "dev" }
  logv("hostname: %s" % hostname)

  #FIXME - this is a shit modification for playing within my local mysql
  hostname='velo1dblx01'

  s = re.search('ve[sl]o([0-9]).*', hostname)
  if s:
    envtype_n = s.group(1)
    envtype = envs[envtype_n]
    logv("envtype: %s" % envtype)
  else:
    die("unable to determine envtype from %s\n" % ( hostname ))

  fmap = { "1": get_envid_dev, "2": get_envid_preprod, "3": get_envid_prod, "6": get_envid_staging }
  envid = fmap[envtype_n](hostname) or die("unable to determine envid")

  log("* step 1 - applying permissions from the repository")
  loop_from_git(conn, str(args.permsdir), args.functions_list, envtype, envid)
  log("* step 2 - removing extra permissions from the server")
  loop_from_db(conn, args.permsdir, args.functions_list, envtype, envid)

  log("flushing privileges...")
  cur.execute("FLUSH PRIVILEGES")

  conn.close()

  log("Job done.")


if __name__ == "__main__":
  main()
