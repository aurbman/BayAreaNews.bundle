#
	#
		# BAY AREA NEWS CHANNELS FOR PLEX
		# VERSION 1.0 | 11/03/2017
		# Forked from https://github.com/kitsuneDEV/HawaiiNews.bundle
	#
#

import requests


NAME 			= 'BAY AREA NEWS'
PREFIX 			= '/video/BayAreaNews'
CHANNELS 		= 'http://projects.kitsune.work/aTV/HNC/channels.json'
ALERTS 			= 'http://projects.kitsune.work/aTV/HNC/alerts.json'

ICON 			= 'icon-default.png'
ART    			= 'art-default.jpg'

Dict['channels'] = [{
	"name":    "KTVU",
	"url":     "http://dcs-live.apis.anvato.net/server/play/10r3b2gtagOkUyAg/1926000/prog.m3u8?x=2830&anv_user=d5ff81654d8e261a04875be29288004030556&fw_ltlg=&fw_sdk_flag=%2Bslcb%2Bvicb&fw_metr=7&_dev=web&fw_did=d5ff81654d8e261a04875be29288004030556&fw_sdk_flag_safe=%252Bslcb%252Bvicb&rdid=unknown&is_lat=1&_tkx_anvack=anvato_epfox_app_web_prod_b3373168e12f423f41504f207000188daf88251b&_tkx_callsign=c100014&t=1509643180&X-Anvato-Adst-Auth=IpqeobEhHOpE9QJz3wnQCPkE+bvqAABDmzFXidklEgdecDfZKWxKnldD2NRAMLPr&_shost=176160788&_fp=6f881b24ba922386f2c34573ea20865f&anvsid=i176160788-n9e8e3860-e3c8-42cb-8493-4a8c2f57c50d&anv=1509643400338&X-Anvato-Adst-Auth=q3zQ7Ztwi6NOdJgV03sCpUrsCNbWhrAescsqxh5XQoU6U5TayB46CGyJujsfX6Y2",
	"thumb":   "",
	"art":     "",
	"summary": "KTVU Fox News"
}]

Dict['alerts'] = []


def Start():
	ObjectContainer.title1 	= NAME
	ObjectContainer.art 	= R(ART)
	DirectoryObject.art 	= R(ART)
	VideoClipObject.art 	= R(ART)

	HTTP.CacheTime = 1
	HTTP.ClearCache()

	# Dict.Reset()

	# load_JSON()

####################################################################################

@handler(PREFIX, NAME, ICON)
def MainMenu():

	oc = ObjectContainer(no_cache=True)

	# USER PREFS
	user_local 	= Prefs['user_local']
	force_HD 	= Prefs['force_HD']

	for item in Dict['channels']:
		title 	= unicode(item['name'])
		thumb 	= item.get('thumb', 'na')
		art 	= item.get('art', 'na')
		url 	= item['url']

	# ADD EACH CHANNEL
		oc.add(CreateVideoClipObject(
			url = item['url'],
			title = '⁍ ' + unicode(item['name']),
			thumb = R(item['thumb']),
			art = R(item['art']),
			summary = unicode(item['summary'])
		))

	# ADD WEATHER/TRAFFIC/INFO BUTTONS
	for itemI in Dict['alerts']:
		oc.add(DirectoryObject(
			key=Callback(showModal, title=unicode(itemI['name']), summary=unicode(itemI['summary'])),
			title = '• ' + unicode(itemI['name']),
			thumb = R(itemI['thumb']),
			art = R(itemI['art']),
			summary = unicode(itemI['summary'])
		))

	# LASTELY ADD REFRESH BUTTON
	# oc.add(DirectoryObject(
	# 	key=Callback(load_JSON),
	# 	title='UPDATE CHANNELS', thumb=R('icon-REFRESH.png'), summary=''
	# 	))

	oc.add(PrefsObject(title='Settings'))
	return oc

####################################################################################

@route(PREFIX + '/stream')
def CreateVideoClipObject(url, title, thumb, art, summary,
						  c_audio_codec = None, c_video_codec = None,
						  c_container = None, c_protocol = None,
						  optimized_for_streaming = True,
						  include_container = False, *args, **kwargs):

	vco = VideoClipObject(
		key = Callback(CreateVideoClipObject,
					   url = url, title = title, thumb = thumb, art = art, summary = summary,
					   optimized_for_streaming = True, include_container = True),
		rating_key = url,
		title = title,
		thumb = thumb,
		art = art,
		summary = summary,
		#url = url,
		items = [
			MediaObject(
				parts = [
					PartObject(
						key = HTTPLiveStreamURL(url = url)
					)
				],
				optimized_for_streaming = True
			)
		]
	)

	if include_container:
		return ObjectContainer(objects = [vco], no_cache=True)
	else:
		return vco

####################################################################################

@route(PREFIX+'/load_data')
def load_JSON():
	HTTP.ClearCache()

	ID 		= HTTP.Request('https://plex.tv/pms/:/ip').content
	RNG 	= HTTP.Request('http://projects.kitsune.work/aTV/HNC/ping.php?ID='+str(ID)).content

	# LOAD CHANNELS JSON
	# IF HD?
	try:
		dataChannels = JSON.ObjectFromString(HTTP.Request(CHANNELS+'?v='+RNG, cacheTime = 1).content)
	except Exception:
		Log("HNC :: Unable to load [channels] JSON.")
	else:
		Dict['channels'] = dataChannels

	# LOAD ALERTS JSON
	try:
		dataAlerts = JSON.ObjectFromString(HTTP.Request(ALERTS+'?v='+RNG, cacheTime = 1).content)
	except Exception:
		Log("HNC :: Unable to load [alerts] JSON.")
	else:
		Dict['alerts'] = dataAlerts
	return MainMenu()

####################################################################################

def returnMain():
	return MainMenu()

####################################################################################

@route(PREFIX+'/modal')
def showModal(title, summary):
	return ObjectContainer(header=title, message=summary)
