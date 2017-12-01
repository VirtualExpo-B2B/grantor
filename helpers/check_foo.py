#!/usr/bin/env python3
#coding: utf8


from helpers.common import *
from helpers.mappings import *

# vérifie si les global_pemrs d'un ursr (passée en param) son uptodate à celles trouvée en base
# check whether global_perms for a specific user@sql_host are up-to-date against an array of permissions
def check_global_perms(conn, user, sql_host, global_perms_content):
    uptodate=True
    cur=conn.cursor()

    for gperm in global_perms_content:
        if len(gperm) > 0:
            cur.execute("SELECT %s FROM mysql.user WHERE User='%s' AND Host='%s'" % (gperm[0], user, sql_host))
            # FIXME: assert 1 row?
            db_val = cur.fetchall()[0][0]
            val = gperm[1]
            uptodate = (val == db_val)
            if uptodate == False:
                logv("user %s@%s: global permissions are not up-to-date" % (user, sql_host))
                return uptodate

    return uptodate


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



    if not compare_array(db_hosts, filer_hosts_list):
        return False

    return True



# check if password in local is the same as the password in db
def check_user_password(envid, conn, user, password_in_local):
    cur = conn.cursor()
    cur.execute("select Password from mysql.user where user ='%s'" % (user))
    r=cur.fetchall()

    return r[0][0].strip()==password_in_local.strip()


# check si le contenu des droits databases sur le filer est uptodate au droits database en db
def check_user_for_database(envid, conn, user, user_local_dir):

    sql_get_user_host="SELECT DISTINCT Host FROM mysql.tables_priv WHERE User = '%s' limit 1" % (user)
    cur=conn.cursor()
    cur.execute(sql_get_user_host)

    r=cur.fetchall()

    host=r[0][0]

    sql_get_user_priv_for_host="SELECT Db,Table_name, Table_priv FROM mysql.tables_priv WHERE User = '%s' AND Host = '%s'" % (user, host)

    cur.execute(sql_get_user_priv_for_host)

    priv = cur.fetchall()


    droits_local=['',]
    droits_local.remove('')

    p = read_folder_to_array('', user_local_dir)
    for path, subdirs, files in p:

        if 'databases' in path.split('/') and 'tables' in path.split('/'):

            db=path.replace(user_local_dir + "databases/",'').replace('/tables','')
            droits_local.append((db,files[0],quick_read(path + "/" + files[0])))



    print(priv)
    print(droits_local)
    if not compare_array(priv, droits_local):
        return False


    return True

def check_db_perms(arg1, arg2, arg3, arg4, arg5):
    print("check db perms")


## juste des tests --------------------------- TO REMOVE AFTER --------------------------------------
def test_databasepriv():
    print("test database")
    from conn_hia import getconnection
    conn = getconnection()

    r=check_user_for_database("", conn, 'app_scenario_bo','/home/hiacine.ghaoui/workspace/perms/site/app_inovo/')
    print(r)

'''
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
'''
'''
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
'''
'''
def test_password():
    print("test password")
    from conn_hia import getconnection
    conn = getconnection()

    s = quick_read('/home/hiacine.ghaoui/workspace/perms/site/app_scenario_bo/passwords/dev')
    r=check_user_password("", conn, 'app_scenario_bo', s)
    print(r)
'''



if __name__ == '__main__':
    test_databasepriv()





