#!/usr/bin/python3

import gi
import util
import requests
import sys

gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')

from gi.repository import Notify, Gtk
from config import Config
from app import App

if __name__ == '__main__':
    util.get_lock()

    # Load the configuration
    config = Config()

    # Version check
    util.Logger.info('Checking version')
    Notify.init('SpotifyTools')

    with open(f'{util.get_dirname(__file__)}/version', 'r') as version_file:
        version = version_file.read() or '0.0.0'

    up_version = requests.get('https://raw.githubusercontent.com/XECortex/spotifytools/main/version').text

    # Show a desktop notification if a new version is available
    if version != up_version:
        util.Logger.warn(f'Not up to date, current version: {version}, up version: {up_version}')
        Notify.Notification.new('SpotifyTools update available', f'<i>Current version: {version}\nNew version: {up_version}</i>\n\nDownload at\n<tt>https://github.com/XECortex/spotifytools</tt>', 'system-software-update').show()

    # Run the App
    try:
        if config.values['launch_spotify'] and not util.process_running('spotify'):
            util.launch_spotify()

        app = App(config)

        if not config.values['hide_window']:
            app.open_main_window('playing')

        Gtk.main()
    except KeyboardInterrupt:
        print('')
        util.Logger.error('Stopping (KeyboardInterrupt)')
        app.main_quit()

    sys.exit(1)