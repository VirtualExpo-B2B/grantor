#!/usr/bin/env python3
#coding: utf8
from helpers.mysql_user_creation import create_new_mysql_user


def display_menu():
    print("Mysql Grants Tool\nWhat do you wanna do ?\n")

    menu=dict(A="create a new mysql user",
           B="apply mysql grants for a signle user",
           C="apply mysql grants for ALL users",
           D="retrieve ALL mysql grants from PROD",
           E="check if my local repo is same as prod mysql grants")

    for s in menu:
        print("\t%s - %s" % (s,menu[s]))

    try:
        choice=str(input("")).upper()

        if choice=='A':
            my_class=mysql_user_creation()
            my_class.create_new_mysql_user()

        elif choice=='B':
            apply_grants_for_single_user()

        elif choice == 'C':
            apply_grants_for_all_users()

        elif choice == 'D':
            retrieve_all_mysql_grants_from_prod()

        elif choice == 'E':
            check_if_my_repo_is_same_as_prod()

    except:
        print("ton choix n'est pas correct\n\n")
        display_menu()





if __name__ == '__main__':
    display_menu()