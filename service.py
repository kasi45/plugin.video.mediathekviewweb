# -*- coding: utf-8 -*-

import json
import xbmc
from xbmcaddon import Addon
from resources.lib.control import inAdvancedsettings

addonId = Addon().getAddonInfo('id')

def setWebSrv(ADDONID):
    while True:
        #control.jsonrpc('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"services.webserver", "value":true}, "id":1}')
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
    currentWebSkin = json.loads(xbmc.executeJSONRPC(
        '{"jsonrpc":"2.0","method":"Settings.GetSettingValue","params":{"setting":"services.webskin"},"id":1}'))[
        "result"]["value"]
    isWebSrv = False
    if inAdvancedsettings('webserver'):
        isWebSrv = True  # start webserver in advancedsettings.xml
    else:
        isWebSrv = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.GetSettingValue","params":{"setting":"services.webserver"},"id":1}'))["result"]["value"]

    if not isWebSrv: xbmc.startServer(iTyp=xbmc.SERVER_WEBSERVER, bStart=True)
    if currentWebSkin != addonId: setWebSrv(addonId)
