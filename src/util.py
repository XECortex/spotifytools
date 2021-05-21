import colors
import socket
import sys
import os
import psutil
import dbus
import urllib
import requests
import re

from datetime import datetime
from subprocess import check_output
from bs4 import BeautifulSoup


def get_timestamp():
    return datetime.now().strftime('%H:%M:%S')


class Logger():
    def hidebug(msg):
        pass # print(f'{get_timestamp()}: {colors.BOLD + colors.BLACK}DEBUG{colors.RESET + colors.BLACK}: {msg}{colors.RESET}')

    def debug(msg):
        print(f'{get_timestamp()}: {colors.BOLD + colors.BRIGHT_BLACK}DEBUG{colors.RESET}: {msg}{colors.RESET}')

    def info(msg):
        print(f'{get_timestamp()}: {colors.BOLD + colors.BLUE}INFO{colors.RESET}: {msg}{colors.RESET}')

    def warn(msg):
        print(f'{get_timestamp()}: {colors.BOLD + colors.YELLOW}WARN{colors.RESET}: {msg}{colors.RESET}')

    def error(msg):
        print(f'{get_timestamp()}: {colors.BOLD + colors.BRIGHT_RED}ERROR{colors.RESET}: {msg}{colors.RESET}')


# Check if another instance is already running
def get_lock():
    get_lock._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    try:
        get_lock._lock_socket.bind('\0spotifytools')
    except socket.error:
        Logger.error('Another instance is already running')
        sys.exit(1)


def get_dirname(file_path):
    return os.path.dirname(os.path.realpath(file_path))


def process_running(name):
    # Iterate over all running processes
    for proc in psutil.process_iter():
        try:
            if name.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return False


def launch_spotify():
    Logger.info('Launching Spotify')
    # Launch Spotify without any console logging and disown the process
    os.system('spotify >/dev/null 2>&1 &')


def spotify_pactl(mute):
    # Mute all Spotify-players
    # List sink-inputs
    sink_list = check_output(['pactl', 'list', 'sink-inputs']).splitlines()
    current_id = 0

    # Iterate over the lines of the output
    for line in sink_list:
        line = str(line.decode())

        # Mute Spotify
        if line.startswith('Sink Input #'):
            current_id = line[12:]
        elif line.endswith('binary = "spotify"'):
            Logger.hidebug(f'{"Muting" if mute else "Unmuting"} sink-input #{current_id}')
            os.system(f'pactl set-sink-input-mute "{current_id}" {"1" if mute else "0"}')


def get_spotify_metadata():
    metadata = {}

    # If Spotify is running, this will return the metadata of the currently playing track,
    # else, it will return that Spotify is NOT running
    try:
        raw = dbus.Interface(dbus.SessionBus().get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2'), 'org.freedesktop.DBus.Properties').Get('org.mpris.MediaPlayer2.Player', 'Metadata')

        metadata['trackid'] = raw['mpris:trackid'] or 'spotify:tack:0000000000000000000000'
        metadata['url'] = raw['xesam:url'] or 'https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC'
        metadata['title'] = raw['xesam:title'] or 'Unknown'
        metadata['artist'] = raw['xesam:artist'] if raw['xesam:artist'][0] else ['Unknown']
        metadata['album'] = raw['xesam:album'] or 'Unknown'
        metadata['cover'] = raw['mpris:artUrl'].replace('open.spotify.com', 'i.scdn.co') or f'{get_dirname(__file__)}/assets/default_cover.png'
        metadata['length'] = raw['mpris:length'] or 0000000

        # Detect if Spotify is playing an ad
        metadata['is_ad'] = metadata['trackid'].startswith('spotify:ad')
        metadata['running'] = True

        return metadata
    except Exception:
        return { 'running': False }


def spotify_player():
    return dbus.Interface(dbus.SessionBus().get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2'), 'org.mpris.MediaPlayer2.Player')


def get_playback_status():
    try:
        return dbus.Interface(dbus.SessionBus().get_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2'), 'org.freedesktop.DBus.Properties').Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
    except Exception:
        return 'Paused'


def human_readable_size(size, decimal_places = 1):
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if size < 1024.0 or unit == 'PiB':
            break
        size /= 1024.0
    return f'{size:.{decimal_places}f} {unit}'


def get_dir_size(path):
    return sum(os.path.getsize(os.path.join(path, f)) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))


def google_lyrics(query):
    # Search a song with Google to get its lyrics
    Logger.info(f'Searching lyrics for "{query}"...')

    url = f'http://www.google.com/search?q={urllib.parse.quote(query)}%20lyrics'
    result = requests.get(url, headers={ 'User-agent': 'python', 'Accept-Language': 'en-US, en;q=0.8, *;q=0.7', 'Connection': 'keep-alive' }).text

    # Dissamble the HTML to get the content of the lyric box
    soup = BeautifulSoup(result, 'lxml')
    lyrics = re.sub('</?(?:div|span).*?>', '', str(soup.select_one('div.hwc div div.BNeawe.tAd8D.AP7Wnd')), flags=re.MULTILINE)

    return (lyrics if lyrics != 'None' else 'No lyrics available')
