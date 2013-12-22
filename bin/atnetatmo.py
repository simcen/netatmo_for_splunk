"""
This scripts provides access to Netatmo API inside a Splunk App
The response is handled by a wrapper script (getdata.py) that prepares the JSON data output.
License: Public Domain CC0
Inspired by https://github.com/philippelt/netatmo-api-python...  cleaned all I do not need.
Author: meno@atremar.com, 10.10.2013
"""

import os, sys
import json, time
import ConfigParser
import hashlib
import base64
import uuid

# HTTP libraries depends upon Python 2 or 3
if sys.version_info[0] == 3 :
    import urllib.parse, urllib.request
else:
    from urllib import urlencode
    import urllib2

# Read configuration files

try:
    parser = ConfigParser.SafeConfigParser()
    # TODO: relative paths when executed by Splunk
    conf1 = '/opt/splunk/etc/apps/netatmo/default/netatmo.conf'
    conf2 = '/opt/splunk/etc/apps/netatmo/local/netatmo.conf'

    # file in ../local has precedence
    if os.access(conf1, os.R_OK):
       conf = conf1
    if os.access(conf2, os.R_OK):
       conf = conf2
    parser.read(conf)

#    for stanza in [ 'auth', 'api' ]:
#        print '%s stanza exists: %s' % (stanza, parser.has_section(stanza))
#        for candidate in [ 'username', 'password', 'client-id', 'client-secret' ]:
#            print '%s.%-12s  : %s' % (stanza, candidate, parser.has_option(stanza, candidate))
#        print

    if parser.has_section('auth'):
        confauth = dict(parser.items('auth'))
    if parser.has_section('api'):
        confapi = dict(parser.items('api'))

except ConfigParser.ParsingError, err:
    print 'Could not parse:', err

# User specs
_CLIENT_ID     = confauth.get("client-id")
_CLIENT_SECRET = confauth.get("client-secret")
_USERNAME      = confauth.get("username")
_PASSWORD      = confauth.get("password")

# netatmo URLs
_BASE_URL       = "http://" + confapi.get("base") + "/"
_AUTH_REQ       = _BASE_URL + confapi.get("authorization")
_GETUSER_REQ    = _BASE_URL + confapi.get("getuser")
_DEVICELIST_REQ = _BASE_URL + confapi.get("devicelist")
_GETMEASURE_REQ = _BASE_URL + confapi.get("getmeasure")


class ClientAuth:
    "Request authentication and keep access token available through token method. Renew it automatically if necessary"

    def __init__(self, clientId=_CLIENT_ID,
                       clientSecret=_CLIENT_SECRET,
                       username=_USERNAME,
                       password=_PASSWORD):

        postParams = {
                "grant_type" : "password",
                "client_id" : clientId,
                "client_secret" : clientSecret,
                "username" : username,
                "password" : password
                }
        resp = postRequest(_AUTH_REQ, postParams)

        self._clientId = clientId
        self._clientSecret = clientSecret
        self._accessToken = resp['access_token']
        self.refreshToken = resp['refresh_token']
        self._scope = resp['scope']
        self.expiration = int(resp['expire_in'] + time.time())

    @property
    def accessToken(self):
        "Provide the current or renewed access token"

        if self.expiration < time.time(): # Token should be renewed

            postParams = {
                    "grant_type" : "refresh_token",
                    "refresh_token" : self.refreshToken,
                    "client_id" : self._clientId,
                    "client_secret" : self._clientSecret
                    }
            resp = postRequest(_AUTH_REQ, postParams)

            self._accessToken = resp['access_token']
            self.refreshToken = resp['refresh_token']
            self.expiration = int(resp['expire_in'] + time.time())

        return self._accessToken


class User:

    def __init__(self, authData):

        postParams = {
                "access_token" : authData.accessToken
                }
        resp = postRequest(_GETUSER_REQ, postParams)
        self.rawData = resp['body']
        self.id = self.rawData['_id']
        self.devList = self.rawData['devices']
        self.ownerMail = self.rawData['mail']


class DeviceList:

    def __init__(self, authData):

        self.getAuthToken = authData.accessToken
        postParams = {
                "access_token" : self.getAuthToken
                }
        self.resp = postRequest(_DEVICELIST_REQ, postParams)

    def getAll(self):
        response = self.resp
        return response if len(response) else None


# Utilities

def postRequest(url, params):

    if sys.version_info[0] == 3:
        req = urllib.request.Request(url)
        req.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
        params = urllib.parse.urlencode(params).encode('utf-8')
        resp = urllib.request.urlopen(req, params).readall().decode("utf-8")
    else:
        params = urlencode(params)
        headers = {"Content-Type" : "application/x-www-form-urlencoded;charset=utf-8"}
        req = urllib2.Request(url=url, data=params, headers=headers)
        resp = urllib2.urlopen(req).read()
    return json.loads(resp)



if __name__ == "__main__":

    from sys import exit, stderr

    if not _CLIENT_ID or not _CLIENT_SECRET or not _USERNAME or not _PASSWORD :
           stderr.write("Missing arguments to check lnetatmo.py")
           exit(1)

#    authorization = ClientAuth()                # Test authentication method
#    user = User(authorization)                  # Test GETUSER
#    devList = DeviceList(authorization)         # Test DEVICELIST
#    devList.MinMaxTH()                          # Test GETMEASURE

    # If we reach this line, all is OK
    exit(0)
