# -*- coding: utf-8 -*-

# http://10.128.5.167:8080/resources/media/ard.png
# http://127.0.0.1:8080/resources/media/ard.png
# http://localhost:8080/resources/media/ard.png

import datetime
from os.path import join
import sys, json
from resources.lib.mediathekviewweb import MediathekViewWeb
from resources.lib import control
from resources.lib.searchdb import *

# add pytz module to path
module_dir = join(control.addonPath, "resources", "lib", "pytz")
sys.path.insert(0, module_dir)
import pytz

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1]) if len(sys.argv) > 1 else ''

artPath = control.artPath()
addonFanart = control.addonFanart()


PER_PAGE = int(control.getSetting("per_page"))
FUTURE = True if control.getSetting("enable_future")=='true' else False
QUALITY = int(control.getSetting("quality"))
SUBTITLE = True if control.getSetting("enable_subtitle")=='true' else False

if SUBTITLE == 'true':
    from resources.lib.subtitles import download_subtitle

def root():
    queries = load_queries()
    if queries != []:
        addDirectoryItem("Letzte Suchanfrage", 'lastQueries', 'search.png', 'DefaultVideo.png')
    addDirectoryItem("Überall suchen", 'channel&bSearch=True&bChannels=False', 'search.png', 'DefaultVideo.png')
    addDirectoryItem("Auf Sender suchen", 'channel&bSearch=True&bChannels=True', 'search.png', 'DefaultVideo.png')
    addDirectoryItem("Überall stöbern", 'channel&bSearch=False&bChannels=False', 'search.png', 'DefaultVideo.png')
    addDirectoryItem("Auf Sender stöbern", 'channel&bSearch=False&bChannels=True', 'search.png', 'DefaultVideo.png')
    addDirectoryItem("Einstellungen", 'addonSettings', 'tools.png', 'DefaultAddonProgram.png',  isFolder=False)
    setEndOfDirectory(cache=False)

def showChannels(bSearch, bChannels):
    if bChannels:
        data = {'error': None,
                'channels': ['ARD', 'ZDF', 'MDR', 'ARTE.DE', '3Sat', 'PHOENIX', 'NDR', 'WDR', 'SWR', 'SRF', 'Funk.net', 'BR', 'SR', 'Radio Bremen TV', 'rbtv', 'DW', 'HR', 'RBB',
                             'ZDF-tivi', 'KiKA']}   #  'ORF',

        channels = data["channels"]
        for channel in channels:
            if bSearch:
                addDirectoryItem(channel, 'searchQuery&channel=%s' % (channel), channel, join(artPath, 'icon.png'))  # Auf Sender suchen
            else:
                addDirectoryItem(channel, 'list_videos&channel=%s' % (channel) , channel, join(artPath, 'icon.png')) # Auf Sender stöbern
        setEndOfDirectory()
    else:
        if bSearch: # Überall suchen
            query = showKeyBoard()
            if not query: exit()
            save_query(query)
            list_videos(query=query)
        else:        # Überall stöbern
            list_videos()

def last_queries():
    queries = load_queries()
    if queries == []: return
    lst = []
    delete_option = False
    for index, item in enumerate(queries):
        query = item.get('query')
        if type(query) == str:
            query = control.py2_encode(query)
        channel = item.get('channel')
        if channel:
            if query:
                label = "{0}: {1}".format(channel, query)
            else:
                label = "{0}".format(channel)
            thumb = channel + '.png'
        else:
            channel = None
            label = query
            thumb = 'icon.png'
        if label not in lst:
            delete_option = True
            addDirectoryItem(label, 'list_videos&query=%s&channel=%s' % (query, channel), thumb,
                                                   'DefaultAddonsSearch.png',
                                                   context=("Suchanfrage löschen", 'removeQuery&index=%s' % index))
            lst += [(label)]

    if delete_option:
        addDirectoryItem("[B]Suchverlauf löschen[/B]", 'searchClear', 'tools.png', 'DefaultAddonProgram.png', isFolder=False)
    setEndOfDirectory(cache=False)  # addons  videos  files

