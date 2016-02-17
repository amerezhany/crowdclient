# Crowd REST users/groups manipulation script

## Requirements

http://www.python-requests.org/en/latest/

## Install

You can install requests with: `pip install requests`

## Configuration
Need to add you IP (from where you're running this script) to the Crowd "Remote Addresses" list under your particular application

## Usage
`./crowdclient.py add -U f.username -G jira-developers`
While running script with ask for Crowd user/pass and host for Crowd Application
