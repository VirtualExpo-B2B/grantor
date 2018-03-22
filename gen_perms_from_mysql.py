#!/usr/bin/env python3
#coding: utf8

import argparse
import code
import time
import os, sys
import pymysql

from helpers.gen_users_from_db import *
#
# filesystem layout:
#
# +-- _data
# |   +-- metamap
# |       +-- common
# |       +-- dev
# |       +-- staging
# |       +-- prod
# +-- $function
#     +-- mysql_version
#     +-- $user
#         +-- global_perms
#         +-- databases
#         |   +-- database1
#         |       +-- perms
#         |       +-- tables
#         |           +-- table1
#         +-- hosts
#         |   +-- dev
#         |   +-- staging
#         |   +-- prod
#         +-- passwords
#         |   +-- dev
#         |   +-- staging
#         |   +-- prod

def die(str):
  print(str + '\n')
  sys.exit(1)

  
def store_mysql_version(d, conn):
  # we wrongfully assume that `d' has been created
  cur = conn.cursor()
  cur.execute('SHOW VARIABLES LIKE "version"')
  version = cur.fetchall()[0][1]
  f = open(d + '/mysql_version', 'w')
  f.write(version.split('-')[0] + "\n")
  f.close()

def main():
  global args

  parser = argparse.ArgumentParser(prog='perms-extractor', description='Generates a MySQL grants reference tree')
  parser.add_argument('-s', '--server', nargs=1, help='address of the MySQL server', required=True)
  parser.add_argument('-u', '--user', nargs=1, default=['root'], help='authentication user')
  parser.add_argument('-p', '--passwd', nargs=1, help='password of the authentication user', required=True)
  parser.add_argument('-f', '--function', nargs=1, required=True, help='database function')
  parser.add_argument('-d', '--destdir', nargs=1, default=['perms'], help='path to the output directory')
  parser.add_argument('-v', '--verbose', default=False, action='store_true', help='tell me whattya doin')
  parser.add_argument('-P', '--passwords', default=False, action='store_true', help='extract only passwords from the remote server, requires --envtype')
  parser.add_argument('-T', '--envtype', nargs=1, required=True, help='environment type, ex: dev, prod, etc...')

  args = parser.parse_args()

  logv("connecting to %s" % args.server[0])
  conn = pymysql.connect( host=args.server[0], user=args.user[0], passwd=args.passwd[0] )
  logv("connected to %s" % args.server[0])

  for d in args.destdir[0], args.destdir[0] + '/' + args.function[0]:
    safe_mkdir(d)

  if args.passwords and not args.envtype:
    die("-P requires -T")

  store_mysql_version(args.destdir[0] + '/' + args.function[0], conn)

  gen_users_from_db(args.destdir[0] + '/' + args.function[0], conn)

  conn.close()


if __name__ == "__main__":
  main()