def chk_duplicates(url, title, topic, duplicates):
    try:
        if 'Audiodeskription' in title: return True
        elif 'Hörfassung' in title: return True
        elif 'Trailer' in topic: return True
        for j in duplicates:
            if url.split("//")[1] == j['url'].split("//")[1]:
                return True
            elif title == j['title']:
                return True
            else:
                continue
    except:
        pass

def showKeyBoard(sDefaultText=""):
    # Create the keyboard object and display it modal
    oKeyboard = control.keyboard(sDefaultText, "Suche")
    oKeyboard.doModal()
    sTerm = oKeyboard.getText() if oKeyboard.isConfirmed() else None
    if sTerm is None or sTerm == '': return
    sSearchText = sTerm.strip()
    if len(sSearchText) > 0: return sSearchText
    return

def addDirectoryItem(name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True):
    url = '%s?action=%s' % (sysaddon, query) if isAction == True else query
    thumb = getMedia(thumb, icon)
    #laut kodi doku - ListItem([label, label2, path, offscreen])
    listitem = control.item(name, offscreen=True) # Removed iconImage and thumbnailImage
    listitem.setArt({'thumb': thumb, 'poster': thumb, 'icon': icon, 'banner': getMedia('banner')})
    if not context == None:
        cm = []
        cm.append((context[0], 'RunPlugin(%s?action=%s)' % (sysaddon, context[1])))
        listitem.addContextMenuItems(cm)
    # isMatch, sPlot = cParser.parseSingleResult(query, "plot'.*?'([^']+)")
    sPlot = '[COLOR blue]{0}[/COLOR]'.format(name)
    if isFolder:
        listitem.setInfo('video', {'overlay': 4, 'plot': control.unquote_plus(sPlot)})
        listitem.setIsFolder(True)
    listitem.setProperty('fanart_image', addonFanart)
    control.addItem(syshandle, url, listitem, isFolder)

def setEndOfDirectory(content='', cache=True ): # addons  videos  files
    # https://romanvm.github.io/Kodistubs/_autosummary/xbmcplugin.html#xbmcplugin.setContent
    control.content(syshandle, content)
    control.directory(syshandle, succeeded=True, cacheToDisc=cache)

def getMedia(mediaFile=None, icon=None):
    mediaFile = mediaFile.lower()
    icon = icon if icon and icon.rsplit('.')[-1] == 'png' else 'icon.png'
    mediaFile = mediaFile if mediaFile.rsplit('.')[-1] == 'png' else mediaFile + '.png'
    if control.exists(join(artPath, mediaFile)):
        if control.inAdvancedsettings('favourites.xml'):
            mediaFile = 'http://kodi:kasi@127.0.0.1:8080/resources/media/%s' % mediaFile
        else:
            mediaFile = join(artPath, mediaFile)
    elif mediaFile.startswith('http'):
        return mediaFile
    elif control.exists(join(artPath, icon)):
        mediaFile = join(artPath, icon)
    else:
        mediaFile = icon
    return mediaFile

