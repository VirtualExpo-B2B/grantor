#!/usr/bin/env python3
#coding: utf8


from helpers.common import *
from helpers.mappings import *

# mysql -uroot -p$(cat /root/.mpwd) -B -N -e 'describe mysql.db' | grep _priv | awk '{ print $1 }'  | sed -e 's/^/"/' -e 's/$/", /' |  '\n'
user_db_privs = [ "Select_priv", "Insert_priv", "Update_priv", "Delete_priv", "Create_priv", "Drop_priv", "Grant_priv", "References_priv", "Index_priv", "Alter_priv", "Create_tmp_table_priv", "Lock_tables_priv", "Create_view_priv", "Show_view_priv", "Create_routine_priv", "Alter_routine_priv", "Execute_priv", "Event_priv", "Trigger_priv" ]


# get one host for a user
def get_first_host_for_user(conn, user):
    sql = "SELECT DISTINCT Host FROM mysql.user WHERE User = '%s' LIMIT 1" % (user)
    cur = conn.cursor()
    cur.execute(sql)
    r = cur.fetchall()
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
            logv("checking global priv %s for user %s@%s" % ( gperm[0], user, sql_host ) )
            cur.execute("SELECT %s FROM mysql.user WHERE User='%s' AND Host='%s'" % (gperm[0], user, sql_host))
            # FIXME: assert 1 row?
            res = cur.fetchall()
            if len(res) == 0:
              log("user %s@%s doesn't exist yet, triggering update" % ( user, sql_host ))
              return False
            db_val = res[0][0]
            val = gperm[1]
            uptodate = (val == db_val)
            if uptodate == False:
                logv("user %s@%s: global permissions are NOT up-to-date [priv %s:%s should be %s" % (user, sql_host, gperm[0], db_val, val))
                return False

    if uptodate == True:
        logv("user %s@%s: global permissions are up-to-date" % (user, sql_host))

    return uptodate


# check if password in local is the same as the password in db
def check_user_password(conn, user, sql_host, password):
    logv("checking password for user %s@%s" % ( user, sql_host ) )
    cur = conn.cursor()
    cur.execute("select password from mysql.user where user ='%s' AND host='%s'" % (user, sql_host))
    r = cur.fetchall()
    if len(r) == 0:
      return False
    return r[0][0] == password

def apply_user_password(conn, user, sql_host, password, noop):
    noop_str = '[noop] ' if noop else ''
    
    log("%supdating password for %s@%s" % ( noop_str, user, sql_host ) )

    if not noop:
        cur = conn.cursor()
        cur.execute("UPDATE mysql.user SET password = '%s' WHERE user='%s' AND host='%s'" % ( password, user, sql_host ))
        cur.fetchall()


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


def check_user_table_priv(conn, permsdir, function, user, host, db, table):
    path = makepath(permsdir, function, user, 'databases', db, 'tables', table)

    sql = "SELECT Table_priv FROM mysql.tables_priv WHERE User = '%s' AND Host = '%s' AND Db = '%s' AND Table_name='%s'" % ( user, host, db, table )

    cur = conn.cursor()
    cur.execute(sql)
    res = cur.fetchall()

    if len(res) == 0:
        logv("missing table priv for %s@%s on %s.%s [function=%s]" % (  user, host, db, table, function ) )
        return False

    # split the SQL set into an array
    remote_privs = res[0][0].split(',')
    target_privs = quick_read(path).split('\n')

    # no target privs - nothing to update.
    if target_privs == False:
        logv("empty target privileges for %s@%s on %s.%s [function=%s]" % ( user, host, db, table, function ) )
        return True

    if 'Create' not in target_privs:
        target_privs.append('Create')
     
    remote_privs.sort()
    target_privs.sort()

    if target_privs == remote_privs:
        logv("privileges are OK for %s@%s on %s.%s [function=%s]" % ( user, host, db, table, function ) )
        return True
    else:
        logv("privilege mismatch [%s, should be %s] for %s@%s on %s.%s [function=%s]" % ( remote_privs, target_privs, user, host, db, table, function ) )
        return False
