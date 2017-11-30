#!/usr/bin/env python3
#coding: utf8

import helpers.common

# vérifie si les global_pemrs d'un ursr (passée en param) son identique à celles trouvée en base
def check_foo_global_perms(conn, user, global_perms):

    identique=True

    cur=conn.cursor()

    for gperm in global_perms:

        if len(gperm)>0:
            cur.execute("SELECT distinct %s from mysql.user where user='%s'" % (gperm.split(':')[0], user))
            db_val=cur.fetchall()[0][0]
            val=gperm.split(':')[1].strip()
            identique=val==db_val
            if identique==False:
                print("PAS PAREIL --> %s - %s " % (val,db_val))
                return identique

    return identique



def check_foo_hosts(conn, user, hosts):

    identique=True

    cur=conn.cursor()

    print(hosts)

    for host in hosts:

        if len(host)>0:
            cur.execute("SELECT Host FROM mysql.user WHERE User='%s'" % (user))
            db_hosts=cur.fetchall()[0]
            print(db_hosts)
            '''
            identique=val==db_val
            if identique==False:
                print("PAS PAREIL --> %s - %s " % (val,db_val))
                return identique
            '''

    return identique










## juste des tests
def test_globalperms():
    #check_foo_global_perms('velo1dblx01-1', 'app_scenario_bo', )
    from conn_hia import getconnection
    conn =getconnection()

    from helpers.common import quick_read
    s=quick_read('/home/hiacine.ghaoui/workspace/perms/site/app_scenario_bo/global_perms')
    p=s.strip().split("\n")

    r=check_foo_global_perms(conn, 'app_scenario_bo', p)

    conn.close()

    print(r)

def test_hosts():
    #check_foo_global_perms('velo1dblx01-1', 'app_scenario_bo', )
    from conn_hia import getconnection
    conn =getconnection()

    from helpers.common import quick_read
    s=quick_read('/home/hiacine.ghaoui/workspace/perms/site/app_scenario_bo/hosts/dev')
    p=s.strip().split("\n")

    print (p)
   # r=check_foo_global_perms(conn, 'app_scenario_bo', p)

    conn.close()

   # print(r)





if __name__ == '__main__':
    test_hosts()





