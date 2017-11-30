#coding: utf8

import pymysql
from helpers.common import  quick_read





def check_mysql_version(db_connection, local_mysql_version_file):



    # we wrongfully assume that `d' has been created
    cur = db_connection.cursor()
    cur.execute('SHOW VARIABLES LIKE "version"')
    version = cur.fetchall()[0][1].split('-')[0]


    git_mysql_version=quick_read(local_mysql_version_file).split('-')[0]

    return version==git_mysql_version



if __name__ == '__main__':

    #FIXME : à mettre dans un fichier commun, voir pour la recupe des user mdp
    conn = pymysql.connect(host="velo1dblx01-1", user="dev", passwd="PleaseBeCareful")

    # FIXME : voir comment faire pour le chemin
    perms_dir = "/home/hiacine.ghaoui/workspace/perms"

    v=check_mysql_version(conn, "%s/site/mysql_version" % (perms_dir))
    conn.close()


    if v:
        print("même version")
    else:
        print("WARNING : version mysql différente")
