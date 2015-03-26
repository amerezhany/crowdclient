#!/usr/bin/env python
# coding: utf-8

import sys
import getpass
import argparse
import requests
import xml.etree.ElementTree as ET

# parse options/arguments
parser = argparse.ArgumentParser(description="jira manipulation cli")

# action options: this is first argument to command line
parser.add_argument(" ", nargs="?")

parser.add_argument("-U", "--usernames", dest="username_s")
parser.add_argument("-G", "--groups", dest="group_s")

args = parser.parse_args()

# helper _actions_ dictionary
actions_dic = {
    'add': '[usernames] [groups]',
    'remove': '[usernames] [groups]',
    'list-users': '[group/groups]',
    'list-users-nested': '[group/groups]',
    'list-groups': '[user/users]',
    'list-groups-nested': '[user/users]',
}

def actions_usage():
    print("Please use the following actions:\n")
    for i in actions_dic:
        print(i + " " + actions_dic[i])

# if no additional arguments supplied
if len(sys.argv) < 3:
    parser.print_help()
    print("\n")
    actions_usage()
    sys.exit()

if sys.argv[1] not in actions_dic:
    actions_usage()
    sys.exit()

#auth_user = raw_input('auth_user: ')
auth_user = 'apex'

try:
    #auth_pass = getpass.getpass()
    auth_pass = 'apex123'
except KeyboardInterrupt:
    print("\n" + "You have pressed ctrl-c, please try again.\n")
    sys.exit()

if len(auth_pass) == 0:
    print("\n" + sys.argv[0] + ": you haven't supplied password. Please try again\n")
    sys.exit()

headers = {'content-type': 'application/xml'}
crowd_url = 'http://jira.ontrq.com:8095/crowd/rest/usermanagement/1'

def users_groups_manip(act):
    # TODO: add code to check if particular user of group exists
    username_s_l = args.username_s.split(',')
    group_s_l = args.group_s.split(',')
    for username in username_s_l:
        for group in group_s_l:
            try:
                if act == 'add':
                    values = '<?xml version="1.0" encoding="UTF-8"?> <group name="' + group + '"/>'
                    url_post = crowd_url + '/user/group/direct?username=' + username 
                    s = requests.post(url_post, data=values, headers=headers, auth=(auth_user, auth_pass))

                    if s.status_code == 201:
                        print("User: `" + username + "' added to `" + group + "'")
                    else:
                        print("User: `" + username + "' was not added to `" + group + "'")
                else:
                    url_delete = crowd_url + '/user/group/direct?username=' + username + '&groupname=' + group
                    s = requests.delete(url_delete, auth=(auth_user, auth_pass))

                    if s.status_code == 204:
                        print("User: `" + username + "' removed from `" + group + "'")
                    else:
                        print("User: `" + username + "' was not removed from `" + group + "'")

            except Exception:
                print("\n" + sys.argv[0] + ": cannot update: `" + group + "' with user: `" + username + "'\n")

def list_users(nested):
    group_s_l = args.group_s.split(',')
    for group in group_s_l:
        try:
            if nested:
                url_get =  'http://jira.ontrq.com:8095/crowd/rest/usermanagement/1' + '/group/user/nested?groupname=' + group
            else:
                url_get =  'http://jira.ontrq.com:8095/crowd/rest/usermanagement/1' + '/group/user/direct?groupname=' + group

            s = requests.get(url_get, auth=(auth_user, auth_pass))

            if s.status_code != 200:
                print("\n" + sys.argv[0] + ": no such group: `" + group + "'\n")

            t = ET.fromstring(s.text)
            print "\nUsers in group: `" + group + "':"
            for user in t.findall('user'):
                print user.get('name')
        except Exception:
            print("\n" + sys.argv[0] + ": cannot list the users of the group: `" + group + "'\n")

def list_groups(nested):
    username_s_l = args.username_s.split(',')
    for username in username_s_l:
        try:
            if nested:
                url_get =  'http://jira.ontrq.com:8095/crowd/rest/usermanagement/1' + '/user/group/nested?username=' + username
            else:
                url_get =  'http://jira.ontrq.com:8095/crowd/rest/usermanagement/1' + '/user/group/direct?username=' + username

            s = requests.get(url_get, auth=(auth_user, auth_pass))

            if s.status_code != 200:
                print("\n" + sys.argv[0] + ": no such user found: `" + username + "'\n")

            t = ET.fromstring(s.text)
            print "\nMembership of a user: `" + username + "':"
            for group in t.findall('group'):
                print group.get('name')
        except Exception:
            print("\n" + sys.argv[0] + ": cannot list the groups of the user: `" + username + "'\n")

def main():
    if sys.argv[1] == 'add':
        users_groups_manip("add")
    elif sys.argv[1] == "remove":
        users_groups_manip("remove")

    elif sys.argv[1] == "list-users":
        list_users(False)
    elif sys.argv[1] == "list-users-nested":
        list_users(True)

    elif sys.argv[1] == "list-groups":
        list_groups(False)
    elif sys.argv[1] == "list-groups-nested":
        list_groups(True)

if __name__ == '__main__':
    main()
