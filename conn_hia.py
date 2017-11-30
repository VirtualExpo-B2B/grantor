#conding: utf8

import pymysql

def getconnection():
    return pymysql.connect(host="velo1dblx01-1.virtual-expo.com", user="dev", passwd="PleaseBeCareful")


