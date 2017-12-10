#coding: utf8

from tkinter import *
from myevents import *
from tools import *
import os


gui_version="1.0.0"



# ---------------------- FORMS --------------------------------------------
def center(toplevel):
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w/2 - size[0]/2
    y = h/2 - size[1]/2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))

def display_main_form():
    main=Tk()
    main['bg'] = 'white'
    main.resizable(width=False, height=False)
    main.geometry('{}x{}'.format(700, 600))
    center(main)

    lb= PanedWindow(main, orient=HORIZONTAL)
    lb.pack(side=BOTTOM, expand=Y, fill=BOTH, pady=2, padx=2)

    lp = PanedWindow(main, orient=HORIZONTAL)
    lp.pack(side=LEFT, expand=Y, fill=BOTH, pady=2, padx=2)

    lt = PanedWindow(main, orient=VERTICAL)
    lt.pack(side=LEFT, expand=Y, fill=BOTH, pady=2, padx=2)

    lrr = PanedWindow(main, orient=VERTICAL)
    lrr.pack(side=RIGHT, expand=Y, fill=BOTH, pady=2, padx=2)

    lr = PanedWindow(main, orient=VERTICAL)
    lr.pack(side=RIGHT, expand=Y, fill=BOTH, pady=2, padx=2)

    liste_type_db = Listbox(lp)
    liste_users = Listbox(lt)
    liste_db = Listbox(lr)
    liste_tables = Listbox(lrr)

    liste_type_db.pack()
    liste_users.pack()
    liste_db.pack()
    liste_tables.pack()

    Label(lp, text="Type DB").pack(padx=10, pady=3)
    Label(lt, text="users").pack(padx=10, pady=3)
    Label(lr, text="db").pack(padx=10, pady=3)
    Label(lrr, text="tables").pack(padx=10, pady=3)

    #scrollbar_db = Scrollbar(liste_db)
    #scrollbar_db.pack(side=RIGHT, fill=Y)

    ## Liste TYPE DB ---------------------
    for dir in get_dir_list(permsdir):
        if not dir == '.git'  and os.path.isdir(os.path.join(permsdir, "")+dir):
            liste_type_db.insert('end', dir)
    liste_type_db.bind("<Double-Button-1>", lambda event :liste_type_double_leftclick_handler(liste_type_db, liste_users, liste_db, liste_tables))

    ## Liste USERS -------------------------
    liste_users.bind ("<Double-Button-1>", lambda event :liste_user_double_leftclick_handler(liste_users, liste_db, liste_tables))

    ## Liste DB ------------------------------
    liste_db.bind("<Double-Button-1>", lambda event: liste_double_leftclick_handler(liste_db, liste_tables))

    ## Liste TABLES ------------------------------
    liste_tables.bind ("<Double-Button-1>", lambda event :liste_table_doubleclick_handle(liste_tables))

    main.mainloop()




if __name__ == '__main__':
    display_main_form()
    #d=os.listdir(permsdir)
    #print(d)
