#!/usr/bin/env python3
#coding: utf8


from helpers.common import *
from helpers.mappings import *

# mysql -uroot -p$(cat /root/.mpwd) -B -N -e 'describe mysql.db' | grep _priv | awk '{ print $1 }'  | sed -e 's/^/"/' -e 's/$/", /' |  '\n'
user_db_privs = [ "Select_priv", "Insert_priv", "Update_priv", "Delete_priv", "Create_priv", "Drop_priv", "Grant_priv", "References_priv", "Index_priv", "Alter_priv", "Create_tmp_table_priv", "Lock_tables_priv", "Create_view_priv", "Show_view_priv", "Create_routine_priv", "Alter_routine_priv", "Execute_priv", "Event_priv", "Trigger_priv" ]


# get one host for a user
def get_first_host_for_user(conn, user):
    sql=sql_get_user_host="SELECT DISTINCT Host FROM mysql.user where user = '%s' limit 1" % (user)
    cur=conn.cursor()
    cur.execute(sql)
    r=cur.fetchall()
    try:
        return r[0][0]
    except:
        return False

# vérifie si les global_pemrs d'un ursr (passée en param) son uptodate à celles trouvée en base
# check whether global_perms for a specific user@sql_host are up-to-date against an array of permissions
def check_global_perms_ok(conn, user, sql_host, global_perms_content):
    uptodate=True
    cur=conn.cursor()

    for gperm in global_perms_content:
        if len(gperm) > 0:
            logv("checking priv %s for user %s@%s" % ( gperm[0], user, sql_host ) )
            cur.execute("SELECT %s FROM mysql.user WHERE User='%s' AND Host='%s'" % (gperm[0], user, sql_host))
            # FIXME: assert 1 row?
            res = cur.fetchall()
            if len(res) == 0:
              log("USER %s@%s doesn't exist yet, triggering update" % ( user, sql_host ))
              return False
            db_val = res[0][0]
            val = gperm[1]
            uptodate = (val == db_val)
            if uptodate == False:
                logv("user %s@%s: global permissions are not up-to-date" % (user, sql_host))
                return uptodate

    logv("user %s@%s: global permissions are up-to-date" % (user, sql_host))
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

def check_db_perms(conn, permsdir, function, user, db):
    True


# check if password in local is the same as the password in db
def check_user_password(conn, user, sql_host, password):
    logv("checking password for user %s@%s" % ( user, sql_host ) )
    cur = conn.cursor()
    cur.execute("select password from mysql.user where user ='%s' AND host='%s'" % (user, sql_host))
    r = cur.fetchall()
    if len(r) == 0:
      return False
    return r[0][0] == password

def apply_user_password(conn, user, sql_host, password):
    log("UPDATING password for user %s@%s" % ( user, sql_host ) )
    cur = conn.cursor()
    cur.execute("UPDATE mysql.user SET password = '%s' WHERE user='%s' AND host='%s'" % ( password, user, sql_host ))
    cur.fetchall()


#FIXME: IN PROGRESS
def check_user_db_priv(conn, permsdir, function, user, host, db):

    local_db_priv=quick_read(permsdir + '/' + function + '/' + user + '/databases/' + db + '/perms').split('\n')
    mysql_db_priv=[]
    cur = conn.cursor()

    for priv in user_db_privs:
        cur.execute("SELECT %s FROM mysql.db WHERE User='%s' AND Host='%s' AND Db='%s'" % (priv, user, host, db))
        res = cur.fetchall()
        if len(res) > 0:
            mysql_db_priv.append("%s: %s" % (priv, res[0][0]))


    return compare_array(local_db_priv, mysql_db_priv)





#Application des permissions db pour un user
def apply_user_db_priv(conn, permsdir, function, user, host, db):

    log("UPDATING %s db permision for user %s@%s" % (db, user, host))
    local_db_priv=quick_read(permsdir + '/' + function + '/' + user + '/databases/' + db + '/perms').split('\n')

    columns = ['User', 'Host', 'Db']
    privs = []
    for perm in local_db_priv:

        columns.append(perm.split(': ')[0])
        privs.append("'" + perm.split(': ')[1] + "'")

    sql = "REPLACE INTO mysql.db ( %s ) VALUES ( '%s', '%s', '%s', %s )" % (','.join(columns), user, host, db, ','.join(privs))

    cur = conn.cursor()
    cur.execute(sql)

    return True


# check si le contenu des droits databases sur le filer est uptodate au droits database en db
def check_user_for_database(envid, conn, user, host, user_local_dir):
    sql_get_user_host="SELECT DISTINCT Host FROM mysql.tables_priv WHERE User = '%s' and host='%s'" % (user,host)
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

    if not compare_array(priv, droits_local):
        return False


    return True


