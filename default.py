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
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))
  
def playVideo(url, title):
  
  u = lrt.getVideoStreamURL(url)
  
  if not u:
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

print path
print params
print mode
  
if mode == None:
  build_main_directory()
elif mode == 1:
  playVideo(url, title)
