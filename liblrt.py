#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import urllib
import sys

import simplejson as json

LRT_URL = 'http://www.lrt.lt/'
VIDEOS_COUNT_PER_PAGE = 100 
LATEST_NEWS_URL = LRT_URL + 'data-service/module/mediaNews/callback/top_media/limit/' + str(VIDEOS_COUNT_PER_PAGE)
LATEST_VIDEOS_URL = LRT_URL + 'data-service/module/media/callback/latest_media/order/dateZ/limit/' + str(VIDEOS_COUNT_PER_PAGE)
POPULAR_VIDEOS_URL = LRT_URL + 'data-service/module/media/callback/popular_media/order/viewsZ/date/7/limit/' + str(VIDEOS_COUNT_PER_PAGE)
TVSHOW_VIDEOS_URL = LRT_URL + 'data-service/module/media/callback/popular_media/program/%d/limit/' + str(VIDEOS_COUNT_PER_PAGE)
SEARCH_VIDEOS_URL = LRT_URL + 'data-service/module/media/callback/popular_media/order/dateZ/content/%s/limit/' + str(VIDEOS_COUNT_PER_PAGE)

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
  html = html.replace('"+(md.device == \'mobile\'?\'640/360\':\'870/490\')', '/500/280/size16x9"')
  
  source = re.findall('sources: [\[\s]*\{([^\}]*)\}', html, re.DOTALL)
  
  if not source:
    return result  
  
  source = re.sub('\n[\s]*(\/\/[^\n]*)' ,'' ,source[0], 0, re.DOTALL)
  
  url_hash = url.split('#', 1)
  if len(url_hash) == 2:
    url_hash = url_hash[1]
  else:
    url_hash = '';
  
  source = re.sub('("[\+\s]*location.hash.substring\(1\))', url_hash + '"', source, 0, re.DOTALL)
  source = source.replace('"file"', 'file')      
 
  mfile = re.findall('file[:\s]*"(.*?)"' ,source, re.DOTALL)
  
  result['url'] = mfile[0].replace('\/','/')
    
  image = re.findall('image: "(.*?)"', html, re.DOTALL)
  if image:
    result['image'] = LRT_URL + image[0]
  
  return result

def str_duration_to_int(duration):
  
  parts = duration.split(':')
  if not parts:
    return 0
  
  return int(parts[0])*3600+int(parts[1])*60+int(parts[2])

def getLatestNews():
  
  json = getLRTJSON(LATEST_NEWS_URL)
  
  result = {}
  result['startRow'] = json['startRow']
  result['endRow'] = json['endRow']
  result['totalRows'] = json['totalRows']
  
  dataList = []
  
  for data in json['data']:
    d = {}
    d['title'] = data['title']
    
    if data['content']:
      d['plot'] = data['content'].replace('\t','').strip()
    else:
      d['plot'] = ''
      
    if data['category']:
      d['genre'] = data['category']
    else:
      d['genre'] = ''
      
    if data['date']:
      d['aired'] = data['date']  
    
    if 'length' in data:
	d['duration'] = str_duration_to_int(data['length'])
    
    d['thumbnailURL'] = LRT_URL + '/mimages/News/images/' + str(data['newsId']) + '/500/280/size16x9'
    d['url'] = LRT_URL + 'mediateka/irasas/' + str(data['id']) + '/lrt#wowzaplaystart=' + str(data['start']) + '&wowzaplayduration=' + str(data['end'])
    
    dataList.append(d)
    
  result['data'] = dataList
  
  return result

def getLatestVideos():
  
  json = getLRTJSON(LATEST_VIDEOS_URL)
  return parseStandartJSON(json)

def getPopularVideos():
  
  json = getLRTJSON(POPULAR_VIDEOS_URL)
  return parseStandartJSON(json)

def getTVShowVideos(mediaId):
  
  json = getLRTJSON(TVSHOW_VIDEOS_URL % mediaId)  
  return parseStandartJSON(json)

def getSearchVideos(key):

  json = getLRTJSON(SEARCH_VIDEOS_URL % urllib.quote(key.encode("utf-8")))
  return parseStandartJSON(json)

def parseStandartJSON(json):
  result = {}
  result['startRow'] = json['startRow']
  result['endRow'] = json['endRow']
  result['totalRows'] = json['totalRows']
  
  dataList = []
  
  for data in json['data']:
    d = {}
    
    d['title'] = data['title']
    
    if data['content']:
      d['plot'] = data['content'].replace('\t','').strip()
    else:
      d['plot'] = ''
      
    if data['category']:
      d['genre'] = data['category']
    else:
      d['genre'] = ''
      
    if data['date']:
      d['aired'] = data['date']
      
    d['duration'] = str_duration_to_int(data['end']) - str_duration_to_int(data['start'])
    
    d['thumbnailURL'] = LRT_URL + '/mimages/Media/items/' + str(data['id']) + '/500/280'
    
    d['url'] = LRT_URL + 'mediateka/irasas/' + str(data['id']) + '/lrt'
    
    dataList.append(d)
  
  result['data'] = dataList
  
  return result

def getLRTJSON(url):

  jsonData = getURL(url)
  response = json.loads(jsonData)['response']
  
  if not response:
    return False
  
  data = response['data']
  
  if not data:
    return False
  
  return response

def getTVShowsList():
  
  html = getURL(LRT_URL + 'mediateka/irasai')
  
  tvList = []
  
  select = re.findall('<select id="show"[^>]*>(.*?)</select>', html, re.DOTALL)
  items = re.findall('<option value="(\d{2,10})">(.*?)</option>', select[0], re.DOTALL)
  for item in items:
    show = {'id': item[0], 'title': item[1]}
    tvList.append(show)
    
  return tvList

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

def test3():
  print "test3()"
  getLatestNews()
  
def test4():
  print "test4()"
  getVideoStreamURL('http://www.lrt.lt/mediateka/irasas/84760/lrt#wowzaplaystart=695000&wowzaplayduration=187000')
  getVideoStreamURL('http://www.lrt.lt/mediateka/tiesiogiai/lrt-televizija')

def test5():
  print "test5()"
  print getTVShowsList()

if __name__ == '__main__':
  test5()