def list_videos(query=None, channel=None, page=1):
    m = MediathekViewWeb(PER_PAGE, FUTURE)
    data = m.search(query, channel, page)
    if data["err"]:
        control.dialog.notification("Error", data["err"])
        return
    results = data["result"]["results"]

    no_duplicates = []

    for i in results:
        try:
            dt = datetime.datetime.fromtimestamp(i["timestamp"], pytz.timezone("Europe/Berlin"))
        except:
            pass
        url = ''
        if QUALITY == 0:  # Hoch
            for j in ("url_video_hd", "url_video", "url_video_low"):
                if i.get(j) == '':
                    continue
                else:
                    url = i.get(j)
                    break

        elif QUALITY == 1:  # Mittel
            for j in ("url_video", "url_video_low"):
                if i.get(j) == '':
                    continue
                else:
                    url = i.get(j)
                    break
        else:  # Niedrig
            url = i.get("url_video_low")

        if url == '': continue

        if not chk_duplicates(url, i["title"], i["topic"], no_duplicates) == True:
            no_duplicates.append({'url': url, 'title': i["title"]})
        else:
            continue

        today = datetime.date.today()
        if dt.date() == today:
            date = "Heute"
        elif dt.date() == today + datetime.timedelta(days=-1):
            date = "Gestern"
        else:
            date = dt.strftime("%d.%m.%Y")

        li = control.item("[{0}] {1} - {2}".format(i["channel"], i["topic"], i["title"]))
        li.setArt({'thumb': getMedia(i["channel"]), 'poster': getMedia(i["channel"]), 'banner': getMedia('banner')}) # favourites ok
        li.setProperty('Fanart_Image', addonFanart)

        li.setInfo("video", {
            "title": i["title"],
            "plot": "[B]" + i["title"] + "\n\n" + date + " - " + dt.strftime("%H:%M") + "[/B]\n" + i["description"],
            "dateadded": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "date": dt.strftime("%d.%m.%Y"),
            "aired": dt.strftime("%d.%m.%Y"),
            "year": dt.year,
            "duration": i["duration"],
            "studio": i["channel"],
        })
        li.setProperty("isPlayable", "true")

        control.addItem(
            syshandle,
            '%s?action=play&url=%s' %(sysaddon, url),   #sysaddon(action="play", url=url, subtitle=i["url_subtitle"]),
            li,
            isFolder=False
        )

    if len(results) == PER_PAGE:
        next_page = page + 1 # if page else 2
        li = control.item("[COLOR blue]Nächste Seite[/COLOR]")
        li.setArt({'poster': getMedia('next'), 'icon': getMedia('next')})
        li.setProperty('Fanart_Image', addonFanart)
        li.setInfo('video', {'overlay': 4, 'plot': ' '}) # Alt+255

        control.addItem(
            syshandle,
            '%s?action=list_videos&page=%s&query=%s&channel=%s' % (sysaddon, next_page, query, channel),
            li,
            isFolder=True
        )
    control.content(syshandle, 'videos')
    control.directory(syshandle, cacheToDisc=True)

def play(params):
    li = control.item(path=params['url'])
    if SUBTITLE == 'true':
        subtitle_file = join(control.addonPath, "subtitle.srt")
        subtitle_downloaded = download_subtitle(params['subtitle'], subtitle_file)
        if subtitle_downloaded:
            li.setSubtitles([subtitle_file])
    control.resolveUrl(syshandle, True, li)



## =======================================================================================

params = dict(control.parse_qsl(control.urlsplit(sys.argv[2]).query))

action = params.get('action')
bSearch = eval(params.get('bSearch')) if params.get('bSearch') else None
bChannels = eval(params.get('bChannels')) if params.get('bChannels') else None

if action == None or action == 'root':
    root()

elif action == 'searchQuery':
    query = showKeyBoard()
    if not query: exit()
    channel = params.get("channel") if params.get("channel") != 'None' else None
    page = int(params.get("page")) if params.get("page") else 1
    save_query(query, channel)
    list_videos(query=query, channel=channel, page=page)

elif action == 'lastQueries':
    last_queries()

elif action == 'removeQuery':
    remove_query(params)
    queries = load_queries()
    if queries == []:
        xbmc.executebuiltin('Action(ParentDir)')
    else:
        xbmc.executebuiltin('Container.Refresh')

elif action == 'searchClear':
    remove_all_query()
    xbmc.executebuiltin('Action(ParentDir)')

elif action == 'channel':
    showChannels(bSearch, bChannels)

elif action == 'list_videos':
    page = int(params.get("page")) if params.get("page") else 1
    query = params.get("query") if params.get("query") != 'None' else None
    channel = params.get("channel") if params.get("channel") != 'None' else None
    save_query(query, channel)
    list_videos(query=query, channel=channel, page=page)

elif action == 'play':
    play(params)

elif action == 'addonSettings':
    control.openSettings()

# try:
#     import pydevd
#     if pydevd.connected: pydevd.kill_all_pydev_threads()
# except: pass