import os
from helpers.mappings import *
from helpers.common import *

def drop_user(conn, user, host):
    cur = conn.cursor()
    cur.execute("DELETE FROM mysql.user WHERE User='%s' AND Host='%s'" % ( user, host ))
    cur.fetchall()

def revoke_db_privs(conn, user, host, db):
    cur = conn.cursor()
    cur.execute("DELETE FROM mysql.db WHERE User='%s' AND Host='%s' AND Db='%s'" % ( user, host, db ))
    cur.fetchall()

def check_global_users(conn, permsdir, functions, envtype, envid):
    cur = conn.cursor()
    res = cur.execute('SELECT User, Host FROM mysql.user')

    for line in cur.fetchall():
        user = line[0]
        sql_host = line[1]

        # reverse lookup
        host = map_meta_from_host(sql_host)

        # m = folx

        foundit = False
        for f in functions:
            if not os.path.isfile(makepath(permsdir, f,  user, 'hosts', envtype)):
                break
            else:
                r = quick_read(makepath(permsdir, f,  user, 'hosts', envtype))
                meta = r.split('\n')
                if m in meta:
                    foundit = True
                    break

        if foundit == False:
                logv("dropping user %s@%s" % (user, host))
                drop_user(conn, user, host)

def check_db_privs(conn, permsdir, functions, envtype, envid):

    cur = conn.cursor()
    res = cur.execute("SELECT * FROM mysql.db")

    for row in res.fetchall():
        host = row[0]
        db = row[1]
        user = row[2]

        # this is quite easy: if the file exists in permsdir,
        # then the proper perms will have been applied during
        # the previous stage. if the file is absent in permsdir,
        # it means the user no longer has any privs on the db.
        flag = False
        for f in functions:
            if os.path.isfile(makepath(permsdir, f, user, 'databases', db, 'perms')):
                flag = True

        if flag == False:
            revoke_db_privs(conn, user, host, db)

def delete_table_priv(conn, host, db, user, table_name):
    cur = conn.cursor()
    cur.execute("DELETE FROM mysql.tables_priv WHERE User='%s' AND Db='%s' AND Host='%s' AND Table_name='%s'" % ( user, db, host, table_name ))
    cur.fetchall()

# iterates over each row of mysql.tables_priv
def check_tables_privs(conn, permsdir, functions, envtype, envid):
    cur = conn.cursor()
    res = cur.execute("SELECT Host, Db, User, Table_name FROM mysql.tables_priv")

    for host, db, user, table_name in res.fetchall():
        found = False
        for f in functions:
            if os.path.isfile(makepath(permsdir, f, user, 'databases', db, 'tables', table_name)):
                found = True
                break
        if found == False:
            delete_table_priv(conn, host, db, user, table_name)

def loop_from_db(conn, permsdir, functions, envtype, envid):
    check_global_users(conn, permsdir, functions, envtype, envid)
    check_db_privs(conn, permsdir, functions, envtype, envid)
    check_tables_privs(conn, permsdir, functions, envtype, envid)
