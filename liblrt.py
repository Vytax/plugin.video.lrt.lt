#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import urllib
import urllib2
import sys

import simplejson as json

from StringIO import StringIO
import gzip

from HTMLParser import HTMLParser
htmlParser = HTMLParser()

LRT_URL = 'http://www.lrt.lt/'
VIDEOS_COUNT_PER_PAGE = 100 
LATEST_NEWS_URL = LRT_URL + 'data-service/module/mediaNews/callback/top_media/startRow/%d/limit/' + str(VIDEOS_COUNT_PER_PAGE)
LATEST_VIDEOS_URL = LRT_URL + 'data-service/module/media/callback/latest_media/startRow/%d/order/dateZ/limit/' + str(VIDEOS_COUNT_PER_PAGE)
POPULAR_VIDEOS_URL = LRT_URL + 'data-service/module/media/callback/popular_media/startRow/%d/order/viewsZ/date/7/limit/' + str(VIDEOS_COUNT_PER_PAGE)
TVSHOW_VIDEOS_URL = LRT_URL + 'data-service/module/media/callback/popular_media/program/%d/startRow/%d/limit/' + str(VIDEOS_COUNT_PER_PAGE)
SEARCH_VIDEOS_URL = LRT_URL + 'data-service/module/media/callback/popular_media/order/dateZ/content/%s/startRow/%d/limit/' + str(VIDEOS_COUNT_PER_PAGE)
PLAYLISTS_URL = LRT_URL + 'data-service/module/play/callback/playlists_%d/category/%d/enable/true/count/0/limit/' + str(VIDEOS_COUNT_PER_PAGE)
PLAYLIST_URL = LRT_URL
PLAYLISTSGROUPS_URL = LRT_URL + 'mediateka/grojarasciai'
KIDS_VIDEOS_URL = LRT_URL + 'data-service/module/kids/callback/load_media/category/%s/age/%s/startRow/%d/limit/' + str(VIDEOS_COUNT_PER_PAGE)

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
  
  request = urllib2.Request(url)
  request.add_header('Accept-encoding', 'gzip')
  response = urllib2.urlopen(request)
  if response.info().get('Content-Encoding') == 'gzip':
    buf = StringIO(response.read())
    f = gzip.GzipFile(fileobj=buf)
    return f.read()  
  
  return response.read()

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
  
  source = re.sub(re.compile('\n[\s]*(\/\/[^\n]*)', re.DOTALL), '', source[0])
  
  url_hash = url.split('#', 1)
  if len(url_hash) == 2:
    url_hash = url_hash[1]
  else:
    url_hash = '';
  
  source = re.sub(re.compile('("[\+\s]*location.hash.substring\(1\))', re.DOTALL), url_hash + '"', source)
  source = source.replace('"file"', 'file')      
 
  mfile = re.findall('file[:\s]*"(.*?)"' ,source, re.DOTALL)
  
  result['url'] = mfile[0].replace('\/','/')
    
  image = re.findall('image: "(.*?)"', html, re.DOTALL)
  if image:
    result['image'] = LRT_URL + image[0]
  
  return result

def str_duration_to_int(duration):
  if not duration:
    return 0
  
  parts = duration.split(':')
  if not parts:
    return 0
  
  return int(parts[0])*3600+int(parts[1])*60+int(parts[2])

def getLatestNews(startRow=0):
  
  json = getLRTJSON(LATEST_NEWS_URL % startRow)
  
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
    
    d['thumbnailURL'] = LRT_URL + 'mimages/News/images/' + str(data['newsId']) + '/500/280/size16x9'
    d['url'] = LRT_URL + 'mediateka/irasas/' + str(data['id']) + '/lrt#wowzaplaystart=' + str(data['start']) + '&wowzaplayduration=' + str(data['end'])
    
    dataList.append(d)
    
  result['data'] = dataList
  
  return result

def getLatestVideos(startRow=0):
  
  json = getLRTJSON(LATEST_VIDEOS_URL % startRow)
  return parseStandartJSON(json)

def getPopularVideos(startRow=0):
  
  json = getLRTJSON(POPULAR_VIDEOS_URL % startRow)
  return parseStandartJSON(json)

def getTVShowVideos(mediaId, startRow=0):
  
  json = getLRTJSON(TVSHOW_VIDEOS_URL % (mediaId, startRow))  
  return parseStandartJSON(json)

def getSearchVideos(key, startRow=0):

  json = getLRTJSON(SEARCH_VIDEOS_URL % (urllib.quote(key.encode("utf-8")), startRow))
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
      
    #d['duration'] = str_duration_to_int(data['end']) - str_duration_to_int(data['start'])
    
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

