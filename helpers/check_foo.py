#!/usr/bin/env python3
#coding: utf8

from common import *

# vérifie si les global_pemrs d'un ursr (passée en param) son identique à celles trouvée en base
def check_global_perms_for_user(conn, user, sql_host, global_perms_content):

    identique=True

    cur=conn.cursor()

    for gperm in global_perms_content:

        if len(gperm)>0:
            cur.execute("SELECT %s FROM mysql.user WHERE User='%s' AND Host='%s'" % (gperm.split(':')[0], user, sql_host))
            # FIXME: assert 1 row!
            db_val=cur.fetchall()[0][0]
            val=gperm.split(':')[1].strip()
            identique=val==db_val
            if identique==False:
                print("PAS PAREIL --> %s - %s " % (val,db_val))
                return identique

    return identique



def check_foo_hosts(envid, conn, user, hosts):

    identique=True

    cur=conn.cursor()

    print(hosts)



    filer_hosts_list=('',)

    for host in hosts:


        print(host)



        if len(hosts)>0:
            cur.execute("SELECT Host FROM mysql.user WHERE User='%s'" % (user))
            db_hosts=cur.fetchall()[0][0]
            print(db_hosts)
            filer_hosts_list.__add__(db_hosts)

            '''
            identique=val==db_val
            if identique==False:
                print("PAS PAREIL --> %s - %s " % (val,db_val))
                return identique
            '''

    print(filer_hosts_list)

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

    r=check_foo_hosts('ndev1',conn, 'app_scenario_bo', p)

    conn.close()

   # print(r)





if __name__ == '__main__':
    test_hosts()





