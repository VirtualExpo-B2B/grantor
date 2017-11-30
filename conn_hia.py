#conding: utf8

import pymysql

def getconnection():
    return pymysql.connect(host="velo1dblx01-1", user="dev", passwd="PleaseBeCareful")


