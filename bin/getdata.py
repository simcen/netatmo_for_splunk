#!/usr/bin/python

import lnetatmo

auth = lnetatmo.ClientAuth()
devList = lnetatmo.DeviceList(auth)

print devList.lastData()

