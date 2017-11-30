#!/usr/bin/env python3
#coding: utf8


from common import *
from mappings import *

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



## check if host in local is the same as the hos in db for a user

def check_foo_hosts(envid, conn, user, hosts):
    cur=conn.cursor()

    filer_hosts_list=['',]
    filer_hosts_list.remove('')
    db_hosts=['',]
    db_hosts.remove('')

    for h in hosts:
        arr=get_hosts_from_meta("","",h)# get array of environment ip
        for h2 in arr:
            filer_hosts_list.append(h2) # ajoute les ip trouvées dans le repo local

    cur.execute("SELECT Host FROM mysql.user WHERE User='%s'" % (user))
    for h in cur.fetchall():
        db_hosts.append(h[0])



    if not is_this_array_is_in_the_other(db_hosts, filer_hosts_list):
        return False

    if not is_this_array_is_in_the_other(filer_hosts_list,db_hosts):
        return False

    return True



# check if password in local is the same as the password in db
def check_user_password(envid, conn, user, password_in_local):
    cur = conn.cursor()
    cur.execute("select Password from mysql.user where user ='%s'" % (user))
    r=cur.fetchall()

    return r[0][0].strip()==password_in_local.strip()







## juste des tests --------------------------- TO REMOVE AFTER --------------------------------------
def test_globalperms():
    #check_foo_global_perms('velo1dblx01-1', 'app_scenario_bo', )
    from conn_hia import getconnection
    conn =getconnection()

    from helpers.common import quick_read
    s=quick_read('/home/hiacine.ghaoui/workspace/perms/site/app_scenario_bo/global_perms')
    p=s.strip().split("\n")

    r=check_global_perms_for_user(conn, 'app_scenario_bo', p)

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
    print("test_hosts %s" % (r))

def test_password():
    print("test password")
    from conn_hia import getconnection
    conn = getconnection()

    s = quick_read('/home/hiacine.ghaoui/workspace/perms/site/app_scenario_bo/passwords/dev')
    r=check_user_password("", conn, 'app_scenario_bo', s)
    print(r)


if __name__ == '__main__':
    test_password()





