#conding: utf8




def delete_user(envid, conn, user):
    sql="drop user %s" % (user)
