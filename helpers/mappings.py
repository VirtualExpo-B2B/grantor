#!/usr/bin/env python3
#coding: utf8
# vim: sw=4

from helpers.common import *

# convert meta-hosts to an array of MySQL hosts
# we first look for the most specific mapping, then we
# fallback to common
# note: envid isn't used yet.
def get_hosts_from_meta(permsdir, envtype, envid, meta_host):

    for source in envtype, 'common':
        m = parse_map(makepath(permsdir, '_data', 'metamap', source))
        f = search_meta(m, meta_host)
        if f != None:
            return f

    return None

# convert MySQL host to meta
def get_meta_from_host(permsdir, envtype, envid, host):
    for source in envtype, 'common':
        m = parse_map(makepath(permsdir, '_data', 'metamap', source))
        f = search_host(m, host)
        if f != None:
            return f

    return None

def search_meta(m, meta_host):
    return m[meta_host] if meta_host in m else None

def search_host(m, host):
    for meta in m:
        if host in m[meta]:
            return meta

    return None

def parse_map(filepath):
    f = quick_read(filepath)

    m = dict((k.strip(), v)
            for k, v in ((k2, v2.split(','))
	        for k2, v2 in (line.split(':', maxsplit=1)
	            for line in f.split('\n'))))
    for meta_host in m:
        m[meta_host] = [x.strip() for x in m[meta_host]]
    return m
