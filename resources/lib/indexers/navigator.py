    # -*- coding: utf-8 -*-

'''
    dmdamedia Addon
    Copyright (C) 2020

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import os,sys,re,xbmc,xbmcgui,xbmcplugin,xbmcaddon, time, locale, json
import resolveurl
from resources.lib.modules import client, control
from resources.lib.modules.utils import py2_encode, py2_decode, safeopen
from datetime import date

if sys.version_info[0] == 3:
    import urllib.parse as urlparse
    from urllib.parse import quote_plus
else:   
    import urlparse
    from urllib import quote_plus

sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1])
addonFanart = control.addonInfo('fanart')

base_url = 'https://moziklub.net/'
embed_url = 'https://moziklub.net/ajax/embed'
search_url = 'https://moziklub.net/search/'

class navigator:
    def __init__(self):
        try:
            locale.setlocale(locale.LC_ALL, "hu_HU.UTF-8")
        except:
            try:
                locale.setlocale(locale.LC_ALL, "")
            except:
                pass
        try:
            self.infoPreload = xbmcaddon.Addon().getSettingBool('infopreload')
        except:
            self.infoPreload = xbmcaddon.Addon().getSetting('infopreload').lower() == 'true'
        self.base_path = py2_decode(control.dataPath)
        self.searchFileName = os.path.join(self.base_path, "search.history")

    def getRoot(self):
        content = client.request(base_url)
        navBar = client.parseDOM(content, 'ul', attrs={'class': 'navbar-nav.*?'})[0]
        navItems = client.parseDOM(navBar, 'li', attrs={'class': 'nav-item'})
        self.addDirectoryItem('Keresés', 'search', '', 'DefaultFolder.png')
        for navItem in navItems:
            url = client.parseDOM(navItem, 'a', attrs={'class': 'nav-link'}, ret='href')[0]
            if not 'kerelem' in url:
                title = client.parseDOM(navItem, 'a', attrs={'class': 'nav-link'})[0]
                title = re.search(r".*>(.*)", title, re.S).group(1).strip()
                self.addDirectoryItem(title, 'sorting&url=%s' % url, '', 'DefaultFolder.png')
        self.addDirectoryItem('Kategóriák', 'categories', '', 'DefaultFolder.png')
        self.endDirectory()

    def getSorting(self, url):
        content = client.request(url)
        try:
            formRadio = client.parseDOM(content, 'div', attrs={'class': 'form-radio'})[0]
            labels = client.parseDOM(formRadio, 'label')
            for label in labels:
                name = client.parseDOM(label, 'input', ret = 'name')[0]
                value = client.parseDOM(label, 'input', ret = 'value')[0]
                title = client.parseDOM(label, 'span')[0].strip()
                self.addDirectoryItem(title, 'items&url=%s?%s=%s&page=1' % (url, name, value), '', 'DefaultFolder.png')
            self.endDirectory()
        except:
            self.getItems("%s?" % url, "1")

    def getCategories(self):
        content = client.request(base_url)
        categories = client.parseDOM(content, 'li', attrs={'class': 'col-4'})
        for category in categories:
            url = client.parseDOM(category, 'a', ret = 'href')[0]
            title = client.parseDOM(category, 'a')[0].strip()
            self.addDirectoryItem(title, 'items&url=%s&page=1' % url, '', 'DefaultFolder.png')
        self.endDirectory()

    def getItems(self, url, page):
        if url.startswith(search_url):
            url = "%s%s?" % (search_url, quote_plus(url[len(search_url):]))
        content = client.request("%s&page=%s" % (url, page))
        items = client.parseDOM(content, 'div', attrs={'class': 'col-lg-2'})
        for item in items:
            itemUrl = client.parseDOM(item, 'a', ret = 'href')[0]
            overlay = client.parseDOM(item ,'div', attrs={'class': 'card-overlay'})[0]
            picture = client.parseDOM(overlay, 'picture')[0]
            thumb = client.parseDOM(picture, 'img', ret = 'data-src')[0]
            try:
                imdb = client.parseDOM(item, 'div', attrs={'class': 'card-imdb'})[0]
                imdb = " | [COLOR yellow]IMDB: %s[/COLOR]" % client.parseDOM(imdb, 'div')[0].strip()
            except:
                imdb = ""
            body = client.parseDOM(item, 'div', attrs={'class': 'card-body'})[0]
            ul = client.parseDOM(body, 'ul')[0]
            category = client.parseDOM(ul, 'li')[0].strip()
            year = client.parseDOM(ul, 'li')[1].strip()
            title = client.parseDOM(body, 'h3', attrs={'class': 'title'})[0].strip()
            titleSub = client.parseDOM(body, 'h4', attrs={'class': 'title_sub'})[0]
            sorozat = ""
            if "sorozat" in itemUrl and "sorozatok" not in url:
                sorozat = " | [COLOR blue]Sorozat[/COLOR]"
            self.addDirectoryItem('%s%s | [COLOR green]%s[/COLOR] | [COLOR red]%s[/COLOR]%s' % (title, sorozat, category, year, imdb), 'sources&url=%s' % itemUrl, thumb, 'DefaultMovies.png', isFolder=True, meta={'title': title}, banner=thumb)
        if "%s&page=%d" % (url, int(page)+1) in content:
            self.addDirectoryItem(u'[I]K\u00F6vetkez\u0151 oldal >>[/I]', 'items&url=%s&page=%d' % (url, int(page)+1), '', 'DefaultFolder.png')
        self.endDirectory('movies')

    def getSources(self, url, serie):
        content = client.request(url)
        layoutSection = client.parseDOM(content, 'div', attrs={'class': 'row gx-xl-5'})[0]
        title = client.parseDOM(layoutSection, 'h1', attrs={'class': 'h3.*?'})[0]
        try:
            episode = client.parseDOM(title, 'span')[0].strip()
            title = "%s - %s" % (re.search(r"(.*?)<", title).group(1).strip(), episode)
        except:
            pass
        title = title.strip()
        cardTag = client.parseDOM(layoutSection, 'div', attrs={'class': 'card-tag.*?'})[0]
        category = client.parseDOM(cardTag, 'a')[0].strip()
        colMd = client.parseDOM(layoutSection, 'div', attrs={'class': 'col-md'})[0]
        plot = client.parseDOM(colMd, 'p')[0].strip()
        picture = client.parseDOM(layoutSection, 'picture')[0]
        thumb = client.parseDOM(picture, 'img', ret = 'data-src')[0]
        ul = client.parseDOM(colMd, 'ul')[0]
        try:
            duration = re.search(r".*([0-9]+) óra ([0-9]+) perc", colMd)
            if duration:
                duration = int(duration.group(1))*60*60 + int(duration.group(2))*60
        except:
            duration = 0
        accordionItems = client.parseDOM(layoutSection, 'div', attrs={'class': 'accordion-item'})
        dirType = "movies"
        if accordionItems:
            if serie:
                dirType = "episodes"
                accordionTitle = client.parseDOM(accordionItems[int(serie)], 'div', attrs={'class': 'accordion-header'})[0].strip()
                cardEpisodes = client.parseDOM(accordionItems[int(serie)], 'div', attrs={'class': 'card-episode'})
                for cardEpisode in cardEpisodes:
                    url = client.parseDOM(cardEpisode, 'a', ret = 'href')[0]
                    episodeTitle = client.parseDOM(cardEpisode, 'a')[0].strip()
                    self.addDirectoryItem("%s - %s %s " % (title, accordionTitle, episodeTitle), 'sources&url=%s' % url, thumb, 'DefaultTVShows.png', meta={'title': title, 'duration': duration, 'plot': plot, 'fanart': thumb})
            else:
                dirType = "tvshows"
                for i in range(len(accordionItems)):
                    accordionTitle = client.parseDOM(accordionItems[i], 'div', attrs={'class': 'accordion-header'})[0].strip()
                    self.addDirectoryItem('%s - %s' % (title, accordionTitle), 'sources&url=%s&serie=%d' % (url, i), thumb, 'DefaultTVShows.png', meta={'title': title, 'duration': duration, 'plot': plot, 'fanart': thumb})
        else:
            streams = client.parseDOM(content, 'div', attrs={'class': 'card-stream.*?'})
            for stream in streams:
                dataId = client.parseDOM(stream, 'button', ret = 'data-id')[0]
                iFrame = client.request(embed_url, post="id=%s" % dataId)
                url = client.parseDOM(iFrame, 'iframe', ret = 'data-src')[0]
                host = urlparse.urlparse(url).netloc
                self.addDirectoryItem("%s | [COLOR red]%s[/COLOR]" % (title, host), 'playmovie&url=%s' % url, thumb, 'DefaultMovies.png', isFolder=False, meta={'title': title, 'duration': duration, 'plot': plot, 'fanart': thumb})
        self.endDirectory(type=dirType)


    def getSearches(self):
        self.addDirectoryItem('[COLOR lightgreen]Új keresés[/COLOR]', 'newsearch', '', 'DefaultFolder.png')
        try:
            file = safeopen(self.searchFileName, "r")
            olditems = file.read().splitlines()
            file.close()
            items = list(set(olditems))
            items.sort(key=locale.strxfrm)
            if len(items) != len(olditems):
                file = safeopen(self.searchFileName, "w")
                file.write("\n".join(items))
                file.close()
            for item in items:
                self.addDirectoryItem(item, 'historysearch&url=%s%s' % (search_url, quote_plus(item)), '', 'DefaultFolder.png')
            if len(items) > 0:
                self.addDirectoryItem('[COLOR red]Keresési előzmények törlése[/COLOR]', 'deletesearchhistory', '', 'DefaultFolder.png') 
        except:
            pass   
        self.endDirectory()

    def deleteSearchHistory(self):
        if os.path.exists(self.searchFileName):
            os.remove(self.searchFileName)

    def doSearch(self):
        search_text = self.getText(u'Add meg a keresend\xF5 film c\xEDm\xE9t')
        if search_text != '':
            if not os.path.exists(self.base_path):
                os.mkdir(self.base_path)
            file = safeopen(self.searchFileName, "a")
            file.write("%s\n" % search_text)
            file.close()
            self.getItems("%s%s" % (search_url, search_text), 1)


    def playMovie(self, url):
        try:
            xbmc.log('Moziklub: resolving URL %s with ResolveURL' % url, xbmc.LOGINFO)
            direct_url = resolveurl.resolve(url)
            if direct_url:
                direct_url = py2_encode(direct_url)
            else:
                direct_url = url
        except Exception as e:
            xbmcgui.Dialog().notification(urlparse.urlparse(url).hostname, str(e))
            return
        if direct_url:
            xbmc.log('Moziklub: playing URL: %s' % direct_url, xbmc.LOGINFO)
            play_item = xbmcgui.ListItem(path=direct_url)
            if 'm3u8' in direct_url:
                from inputstreamhelper import Helper
                is_helper = Helper('hls')
                if is_helper.check_inputstream():
                    if sys.version_info < (3, 0):  # if python version < 3 is safe to assume we are running on Kodi 18
                        play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')   # compatible with Kodi 18 API
                    else:
                        play_item.setProperty('inputstream', 'inputstream.adaptive')  # compatible with recent builds Kodi 19 API
                    try:
                        play_item.setProperty('inputstream.adaptive.stream_headers', direct_url.split("|")[1])
                        play_item.setProperty('inputstream.adaptive.manifest_headers', direct_url.split("|")[1])
                    except:
                        pass
                    play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
            xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)

    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True, Fanart=None, meta=None, banner=None):
        url = '%s?action=%s' % (sysaddon, query) if isAction == True else query
        if thumb == '': thumb = icon
        cm = []
        if queue == True: cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
        if not context == None:
            for item in context:
                cm.append((py2_encode(item[0]), 'RunPlugin(%s?action=%s)' % (sysaddon, item[1])))
        item = xbmcgui.ListItem(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb, 'poster': thumb, 'banner': banner})
        if Fanart == None: Fanart = addonFanart
        item.setProperty('Fanart_Image', Fanart)
        if isFolder == False: item.setProperty('IsPlayable', 'true')
        if not meta == None: item.setInfo(type='Video', infoLabels = meta)
        xbmcplugin.addDirectoryItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)


    def endDirectory(self, type='addons'):
        xbmcplugin.setContent(syshandle, type)
        #xbmcplugin.addSortMethod(syshandle, xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.endOfDirectory(syshandle, cacheToDisc=True)

    def getText(self, title, hidden=False):
        search_text = ''
        keyb = xbmc.Keyboard('', title, hidden)
        keyb.doModal()

        if (keyb.isConfirmed()):
            search_text = keyb.getText()

        return search_text
