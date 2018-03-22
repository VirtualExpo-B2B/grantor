#!/usr/bin/env python3
#coding: utf8

import argparse
import code
import time
import os, sys
import pymysql

def gen_user_password(d, conn, user):
  '''stores the password of $user'''

  cur = conn.cursor()

  safe_mkdir(d + '/passwords')
  f = open(d + '/passwords/' + args.envtype[0], 'w')
  cur.execute("SELECT Password FROM mysql.user WHERE User='%s'" % ( user ))
  res = cur.fetchall()
  f.write(res[0][0] + "\n")
  f.close()
