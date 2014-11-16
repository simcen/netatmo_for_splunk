"""
This scripts provides access to Netatmo API inside a Splunk App
The response is handled by a wrapper script (getdata.py) that prepares the JSON data output.
License: Public Domain CC0
Inspired by https://github.com/philippelt/netatmo-api-python...  cleaned all I do not need.
Author: meno@atremar.com, 10.10.2013

Infos that go into the change history:
- newest entry @ the beginning
- who changed
- what was changed

History
2013.10.10  meno@atremar.com - Initial Version
2014.01.01  sinloft@gmail.com - Enabled reading the co2 values of additional indoor modules

"""

import os, sys
import json, time
import ConfigParser
import hashlib
import base64
import uuid
import logging as logger



# HTTP libraries depends upon Python 2 or 3
if sys.version_info[0] == 3 :
    import urllib.parse, urllib.request
else:
    from urllib import urlencode
    import urllib2

logger.basicConfig(level=logger.DEBUG, format='%(asctime)s %(levelname)s %(message)s',
                   filename=os.path.join(os.environ['SPLUNK_HOME'],'var','log','splunk','netatmo.log'),
                   filemode='a')
logger.setLevel("ERROR")

# Read configuration files
try:
    parser = ConfigParser.SafeConfigParser()
    conf_base = os.path.abspath(os.path.dirname(sys.argv[0])+"/..")
    logger.debug("The base path is: %s" % conf_base)
    conf1 = conf_base+'/default/netatmo.conf'
    conf2 = conf_base+'/local/netatmo.conf'

    # file in ../local has precedence
    conf=None
    if os.access(conf1, os.R_OK):
       conf = conf1
    if os.access(conf2, os.R_OK):
       conf = conf2
    logger.debug("The selected conf is: %s" % conf)
    parser.read(conf)
    if logger.getLevelName == "DEBUG" :

        for stanza in [ 'auth', 'api' ]:
            logger.debug('%s stanza exists: %s' % (stanza, parser.has_section(stanza)))
            for candidate in [ 'username', 'password', 'client-id', 'client-secret' ]:
                logger.debug('%s.%-12s  : %s' % (stanza, candidate, parser.has_option(stanza, candidate)))

    if parser.has_section('auth'):
        confauth = dict(parser.items('auth'))
    if parser.has_section('api'):
        confapi = dict(parser.items('api'))

except ConfigParser.ParsingError, err:
    print 'Could not parse:', err
    logger.error(err)

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
        logger.debug("Got a response %s." % json.dumps(self.resp['body'],sort_keys=True, indent=4))
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
            station_meta_data = {"station_name":station['station_name'],"module_name":station["module_name"],"_id":station['_id'],"type":station['type']}
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


# Utilities

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
