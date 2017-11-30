#!/usr/bin/env python3
#coding: utf8

import argparse
import os, sys
import common


def loop_from_git(conn, permsdir, functions, envtype, envid):

  logv("List of functions: {}".format(functions))

  for function in functions:
    logv("checking perms for function %s" % function)
    functiondir = permsdir + '/' + function
    logv("functiondir: %s" % functiondir)
  
    dirs = os.listdir(functiondir)

    for directory in dirs:
      logv("directory: %s" % directory)


#    for dirs in os.listdir(functiondir):
#      logv("dir:" % dirs)
#    for root, dirs, files in os.walk(functiondir):
#      for filename in files:
#        logv(os.path.join(root, filename))
#      for dirname in dirs:
#        logv(os.path.join(root, dirname))
#        logv(
   
   
   
   #of = open(path, 'r')

if __name__ == "__main__":
#  parser = argparse.ArgumentParser(description='')
#  parser.add_argument('-v', '--verbose', default=False, action='store_true', help='tell me whattya doin')
#  parser.add_argument('-f', '--functions', action='store', dest='function_list',
#                        type=str, nargs='*', default=['site'],
#                        help="Examples: -f site, -f site tech dmt")
#
#  args = parser.parse_args()


  loop_from_git('conn', '/home/claire/Repos/mysql/perms', ['site'], 'dev', 1)
