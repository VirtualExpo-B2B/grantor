#coding: utf8

from tkinter import *
import os
from helpers.common import *

from tools import *

permsdir="H:\\CODE\\PYTHON\\Perms"

current_info={'type_db': '', 'user': '', 'db': '', 'table': '', 'db_global_perm': (), 'db_perms': (), 'table_priv': ()}


# -------------------- EVENTS ----------------------------------------------
## TYPE DB
def liste_type_double_leftclick_handler(liste_type_db, liste_users, l_db, l_table):

    current_info['type_db'] = str((liste_type_db.get(ACTIVE)))
    current_info['user'] = ''
    current_info['db'] = ''
    current_info['table'] = ''
    current_info['db_global_perm'] = ()
    current_info['db_perms'] = ()

    dir = os.path.join(permsdir, "") + current_info['type_db']

    users = get_dir_list(dir)

    listbox_clear(liste_users)
    listbox_clear(l_db)
    listbox_clear(l_table)


    for user in users:
        liste_users.insert('end', user)





## USER
def liste_user_double_leftclick_handler(l_user, l_db, l_table):
    current_info['user']=str((l_user.get(ACTIVE)))
    current_info['db']=''
    current_info['table']=''
    current_info['db_global_perm']=()
    current_info['db_perms']=()

    dir = "%s%s/%s" % (os.path.join(permsdir, ""), current_info['type_db'], current_info['user'])

    if os.path.exists("%s/global_perms" %(dir)):
        s=quick_read("%s/global_perms" %(dir)).split('\n')
        print("global perms pour %s" % current_info['user'])
        print(s)

    dir = "%s/databases/" % (dir)

    dbs = get_dir_list(dir)
    listbox_clear(l_db)
    listbox_clear(l_table)

    for db in dbs:
        l_db.insert('end', db)




## DB
def liste_double_leftclick_handler(l_db, l_table):
    current_info['db'] = str((l_db.get(ACTIVE)))
    current_info['table'] = ''
    current_info['db_global_perm'] = ()
    current_info['db_perms'] = ()

    dir = "%s%s/%s/databases/%s" % (os.path.join(permsdir, ""), current_info['type_db'], current_info['user'], current_info['db'])
    perms_file="%s/perms" % (dir)
    dir="%s/tables" % (dir)

    if os.path.exists(perms_file):
        current_info['db_perms']=quick_read(perms_file).split('\n')
        print(str(current_info['db_perms']))



    tables = get_file_list(dir)
    listbox_clear(l_table)
    for table in tables:
        l_table.insert('end', table)



def liste_table_doubleclick_handle(l_table):
    current_info['table'] = str((l_table.get(ACTIVE)))


    file_path = "%s%s/%s/databases/%s/tables/%s" % (os.path.join(permsdir, ""), current_info['type_db'], current_info['user'], current_info['db'], current_info['table'])
    print(file_path)


