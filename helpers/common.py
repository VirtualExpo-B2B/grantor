# vim: set sw=4
#coding: utf8

import pymysql
import os, sys
import time



def quick_write(path, contents):
    try:
        of = open(path, 'w')
        of.write(contents)
        of.close()
    except:
        return False


def quick_read(path):
    try:
        file = open(path, 'r')
        content=file.read()
        file.close()
        return content
    except:
        return False

def die(str):
    print(str)
    sys.exit(0)

def logv_set(flag):
    global g_verbose
    g_verbose = flag

def logv(str):
    global g_verbose
    if g_verbose:
        print('[' + time.strftime("%c") + '] ' + str + "\n")

def log(str):
    print('[' + time.strftime("%c") + '] ' + str + "\n")

# concatenate all its arguments, adding '/' between elements
def makepath(*arg):
  result = ""
  for i in arg:
      if result == "":
          result += i
      else:
          result += ( '/' + i )
  return result




# permet de vérifier si un tableaux est identique à l'autre
def is_this_array_is_in_the_other(array_one, array_two):

    for val in array_one:
        if val not in array_two:
            return False

    return True





