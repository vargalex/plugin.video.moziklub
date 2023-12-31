# -*- coding: utf-8 -*-

'''
    dmdamedia Add-on
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


import sys, xbmcgui
from resources.lib.indexers import navigator

if sys.version_info[0] == 3:
    from urllib.parse import parse_qsl
else:
    from urlparse import parse_qsl


params = dict(parse_qsl(sys.argv[2].replace('?','')))

action = params.get('action')

url = params.get('url')

page = params.get('page')

serie = params.get('serie')


if action == None:
    navigator.navigator().getRoot()

elif action == 'sorting':
    navigator.navigator().getSorting(url)

elif action == 'categories':
    navigator.navigator().getCategories()

elif action == 'items':
    navigator.navigator().getItems(url, page)

elif action == 'sources':
    navigator.navigator().getSources(url, serie)

elif action == 'playmovie':
    navigator.navigator().playMovie(url)

elif action == 'search':
    navigator.navigator().getSearches()

elif action == 'historysearch':
    navigator.navigator().getItems(url, 1)

elif action == 'newsearch':
    navigator.navigator().doSearch()

elif action == 'deletesearchhistory':
    navigator.navigator().deleteSearchHistory()

elif action == 'inputStreamSettings':
    import xbmcaddon
    xbmcaddon.Addon(id='inputstream.adaptive').openSettings()
