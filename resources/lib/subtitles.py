# -*- coding: utf-8 -*-
import os
import requests
import sys
import xbmcvfs

from resources.lib.utils import py2_encode, addon_dir

# add pycaption module to path

module_dir = os.path.join(addon_dir, "resources", "lib", "pycaption")
sys.path.insert(0, module_dir)

# we need this fork: https://github.com/lucasheld/pycaption/tree/py27-py3-compat
from pycaption import SRTWriter, detect_format


def download_subtitle(url, destination):
    if not url:
        return False
    r = requests.get(url)
    if not r.ok:
        return False
    reader = detect_format(r.text)
    if not reader:
        return False
    srt = SRTWriter().write(reader().read(r.text))
    if xbmcvfs.exists(destination):
        xbmcvfs.delete(destination)
    f = xbmcvfs.File(destination, 'w')
    try:
        f.write(py2_encode(srt))
    finally:
        f.close()
    return True
