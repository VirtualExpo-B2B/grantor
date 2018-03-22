#!/usr/bin/env python3
#coding: utf8

import argparse
import socket
import os, re
import signal
import shutil
import tempfile

from helpers.common import *
from helpers.loop_from_git import *
from helpers.loop_from_db import *

grantor_repo_version = "1.4"

def get_envtype(args, hostname):
    envmap_path = makepath(args.permsdir, '_data', 'envmap')
    if not os.path.isdir(envmap_path):
        die("ERROR: unable to find envmap in the permissions repository,\n" + \
            "       and no --envtype given.")

    for filename in os.listdir(envmap_path):
        pattern = quick_read(makepath(envmap_path, filename))
        if re.search(pattern, hostname):
            return filename

    die("ERROR: unable to determine envtype, nothing matched. Check your\n" + \
        "envmap or use --envtype.")

def handler(signum, frame):
    print("Timeout reached")
    die("ABORT: answer me!")

def git_clone_repository(args):
    log("cloning %s in %s" % (args.repository, args.permsdir))
    os.system("git clone %s %s" % (args.repository, args.permsdir))

    if args.branch and args.branch != "master":
        os.system("cd %s && git checkout %s" % (args.permsdir, args.branch))

    return True


def main():
    parser = argparse.ArgumentParser(description='Applies permissions to a MySQL instance')
    parser.add_argument('-s', '--server', help='address or hostname of the MySQL server', required=True, type=str, action='store')
    parser.add_argument('-u', '--user',  default='root', help='username to authenticate with', type=str, action='store')
    parser.add_argument('-p', '--passwd', help='password of the user to authenticate with', required=True, type=str, action='store')
    parser.add_argument('-P', '--permsdir', required=False, help='path to the perms directory', type=str)
    parser.add_argument('-R', '--repository', required=False, type=str, action='store', help='URL of the git repository to clone')
    parser.add_argument('-b', '--branch', required=False, type=str, action='store', help='branch to checkout in the cloned repository')
    parser.add_argument('-f', '--function', required=True, help='functions to restore, ex: common,site,dwh', type=str, dest='functions_list', action='store')
    parser.add_argument('-U', '--single-user', dest='single_user', help='if you wanna work with only one user', required=False, type=str)
    parser.add_argument('-e', '--envtype', dest='envtype', help='envtype override', required=False, type=str)
    parser.add_argument('-n', '--noop', default=False, action='store_true', help='scared, huh?')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='tell me whattya doin\'')

    args = parser.parse_args()
    
    log("MySQL Grantor starting...")
    
    args.functions_list = args.functions_list.split(',')
    p = __file__
    while (os.path.islink(p)):
        p = os.readlink(p)
    args.progdir = os.path.dirname(p)

    if not args.repository and not args.branch and not args.permsdir:
        args.repository = 'ssh://git@gitlab.virtual-expo.com/sql/perms.git'
        log('WARNING: you didn\'t specify --permsdir, nor --repository, nor --branch.')
        log("WARNING: assuming %s / master" % args.repository)

    if args.repository or args.branch:
        if not args.repository and args.branch:
            args.repository = 'http://gitlab.virtual-expo.com/sql/perms.git'

        # if we got a -P, clone into this directory.
        if args.permsdir:
            # git won't clone into an non-empty directory.
            if len(os.listdir(args.permsdir)) > 0:
                die('you specified both --repository/--branch and --permsdir, but target directory is not empty.')
        else: # otherwise, clone into a temporary directory
            args.tmpdir = tempfile.TemporaryDirectory()
            args.permsdir = args.tmpdir.name

        git_clone_repository(args) or die('unable to clone the git repository')

    try:
        repository_version = quick_read(makepath(args.permsdir, '_version'))
    except:
        log("ERROR: the repository has no _version file; this version of Grantor requires it.")
        sys.exit(1)

    if float(repository_version) != float(grantor_repo_version):
        log("ERROR: permissions repository version is %s, expected %s" % ( repository_version, grantor_repo_version ) )
        sys.exit(1)
    
    flag_common = False
    for f in args.functions_list:
        if f == 'common':
            flag_common = True
        if not os.path.isdir(makepath(args.permsdir, f)):
            die("error: function %s doesn't exist in %s" % (f, args.permsdir))
    if not flag_common and not args.single_user:
        timeout = 5 # timeout in seconds for reading the answer
        log("WARNING: You have not called the function 'common'. You are going to drop the root user and others.")
        log("Are you really sure dumb ass ? (y/N)")
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(timeout)
        answer = input('--> ')
        # disable the alarm after success
        signal.alarm(0)
        if answer != 'y':
            die("ABORT: invoke the 'common' function")

    if args.noop:
        log("> performing a dry-run (--noop)")

    global_set(g_verbose, args.verbose)
    
    tty = open("/dev/stdout", "r")
    args.isatty = tty.isatty()

    logv("connecting to %s (user: %s)... " % (args.server, args.user))
    conn = pymysql.connect( host=args.server, user=args.user, passwd=args.passwd )
    cur = conn.cursor()
    cur.execute("SHOW VARIABLES LIKE 'hostname'")
    res = cur.fetchall()
    hostname = res[0][1]

    logv("connected!")
    logv("server hostname: %s" % hostname)

    if not args.envtype:
        args.envtype = get_envtype(args, hostname)

    logv("-> using envtype: %s" % args.envtype)

    log("* step 1 - applying permissions from the repository")
    loop_from_git(conn, args)
    log("* step 2 - removing extra permissions from the server")
    loop_from_db(conn, args)

    if not args.noop:
        log("flushing privileges...")
        cur.execute("FLUSH PRIVILEGES")

    conn.close()

    log("Job done.")


if __name__ == "__main__":
    main()
