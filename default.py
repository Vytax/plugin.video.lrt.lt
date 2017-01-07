#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import urllib

import xbmcgui
import xbmcplugin
import xbmcaddon

import liblrt as lrt

settings = xbmcaddon.Addon(id='plugin.video.lrt.lt')

def mediaPath(mfile):
  return os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', mfile )

thumbnails = {}
thumbnails['lrt-televizija'] = mediaPath('LTV1live.jpg')
thumbnails['lrt-kultura'] = mediaPath('LTV2live.jpg')
thumbnails['lrt-lituanica'] = mediaPath('WORLDlive.jpg')
thumbnails['lrt-radijas'] = mediaPath('LRlive.jpg')
thumbnails['lrt-klasika'] = mediaPath('Klasikalive.jpg')
thumbnails['lrt-opus'] = mediaPath('Opuslive.jpg')

def getParameters(parameterString):
  commands = {}
  splitCommands = parameterString[parameterString.find('?') + 1:].split('&')
  for command in splitCommands:
    if (len(command) > 0):
      splitCommand = command.split('=')
      key = splitCommand[0]
      value = splitCommand[1]
      commands[key] = value
  return commands

def build_main_directory():  
  urls = lrt.getLiveURLs()
  
  for url in urls:
    listitem = xbmcgui.ListItem(url['name'])
    listitem.setProperty('IsPlayable', 'true')
    
    contentType = url['contentType']
    
    info = {}
    if contentType == 'video':
      info = { 'plot': 'Dabar rodoma: ' + url['nowPlaying'] }
    else:
      info = { 'title': url['name'], 'plot': 'Dabar grojama: ' + url['nowPlaying'] }
      
    listitem.setInfo(type = 'video', infoLabels = info )
      
    channel = url['url'].split('/')[-1]
    if channel in thumbnails:
      listitem.setThumbnailImage(thumbnails[channel])
      
    u = {}
    u['mode'] = 1
    u['url'] = url['url']
    u['title'] = url['name']
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?' + urllib.urlencode(u), listitem = listitem, isFolder = False, totalItems = 0)
  
  listitem = xbmcgui.ListItem("[ Mediateka ]")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=2', listitem = listitem, isFolder = True, totalItems = 0)
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def build_mediateka_directory():
  listitem = xbmcgui.ListItem("Naujienų reportažai")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=3', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Naujausi įrašai")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=4', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Populiariausi įrašai")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=5', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Laidos")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=6', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem("Grojaraščiai")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=9', listitem = listitem, isFolder = True, totalItems = 0)  
  
  listitem = xbmcgui.ListItem("Vaikams")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=12', listitem = listitem, isFolder = True, totalItems = 0)  
  
  listitem = xbmcgui.ListItem("Paieška")
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=8', listitem = listitem, isFolder = True, totalItems = 0)
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def build_media_list(mode, **args):
  
  data = {}
  
  searchKey = None
  if 'searchKey' in args:
    searchKey = args['searchKey']
  
  if mode == 3:
    data = lrt.getLatestNews(args['startRow']) 
  elif mode == 4:
    data = lrt.getLatestVideos(args['startRow'])
  elif mode == 5:
    data = lrt.getPopularVideos(args['startRow'])
  elif mode == 7:
    data = lrt.getTVShowVideos(args['mediaId'], args['startRow'])
  elif mode == 8:
    if not searchKey:
      dialog = xbmcgui.Dialog()
      searchKey = dialog.input('Vaizdo įrašo paieška', type=xbmcgui.INPUT_ALPHANUM)
    data = lrt.getSearchVideos(searchKey, args['startRow'])
  elif mode == 11:
    data = lrt.getPlaylist(args['mediaId'])
  elif mode == 14:
    data = lrt.getKidsVideoList(args['age'], args['mediaId'], args['startRow'])
    
  if data:
    tvList = data['data']
    
    for tv in tvList:
      listitem = xbmcgui.ListItem(tv['title'])
      listitem.setProperty('IsPlayable', 'true')
      
      info = { 'title': tv['title'], 'plot': tv['plot'], 'genre': tv['genre'] }
      
      if 'aired' in tv:
        info['aired'] = tv['aired']

      if 'duration' in tv:	
	if tv['duration']:
	  if hasattr(listitem, 'addStreamInfo'):
	    listitem.addStreamInfo('video', { 'duration': tv['duration'] })
	  else:
	    info['duration'] = tv['duration']          
  
      listitem.setInfo(type = 'video', infoLabels = info )
      
      listitem.setThumbnailImage(tv['thumbnailURL'])
      
      url = ''
      
      if 'type' in tv:
        if tv['type'] == 'youtube':
          url = 'plugin://plugin.video.youtube/play/?video_id=' + tv['youtubeID']
      
      else:
        u = {}
        u['mode'] = 1
        u['url'] = tv['url']
        u['title'] = tv['title']
        url = sys.argv[0] + '?' + urllib.urlencode(u)
      
      xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url=url, listitem = listitem, isFolder = False, totalItems = 0)
    
    page = int(data['startRow'] / lrt.VIDEOS_COUNT_PER_PAGE) + 1
    pageCount = int( (data['totalRows'] - 1) / lrt.VIDEOS_COUNT_PER_PAGE) + 1
    
    if page < pageCount:
      listitem = xbmcgui.ListItem('[Daugiau...] (%d/%d)' % (page, pageCount))
      listitem.setProperty('IsPlayable', 'false')
      u = {}
      u['mode'] = mode
      u['startRow'] = args['startRow'] + lrt.VIDEOS_COUNT_PER_PAGE
      
      if args['mediaId']:
	u['mediaId'] = args['mediaId']
	
      if searchKey:
	u['searchKey'] = searchKey
	
      if 'age' in args:
        u['url'] = args['age']
	
      xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?' + urllib.urlencode(u), listitem = listitem, isFolder = True, totalItems = 0)
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(503)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def build_tv_shows_list():
  
  tvList = lrt.getTVShowsList()
  
  for tv in tvList:
    listitem = xbmcgui.ListItem(tv['title'])
    listitem.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=7&mediaId=' + tv['id'], listitem = listitem, isFolder = True, totalItems = 0)
    
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))
  
