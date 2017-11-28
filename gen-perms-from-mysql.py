#!/usr/bin/env python3

import argparse
import code
import time
import sys
import pymysql

# - dbtype [arg]
#   `- user [select]
#      `- db [select]
#      |  `- table -> perms [select]
#      `- sources [select]

def main():
  parser = argparse.ArgumentParser(prog='perms-extractor', description='Generates a MySQL grants reference tree')
  parser.add_argument('-s', '--server', nargs=1, help='address of the MySQL server')
  parser.add_argument('-u', '--user', nargs=1, default='root', help='username to authenticate')
  parser.add_argument('-p', '--passwd', nargs=1, help='password of the user')
  parser.add_argument('-t', '--srvtype', nargs=1, default='prod', help='type of database node (prod/dwh/dmt/tech/...)')
  parser.add_argument('-d', '--destdir', nargs=1, default='perms', help='path to the output directory')

  args = parser.parse_args()

  conn = pymysql.connect( host=args.server, user=args.user, passwd=args.passwd )
  cur = conn.cursor()
  cur.execute('SHOW DATABASES')
  for row in cur.fetchall():
    print(row[0])

  conn.close()


if __name__ == "__main__":
  main()
