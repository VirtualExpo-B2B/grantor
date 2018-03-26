#!/usr/bin/env python3
#coding: utf8

import argparse
import code
import time
import os, sys
import pymysql

from helpers.gen_user import *
from helpers.gen_hosts import *
from helpers.mappings import *
from helpers.common import *

def gen_users_from_db(d, conn, args):
    '''iterates over all users found in the mysql.user table'''

    logv("listing users...")
    g_net_count = 1
    logv("g_net_count = %d" % g_net_count)
  
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
            gen_user_password(du, conn, user, args.envtype[0])
        else:
            g_net_count = gen_hosts(du, cur, user, args, g_net_count)
            do_user(du, conn, user)
