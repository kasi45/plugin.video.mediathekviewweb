# -*- coding: UTF-8 -*-

#2021-07-20
#edit 2023-03-13

import os, sys
import xbmc, xbmcplugin, xbmcaddon, xbmcgui, xbmcvfs

is_python2 = sys.version_info.major == 2

if is_python2:
    from xbmc import translatePath
    from HTMLParser import HTMLParser
    unescape = HTMLParser().unescape
    from urlparse import urlparse, parse_qsl, urljoin, parse_qs, urlsplit
    from urllib import quote_plus, unquote_plus, quote, unquote, urlencode, urlretrieve
    from urllib2 import Request, urlopen
else:
    from xbmcvfs import translatePath
    from html import unescape
    from html.parser import HTMLParser
    from urllib.parse import urlparse, quote_plus, parse_qsl, unquote_plus, urljoin, quote, unquote, urlencode, parse_qs, urlsplit
    from urllib.request import Request, urlopen, urlretrieve



def py2_decode(value):
    if is_python2:
        try:
            return value.decode('utf-8')
        except:
            return value
    return value

def py2_encode(value):
    if is_python2:
        try:
            return value.encode('utf-8')
        except:
            return value
    return value

# xbmcaddon
Addon = xbmcaddon.Addon()
addonInfo = xbmcaddon.Addon().getAddonInfo
addonId = addonInfo('id')
addonName = addonInfo('name')
addonPath = addonInfo('path')

setSetting = xbmcaddon.Addon().setSetting
_getSetting = xbmcaddon.Addon().getSetting

def getSetting(Name, default=''):
    result = _getSetting(Name)
    if result:
        return result
    else:
        return default

# xbmc
skin = xbmc.getSkinDir()
infoLabel = xbmc.getInfoLabel
condVisibility = xbmc.getCondVisibility
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
keyboard = xbmc.Keyboard


# kb = xbmc.Keyboard('default', 'heading', True)
# kb.setDefault('password') # optional
# kb.setHeading('Enter password') # optional
# kb.setHiddenInput(True) # optional
# kb.doModal()
# if (kb.isConfirmed()):
#   text = kb.getText()


execute = xbmc.executebuiltin
player = xbmc.Player()
abortRequested = xbmc.Monitor().abortRequested()
jsonrpc = xbmc.executeJSONRPC
getInfoLabel = xbmc.getInfoLabel


# xbmcvfs
listDir = xbmcvfs.listdir
openFile = xbmcvfs.File
makeFile = xbmcvfs.mkdir
mkDir = xbmcvfs.mkdir
exists = xbmcvfs.exists

# xbmcplugin
resolveUrl = xbmcplugin.setResolvedUrl
addItem = xbmcplugin.addDirectoryItem
directory = xbmcplugin.endOfDirectory
content = xbmcplugin.setContent
property = xbmcplugin.setProperty

def sortLabel(syshandle):
    xbmcplugin.addSortMethod(syshandle, xbmcplugin.SORT_METHOD_LABEL)

# xbmcgui
window = xbmcgui.Window(10000)
currentWindowId = xbmcgui.Window(xbmcgui.getCurrentWindowId())
item = xbmcgui.ListItem
dialog = xbmcgui.Dialog()
progressDialog = xbmcgui.DialogProgress()
progressDialogBG = xbmcgui.DialogProgressBG()

dataPath = py2_decode(translatePath(addonInfo('profile')))

bookmarksFile = os.path.join(dataPath, 'bookmarks.db')

settingsFile = os.path.join(py2_decode(translatePath(addonInfo('path'))), 'resources', 'settings.xml')

def addonIcon():
    return addonInfo('icon')

def artPath():
    return os.path.join(py2_decode(translatePath(addonInfo('path'))), 'resources', 'media')

def addonThumb():
    return os.path.join(artPath(), 'poster.png')

def addonPoster():
    return os.path.join(artPath(), 'poster.png')

def addonBanner():
    return os.path.join(artPath(), 'banner.png')

def addonFanart():
    return os.path.join(artPath(), 'fanart.jpg')

def addonNext():
    return os.path.join(artPath(), 'next.png')

def addonNoPicture():
    return os.path.join(artPath(), 'no-picture.png')

def infoDialog(message, heading=addonInfo('name'), icon='', time=3000, sound=False):
    if icon == '': icon = addonIcon()
    elif icon == 'INFO': icon = xbmcgui.NOTIFICATION_INFO
    elif icon == 'WARNING': icon = xbmcgui.NOTIFICATION_WARNING
    elif icon == 'ERROR': icon = xbmcgui.NOTIFICATION_ERROR
    dialog.notification(heading, message, icon, time, sound=sound)