def getPlaylistsGroups():
  
  html = getURL(PLAYLISTSGROUPS_URL)
  items = re.findall('<div class="blockTop blockTopSimple beforefilter">(.*?)</div>', html, re.DOTALL)
  
  tvList = []
  
  for i, item in enumerate(items):
    tvList.append({'id': i+1, 'title': item })
    
  return tvList

def getPlaylists(mediaId, startRow=0):
  
  json = getLRTJSON(PLAYLISTS_URL % (mediaId, mediaId))

  if not json:
    return []

  tvList = []
  for item in json['data']:
    
    tv = {}
    tv['id'] = item['id']
    tv['title'] = item['title']
    tv['date'] = item['date']
    tv['thumbnailURL'] = LRT_URL + 'mimages/PlayList/items/' + str(item['id']) + '/500/280'
    
    tvList.append(tv)
    
  return tvList

def getPlaylist(mediaId):
  
  html = getURL(LRT_URL + 'mediateka/grojarasciai/id/' + str(mediaId))
  
  items = re.findall('<div class="playlist-scroll">.*?</div>', html, re.DOTALL)
  if not items:
    return []

  tvList = []

  items = re.findall('<img class="pl-rec-img" src="http://www.lrt.lt/mimages/Media/items/(\d+)/240/135/"  alt="([^"]*)"/>', items[0], re.DOTALL)
  for i, title in items:
    tv = {}
    tv['title'] = title
    tv['url'] = LRT_URL + 'mediateka/irasas/' + i
    tv['thumbnailURL'] = LRT_URL + 'mimages/Media/items/' + i + '/500/280'
    tv['plot'] = ''
    tv['genre'] = ''
    tvList.append(tv)
    
  return {'data': tvList, 'startRow': 1, 'totalRows': 1}
    
def getKidsAgeGroups():
  
  html = getURL(LRT_URL + 'vaikams')
  
  items = re.findall('<a class="[^"]*" href="http://www.lrt.lt/vaikams/([^"]*)"><br>([^<]*)</a>', html, re.DOTALL)
  if not items:
    return []
  
  tvList = []
  
  for i, item in enumerate(items):
    tv = {}
    tv['title'] = item[1]
    tv['id'] = '%d:%s' % (i+1, item[0])
    tvList.append(tv)
  
  return tvList

def getKidsCategory(age, cat=None):
  
  age = age.split(':')
  
  url = LRT_URL + 'vaikams/' + age[1]
  
  if cat:
    cat = str(cat)
    url = url + '/' + cat
  
  html = getURL(url)
  
  jsonData = re.findall('GLOBAL\.kidsCategories = (\{.*?)</script>', html, re.DOTALL)
  if not jsonData:
    return None
  
  data = json.loads(jsonData[0])  
  
  parents = []
  for i in data.keys():
    v = data[i]
    if v['parent']:
      parents.append(v['parent'])
  
  items = []
  for i in data.keys():
    v = data[i]
    if v['parent'] == cat and age[0] in v['age']:
      tv = {}
      tv['title'] = v['name']
      tv['id'] = int(v['id'])
      tv['thumbnailURL'] = LRT_URL + v['image']
      if v['id'] in parents:
        tv['type'] = 'cat'
      else:
        tv['type'] = 'list'
      items.append(tv)
  
  return items

def getKidsVideoList(age, cat, startRow=0):
  
  if not cat or not age:
    return None
  
  age = age.split(':')
  
  jsonData = getLRTJSON(KIDS_VIDEOS_URL % (cat, age[0], startRow))
  
  if not jsonData:
    return None
  
  result = {}
  result['startRow'] = jsonData['startRow']
  result['endRow'] = jsonData['endRow']
  result['totalRows'] = jsonData['totalRows']
  
  dataList = []
  
  for data in jsonData['data']:
    d = {}
    
    d['title'] = data['title']
    
    if data['content']:
      d['plot'] = htmlParser.unescape(data['content']).replace('\t','').strip()
    else:
      d['plot'] = ''      
      
    if data['date']:
      d['aired'] = data['date']
      
    d['genre'] = ''    
    
    dataType = int(data['type'])
    
    if dataType == 3:
      
      img = data['image']
      
      yid = re.findall('http:\/\/img\.youtube\.com\/vi\/([^\/]*)\/', img)      
      if yid:
        yid = yid[0]
      else:
        continue
      
      d['type'] = 'youtube'
      d['youtubeID'] = yid
      d['thumbnailURL'] = img
      
    elif dataType == 4:
      
      d['thumbnailURL'] = LRT_URL + data['image']
    
      d['url'] = LRT_URL + 'vaikams/%s/%s/%s' % (age[1], cat, data['id'])
    
    else:
      continue
      
    dataList.append(d)
  
  result['data'] = dataList
  
  return result
  
