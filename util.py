
import os
import dbus
import urllib
import requests
import re

from datetime import datetime
from bs4 import BeautifulSoup
from subprocess import check_output


def get_timestamp(): return datetime.now().strftime('%H:%M:%S.%f')
def get_dirname(file_path): return os.path.dirname(os.path.realpath(file_path))
def spotify_player(): return dbus.Interface(dbus.SessionBus().get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2'), 'org.mpris.MediaPlayer2.Player')


class Logger():
	def hidebug(msg): print(f'\033[34m{get_timestamp()}\033[0m: \033[30;1mHIDEBUG\033[0;30m: {msg}\033[0m')
	# def hidebug(msg): pass
	def debug(msg): print(f'\033[34m{get_timestamp()}\033[0m: \033[90;1mDEBUG\033[0;90m: {msg}\033[0m')
	def info(msg): print(f'\033[34m{get_timestamp()}\033[0m: \033[1mINFO\033[0m: {msg}')
	def warn(msg): print(f'\033[34m{get_timestamp()}\033[0m: \033[33;1mWARN\033[0;33m: {msg}\033[0m')
	def error(msg): print(f'\033[34m{get_timestamp()}\033[0m: \033[91;1mERROR\033[0;91m: {msg}\033[0m')


def launch_spotify():
	Logger.info('Launching Spotify')
	# Launch Spotify without any console logging and disown the process
	os.system('spotify >/dev/null 2>&1 & disown')


def get_spotify_metadata():
	metadata = {}

	# If Spotify is running, this will return the metadata of the currently playing track,
	# else, it will return that Spotufy is NOT running
	try:
		raw = dbus.Interface(dbus.SessionBus().get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2'), 'org.freedesktop.DBus.Properties').Get('org.mpris.MediaPlayer2.Player', 'Metadata')

		metadata['trackid'] = raw['mpris:trackid'] or 'spotify:tack:0000000000000000000000'
		metadata['url'] = raw['xesam:url'] or 'https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC'
		metadata['title'] = raw['xesam:title'] or 'Unknown'
		metadata['artist'] = raw['xesam:artist'] if raw['xesam:artist'][0] else ['Unknown']
		metadata['album'] = raw['xesam:album'] or 'Unknown'
		metadata['cover'] = raw['mpris:artUrl'].replace('open.spotify.com', 'i.scdn.co') or f'{get_dirname(__file__)}/assets/cover.png'
		metadata['length'] = raw['mpris:length'] or 0000000

		# Detect if Spotify is playing an ad
		metadata['is_ad'] = metadata['trackid'].startswith('spotify:ad')
		metadata['running'] = True

		return metadata
	except Exception:
		return { 'running': False }


def get_playback_status():
	try: return dbus.Interface(dbus.SessionBus().get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2'), 'org.freedesktop.DBus.Properties').Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
	except: return 'Paused'


def google_lyrics(query):
	# Search a song with Google to get its lyrics
	Logger.info(f'Searching lyrics for "{query}"...')

	url = f'http://www.google.com/search?q={urllib.parse.quote(query)}%20lyrics'
	result = requests.get(url, headers={ 'User-agent': 'python', 'Accept-Language': 'en-US, en;q=0.8, *;q=0.7', 'Connection': 'keep-alive' }).text

	# Dissamble the HTML to get the content of the lyric box
	soup = BeautifulSoup(result, 'lxml')
	lyrics = re.sub('</?(?:div|span).*?>', '', str(soup.select_one('div.hwc div div.BNeawe.tAd8D.AP7Wnd')), flags=re.MULTILINE)

	return (lyrics if lyrics != 'None' else 'No lyrics available')


def spotify_pactl(mute):
	# Mute all Spotify-players
	# List sink-inputs
	sink_list = check_output(['pactl', 'list', 'sink-inputs']).splitlines()
	current_id = 0

	# Iterate over the lines of the output
	for line in sink_list:
		line = str(line.decode())

		# Mute Spotify
		if line.startswith('Sink Input #'): current_id = line[12:]
		elif line.endswith('binary = "spotify"'):
			Logger.hidebug(f'{"Muting" if mute else "Unmuting"} sink-input #{current_id}')
			os.system(f'pactl set-sink-input-mute "{current_id}" {"1" if mute else "0"}')
