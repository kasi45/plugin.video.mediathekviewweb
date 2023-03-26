# -*- coding: utf-8 -*-

import sys
from os.path import join
from resources.lib.mediathek import cMediathek
from resources.lib import control
from resources.lib import searchdb
import xbmc

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1]) if len(sys.argv) > 1 else ''

artPath = control.artPath()
addonFanart = control.addonFanart()

def window(title='', content='', filename=''):
    import xbmcgui, time, os
    if content == '' and filename == '': return
    if content == '' and filename != '':
        file = join(control.py2_decode(control.translatePath(control.addonInfo('path'))), 'resources', filename)
        if sys.version_info[0] == 2:
            with open(file, 'r') as f:
                content = f.read()
        else:
            with open(file, 'rb') as f:
                content = f.read().decode('utf8')

        window_id = 10147
        control_label = 1
        control_textbox = 5
        timeout = 1
        xbmc.executebuiltin("ActivateWindow({})".format(window_id))
        w = xbmcgui.Window(window_id)
        # Wait for window to open
        start_time = time.time()
        while (not xbmc.getCondVisibility("Window.IsVisible({})".format(window_id)) and
               time.time() - start_time < timeout):
            xbmc.sleep(100)
        # noinspection PyUnresolvedReferences
        w.getControl(control_label).setLabel(title)
        # noinspection PyUnresolvedReferences
        w.getControl(control_textbox).setText(content)
## =======================================================================================

params = dict(control.parse_qsl(control.urlsplit(sys.argv[2]).query))

action = params.get('action')

if action == None or action == 'root':
    #cMediathek().root()
    cMediathek().root_all()

elif action == 'mediathek':
    cMediathek().get(params)

elif action == 'search_menu':
    cMediathek().searchMenu()
elif action == 'search_last':
    cMediathek().searchLast()
elif action == 'search_channel':
    cMediathek().searchChannel()
elif action == 'search_new':
    channel = params.get("channel")
    query = searchdb.searchNew(channel=channel)

elif action == 'browse_menu':
    cMediathek().browseMenu()
elif action == 'browse_channel':
    cMediathek().searchChannel(bSearch=False)
elif action == 'browse':
    cMediathek().get()

elif action == 'removeQuery':   # von contextMenu
    searchdb.remove_query(params)
    queries = searchdb.load_queries()
    if queries == []:
        xbmc.executebuiltin('Action(ParentDir)')
    else:
        xbmc.executebuiltin('Container.Refresh')

elif action == 'searchClear':
    searchdb.remove_all_query()
    xbmc.executebuiltin('Action(ParentDir)')

elif action == 'list_videos':
    page = int(params.get("page")) if params.get("page") else 1
    query = params.get("query") if params.get("query") != 'None' else None
    channel = params.get("channel") if params.get("channel") != 'None' else None
    searchdb.save_query(query, channel)
    cMediathek().get(params)

elif action == 'play':
    cMediathek().play(params)

elif action == 'addonSettings':
    control.openSettings()

elif action == "download":
    from resources.lib import downloader
    downloader.download(name=params.get("name"), image=params.get("image"), url=params.get("url"), subfolder=params.get("subfolder"))

elif action == "downloadInfo":
        window('Hilfe zum Syntax für den Ordnerpfad', '', 'downloadinfo.txt')

# try:
#     import pydevd
#     if pydevd.connected: pydevd.kill_all_pydev_threads()
# except: pass

