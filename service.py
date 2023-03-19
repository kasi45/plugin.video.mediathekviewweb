# -*- coding: utf-8 -*-

import json
import xbmc
from xbmcaddon import Addon
from resources.lib.control import inAdvancedsettings

addonId = Addon().getAddonInfo('id')

# //    services.webserver
# //    services.webserverport
# //    services.webserverusername
# //    services.webserverpassword
# //    services.webskin
#   Require authentication     #???


def setWebSrv(ADDONID):
    while True:
        xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"services.webserverpassword", "value":"%s"}, "id":1}' % 'kasi')
        struktur = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.GetSettingValue","params":{"setting":"services.webserverpassword"},"id":1}'))
        try:
            if struktur["result"]["value"] == 'kasi':
                break
            else:
                xbmc.sleep(1000)
        except:
            pass

    while True:
        #xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"services.webserverpassword", "value":"%s"}, "id":1}' % 'kasi')
        xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"services.webskin", "value":"%s"}, "id":1}' % ADDONID)
        struktur = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.GetSettingValue","params":{"setting":"services.webskin"},"id":1}'))
        try:
            if struktur["result"]["value"] == ADDONID:
                break
            else:
                xbmc.sleep(1000)
        except:
            pass
    # xbmc.startServer(iTyp=xbmc.SERVER_WEBSERVER, bStart=True)

if inAdvancedsettings('favourites.xml'):
    currentWebserverpassword = json.loads(xbmc.executeJSONRPC(
        '{"jsonrpc":"2.0","method":"Settings.GetSettingValue","params":{"setting":"services.webserverpassword"},"id":1}'))[
        "result"]["value"]
    if currentWebserverpassword != 'kasi': setWebSrv(addonId)

    currentWebSkin = json.loads(xbmc.executeJSONRPC(
        '{"jsonrpc":"2.0","method":"Settings.GetSettingValue","params":{"setting":"services.webskin"},"id":1}'))[
        "result"]["value"]
    if currentWebSkin != addonId: setWebSrv(addonId)

    # import pydevd
    # pydevd.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)

    isWebSrv = False
    # if inAdvancedsettings('webserver'):
    #     isWebSrv = True  # start webserver in advancedsettings.xml
    # else:
    try:
        isWebSrv = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.GetSettingValue","params":{"setting":"services.webserver"},"id":1}'))["result"]["value"]
        if not isWebSrv: xbmc.startServer(iTyp=xbmc.SERVER_WEBSERVER, bStart=True)
    except:
        pass


