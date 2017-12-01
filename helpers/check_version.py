#!/usr/bin/env python3
# #coding: utf8

import pymysql
from helpers.common import  *






def check_mysql_version(conn, local_mysql_version_file):



    # we wrongfully assume that `d' has been created
    cur = conn.cursor()
    cur.execute('SHOW VARIABLES LIKE "version"')
    version = cur.fetchall()[0][1].split('-')[0]


    git_mysql_version=quick_read(local_mysql_version_file).split('-')[0]

    print("%s / %s" % (git_mysql_version, version))


    return version==git_mysql_version



if __name__ == '__main__':

    from conn_hia import getconnection

    conn = getconnection()

    # FIXME : voir comment faire pour le chemin


    v=check_mysql_version(conn, "/home/hiacine.ghaoui/workspace/perms/site/mysql_version")

    print("yyy %s" % (v))
    conn.close()


    if v:
        print("même version")
    else:
        print("WARNING : version mysql différente")
