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

# get all data from devicelist endpoint
lastdata = devList.getAll()

# JSON output
print json.dumps(lastdata)

