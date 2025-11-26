#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""
#########################################################
#                                                       #
#  RadioM Plugin                                        #
#  Version: 1.4                                         #
#  Created by Lululla (https://github.com/Belfagor2005) #
#  Modified by Mmark                                    #
#  License: Gnu Gpl v2                                  #
#  https://creativecommons.org/licenses/by-nc-sa/4.0    #
#  Last Modified: "17:38 - 20251125"                    #
#                                                       #
#  Credits:                                             #
#  - Original concept by Lululla                        #
#  - Development by Mmark                               #
#  Usage of this code without proper attribution        #
#  is strictly prohibited.                              #
#  For modifications and redistribution,                #
#  please maintain this credit header.                  #
#########################################################
"""

from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryPixmapAlphaTest, MultiContentEntryText
from Components.Pixmap import Pixmap
from Components.ServiceEventTracker import InfoBarBase
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.InfoBarGenerics import (
    InfoBarMenu,
    InfoBarSeek,
    InfoBarNotifications,
    InfoBarShowHide,
)
from Screens.Screen import Screen
from enigma import (
    RT_HALIGN_LEFT,
    RT_VALIGN_CENTER,
    eServiceReference,
    getDesktop,
    eTimer,
    loadPNG,
    eListboxPythonMultiContent,
    gFont,
)
from re import sub
from os.path import join, dirname, exists, getsize
from os import walk, remove
import sys
import requests
import codecs
from json import loads as json_loads
from datetime import datetime as dt
from time import time
from PIL import Image
import shutil

from . import _, Utils
from .PicLoader import PicLoader
from .Console import Console as xConsole


try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

import logging
logging.basicConfig(level=logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


global skin_path, x, y

currversion = '1.4'
THISPLUG = dirname(sys.modules[__name__].__file__)
skin_path = THISPLUG
iconpic = 'plugin.png'
screenWidth = getDesktop(0).size().width()
installer_url = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL0JlbGZhZ29yMjAwNS9SYWRpby04MC1zL21haW4vaW5zdGFsbGVyLnNo'
developer_url = 'aHR0cHM6Ly9hcGkuZ2l0aHViLmNvbS9yZXBvcy9CZWxmYWdvcjIwMDUvUmFkaW8tODAtcw=='
aspect_manager = Utils.AspectManager()
sc = AVSwitch().getFramebufferScale()

x = 220
y = 220
PY3 = sys.version_info.major >= 3

if PY3:
    unidecode = str

if not PY3:
    # Python 2
    unicode = unicode
else:
    # Python 3
    unicode = str


if screenWidth == 2560:
    skin_path = THISPLUG + '/skin/wqhd'
    x = 450
    y = 450
elif screenWidth == 1920:
    skin_path = THISPLUG + '/skin/fhd'
    x = 340
    y = 340
else:
    skin_path = THISPLUG + '/skin/hd'
    # x = 220
    # y = 220


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1"
}


def geturl(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        return response.content
    except Exception as e:
        print("Error geturl: " + str(e))
        return ''


class radioList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, True, eListboxPythonMultiContent)

        if screenWidth == 2560:
            item_height = 50
            font_size = 42
        elif screenWidth == 1920:
            item_height = 50
            font_size = 38
        else:
            item_height = 40
            font_size = 34

        self.l.setItemHeight(item_height)
        self.l.setFont(0, gFont('Regular', font_size))


def RListEntry(download):
    res = [(download)]
    col = 0xffffff
    colsel = 0xf07655
    pngx = join(skin_path, "folder.png")
    if screenWidth == 2560:
        icon_pos = (10, 6)
        text_pos = (80, 0)
        text_size = (800, 50)
    elif screenWidth == 1920:
        icon_pos = (10, 6)
        text_pos = (60, 0)
        text_size = (600, 50)
    else:
        icon_pos = (10, 6)
        text_pos = (0, 0)
        text_size = (400, 40)

    res.append(MultiContentEntryPixmapAlphaTest(pos=icon_pos, size=(35, 35), png=loadPNG(pngx)))
    res.append(MultiContentEntryText(pos=text_pos, size=text_size, font=0, text=download, color=col, color_sel=colsel, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))

    return res


def showlist(datal, list):
    plist = []
    for name in datal:
        plist.append(RListEntry(name))
    list.setList(plist)


def resizePoster(x, y, dwn_poster):
    try:
        from PIL import Image
        with Image.open(dwn_poster) as img:
            new_width = x
            new_height = y
            try:
                rimg = img.resize((new_width, new_height), Image.LANCZOS)
            except Exception:
                rimg = img.resize((new_width, new_height), Image.ANTIALIAS)
            rimg.save(dwn_poster)
    except Exception as e:
        print("ERROR resizePoster: " + str(e))


def titlesong2(url):
    try:
        print("DEBUG titlesong2: Fetching URL: " + str(url))
        r = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        print("DEBUG titlesong2: Status code: " + str(r.status_code))
        data = r.json()
        print("DEBUG titlesong2: JSON data type: " + str(type(data)))
        return data
    except Exception as e:
        print("DEBUG titlesong2: Error: " + str(e))
        return {"error": str(e)}


def titlesong(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        data = r.json()

        real_duration = data.get("track", {}).get("duration", 0)

        if real_duration <= 0:
            real_duration = 210

        start_time = dt.strptime(data.get("started_at", "")[:19], "%Y-%m-%d %H:%M:%S")
        end_time = dt.strptime(data.get("ends_at", "")[:19], "%Y-%m-%d %H:%M:%S")
        timestamp_duration = int((end_time - start_time).total_seconds())

        real_duration = timestamp_duration if 30 < timestamp_duration < 600 else real_duration
        comeback = (
            'Artist: ' + data.get("artist", {}).get("name", "") + '\n' +
            'Title: ' + data.get("title", "") + '\n' +
            'Duration: ' + str(real_duration) + ' sec'
        )

        return {
            "comeback": comeback,
            "duration": real_duration,
            "title": data.get("title", ""),
            "artist": data.get("artist", {}).get("name", "")
        }

    except Exception as e:
        return {"error": str(e)}


class radiom1(Screen):
    def __init__(self, session):
        skin = join(skin_path, 'radiom.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        Screen.__init__(self, session)
        self.session = session
        self.list = []
        self['list'] = radioList([])
        self['info'] = Label('HOME RADIO VIEW')
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Select'))
        self['key_yellow'] = Button(_('Update'))
        self.currentList = 'list'
        self["logo"] = Pixmap()
        self["back"] = Pixmap()
        self.picload = PicLoader()
        global x, y
        pic = skin_path + "/ft.jpg"
        x = 430
        y = 430
        if screenWidth == 1920:
            x = 340
            y = 340
        if screenWidth == 2560:
            x = 640
            y = 640
        resizePoster(x, y, pic)
        self.picload.setPara((x, y, sc[0], sc[1], 0, 1, "#00000000"))
        self.picload.addCallback(self.showback)
        self.picload.startDecode(pic)
        self.Update = False
        self['setupActions'] = ActionMap(
            [
                'OkCancelActions',
                'DirectionActions',
                'HotkeyActions',
                'InfobarEPGActions',
                'ChannelSelectBaseActions'
            ],
            {
                'ok': self.okClicked,
                'back': self.close,
                'cancel': self.close,
                'yellow': self.update_me,
                'green': self.okClicked,
                "up": self.up,
                "down": self.down,
                "left": self.left,
                "right": self.right,
                'yellow_long': self.update_dev,
                'info_long': self.update_dev,
                'infolong': self.update_dev,
                'showEventInfoPlugin': self.update_dev,
                'red': self.close
            },
            -1
        )
        self.timer = eTimer()
        if exists('/var/lib/dpkg/status'):
            self.timer_conn = self.timer.timeout.connect(self.check_vers)
        else:
            self.timer.callback.append(self.check_vers)
        self.timer.start(500, 1)
        self.onLayoutFinish.append(self.openTest)

    def check_vers(self):
        remote_version = '0.0'
        remote_changelog = ''
        req = Utils.Request(Utils.b64decoder(installer_url), headers={'User-Agent': 'Mozilla/5.0'})
        page = Utils.urlopen(req).read()
        if PY3:
            data = page.decode("utf-8")
        else:
            data = page.encode("utf-8")
        if data:
            lines = data.split("\n")
            for line in lines:
                if line.startswith("version"):
                    remote_version = line.split("=")
                    remote_version = line.split("'")[1]
                if line.startswith("changelog"):
                    remote_changelog = line.split("=")
                    remote_changelog = line.split("'")[1]
                    break
        self.new_version = remote_version
        self.new_changelog = remote_changelog
        if currversion < remote_version:
            self.Update = True
            self['key_green'].show()
            self.session.open(MessageBox, _('New version %s is available\n\nChangelog: %s\n\nPress info_long or yellow_long button to start force updating.') % (self.new_version, self.new_changelog), MessageBox.TYPE_INFO, timeout=5)

    def update_me(self):
        if self.Update is True:
            self.session.openWithCallback(self.install_update, MessageBox, _("New version %s is available.\n\nChangelog: %s \n\nDo you want to install it now?") % (self.new_version, self.new_changelog), MessageBox.TYPE_YESNO)
        else:
            self.session.open(MessageBox, _("Congrats! You already have the latest version..."),  MessageBox.TYPE_INFO, timeout=4)

    def update_dev(self):
        try:
            req = Utils.Request(Utils.b64decoder(developer_url), headers={'User-Agent': 'Mozilla/5.0'})
            page = Utils.urlopen(req).read()
            data = json_loads(page)
            remote_date = data['pushed_at']
            strp_remote_date = dt.strptime(remote_date, '%Y-%m-%dT%H:%M:%SZ')
            remote_date = strp_remote_date.strftime('%Y-%m-%d')
            self.session.openWithCallback(self.install_update, MessageBox, _("Do you want to install update ( %s ) now?") % (remote_date), MessageBox.TYPE_YESNO)
        except Exception as e:
            print('error xcons: ' + str(e))

    def install_update(self, answer=False):
        if answer:
            cmd1 = 'wget -q "--no-check-certificate" ' + Utils.b64decoder(installer_url) + ' -O - | /bin/sh'
            self.session.open(xConsole, 'Upgrading...', cmdlist=[cmd1], finishedCallback=self.myCallback, closeOnSuccess=False)
        else:
            self.session.open(MessageBox, _("Update Aborted!"),  MessageBox.TYPE_INFO, timeout=3)

    def myCallback(self, result=None):
        print('result: ' + str(result))
        return

    def openTest(self):
        self.names = []
        self.urls = []
        self.pics = []
        self.descriptions = []
        try:
            # Download multiple pages
            all_stations = []

            # Download first 3 pages
            for page in range(1, 4):
                url = "https://laut.fm/stations/all?l=50&page=" + str(page)
                print("Downloading page: " + str(page))

                response = requests.get(url, headers=HEADERS, timeout=10)
                if response.status_code == 200:
                    import re
                    json_match = re.search(r'<script id="app-json" type="application/json">(.*?)</script>', response.text, re.DOTALL)

                    if json_match:
                        json_data = json_match.group(1)
                        stations_data = json_loads(json_data)
                        page_stations = stations_data.get("stations", [])
                        all_stations.extend(page_stations)
                        print("Page " + str(page) + " has " + str(len(page_stations)) + " stations")

            # Process all collected stations
            for station in all_stations:
                display_name = station.get("display_name", station.get("name", ""))
                if display_name:
                    self.names.append(str(display_name))
                    self.urls.append(str(station.get("stream_url", "")))
                    self.pics.append(str(station.get("images", {}).get("station_120x120", "")))
                    self.descriptions.append(str(station.get("description", "")))

            # ADD DEFAULT STATIONS AT THE BEGINNING
            self.names.insert(0, 'PLAYLIST')
            self.urls.insert(0, 'http://75.119.158.76:8090/radio.mp3')
            self.pics.insert(0, skin_path + "/ft.jpg")

            self.names.insert(1, 'RADIO CYRUS')
            self.urls.insert(1, 'http://75.119.158.76:8090/radio.mp3')
            self.pics.insert(1, skin_path + "/ft.jpg")

            print("Loaded " + str(len(self.names)) + " total stations")

        except Exception as e:
            print("Error loading stations: " + str(e))
            import traceback
            traceback.print_exc()
            self.load_fallback_stations()

        print("Final stations count: " + str(len(self.names)))
        showlist(self.names, self['list'])

    def load_fallback_stations(self):
        """Load fallback stations if JSON loading fails"""
        self.names.append('PLAYLIST')
        self.urls.append('http://75.119.158.76:8090/radio.mp3')
        self.pics.append(skin_path + "/ft.jpg")
        self.names.append('RADIO 80')
        self.urls.append('http://laut.fm/fm-api/stations/soloanni80')
        self.pics.append(skin_path + "/80s.png")
        self.names.append('80ER')
        self.urls.append('http://laut.fm/fm-api/stations/80er')
        self.pics.append(skin_path + "/80er.png")
        self.names.append('SCHLAGER-RADIO')
        self.urls.append('http://laut.fm/fm-api/stations/schlager-radio')
        self.pics.append(skin_path + "/shclager.png")
        self.names.append('1000OLDIES')
        self.urls.append('http://laut.fm/fm-api/stations/1000oldies')
        self.pics.append(skin_path + "/1000oldies.png")
        self.names.append('REGGAETON')
        self.urls.append('https://laut.fm/fm-api/stations/reggaeton')
        self.pics.append(skin_path + "/reggaeton.png")
        self.names.append('FLASHBASS-FM')
        self.urls.append('https://laut.fm/fm-api/stations/flashbass-fm')
        self.pics.append(skin_path + "/flashbass.png")
        self.names.append('1000GOLD')
        self.urls.append('https://laut.fm/fm-api/stations/1000goldschlager')
        self.pics.append(skin_path + "/1000gold.png")
        self.names.append('SIMLIVERADIO')
        self.urls.append('https://laut.fm/fm-api/stations/simliveradio')
        self.pics.append(skin_path + "/simliveradio.png")
        self.names.append('RADIO CYRUS')
        self.urls.append('http://75.119.158.76:8090/radio.mp3')
        self.pics.append(skin_path + "/ft.jpg")

    def okClicked(self):
        idx = self['list'].getSelectionIndex()
        if idx is None:
            return
        name = self.names[idx]
        url = self.urls[idx]

        print("Opening station: " + str(name))
        print("Stream URL: " + str(url))

        if 'PLAYLIST' in name:
            self.session.open(radiom2)
        elif 'RADIO CYRUS' in name:
            self.session.open(Playstream2, name, url)
        else:
            pic = skin_path + "/ft.jpg"
            api_url = "http://api.laut.fm/station/" + name.lower().replace(" ", "-")
            print("API URL: " + api_url)
            self.session.open(radiom80, name, url, pic, api_url)

    def selectpic(self):
        idx = self['list'].getSelectionIndex()
        if idx is None:
            return

        pic = self.pics[idx]
        print("Selected station image: " + str(pic))
        if isinstance(pic, str) and pic.startswith('http'):
            try:
                local_path = self.download_image_to_cache(pic)
                if local_path:
                    pic = local_path
                    print("Using downloaded image: " + pic)
                else:
                    pic = skin_path + "/ft.jpg"
                    print("Using fallback image")
            except:
                pic = skin_path + "/ft.jpg"
                print("Error downloading, using fallback")
        else:
            pic = skin_path + "/ft.jpg"

        self.picload = PicLoader()
        self.picload.setPara((x, y, sc[0], sc[1], 0, 1, "#00000000"))
        self.picload.addCallback(self.showback)
        self.picload.startDecode(pic)

    def download_image_to_cache(self, image_url):
        """Download the image and save it in the local cache"""
        try:
            import hashlib
            # Create a unique filename based on the URL
            filename = hashlib.md5(image_url.encode('utf-8')).hexdigest() + ".jpg"
            cache_path = "/tmp/radiom_cache/"

            # Create cache directory if it doesn't exist
            from os import makedirs, path
            if not path.exists(cache_path):
                makedirs(cache_path)

            local_file = cache_path + filename

            # If the file already exists, use it
            if exists(local_file):
                return local_file

            # Download the image
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                with open(local_file, 'wb') as f:
                    f.write(response.content)
                return local_file

        except Exception as e:
            print("Error downloading image: " + str(e))

        return None

    def showback(self, picInfo=None):
        try:
            ptr = self.picload.getData()
            if ptr is not None:
                self["logo"].instance.setPixmap(ptr)
                self["logo"].instance.show()
        except Exception as err:
            self["logo"].instance.hide()
            print("ERROR showImage: " + str(err))

    def up(self):
        self[self.currentList].up()
        self.selectpic()

    def down(self):
        self[self.currentList].down()
        self.selectpic()

    def left(self):
        self[self.currentList].pageUp()
        self.selectpic()

    def right(self):
        self[self.currentList].pageDown()
        self.selectpic()

    def cancel(self):
        Screen.close(self, False)


class radiom2(Screen):
    def __init__(self, session):
        skin = join(skin_path, 'radiom.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        Screen.__init__(self, session)
        self.list = []
        self['list'] = radioList([])
        self['info'] = Label()
        self['info'].setText('UserList')
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Select'))
        self['key_yellow'] = Button()
        self["logo"] = Pixmap()
        self["back"] = Pixmap()
        self["back"].hide()
        self.picload = PicLoader()
        pic = skin_path + "/ft.jpg"
        x = 430
        y = 430
        if screenWidth == 1920:
            x = 340
            y = 340
        if screenWidth == 2560:
            x = 640
            y = 640
        resizePoster(x, y, pic)
        self.picload.setPara((x, y, sc[0], sc[1], 0, 1, "#00000000"))
        self.picload.addCallback(self.showback)
        self.picload.startDecode(pic)
        self['setupActions'] = ActionMap(
            [
                'SetupActions',
                'ColorActions',
                'TimerEditActions'
            ],
            {
                "red": self.close,
                "green": self.okClicked,
                "cancel": self.cancel,
                "ok": self.okClicked,
            },
            -2
        )
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        uLists = THISPLUG + '/Playlists'
        self.names = []
        for root, dirs, files in walk(uLists):
            for name in files:
                if '.txt' in name:
                    self.names.append(name)
        showlist(self.names, self['list'])

    def okClicked(self):
        idx = self['list'].getSelectionIndex()
        if idx is None:
            return
        name = self.names[idx]
        self.session.open(radiom3, name)

    def showback(self, picInfo=None):
        try:
            ptr = self.picload.getData()
            if ptr is not None:
                self["logo"].instance.setPixmap(ptr)
                self["logo"].instance.show()
        except Exception as err:
            self["logo"].instance.hide()
            print("ERROR showImage: " + str(err))

    def cancel(self):
        Screen.close(self, False)


class radiom3(Screen):
    def __init__(self, session, name):
        skin = join(skin_path, 'radiom.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        Screen.__init__(self, session)
        self.name = name
        self.list = []
        self['list'] = radioList([])
        self['info'] = Label()
        self['info'].setText(name)
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Select'))
        self['key_yellow'] = Button()
        self["logo"] = Pixmap()
        self["back"] = Pixmap()
        self["back"].hide()
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        self.is_playing = False
        self.picload = PicLoader()
        pic = skin_path + "/ft.jpg"
        x = 430
        y = 430
        if screenWidth == 1920:
            x = 340
            y = 340
        if screenWidth == 2560:
            x = 640
            y = 640
        resizePoster(x, y, pic)
        self.picload.setPara((x, y, sc[0], sc[1], 0, 1, "#00000000"))
        self.picload.addCallback(self.showback)
        self.picload.startDecode(pic)

        self['setupActions'] = ActionMap(
            [
                'SetupActions',
                'ColorActions',
                'TimerEditActions'
            ],
            {
                "red": self.close,
                "green": self.okClicked,
                "cancel": self.cancel,
                "ok": self.okClicked,
            }, -2
        )
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        uLists = THISPLUG + "/Playlists"
        file1 = uLists + "/" + str(self.name)
        print("Here in showContentA2 file1 = " + file1)
        self.names = []
        self.urls = []
        try:
            with open(file1, "r") as f1:
                for line in f1:
                    if "##" not in line:
                        continue
                    line = line.strip()
                    items = line.split("###")
                    if len(items) < 2:
                        continue
                    name = items[0]
                    url = items[1]
                    self.names.append(name)
                    self.urls.append(url)
                showlist(self.names, self['list'])
        except Exception as e:
            print("Error reading file: " + str(e))

    def okClicked(self):
        idx = self["list"].getSelectionIndex()
        if idx is None:
            return

        name = self.names[idx]
        url = self.urls[idx]

        if self.is_playing:
            self.stop()
            return

        url = url.replace(":", "%3a").replace(" ", "%20")
        ref = "4097:0:1:0:0:0:0:0:0:0:" + str(url)
        print("final reference:   " + ref)
        sref = eServiceReference(ref)
        sref.setName(name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)
        self.is_playing = True

    def stop(self, text=''):
        if self.is_playing:
            try:
                self.is_playing = False
                self.session.nav.stopService()
                self.session.nav.playService(self.srefOld)
                return
            except TypeError as e:
                print(str(e))
                self.close()

    def showback(self, picInfo=None):
        try:
            ptr = self.picload.getData()
            if ptr is not None:
                self["logo"].instance.setPixmap(ptr)
                self["logo"].instance.show()
        except Exception as err:
            self["logo"].instance.hide()
            print("ERROR showImage: " + str(err))

    def cancel(self):
        self.stop()
        Screen.close(self, False)


class radiom80(Screen):
    def __init__(self, session, name, stream_url, pic, api_url):
        skin = join(skin_path, "radiom80.xml")
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        Screen.__init__(self, session)
        self.session = session
        self.name = name
        self.pic = pic
        self.stream_url = stream_url
        self.api_url = api_url
        self['list'] = radioList([])
        self['info'] = Label()
        self['info'].setText(name)
        self['current_song'] = Label()
        self['listeners'] = Label()
        self['format'] = Label()
        self['description'] = Label()
        self['djs'] = Label()
        self["logo"] = Pixmap()
        self["back"] = Pixmap()
        self["back"].hide()
        self.player = '1'
        self.picload = PicLoader()
        global x, y
        pic = pic.replace("\n", "").replace("\r", "")
        x = 430
        y = 430
        if screenWidth == 1920:
            x = 340
            y = 340
        if screenWidth == 2560:
            x = 640
            y = 640
        resizePoster(x, y, pic)
        self.picload.setPara((x, y, sc[0], sc[1], 0, 1, "#00000000"))
        self.picload.addCallback(self.showback)
        self.picload.startDecode(self.pic)
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        self.is_playing = False
        self.cover_timer = eTimer()
        if exists('/var/lib/dpkg/status'):
            self.cover_timer_conn = self.cover_timer.timeout.connect(self.countdown)
        else:
            self.cover_timer.callback.append(self.countdown)

        self.current_artist = ""
        self.current_title = ""
        self.last_song_id = ""
        self.okcoverdown = 'failed'

        self.update_timer = eTimer()
        if exists('/var/lib/dpkg/status'):
            self.update_timer_conn = self.update_timer.timeout.connect(self.countdown)
        else:
            self.update_timer.callback.append(self.countdown)
        self.update_timer.start(10000, False)
        self.last_cover_request = 0
        self.song_start_time = time()
        self.last_song_hash = ""
        self.current_cover = ""
        self.cover_timeout = 0
        self.backing = ""
        self.current_duration = 0

        self['key_red'] = Button(_('Exit'))
        self['key_blue'] = Label("Player 1-2-3")
        self['key_green'] = Button(_('Select'))
        self['key_green'].hide()
        self["actions"] = ActionMap(
            ["OkActions", "SetupActions", "ColorActions", "EPGSelectActions", "InfoActions", "CancelActions"],
            {
                "red": self.cancel,
                "back": self.cancel,
                "blue": self.typeplayer,
                "green": self.openPlay,
                "info": self.countdown,
                "cancel": self.cancel,
                "ok": self.openPlay,
            },
            -2
        )
        self.onShow.append(self.openTest)

    def typeplayer(self):
        if self.player == "2":
            self["key_blue"].setText("Player 3-2-1")
            self.player = "3"
        elif self.player == "1":
            self["key_blue"].setText("Player 2-3-1")
            self.player = "2"
        else:
            self["key_blue"].setText("Player 1-2-3")
            self.player = "1"
        return

    def showback(self, picInfo=None):
        try:
            ptr = self.picload.getData()
            if ptr is not None:
                self["logo"].instance.setPixmap(ptr)
                self["logo"].instance.show()
        except Exception as err:
            self["logo"].instance.hide()
            print("ERROR showImage: " + str(err))

    def showback2(self, picInfo=None):
        try:
            self["back"].instance.show()
        except Exception as err:
            self["back"].instance.hide()
            print("ERROR showback2: " + str(err))

    def selectpic(self):
        try:
            if hasattr(self, 'okcoverdown') and self.okcoverdown == 'success':
                temp_path = '/tmp/artist_temp.jpg'
                final_path = '/tmp/artist.jpg'

                if exists(final_path):
                    try:
                        with Image.open(final_path) as img:
                            if img.format != 'JPEG':
                                img.convert('RGB').save(temp_path, 'JPEG', quality=90)
                                shutil.move(temp_path, final_path)
                    except Exception as conv_err:
                        print("Error conversion: " + str(conv_err))
                        if exists(final_path):
                            remove(final_path)
                        return

                if exists(final_path) and getsize(final_path) > 2048:
                    x = self["logo"].instance.size().width()
                    y = self["logo"].instance.size().height()
                    self["logo"].instance.setPixmap(None)
                    resizePoster(x, y, final_path)
                    self.picload = PicLoader()
                    self.picload.setPara((x, y, sc[0], sc[1], 0, 1, "#FF000000"))

                    def safe_callback(picInfo=None):
                        try:
                            ptr = self.picload.getData()
                            if ptr:
                                self["logo"].instance.setPixmap(ptr)
                                self["logo"].instance.show()
                        except Exception as e:
                            print("Error callback: " + str(e))

                    self.picload.addCallback(safe_callback)
                    self.picload.startDecode(final_path)
                else:
                    print("Invalid or missing image file")

        except Exception as err:
            print("Error selectpic: " + str(err))
            self.picload.startDecode(self.pic)

    def getCover(self, url):
        try:
            temp_path = '/tmp/artist_temp.jpg'
            final_path = '/tmp/artist.jpg'

            with requests.get(url, stream=True, timeout=15) as r:
                r.raise_for_status()
                with open(temp_path, 'wb') as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)

            with Image.open(temp_path) as img:
                img.verify()

            shutil.move(temp_path, final_path)
            return True

        except Exception as e:
            if exists(temp_path):
                remove(temp_path)
            print("Error getCover: " + str(e))
            return False

    def downloadCover(self, title):
        try:
            self.okcoverdown = 'failed'
            clean_title = sub(r'\([^)]*\)', '', title).strip()
            search_query = self.current_artist + " " + clean_title if self.current_artist else clean_title
            itunes_url = 'https://itunes.apple.com/search?term=' + quote(search_query) + '&entity=album&limit=1'
            res = requests.get(itunes_url, timeout=10)
            data = res.json()
            if data.get('resultCount', 0) == 0:
                # Fallback to song search
                itunes_url = 'https://itunes.apple.com/search?term=' + quote(search_query) + '&entity=song&limit=1'
                res = requests.get(itunes_url, timeout=10)
                data = res.json()

            if data.get('resultCount', 0) > 0:
                artwork_url = data['results'][0].get('artworkUrl100', '')
                if artwork_url:
                    artwork_url = artwork_url.replace('100x100bb', '600x600bb')
                    if self.getCover(artwork_url):
                        self.okcoverdown = 'success'
        except Exception as e:
            print("Error download: " + str(e))

    def openTest(self):
        self.timer = eTimer()
        try:
            self.timer_conn = self.timer.timeout.connect(self.loadPlaylist)
        except:
            self.timer.callback.append(self.loadPlaylist)
        self.timer.start(250, True)

    def loadPlaylist(self):
        try:
            self.names = []
            self.urls = []
            display_name = ''
            page_url = ''
            stream_url = ''
            current_song = ''
            listeners = ''
            format = ''
            description = ''
            djs = ''

            print("DEBUG: Calling titlesong2 with API URL: " + str(self.api_url))
            data = titlesong2(self.api_url)

            if "error" in data:
                print("Error: " + data["error"])
                self.okcoverdown = 'failed'
                return

            if "stream_url" in data:
                if "display_name" in data:
                    display_name = str(data["display_name"])

                if "page_url" in data:
                    page_url = str(data["page_url"])
                    print('page_url = ' + page_url)

                if "stream_url" in data:
                    stream_url = str(data["stream_url"])
                    print('stream_url = ' + stream_url)

                if "current_song" in data.get("api_urls", {}):
                    urla = data["api_urls"]["current_song"]
                    self.backing = str(urla)
                    print('url song = ' + self.backing)
                    current_song_data = titlesong2(urla)
                    if "error" in current_song_data:
                        print('Error getting song: ' + current_song_data["error"])
                        current_song = _("Error retrieving song")
                    else:
                        current_song = current_song_data.get("title", _("Unknown Title"))
                        print('current_song = ' + current_song)

                        if hasattr(self, 'last_song'):
                            if self.last_song != current_song:
                                self.downloadCover(current_song)
                                self.selectpic()
                        else:
                            self.downloadCover(current_song)
                            self.selectpic()

                        self.last_song = current_song

                if "listeners" in data.get("api_urls", {}):
                    urlb = str(data["api_urls"]["listeners"])
                    print("Type of data listeners: " + str(type(urlb)))
                    listeners = self.listener(urlb)
                    print('listeners = ' + str(listeners))

                if "format" in data:
                    format = str(data["format"])
                    print('format = ' + format)

                if "description" in data:
                    description = str(data["description"])

                if "djs" in data:
                    djs = str(data["djs"])
                    print('djs = ' + djs)

                self['current_song'].setText(str(current_song))
                self['listeners'].setText(_('Online: ') + str(listeners))
                self['format'].setText(_(format))
                self['description'].setText(_(description))
                self['djs'].setText(_('Dj: ') + str(djs))

                self.names.append(display_name)
                self.urls.append(stream_url)

            self.countdown()
            print('current_song = ' + current_song)
            self['info'].setText(_('Select and Play'))
            self['key_green'].show()
            showlist(self.names, self['list'])

        except Exception as e:
            print("Error loadPlaylist: " + str(e))
            import traceback
            traceback.print_exc()
            self.okcoverdown = 'failed'

    def countdown(self):
        try:
            if not self.backing:
                print("No URLs set for songs")
                return

            data = titlesong(self.backing)
            if "error" in data:
                print("API Error: " + data["error"])
                return

            current_id = data['artist'] + "-" + data['title']
            if self.last_song_id != current_id:
                self['current_song'].setText(data["comeback"])
                self.downloadCover(data['artist'] + " " + data['title'])
                self.selectpic()
                self.last_song_id = current_id

            remaining = data["duration"] - (time() - self.song_start_time)
            if remaining > 0:
                self.cover_timer.start(int(remaining * 1000), False)
            else:
                self.song_start_time = time()
                self.cover_timer.start(1000, False)

        except Exception as e:
            print("Error countdown: " + str(e))

    def openTest2(self):
        print('duration mmm: ' + str(self.duration))
        print(type(self.duration))
        if self.duration > 0:
            duration_seconds = int(self.duration)
            print("Timer in sec: " + str(duration_seconds))
            self.timer = eTimer()
            try:
                self.timer_conn = self.timer.timeout.connect(self.countdown)
            except:
                self.timer.callback.append(self.countdown)
            self.timer.start(duration_seconds * 1000, False)

    def openPlay(self):
        idx = self["list"].getSelectionIndex()
        if idx is None:
            return
        self.showback2()
        name = self.names[idx]
        url = self.urls[idx]
        if self.is_playing:
            self.stop()
            return
        try:
            if self.player == "2":
                self.session.open(Playstream2, name, self.stream_url)
            else:
                url = self.stream_url.replace(":", "%3a").replace(" ", "%20")
                if self.player == "3":
                    ref = "4097:0:1:0:0:0:0:0:0:0:" + str(url)
                else:
                    ref = "4097:0:2:0:0:0:0:0:0:0:" + str(url)

                print("Final reference: " + ref)
                sref = eServiceReference(ref)
                sref.setName(name)
                self.session.nav.stopService()
                self.session.nav.playService(sref)
                self.is_playing = True
                self.countdown()
                self.update_timer.start(1000, False)
        except Exception as e:
            print("Error during playback: " + str(e))

    def listener(self, urlx):
        content = None
        try:
            referer = "https://laut.fm"
            raw = Utils.ReadUrl2(urlx, referer)
            content = json_loads(raw)
        except Exception as e:
            print("err: " + str(e))
        return content

    def cancel(self):
        self.stop()
        self.close()

    def stop(self, text=""):
        if self.is_playing:
            self.timer.stop()
            try:
                self["back"].instance.hide()
                self.is_playing = False
                self.session.nav.stopService()
                self.session.nav.playService(self.srefOld)
                self.cover_timer.stop()
            except TypeError:
                self.cover_timer.stop()
                self.close()
            aspect_manager.restore_aspect()


class Playstream2(Screen, InfoBarMenu, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarShowHide):
    STATE_PLAYING = 1
    STATE_PAUSED = 2

    def __init__(self, session, name, url):
        Screen.__init__(self, session)
        self.skinName = 'MoviePlayer'
        self.sref = None
        InfoBarMenu.__init__(self)
        InfoBarNotifications.__init__(self)
        InfoBarBase.__init__(self)
        InfoBarShowHide.__init__(self)
        try:
            self.init_aspect = int(self.getAspect())
        except:
            self.init_aspect = 0
        self.new_aspect = self.init_aspect
        self['actions'] = ActionMap(
            [
                'WizardActions',
                'MoviePlayerActions',
                'EPGSelectActions',
                'MediaPlayerSeekActions',
                'ColorActions',
                'InfobarShowHideActions',
                'InfobarSeekActions',
                'InfobarActions'
            ],
            {
                'leavePlayer': self.stop,
                'back': self.stop,
                'playpauseService': self.playpauseService,
            },
            -1
        )
        self.allowPiP = False
        self.is_playing = False
        InfoBarSeek.__init__(self, actionmap='MediaPlayerSeekActions')
        self.icount = 0
        self.name = name
        self.url = url
        self.state = self.STATE_PLAYING
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.openPlay)
        return

    def __onStop(self):
        self.stop()

    def openPlay(self):
        if self.is_playing:
            self.stop()
        try:
            url = self.url.replace(':', '%3a').replace(' ', '%20')
            ref = '4097:0:2:0:0:0:0:0:0:0:' + str(url)  # radio
            print('final reference:   ' + ref)
            sref = eServiceReference(ref)
            sref.setName(self.name)
            self.session.nav.stopService()
            self.session.nav.playService(sref)
            self.is_playing = True
        except Exception as e:
            print("Error openPlay: " + str(e))

    def stop(self, text=''):
        if self.is_playing:
            try:
                self.is_playing = False
                self.session.nav.stopService()
                self.session.nav.playService(self.srefOld)
                self.exit()
            except TypeError as e:
                print(str(e))
                self.exit()

    def exit(self):
        aspect_manager.restore_aspect
        self.close()

    def playpauseService(self):
        if self.state == self.STATE_PLAYING:
            self.pause()
            self.state = self.STATE_PAUSED
        elif self.state == self.STATE_PAUSED:
            self.unpause()
            self.state = self.STATE_PLAYING

    def pause(self):
        self.session.nav.pause(True)

    def unpause(self):
        self.session.nav.pause(False)

    def keyLeft(self):
        self['text'].left()

    def keyRight(self):
        self['text'].right()

    def keyNumberGlobal(self, number):
        self['text'].number(number)


def main(session, **kwargs):
    global _session
    _session = session
    session.open(radiom1)


def Plugins(**kwargs):
    return PluginDescriptor(
        name="RadioM",
        description="RadioM from around the world V. " + currversion,
        where=PluginDescriptor.WHERE_PLUGINMENU,
        icon="plugin.png",
        fnc=main
    )
