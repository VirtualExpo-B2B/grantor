#!/usr/bin/env python3
#coding: utf8

import argparse
import code
import time
import os, sys
import pymysql

from helpers.do_user_password import *
from helpers.mappings import *


def lookup_reverse_map(h):
    l = {
        "%": "any",
        "10.80.30.%": "folx",
        "10.80.31.%": "dblx",
        "10.80.32.%": "wklx",
        "10.80.34.%": "bolx",
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

def gen_users_from_db(d, conn):
    '''iterates over all users found in the mysql.user table'''
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
