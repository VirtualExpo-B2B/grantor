#conding: utf8

'''
execute arbitrary SQL code for specific cases
'''
def apply_exceptions(conn, exceptions_file_path):
    stuff = open(exceptions_file_path, 'r').read()

    cur = conn.cursor()
    res = cur.execute(stuff, multi=True)
