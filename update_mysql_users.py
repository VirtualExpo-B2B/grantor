#!/usr/bin/env python3
#coding: utf8

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
  s = re.search('^veso2dblx01-([0-9])$', hostname)
  if s:
    return s.group(1)
  else:
    return False

def get_envid_dev(hostname):
  # velo1ssolx01-1
  s = re.search('^velo1dblx0([0-9])-[0-9]$', hostname)
  if s:
    return s.group(1)
  else:
    s = re.search('^velo1dblx0([0-9])$', hostname)
    return s.group(1) if s else False

  return False

def get_envid_staging(hostname):
  s = re.search('^velo6dblx0([0-9])-[0-9]$', hostname)
  if s:
    return s.group(1)
  else:
    return False

def main():
  parser = argparse.ArgumentParser(description='Applies permissions to a MySQL instance')
  parser.add_argument('-s', '--server', help='address or hostname of the MySQL server', required=True, type=str, action='store')
  parser.add_argument('-u', '--user',  default='root', help='username to authenticate with', type=str, action='store')
  parser.add_argument('-p', '--passwd', help='password of the user to authenticate with', required=True, type=str, action='store')
  parser.add_argument('-P', '--permsdir', required=True, default='../perms', help='path to the perms directory', type=str)
  parser.add_argument('-v', '--verbose', default=False, action='store_true', help='tell me whattya doin')
  parser.add_argument('-f', '--function', required=True, help='function to restore [site/dwh/tech/dmt...]', type=str, dest='functions_list', action='store')
  parser.add_argument('-U', '--single-user', dest='single_user', help='if you wanna work with only one user', required=False, type=str)
  parser.add_argument('-n', '--noop', default=False, action='store_true', help='do ya wanna show changes before we go ?')

  args = parser.parse_args()

  log("MySQL Grantor starting...")

  if args.noop:
    log("> performing a dry-run (--noop)")

  logv_set(args.verbose)

  args.functions_list = args.functions_list.split(',')

  for f in args.functions_list:
    if not os.path.isdir(makepath(args.permsdir, f)):
      die("error: function %s doesn't exist in %s" % (f, args.permsdir))

  logv("connecting to %s (user: %s)... " % (args.server, args.user))
  conn = pymysql.connect( host=args.server, user=args.user, passwd=args.passwd )
  cur = conn.cursor()
  cur.execute("SHOW VARIABLES LIKE 'hostname'")
  res = cur.fetchall()
  hostname = res[0][1]

  logv("connected!\n")

  envs = { "1": "dev", "2": "preprod", "3": "prod", "6": "dev" }
  logv("server hostname: %s" % hostname)

  s = re.search('ve[sl]o([0-9]).*', hostname)
  if s:
    envtype_n = s.group(1)
    envtype = envs[envtype_n]
  else:
    die("error: unable to determine envtype from %s\n" % ( hostname ))

  fmap = { "1": get_envid_dev, "2": get_envid_preprod, "3": get_envid_prod, "6": get_envid_staging }
  envid = fmap[envtype_n](hostname) or die("unable to determine envid")

  logv("-> envtype: %s, envid: %s" % (envtype, envid))

  log("* step 1 - applying permissions from the repository")
  loop_from_git(conn, args, envtype, envid)
  log("* step 2 - removing extra permissions from the server")
  loop_from_db(conn, args, envtype, envid)

  if not args.noop:
    log("flushing privileges...")
    cur.execute("FLUSH PRIVILEGES")

  conn.close()

  log("Job done.")


if __name__ == "__main__":
  main()
