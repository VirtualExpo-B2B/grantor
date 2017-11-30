#coding: utf8
import pymysql



def quick_write(path, contents):
  of = open(path, 'w')
  of.write(contents)
  of.close()


def quick_read(path):
    file = open(path, 'r')
    content=file.read()
    file.close()
    return content


def get_connection(db_hosts):
    return pymysql.connect(host=db_hosts, user="dev", passwd="PleaseBeCareful")


if __name__ == '__main__':
    print(quick_read('/home/hiacine.ghaoui/workspace/perms/site/mysql_version'))




