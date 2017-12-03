#!/usr/bin/env python3
#coding: utf8
#  vim: set sw=4

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
          result += ( '/' + str(i) )
  return result




# permet de vérifier si un tableaux est identique à l'autre
def is_this_array_is_in_the_other(array_one, array_two):

    for val in array_one:
        if val not in array_two:
            return False

    return True

def compare_array(array_one, array_two):
    if not is_this_array_is_in_the_other(array_one, array_two):
        return False
    if not is_this_array_is_in_the_other(array_two,array_one):
        return False

    return True


# depuis un chemin, lit les dossiers et fichiers et met tout ça dans un array de la même structure
def read_folder_to_array(envid, path):
    return os.walk(path)



def drop_all_users(conn):
    sql="SELECT user,host from mysql.user where user not in ('root', 'mysql.sys','user','')"
    cur=conn.cursor()
    cur.execute(sql)
    users=cur.fetchall()

    for user in users:
        print("drop user s%@%s" % (user[0], user[1]))
        cur.execute("DROP USER '%s'@'%s'" % (user[0], user[1]))



#FIXME
# TESTS -------------------------------------------------TO REMOVE-AFTER
if __name__ == '__main__':
    conn=pymysql.connect(host="localhost", user="sexploit", passwd="183a0826ee028d809244926e2321234b")
    drop_all_users(conn)
    conn.close()
