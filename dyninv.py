#!/usr/bin/env python3

import argparse
import json
import requests

debug = 0

# For added security you can remove credentials from here and read them from an encrypted source
cl_id =     'l76b0b05c680fc41123456789123456789'
cl_secret = 'b8f55b73cdc64f123456789123456789'

def get_token():
    ''' Login to CloudIQ to get a token'''

    url = "https://cloudiq.apis.dell.com/auth/oauth/v2/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',
        'client_id': cl_id,
        'client_secret': cl_secret
        }
    response = requests.post(url, data=data, headers=headers)

    response_body = response.json()
    token = response_body["access_token"]
    if debug: print(" ... Access Token     : " + token)

    return token

def get_storage_systems(token):
    '''Get details of all storage systems from CloudIQ REST API'''
    
    url = "https://cloudiq.apis.dell.com/cloudiq/rest/v1/storage_systems/?select=id,ipv4_address,type,free_size,health_score"
    headers = {"Authorization": "Bearer " + token}
    response = requests.get(url, headers = headers)
    payload = response.json()
    if debug:
        print(" ... Storage Systems Payload : ")
        print(json.dumps(payload, indent=4))

    return payload

def empty_inventory():
    return  { "_meta": { "hostvars": {} } }

def create_inventory():
    '''Query the CIQ REST API and create a JSON Ansible-compliant inventory'''
    
    #### Login to CloudIQ to get a token
    token = get_token()

    #### Send API to call to CloudIQ to get the details of all storage systems
    storage_systems = get_storage_systems(token)
    
    #### Build Inventory
    ANSIBLE_INV = empty_inventory() # To satisfy the requirements of using _meta, to prevent ansible from calling your
    #inventory with --host you must at least populate _meta with an empty hostvars object

    for each_array in storage_systems["results"]:
        ANSIBLE_INV[each_array["id"]]= { "hosts": [each_array["ipv4_address"]]}
        ANSIBLE_INV["_meta"]["hostvars"][each_array["ipv4_address"]] = {
            "ip": each_array["ipv4_address"],
            "type": each_array["type"],
            "health_score": each_array["health_score"],
            "freeGB": int(each_array["free_size"]/(1024*1024*1024)) #Convert to GB
            }

    if debug:
        print(" ... Inventory : ")
        print(json.dumps(ANSIBLE_INV, indent=4))

    return ANSIBLE_INV

#### Argument parsing
##The --list option must enlist all the groups and associated hosts and group variables
##The --host option must either return an empty dictionary or a dictionary of variables relevant to that host
parser = argparse.ArgumentParser(description="Ansible dynamic inventory")
parser.add_argument("--list", help="Ansible inventory of all of the groups", action="store_true", dest="list_inventory")
parser.add_argument("--host", help="Ansible inventory of a particular host. DEPRECATED: It only returns empty dict", action="store", dest="ansible_host", type=str)
cli_args = parser.parse_args()
list_inventory = cli_args.list_inventory
ansible_host = cli_args.ansible_host

if debug:
    print("list_inventory: {}".format(list_inventory))
    print("ansible_host: {}".format(ansible_host))

if list_inventory:
    ANSIBLE_INV = create_inventory()
    print(json.dumps(ANSIBLE_INV, indent=4))
    exit() ## Prevents running also the "--host" option if both are specified by accident

if ansible_host: # Not required because we are using the "_meta > hostvars" in main inventory
    print({})


