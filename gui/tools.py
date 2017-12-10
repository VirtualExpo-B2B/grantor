#coding: utf8

import os
from tkinter import *


# ---------------------- TOOLS --------------------------------------------
def get_dir_list(dir):
    r = []
    dir=os.path.join(dir,"")
    files = os.listdir(dir)
    for f in files:
        if os.path.isdir(dir + f):
            r.append(f)
    return r

def get_file_list(dir):
    r = []
    dir=os.path.join(dir,"")
    if not os.path.exists(dir):
        return r

    files = os.listdir(dir)
    for f in files:
        if os.path.isfile(dir + f):
            r.append(f)
    return r

def listbox_clear(liste):
    if liste.size()>0:
        liste.delete(0, liste.size() - 1)