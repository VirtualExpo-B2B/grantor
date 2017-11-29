#!/usr/bin/env python3
#coding: utf8


from helpers.mysql_user_creation import create_new_mysql_user
from helpers.mysql_user_grant_application import apply_grants_for_all_users
from helpers.mysql_user_grant_application import apply_grants_for_single_user
from helpers.check_grant_integrity import check_local_repo_integrity_to_prod
from helpers.gen_perms_from_mysql import retrieve_all_mysql_grants_from_prod


def display_menu():
    print("Mysql Grants Tool\nWhat do you wanna do ?\n")

    menu=dict(
        A="create a new mysql user",
        B="apply mysql grants for a signle user",
        C="apply mysql grants for ALL users",
        D="retrieve ALL mysql grants from PROD",
        E="check if my local repo is same as prod mysql grants"
    )

    for s in menu:
        print("\t%s - %s" % (s,menu[s]))

    try:
        choice=str.upper(raw_input("?"))
        print(choice)

        if choice=='A':
            create_new_mysql_user()

        elif choice=='B':
            apply_grants_for_single_user()

        elif choice == 'C':
            apply_grants_for_all_users()

        elif choice == 'D':
            retrieve_all_mysql_grants_from_prod()

        elif choice == 'E':
            check_local_repo_integrity_to_prod()
        else:
            print("Hein, je ne comprends pas ce que tu veux ???")
            display_menu()
    except:
        print("something went wrong :/\n\n")
        display_menu()





if __name__ == '__main__':
    display_menu()