def build_playlists_groups_list():
  
  tvList = lrt.getPlaylistsGroups()
  
  for tv in tvList:
    listitem = xbmcgui.ListItem(tv['title'])
    listitem.setProperty('IsPlayable', 'false')    
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=10&mediaId=' + str(tv['id']), listitem = listitem, isFolder = True, totalItems = 0)
    
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))
  
def build_playlists_list(mediaId):
  
  tvList = lrt.getPlaylists(mediaId)
  
  for tv in tvList:
    listitem = xbmcgui.ListItem(tv['title'])
    listitem.setProperty('IsPlayable', 'false')
    listitem.setInfo(type = 'video', infoLabels = {'date': tv['date']})
    listitem.setThumbnailImage(tv['thumbnailURL'])
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=11&mediaId=' + str(tv['id']), listitem = listitem, isFolder = True, totalItems = 0)
    
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))
  
def build_kids_age_list():
  
  tvList = lrt.getKidsAgeGroups()
  
  for tv in tvList:
    listitem = xbmcgui.ListItem(tv['title'])
    listitem.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=13&url=' + tv['id'], listitem = listitem, isFolder = True, totalItems = 0)
    
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))
  
def build_kids_cat_list(age, cat=None):
  
  tvList = lrt.getKidsCategory(age, cat)
  
  if not tvList:
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    return
  
  for tv in tvList:
    listitem = xbmcgui.ListItem(tv['title'])
    listitem.setProperty('IsPlayable', 'false')
    listitem.setThumbnailImage(tv['thumbnailURL'])
    mode = '13'
    if tv['type'] == 'list':
      mode = '14'
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=' + mode + '&mediaId=' + str(tv['id']) + '&url=' + age, listitem = listitem, isFolder = True, totalItems = 0)
    
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def playVideo(url, title):
  
  u = lrt.getVideoStreamURL(url)
  
  if not u:
    dialog = xbmcgui.Dialog()
    ok = dialog.ok( "LRT" , 'Nepavyko paleisti vaizdo įrašo!' )
    return
    
  listitem = xbmcgui.ListItem(label = title)
  listitem.setPath(u['url'])
  listitem.setThumbnailImage(u['image'])
  xbmcplugin.setResolvedUrl(handle = int(sys.argv[1]), succeeded = True, listitem = listitem)	


# **************** main ****************

path = sys.argv[0]
params = getParameters(sys.argv[2])
mode = None
url = None
title = None
mediaId = None
startRow = 0
searchKey = None

try:
	url = urllib.unquote_plus(params["url"])
except:
	pass
      
try:
	mode = int(params["mode"])
except:
	pass
      
try:
	title = urllib.unquote_plus(params["title"])
except:
	pass

try:
	mediaId = int(params["mediaId"])
except:
	pass
      
try:
	startRow = int(params["startRow"])
except:
	pass
      
try:
	searchKey = urllib.unquote_plus(params["searchKey"])
except:
	pass

if mode == None:
  build_main_directory()
elif mode == 1:
  playVideo(url, title)
elif mode == 2:
  build_mediateka_directory()
elif mode in [3, 4, 5, 7, 8, 11]:
  build_media_list(mode, mediaId=mediaId, startRow=startRow, searchKey=searchKey)
elif mode == 6:
  build_tv_shows_list()
elif mode == 9:
  build_playlists_groups_list()
elif mode == 10:
  build_playlists_list(mediaId)
elif mode == 12:
  build_kids_age_list()
elif mode == 13:
  build_kids_cat_list(url, mediaId)
elif mode == 14:
  build_media_list(mode, startRow=startRow, mediaId=mediaId, age=url) 
    