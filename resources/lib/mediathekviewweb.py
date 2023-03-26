# -*- coding: utf-8 -*-

import sys, os, time, hashlib, json
import requests
from resources.lib.control import dataPath, addonName, getSetting
profilePath = dataPath

class MediathekViewWeb(object):
    def __init__(self, size=10, future=False):
        self.future = future
        self.size = size
        self.session = requests.session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0",
            "content-type": "text/plain",
        })

        # caching
        self.cacheTime = int(getSetting('cacheTime', 600))
        self._profilePath = profilePath  # common.profilePath
        self._cachePath = ''
        self.__setCachePath()
        self.caching = True


    def search(self, query=None, channel=None, page=1):
        if query == 'None' or query == '': query = None
        if channel == 'None' or channel == '': channel = None
        offset = self.size * (page - 1)
        data = {
            "sortBy": "timestamp",
            "sortOrder": "desc",
            "future": self.future,
            "offset": offset,
            "size": self.size,
        }
        if query or channel:
            data["queries"] = list()
        if query:
            data["queries"].append({
                "fields": [
                    "title",
                    "topic",
                ],
                "query": query,
            })
        if channel:
            data["queries"].append({
                "fields": [
                    "channel",
                ],
                "query": channel,
            })

        data = json.dumps(data)

        # if self.caching and self.cacheTime > 0:
        #     sContent = self.readCache(data)
        #     if sContent:
        #         return json.loads(sContent)

        r = self.session.post(
            "https://mediathekviewweb.de/api/query",
            data=data
        )

        # if r.status_code == 200 and self.caching and self.cacheTime > 0:
        #     self.writeCache(data, r.content)

        return r.json()

    def channels(self):
        r = self.session.get(
            "https://mediathekviewweb.de/api/channels",
        )
        return r.json()

    def __setCachePath(self):
        cache = os.path.join(self._profilePath, 'htmlcache')
        if not os.path.exists(cache):
            os.makedirs(cache)
        self._cachePath = cache

    def readCache(self, url):
        content = ''
        if sys.version_info[0] == 2:
            h = hashlib.md5(url).hexdigest()
        else:
            h = hashlib.md5(url.encode('utf8')).hexdigest()
        cacheFile = os.path.join(self._cachePath, h)
        fileAge = self.getFileAge(cacheFile)
        if 0 < fileAge < self.cacheTime:
            try:
                if sys.version_info[0] == 2:
                    with open(cacheFile, 'r') as f:
                        content = f.read()
                else:
                    with open(cacheFile, 'rb') as f:
                        content = f.read().decode('utf8')
            except Exception:
                #logger.error('Could not read Cache')
                pass
            if content:
                #logger.info('read html for %s from cache' % url)
                return content
        return ''

    def writeCache(self, url, content):
        try:
            if sys.version_info[0] == 2:
                h = hashlib.md5(url).hexdigest()
                with open(os.path.join(self._cachePath, h), 'w') as f:
                    f.write(content)
            else:
                h = hashlib.md5(url.encode('utf8')).hexdigest()
                with open(os.path.join(self._cachePath, h), 'wb') as f:
                    f.write(content.encode('utf8'))
        except Exception:
            #logger.error('Could not write Cache')
            pass

    @staticmethod
    def getFileAge(cacheFile):
        try:
            return time.time() - os.stat(cacheFile).st_mtime
        except Exception:
            return 0

    def clearCache(self):
        files = os.listdir(self._cachePath)
        for file in files:
            os.remove(os.path.join(self._cachePath, file))


