"""
This scripts provides access to Netatmo API inside a Splunk App
The response is handled by a wrapper script (getdata.py) that prepares the JSON data output.
License: Public Domain CC0
Inspired by https://github.com/philippelt/netatmo-api-python...  cleaned all I do not need.
"""

import os, sys
import json, time
import ConfigParser
import hashlib
import base64
import uuid
import logging as logger
import splunk.entity as entity



# HTTP libraries depends upon Python 2 or 3
if sys.version_info[0] == 3 :
    import urllib.parse, urllib.request
else:
    from urllib import urlencode
    import urllib2

logger.basicConfig(level=logger.DEBUG, format='%(asctime)s %(levelname)s %(message)s',
                   filename=os.path.join(os.environ['SPLUNK_HOME'],'var','log','splunk','netatmo.log'),
                   filemode='a')


sessionKey = sys.stdin.readline().strip()
if len(sessionKey) == 0:
    sys.stderr.write("Did not receive a session key from splunkd. " +
                        "Please enable passAuth in inputs.conf for this " +
                        "script\n")
    exit(2)

# Utilities
# Get credentials from Splunk REST
def getCredentials(sessionKey):

    myapp = 'netatmo'
    try:
      # list all credentials
      entities = entity.getEntities(['admin', 'passwords'], namespace=myapp,
                                    owner='nobody', sessionKey=sessionKey)
    except Exception, e:
      raise Exception("Could not get %s credentials from splunk. Error: %s"
                      % (myapp, str(e)))

    # return first set of credentials
    logger.debug("entities: %s" % str(entities.items()))
    for i, c in entities.items():
        return c['username'], c['clear_password']

    raise Exception("No credentials have been found")

# Get auth config from Splunk REST
def getAuthConfig(sessionKey):

    myapp = 'netatmo'
    try:
      # list all credentials
      entities = entity.getEntities(['admin', 'netatmo_config'], namespace=myapp,
                                    owner='nobody', sessionKey=sessionKey)
    except Exception, e:
      raise Exception("Could not get %s credentials from splunk. Error: %s"
                      % (myapp, str(e)))

    # return first set of credentials
    logger.debug("auth entities: %s" % str(entities['auth']))
    #for i, c in entities['auth']:
    return entities['auth']['client-id'], entities['auth']['client-secret']


    raise Exception("No auth settings have been found")

# Get api config from Splunk REST
def getApiConfig(sessionKey):

    myapp = 'netatmo'
    try:
      # list all credentials
      entities = entity.getEntities(['admin', 'netatmo_config'], namespace=myapp,
                                    owner='nobody', sessionKey=sessionKey)
    except Exception, e:
      raise Exception("Could not get %s credentials from splunk. Error: %s"
                      % (myapp, str(e)))

    # return first set of credentials
    logger.debug("api entities: %s" % str(entities['api']))
    return entities['api']['base'], entities['api']['authorization'], entities['api']['getuser'], entities['api']['devicelist'], entities['api']['getmeasure']

    raise Exception("No api settings have been found")


# User specs
# Get username and password from splunk's secure credential storage
_USERNAME, _PASSWORD        = getCredentials(sessionKey)

# Get auth and api settings from netatmo.conf
_CLIENT_ID, _CLIENT_SECRET  = getAuthConfig(sessionKey)
_BASE_URL, _AUTH_REQ, _GETUSER_REQ, _DEVICELIST_REQ, _GETMEASURE_REQ = getApiConfig(sessionKey)
_BASE_URL = "https://" + _BASE_URL + "/"
_AUTH_REQ = _BASE_URL + _AUTH_REQ
_GETUSER_REQ = _BASE_URL + _GETUSER_REQ
_DEVICELIST_REQ = _BASE_URL + _DEVICELIST_REQ
_GETMEASURE_REQ = _BASE_URL + _GETMEASURE_REQ


def postRequest(url, params):

    logger.debug("Posting to url: %s with params: %s" % (url,params))
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


class ClientAuth:
    "Request authentication and keep access token available through token method. Renew it automatically if necessary"

    def __init__(self, clientId=_CLIENT_ID,
                       clientSecret=_CLIENT_SECRET,
                       username=_USERNAME,
                       password=_PASSWORD):

        postParams = {
                "grant_type" : "password",
                "scope" : "read_station",
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
        self.user_id = self.rawData['_id']
        self.devList = self.rawData['devices']
        self.friendDevList = self.rawData['friend_devices']
        self.mail = self.rawData['mail']


class DeviceList:

    def __init__(self, authData):

        self.getAuthToken = authData.accessToken
        postParams = {
                "access_token" : self.getAuthToken
                }
        self.resp = postRequest(_DEVICELIST_REQ, postParams)
        self.rawData = self.resp['body']
        #logger.debug("Got a response %s." % json.dumps(self.resp['body'],sort_keys=True, indent=4))
        self.stations = {}
        for d in self.rawData['devices'] : self.stations[d['_id']] = d
        self.modules = {}
        for m in self.rawData['modules'] : self.modules[m['_id']] = m


    def getAll(self):
        response = self.resp
        return response if len(response) else None


    def techdata2splunk(self):
        lastD = {}
        for i,station in self.stations.items():
            #logger.debug("Station is: %s" % json.dumps(station, sort_keys=True, indent=4))
            station_dashboard_data = station['dashboard_data']
            logger.debug("station data: {}".format(json.dumps(station)))

            module_name = 'unknown'
            if 'module_name' in station:
                module_name = station["module_name"]
                
            station_meta_data = {"station_name":station['station_name'],"module_name":module_name,"_id":station['_id'],"type":station['type']}
            lastD[station['_id']] = dict(station_meta_data.items() + station_dashboard_data.items())

            for m in station['modules']:
                module_dashboard_data = self.modules[m]['dashboard_data']
                module_meta_data = { "station_name":station['station_name'],"module_name":self.modules[m]['module_name'],"_id":m,"station_id":station['_id'],"type":self.modules[m]['type']}
                lastD[m] = dict(module_meta_data.items() + module_dashboard_data.items())

	#logger.debug("lastD is %s", json.dumps(lastD, sort_keys=True, indent=4))
        return lastD if len(lastD) else None


    def metadata2splunk(self):
        #TODO
        return None



if __name__ == "__main__":

    from sys import exit, stderr

    if not _CLIENT_ID or not _CLIENT_SECRET or not _USERNAME or not _PASSWORD :
           stderr.write("Missing arguments to check anetatmo.py")
           exit(1)

    exit(0)
