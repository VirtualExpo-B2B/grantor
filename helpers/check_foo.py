#!/usr/bin/env python3
#coding: utf8

from helpers.common import get_connection

# vérifie si les global_pemrs d'un ursr (passée en param) son identique à celles trouvée en base
def check_foo_global_perms(conn, user, global_perms):


    identique=True

    cur=conn.cursor()

    for gperm in global_perms:


        val=cur.execute("SELECT distinct %s from mysql.user where user='%s'" % (gperm.split(':')[0], user))

        print(val)

    conn.close()



def check_db(user):
    return 1

def check_tables(user):
    return 1






if __name__ == '__main__':
    #check_foo_global_perms('velo1dblx01-1', 'app_scenario_bo', )

    conn = get_connection('velo1dblx01-1')

    from helpers.common import quick_read
    s=quick_read('/home/hiacine.ghaoui/workspace/perms/site/app_scenario_bo/global_perms')
    p=s.split("\n")

    check_foo_global_perms(conn, 'app_scenario_bo', p)

