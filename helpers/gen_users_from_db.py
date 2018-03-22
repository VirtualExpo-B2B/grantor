#!/usr/bin/env python3
#coding: utf8

import argparse
import code
import time
import os, sys
import pymysql

from helpers.gen_user import *
from helpers.mappings import *
from helpers.common import *

def gen_users_from_db(d, conn, args):
    '''iterates over all users found in the mysql.user table'''
    g_net_count = 1

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
            gen_user_password(du, conn, user)
        else:
            cur.execute('SELECT Host FROM mysql.user WHERE User="%s"' % ( user ) )
            res = cur.fetchall()
            safe_mkdir(du + '/hosts')
            f = open(du + '/hosts/' + args.envtype[0], 'w')
            for host in res:
                h = host[0]
                safe_mkdir(makepath(args.permsdir[0], '_data'))
                safe_mkdir(makepath(args.permsdir[0], '_data', 'metamap'))
                meta_host = None
                if not os.path.isfile(makepath(args.permsdir[0], '_data', 'metamap', 'common')):
                    quick_write(makepath(args.permsdir[0], '_data', 'metamap', 'common'), 'any: %' + "\n")
                if os.path.isfile(makepath(args.permsdir[0], '_data', 'metamap', args.envtype[0])):
                    meta_host = get_meta_from_host(args.permsdir[0], args.envtype[0], h)
                    logv("meta_host from existing metamap: %s" % meta_host)
                if meta_host == None:
                    log("WARNING: creating mapping network%s: %s" % (str(g_net_count), h))
                    quick_write(makepath(args.permsdir[0], '_data', 'metamap', args.envtype[0]), 'network' + str(g_net_count) + ': ' + h)
                    meta_host = 'network' + str(g_net_count)
                    g_net_count = g_net_count + 1
                    logv("new meta_host: %s" % meta_host)

                f.write(meta_host + "\n")
            f.close()
            do_user(du, conn, user)
