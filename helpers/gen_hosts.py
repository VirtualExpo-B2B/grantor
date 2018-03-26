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

def gen_hosts(du, cur, user, args, g_net_count):
    '''map all the hosts associated with a mysql user to meta hosts, and write meta hosts'''
    logv("g_net_count = %d" % g_net_count)
    cur.execute('SELECT Host FROM mysql.user WHERE User="%s"' % ( user ) )
    res = cur.fetchall()
    safe_mkdir(du + '/hosts')
    f = open(du + '/hosts/' + args.envtype[0], 'w')
    safe_mkdir(makepath(args.permsdir[0], '_data'))
    safe_mkdir(makepath(args.permsdir[0], '_data', 'metamap'))
    fmap = open(makepath(args.permsdir[0], '_data', 'metamap', args.envtype[0]), 'a')
    for host in res:
        h = host[0]
        meta_host = None
        if not os.path.isfile(makepath(args.permsdir[0], '_data', 'metamap', 'common')):
            quick_write(makepath(args.permsdir[0], '_data', 'metamap', 'common'), 'any: %' + "\n")
        if os.stat(makepath(args.permsdir[0], '_data', 'metamap', args.envtype[0])).st_size != 0:
            meta_host = get_meta_from_host(args.permsdir[0], args.envtype[0], h)
            logv("meta_host from existing metamap: %s" % meta_host)
        if meta_host == None:
            log("WARNING: creating mapping network%d: %s" % (g_net_count, h))
            meta_host = 'network' + str(g_net_count)
            fmap.write(meta_host + ': ' + h + "\n")
            g_net_count = g_net_count + 1
            logv("new meta_host: %s" % meta_host)

        f.write(meta_host + "\n")
    fmap.close()
    f.close()
    return g_net_count
