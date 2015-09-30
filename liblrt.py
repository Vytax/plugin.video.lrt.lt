#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import urllib
import sys

LRT_URL = 'http://www.lrt.lt/'
reload(sys) 
sys.setdefaultencoding('utf8')

def htmlUnescape(txt):
  if sys.version_info < (3, 0):
    import HTMLParser
    return HTMLParser.HTMLParser().unescape(txt)
  
  if sys.version_info < (3, 4):
    import html.parser    
    return html.parser.HTMLParser().unescape(txt)
  
  import html
  return html.unescape(txt)
  

def getURL(url):
  
  res = urllib.urlopen(url)
  return res.read()

def getLiveURLs():
  
  html = getURL(LRT_URL); 
  aside = re.findall('<aside class="right-off-canvas-menu">(.*?)</aside>', html, re.DOTALL)
  
  if not aside: 
    print "Error: getLiveURLs"
    return  
  
  li_items = re.findall('<li.*?>(.*?)</li>', aside[0], re.DOTALL)
  
  liveURLs = []
  
  for li_item in li_items:
    
    liveURL = {}
    
    link = re.findall('<a class="now-channel-link.*?" href="(.*?)">', li_item, re.DOTALL)
    if not link:
      continue
    
    liveURL['url'] = LRT_URL + link[0]
    
    name = re.findall('<span class="channelName">(.*?)</span>', li_item, re.DOTALL)    
    if name:
      liveURL['name'] = htmlUnescape(name[0]).replace('·','').strip()

    now = re.findall('<span class="now">(.*?)</span>', li_item, re.DOTALL)
    if now:
      liveURL['nowPlaying'] = now[0].strip()
      
    contentType = re.findall('<span class="(video|audio)"></span>', li_item, re.DOTALL)
    if contentType:
      liveURL['contentType'] = contentType[0]
    
    if liveURL:
      liveURLs.append(liveURL)
  
  return liveURLs

def getVideoStreamURL(url):
  result = {}
  
  html = getURL(url)
  
  source = re.findall('sources: \[\{"file":"(.*?)"', html, re.DOTALL)
  
  if source:
    result['url'] = source[0].replace('\/','/')
    
  image = re.findall('image: "(.*?)"', html, re.DOTALL)
  if image:
    result['image'] = LRT_URL + image[0]
  
  return result

def test1():
  print 'getLiveURLs():'  
  urls = getLiveURLs()  
  
  if not urls:
    print 'Failed!'
    
  for url in urls:
    print 'Name: ' + url['name']
    print 'Now Playing: ' + url['nowPlaying']
    print 'URL: ' + url['url']
    print 'Type: ' + url['contentType']
    print '-------'    
    

def test2():
  print "getVideoStreamURL()" 
  urls = getLiveURLs()  
  
  if not urls:
    print 'Failed!'
    
  for url in urls:
    u = getVideoStreamURL(url['url'])
    print "url: " + u['url']
    print "image: " + u['image']
    print '-------'   

if __name__ == '__main__':
  test2()