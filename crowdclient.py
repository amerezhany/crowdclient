#!/usr/bin/env python
# coding: utf-8

import sys
import getpass
import argparse
import requests
import xml.etree.ElementTree as ET
import ConfigParser

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
    'list-user-of-group': '[group/groups]',
    'list-user-nested-of-group': '[group/groups]',
    'list-group-of-user': '[user/users]',
    'list-group-nested-of-user': '[user/users]',
    'list-group-of-group': '[group/groups]',
    'list-group-nested-of-group': '[group/groups]',
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

config = ConfigParser.ConfigParser()
config_file = '/tmp/crowdclient.cfg'

try:
    config.read(config_file)
    auth_user      = config.get('credentials', 'username')
    auth_pass      = config.get('credentials', 'password')
    crowd_hostname = config.get('credentials', 'hostname')
except:
    auth_user      = raw_input('auth_user: ')
    auth_pass      = getpass.getpass()
    crowd_hostname = raw_input('crowd_hostname: ')

    if config.has_section('credentials'):
        pass
    else:
        config.add_section('credentials')
        config.set('credentials', 'username', auth_user)
        config.set('credentials', 'password', auth_pass)
        config.set('credentials', 'hostname', crowd_hostname)

        with open(config_file, 'wb') as configfile:
            config.write(configfile)

if len(auth_pass) == 0:
    print("\n" + sys.argv[0] + ": you haven't supplied password. Please try again\n")
    sys.exit()

if len(crowd_hostname) == 0:
    print(sys.argv[0] + ": please check your Crowd URL.\n")
    sys.exit()

headers = {'content-type': 'application/xml'}
crowd_url = crowd_hostname + '/crowd/rest/usermanagement/1'


def user_group_manip(act):
    # TODO:
    # * add code to check if particular user of group exists
    # * add debug
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

def list_user(nested):
    group_s_l = args.group_s.split(',')
    for group in group_s_l:
        try:
            if nested:
                url_get = crowd_url + '/group/user/nested?groupname=' + group
            else:
                url_get = crowd_url + '/group/user/direct?groupname=' + group

            s = requests.get(url_get, auth=(auth_user, auth_pass))

            if s.status_code != 200:
                print("\n" + sys.argv[0] + ": no such group: `" + group + "'\n")

            t = ET.fromstring(s.text)
            print "\nUsers in group: `" + group + "':"
            for user in t.findall('user'):
                print user.get('name')
        except Exception:
            print("\n" + sys.argv[0] + ": cannot list the users of the group: `" + group + "'\n")

def list_group(nested):
    username_s_l = args.username_s.split(',')
    for username in username_s_l:
        try:
            if nested:
                url_get = crowd_url + '/user/group/nested?username=' + username
            else:
                url_get = crowd_url + '/user/group/direct?username=' + username

            s = requests.get(url_get, auth=(auth_user, auth_pass))

            if s.status_code != 200:
                print("\n" + sys.argv[0] + ": no such user found: `" + username + "'\n")

            t = ET.fromstring(s.text)
            print "\nMembership of a user: `" + username + "':"
            for group in t.findall('group'):
                print group.get('name')
        except Exception:
            print("\n" + sys.argv[0] + ": cannot list the groups of the user: `" + username + "'\n")

def list_group_group(nested):
    group_s_l = args.group_s.split(',')
    for group in group_s_l:
        try:
            if nested:
                url_get = crowd_url + '/group/child-group/direct?groupname=' + group
            else:
                url_get = crowd_url + '/group/child-group/nested?groupname=' + group

            s = requests.get(url_get, auth=(auth_user, auth_pass))

            if s.status_code != 200:
                print("\n" + sys.argv[0] + ": no such group: `" + group + "'\n")

            t = ET.fromstring(s.text)
            print "\nGroups in group: `" + group + "':"
            for user in t.findall('group'):
                print user.get('name')
        except Exception:
            print("\n" + sys.argv[0] + ": cannot list the groups of the group: `" + group + "'\n")


def main():
    if sys.argv[1] == 'add':
        user_group_manip("add")
    elif sys.argv[1] == "remove":
        user_group_manip("remove")

    elif sys.argv[1] == "list-user-of-group":
        list_user(False)
    elif sys.argv[1] == "list-user-nested-of-group":
        list_user(True)

    elif sys.argv[1] == "list-group-of-user":
        list_group(False)
    elif sys.argv[1] == "list-group-nested-of-user":
        list_group(True)

    elif sys.argv[1] == "list-group-of-group":
        list_group_group(False)
    elif sys.argv[1] == "list-group-nested-of-group":
        list_group_group(True)

if __name__ == '__main__':
    main()
