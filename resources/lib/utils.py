# -*- coding: utf-8 -*-
import sys, os
import xbmc, xbmcaddon

is_python2 = sys.version_info.major == 2


def py2_decode(value):
    if is_python2:
        return value.decode('utf-8')
    return value

def py2_encode(value):
    if is_python2:
        return value.encode('utf-8')
    return value


def showparentdiritems():
    if not 'false' in xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Settings.GetSettingValue", "params":{"setting":"filelists.showparentdiritems"}}'):
        return True
    else:
        return False

addon_dir = py2_decode(xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')))


def artPath(channel):
    art = channel.lower() + '.png'
    return os.path.join(addon_dir, 'resources', 'media', art)

#removes duplicates
def chk_duplicates(url, title, topic, duplicates):
    try:
        if 'Audiodeskription' in title: return True
        if 'Trailer' in topic: return True
        for j in duplicates:
            if url.split("//")[1] == j['url'].split("//")[1]:
                return True
            elif title == j['title']:
                return True
            else:
                continue
    except:
        pass