def yesnoDialog(line1, line2, line3, heading=addonInfo('name'), nolabel='', yeslabel=''):
    if is_python2:
        return dialog.yesno(heading, line1, line2, line3, nolabel, yeslabel)
    else:
        return dialog.yesno(heading, line1+'\n'+line2+'\n'+line3, nolabel, yeslabel)

def selectDialog(list, heading=addonInfo('name')):
    return dialog.select(heading, list)

def showparentdiritems():
    if not 'false' in xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Settings.GetSettingValue", "params":{"setting":"filelists.showparentdiritems"}}'):
        return True
    else:
        return False

# Modified `sleep` command that honors a user exit request
def sleep(time):
    while time > 0 and not abortRequested:
        xbmc.sleep(min(100, time))
        time = time - 100

def getKodiVersion():
    return xbmc.getInfoLabel("System.BuildVersion").split(".")[0]

def busy():
    if int(getKodiVersion()) >= 18:
        return execute('ActivateWindow(busydialognocancel)')
    else:
        return execute('ActivateWindow(busydialog)')

def idle():
    if int(getKodiVersion()) >= 18:
        return execute('Dialog.Close(busydialognocancel)')
    else:
        return execute('Dialog.Close(busydialog)')

def visible():
    if int(getKodiVersion()) >= 18 and xbmc.getCondVisibility('Window.IsActive(busydialognocancel)') == 1:
        return True
    return xbmc.getCondVisibility('Window.IsActive(busydialog)') == 1

def reload_profile():
    profil = xbmc.getInfoLabel('System.ProfileName')
    sleep(500)
    #if profil:
    xbmc.executebuiltin('LoadProfile(' + profil + ',prompt)')

def openSettings(query=None, id=addonInfo('id')):
    try:
        idle()
        execute('Addon.OpenSettings(%s)' % id)
        if query is None:
            raise Exception()
        c, f = query.split('.')
        if int(getKodiVersion()) >= 18:
            execute('SetFocus(%i)' % (int(c) - 100))
            execute('SetFocus(%i)' % (int(f) - 80))
        else:
            execute('SetFocus(%i)' % (int(c) + 100))
            execute('SetFocus(%i)' % (int(f) + 200))
    except:
        return

# def resetSettings():
#     yes = yesnoDialog("Zurücksetzen der Settings (außer Konten)", 'und einem abschließenden Reload vom Profil', 'Sind Sie sicher?')
#     if not yes: return
#     try:
#         login = getSetting('serienstream.user')
#         password = getSetting('serienstream.pass')
#         os_user = getSetting('subtitles.os_user')
#         os_pass = getSetting('subtitles.os_pass')
#         tmdb = getSetting('api.tmdb')
#         trakt = getSetting('api.trakt')
#         fanart = getSetting('api.fanart.tv')
#         debug = getSetting('status.debug')
#         SettingFile = py2_decode(os.path.join(xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')), "settings.xml"))
#         if xbmcvfs.exists(SettingFile): xbmcvfs.delete(SettingFile)
#         # PROFIL_RELOAD = os.path.join(xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8'), "profil_reload")
#         # open(PROFIL_RELOAD, "w+").write('Profil reload')
#         setSetting(id='serienstream.user', value=login)
#         setSetting(id='serienstream.pass', value=password)
#         setSetting(id='subtitles.os_user', value=os_user)
#         setSetting(id='subtitles.os_pass', value=os_pass)
#         setSetting(id='api.tmdb', value=tmdb)
#         setSetting(id='api.trakt', value=trakt)
#         setSetting(id='api.fanart.tv', value=fanart)
#         setSetting(id='status.debug', value=debug)
#         return True
#     except:
#         return

def getSettingDefault(id):
    import re
    try:
        settings = open(settingsFile, 'r')
        value = ' '.join(settings.readlines())
        value.strip('\n')
        settings.close()
        value = re.findall(r'id=\"%s\".*?default=\"(.*?)\"' % (id), value)[0]
        return value
    except:
        return None

def inAdvancedsettings(word=''):
    advancedsettings = py2_decode(os.path.join(translatePath('special://userdata/'), "advancedsettings.xml"))
    if exists(advancedsettings):
        with open(advancedsettings, 'r') as file:
            content = file.read()
            if word in content: return True
    return False
