#!/usr/bin/python
"""
This scripts retrieves data from Netatmo API via atnetatmo.py and outputs JSON data format.
It is excuted by a splunk scripted input every 7min

License: Public Domain CC0
Inspired by https://github.com/philippelt/netatmo-api-python...  cleaned all I do not need.

Author: meno@atremar.com, 10.10.2013

"""

import atnetatmo
import json

auth = atnetatmo.ClientAuth()
devList = atnetatmo.DeviceList(auth)
user = atnetatmo.User(auth)


# get all data from devicelist endpoint
#lastdata = devList.getAll()

# JSON output
#print json.dumps(lastdata)

# get all data from devicelist endpoint
#lastdata = devList.techdata2splunk()

# JSON output
#print json.dumps(lastdata)


for key,value in devList.techdata2splunk().iteritems():
    # Trying to match modules & stations to owners
    if value['_id']in user.devList :
        value['user_id']=user.user_id
        value['mail']=user.mail
    elif value['_id']in user.friendDevList :
        value['user_id']="Friend"
        value['mail']="incomplete@api"
    else:
        value['user_id']="Anon"
        value['mail']="incomplete@api"

    print json.dumps(value)

