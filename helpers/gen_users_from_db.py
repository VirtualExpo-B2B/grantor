#!/usr/bin/env python3
#coding: utf8

import argparse
import code
import time
import os, sys
import pymysql

from helpers.do_user_password import *
from helpers.mappings import *

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
                safe_mkdir(makepath(args.permsdir, '_data', 'metamap'))
                if not os.path.isfile(makepath(args.permsdir, '_data', 'metamap', 'common')):
                    f_meta_common = open(makepath(args.permsdir, '_data', 'metamap', 'common'), 'w')
                    f_meta_common.write('any: %' + "\n")
                    f_meta_common.close
                if os.path.isfile(makepath(args.permsdir, '_data', 'metamap', args.envtype)):
                    meta_host = get_meta_from_host(args.permsdir, envtype, h)
                if meta_host == False:
                    log("WARNING: creating mapping network_%s: %s" % (user, h))
                    f_meta_envtype = open(makepath(args.permsdir, '_data', 'metamap', args.envtype), 'w')
                    f_meta_envtype.write('network_' + user + ': ' + h)
                    f_meta_envtype.close
                    meta_host = get_meta_from_host(args.permsdir, envtype, h)
                f.write(meta_host + "\n")
            f.close()
            do_user(du, conn, user)
