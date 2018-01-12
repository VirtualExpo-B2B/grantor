#!/usr/bin/env python3
#coding: utf8
# vim: sw=4

from helpers.common import *

def handle_fixed_mappings(meta_host):
    # those mappings are independant of the environment
    # on which the permissions are being applied.
    map = { 
        "any": [ "%" ],
        "veso": [ "10.80.%.%" ],
        "velo30": [ "172.16.30.%" ],
        "velo40": [ "172.16.40.%" ],
        "velo50": [ "172.16.50.%" ],
        "net-vpn": [ "172.16.100.%", "172.16.200.%" ],
        "net-priv": [ "172.16.10.%" ],
        "net-adm": [ "172.16.11.%" ], 
        "admlx": [ "10.80.41.%" ],
        "applx": [ "10.80.50.%" ], # FIXME?
        "net-vpn": [ "172.16.100.%" ],
        "localhost": [ "127.0.0.1", "localhost", "::1" ],
    }
    return map[meta_host] if meta_host in map else False

# convert meta-hosts to an array of MySQL hosts
# folx on ndev1 -> [172.16.130.%]
# envid isn't used yet.
def get_hosts_from_meta(progdir, envtype, envid, meta_host):

    f = handle_fixed_mappings(meta_host)
    if f != False:
        return f

    f = quick_read(makepath(progdir, 'data', 'metamap', envtype))

    map = dict((k.strip(), v.strip()) for k, v in
               (line.split(':') for line in f.split('\n')))

    return [ map[meta_host] ] if meta_host in map else None


# convert MySQL host to meta
def get_meta_from_host(host):

    map = {
        "%": "any",
        "10.80.30.%": "folx",
        "10.80.31.%": "dblx",
        "10.80.32.%": "wklx",
        "10.80.34.%": "bolx",
        "10.80.35.%": "ssolx",
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

    return map[host] if host in map else False
