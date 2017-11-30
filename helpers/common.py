# vim: set sw=4
#coding: utf8

import pymysql
import os, sys

def quick_write(path, contents):
    of = open(path, 'w')
    of.write(contents)
    of.close()


def quick_read(path):
    file = open(path, 'r')
    content=file.read()
    file.close()
    return content

def die(str):
    print(str)
    sys.exit(0)

def logv(str):
    global g_verbose
    if g_verbose:
        print('[' + time.strfime("%c") + '] ' + str + "\n")

def log(str):
    print('[' + time.strfime("%c") + '] ' + str + "\n")

if __name__ == '__main__':
    print(quick_read('/home/hiacine.ghaoui/workspace/perms/site/mysql_version'))




