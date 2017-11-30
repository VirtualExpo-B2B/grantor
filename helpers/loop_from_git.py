#!/usr/bin/env python3
#coding: utf8

import argparse
import os, sys
from helpers.common import *
from helpers.check_foo import *

def loop_from_git(conn, permsdir, functions, envtype, envid):
  logv_set(True)

  logv("List of functions: {}".format(functions))

  for function in functions:
    logv("checking perms for function %s" % function)
    functiondir = '../' + permsdir + '/' + function
    logv("functiondir: %s" % functiondir)
  
    dirs = os.listdir(functiondir)

    for user in dirs:
      logv("user: %s" % user)

      #from helpers.common import quick_read
      global_perms=quick_read(str(permsdir) + '/' + str(function) + '/' + str(user) + '/global_perms')
      global_perms_line=global_perms.split("\n")

      check_foo_global_perms(conn, user, global_perms_line)


if __name__ == "__main__":

  loop_from_git('conn', '/home/claire/Repos/mysql/perms', ['site'], 'dev', 1)
