#!/usr/bin/env python3
#coding: utf8
#  vim: set sw=4

import pymysql
import os, sys
import time


def list_mysql_users(conn, with_host):

    users=[]

    try:
        cur = conn.cursor()
        if with_host:
            cur.execute("SELECT user, host from mysql.user where user not in ('', 'root', 'sys')")
        else:
            cur.execute("SELECT distinct(user) as user from mysql.user where user not in ('', 'root', 'sys')")

        list=cur.fetchall()
        print(list)
        for user in list:
            if with_host:
                users.append(( user[0] , user[1]))
            else:
                users.append(user[0])
    except:
        return []

    for user in users:
        print(user)
    return users

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
        return content.strip()
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
        print('[' + time.strftime("%c") + '] ' + str)

def log(str):
    print('[' + time.strftime("%c") + '] ' + str)

# concatenate all its arguments, adding '/' between elements
def makepath(*arg):
  result = ""
  for i in arg:
      if result == "":
          result += i
      else:
          result += ( '/' + str(i) )
  return result




# permet de vérifier si un tableaux est identique à l'autre
def is_this_array_is_in_the_other(array_one, array_two):

    for val in array_one:
        if val not in array_two:
            return False

    return True

def compare_array(array_one, array_two):
    if not len(array_one) == len(array_two):
        return False

    if not is_this_array_is_in_the_other(array_one, array_two):
        return False
    if not is_this_array_is_in_the_other(array_two,array_one):
        return False

    return True


# depuis un chemin, lit les dossiers et fichiers et met tout ça dans un array de la même structure
def read_folder_to_array(envid, path):
    return os.walk(path)



def drop_all_users(conn):
    cur=conn.cursor()
    users=list_mysql_users(conn, True)

    for user in users:
        sql="drop user 's%'@'%s'" % (user[0], user[1])
        print(sql)
        cur.execute(sql)
