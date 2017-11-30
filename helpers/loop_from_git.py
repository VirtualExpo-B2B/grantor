#!/usr/bin/env python3
#coding: utf8

import argparse
import os, sys

permsdir='../perms'

def logv(str):
  '''verbose logging using global crap'''
  global args
  if args.verbose:
    print(str)


def main():
  parser = argparse.ArgumentParser(description='')
  parser.add_argument('-v', '--verbose', default=False, action='store_true', help='tell me whattya doin')
  parser.add_argument('-f', '--functions', action='store', dest='function_list',
                        type=str, nargs='*', default=['site'],
                        help="Examples: -f site, -f site tech dmt")

  global args
  args = parser.parse_args()


  logv('printsmthg')
  logv("List of functions: {}".format(args.function_list))

  for function in args.function_list:
    logv("checking perms for function %s" % function)
  
#  for root, dirs, files in os.walk(permsdir/function):
#    for file in files:
#      print os.path.join(root, file)
#   
   
   
   #of = open(path, 'r')

if __name__ == "__main__":
  main()
