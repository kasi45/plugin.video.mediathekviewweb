# -*- coding: UTF-8 -*-

# 2023-05-08

import sys
import datetime
from os.path import join

from resources.lib.mediathekviewweb import MediathekViewWeb
from resources.lib import control
from resources.lib  import searchdb

# add pytz module to path
module_dir = join(control.addonPath, "resources", "lib")
sys.path.insert(0, module_dir)
import pytz

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1]) if len(sys.argv) > 1 else ''

artPath = control.artPath()
addonFanart = control.addonFanart()

PER_PAGE = int(control.getSetting("per_page"))
FUTURE = True if control.getSetting("enable_future")=='true' else False
QUALITY = int(control.getSetting("quality"))

#Todo
#SUBTITLE = True if control.getSetting("enable_subtitle")=='true' else False
SUBTITLE = False
if SUBTITLE == 'true':
    from resources.lib.subtitles import download_subtitle

params = dict(control.parse_qsl(control.urlsplit(sys.argv[2]).query))

class cMediathek:
    def __init__(self):
        self.blockedDict = self.blocked_dict()

    def get(self, params):
        try:
            self.list = self.getMediaData(params)
            self.list_videos()
        except:
            return

    def getMediaData(self, params):
        self.next_pages = int(params.get('page')) if params.get('page') else 1
        self.channel = params.get('channel') if params.get('channel') and params.get('channel') != 'None' else None
        self.query = params.get('query') if params.get('query') and params.get('query') != 'None' else None

        m = MediathekViewWeb(PER_PAGE, FUTURE)
        data = m.search(self.query, self.channel, self.next_pages)
        if data["err"]:
            control.dialog.notification("Error", data["err"])
            return

        self.list = data["result"]["results"]
        if self.list == None or len(self.list) == 0:  # nichts gefunden
            control.infoDialog("Nichts gefunden1", time=2000)
        return self.list

    def root(self):
        self.addDirectoryItem("In Mediatheken suchen", 'search_menu', 'search.png', 'DefaultVideo.png')
        self.addDirectoryItem("In Mediatheken stöbern", 'browse_menu', 'search.png', 'DefaultVideo.png')
        downloadFolder = control.getSetting('download.movie.path')
        if len(control.listDir(downloadFolder)[0]) > 0:
            self.addDirectoryItem("Alle Downloads", downloadFolder, 'downloads.png', 'DefaultFolder.png', isAction=False)
        self.addDirectoryItem("Einstellungen", 'addonSettings', 'tools.png', 'DefaultAddonProgram.png', isFolder=False)
        self.setEndOfDirectory()

    def root_all(self):
        queries = searchdb.load_queries()
        if queries != []:
            self.addDirectoryItem("Letzte Suchanfrage", 'search_last', 'search.png', 'DefaultVideo.png')
        self.addDirectoryItem("Auf Sender suchen", 'search_channel', 'search.png', 'DefaultVideo.png')
        self.addDirectoryItem("Überall suchen", 'search_new', 'search.png', 'DefaultVideo.png', isFolder=False)
        self.addDirectoryItem("Auf Sender stöbern", 'browse_channel', 'search.png', 'DefaultVideo.png')
        self.addDirectoryItem("Überall stöbern", 'browse', 'search.png', 'DefaultVideo.png')
        downloadFolder = control.getSetting('download.movie.path')
        if len(control.listDir(downloadFolder)[0]) > 0:
            self.addDirectoryItem("Alle Downloads", downloadFolder, 'downloads.png', 'DefaultFolder.png', isAction=False)
        self.addDirectoryItem("Einstellungen", 'addonSettings', 'tools.png', 'DefaultAddonProgram.png', isFolder=False)
        self.setEndOfDirectory()

    def searchMenu(self):
        queries = searchdb.load_queries()
        if queries != []:
            self.addDirectoryItem("Letzte Suchanfrage", 'search_last', 'search.png', 'DefaultVideo.png')
        self.addDirectoryItem("Auf Sender suchen", 'search_channel', 'search.png', 'DefaultVideo.png')
        self.addDirectoryItem("Überall suchen", 'search_new', 'search.png', 'DefaultVideo.png', isFolder=False)
        self.setEndOfDirectory()

    def browseMenu(self):
        self.addDirectoryItem("Auf Sender stöbern", 'browse_channel', 'search.png', 'DefaultVideo.png')
        self.addDirectoryItem("Überall stöbern", 'browse', 'search.png', 'DefaultVideo.png')
        self.setEndOfDirectory()

    def channelList(self):
        #TODO
        isStaticChannelList = True
        if isStaticChannelList:
            # statisch
            data = {'error': None,
                    'channels': ['ARD', 'ZDF', 'MDR', 'ARTE.DE', '3Sat', 'PHOENIX', 'NDR', 'SWR', 'SRF', 'Funk.net', 'BR',
                                 'SR', 'Radio Bremen TV', 'rbtv', 'DW', 'HR', 'WDR', 'RBB', 'ZDF-tivi', 'KiKA']}
        else:
            m = MediathekViewWeb()
            data = m.channels()
            if data["error"]:
                import xbmcgui
                dialog = xbmcgui.Dialog()
                dialog.notification(_("Error"), data["error"])
                return
            # keine unterstützung für ORF - videos können nicht abgespielt werden
            data["channels"].remove('ORF')

        return data["channels"]

    def searchChannel(self, bSearch=True):
        for channel in self.channelList():
            if bSearch:
                self.addDirectoryItem(channel, 'search_new&channel=%s' % channel, channel, join(artPath, 'icon.png'), isFolder=False)  # Auf Sender suchen
            else:
                self.addDirectoryItem(channel, 'search&channel=%s' % channel, channel, join(artPath, 'icon.png'))  # Auf Sender stöbern
        self.setEndOfDirectory()

    def searchLast(self):
        queries = searchdb.load_queries()
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
                self.addDirectoryItem(label, 'search&query=%s&channel=%s' % (query, channel), thumb,
                                 'DefaultAddonsSearch.png',
                                 context=("Suchanfrage löschen", 'removeQuery&index=%s' % index))
                lst += [(label)]

        if delete_option:
            self.addDirectoryItem("[B]Suchverlauf löschen[/B]", 'searchClear', 'tools.png', 'DefaultAddonProgram.png', isFolder=False)
        self.setEndOfDirectory()  # addons  videos  files

    def addDirectoryItem(self,name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True):
        url = '%s?action=%s' % (sysaddon, query) if isAction == True else query
        thumb = self.getMedia(thumb, icon)
        #laut kodi doku - ListItem([label, label2, path, offscreen])
        listitem = control.item(name, offscreen=True) # Removed iconImage and thumbnailImage
        listitem.setArt({'poster': thumb, 'thumb': thumb,})
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

    def setEndOfDirectory(self, content='', cache=True ): # addons  videos  files
        # https://romanvm.github.io/Kodistubs/_autosummary/xbmcplugin.html#xbmcplugin.setContent
        control.content(syshandle, content)
        control.directory(syshandle, succeeded=True, cacheToDisc=cache)

    def getMedia(self,mediaFile=None, icon=None):
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

    def list_videos(self):
        isDownload = control.getSetting('downloads') == 'true' and len(control.getSetting('download.movie.path')) >= 3 and control.exists(control.translatePath(control.getSetting('download.movie.path')))
        no_duplicates = []
        for i in self.list:
            try:
                if i["channel"] == 'ORF': continue
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
                if sys.version_info[0] == 2:
                    title = i["title"].encode('ascii', 'ignore')
                    topic = i["topic"].encode('ascii', 'ignore') if i.get('topic', False) else None
                else:
                    title = i["title"]
                    topic = i["topic"] if i.get('topic', False) else None

                if not self.chk_duplicates(url, title, topic, no_duplicates) == True:
                    no_duplicates.append({'url': url, 'title': title, 'topic': topic})
                else:
                    continue

                today = datetime.date.today()
                if dt.date() == today:
                    date = "Heute"
                elif dt.date() == today + datetime.timedelta(days=-1):
                    date = "Gestern"
                else:
                    date = dt.strftime("%d.%m.%Y")

                li = control.item("[{0}] {1} - {2}".format(i["channel"], topic, title))
                li.setArt({'thumb': self.getMedia(i["channel"]), 'poster': self.getMedia(i["channel"]), 'banner': self.getMedia('banner')})  # favourites ok
                li.setProperty('Fanart_Image', addonFanart)

                li.setInfo("video", {
                    "title": title,
                    "plot": "[B]" + title + "\n\n" + date + " - " + dt.strftime("%H:%M") + "[/B]\n" + i["description"],
                    "dateadded": dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "date": dt.strftime("%d.%m.%Y"),
                    "aired": dt.strftime("%d.%m.%Y"),
                    "year": dt.year,
                    "duration": i["duration"],
                    "studio": i["channel"],
                })

                li.setProperty("isPlayable", "true")
                cm = []
                subFolder = topic
                downloadTitle = control.quote(title.replace(' ', '_'))
                if isDownload:
                    cm.append(("Download", 'RunPlugin(%s?action=download&name=%s&image=%s&url=%s&subfolder=%s)' % (sysaddon, downloadTitle, self.getMedia(i["channel"]), url, subFolder)))
                cm.append(('Einstellungen', 'RunPlugin(%s?action=addonSettings)' % sysaddon))
                li.addContextMenuItems(cm)
                control.addItem(
                    syshandle,
                    '%s?action=play&url=%s&title=%s' % (sysaddon, url, title),  # sysaddon(action="play", url=url, subtitle=i["url_subtitle"]),
                    li,
                    isFolder=False
                )
            except:
                pass

        if len(self.list) == PER_PAGE:
            next_page = self.next_pages + 1  # if page else 2
            li = control.item("[COLOR blue]Nächste Seite[/COLOR]")
            li.setArt({'poster': self.getMedia('next'), 'icon': self.getMedia('next')})
            li.setProperty('Fanart_Image', addonFanart)
            li.setInfo('video', {'overlay': 4, 'plot': ' '})  # Alt+255

            control.addItem(
                syshandle,
                '%s?action=search&page=%s&query=%s&channel=%s' % (sysaddon, next_page, self.query, self.channel),
                li,
                isFolder=True
            )
        self.setEndOfDirectory(content='videos', cache=True)  # addons  videos  files


    def blocked_dict(self):
        blockedDict = ['Audiodeskription', 'Hörfassung', 'Trailer']  # permanenter Block
        blockedStr = control.getSetting('blockedStr').split(',')  # aus setting.xml blockieren
        if len(blockedStr) <= 1: blockedStr = control.getSetting('blockedStr').split()
        for i in blockedStr: blockedDict.append(i.lower())
        return blockedDict

    def chk_duplicates(self, url, title, topic, duplicates):
        try:
            for i in self.blockedDict:
                if i.lower() in title.lower(): return True

            for j in duplicates:
                # if url.split("//")[1] == j['url'].split("//")[1]:
                #     return True
                if title == j['title'] and topic == j['topic']:
                    return True
                else:
                    continue
        except:
            pass

    def play(self, params):
        li = control.item(path=params['url'])
        if SUBTITLE == 'true':
            subtitle_file = join(control.addonPath, "subtitle.srt")
            subtitle_downloaded = download_subtitle(params['subtitle'], subtitle_file)
            if subtitle_downloaded:
                li.setSubtitles([subtitle_file])
        control.resolveUrl(syshandle, True, li)
