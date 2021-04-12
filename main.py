#!/usr/bin/env python3

import gi
import requests

gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk, Notify
from app import App


VERSION = '1.1'

if __name__ == '__main__':
    print('[INFO] Checking version')
    Notify.init('SpotifyTools')
    
    # Version check
    up_version = requests.get('https://raw.githubusercontent.com/XECortex/spotifytools/main/version').text
    
    # Show a desktop notification if a new version is available
    if VERSION != up_version:
        print(f'[WARN] Not up to date, current version: {VERSION}, up version: {up_version}')
        Notify.Notification.new('Update', f'A new version of SpotifyTools is available on GitHub, check out\n<tt>https://github.com/XECortex/spotifytools</tt>\n\n<i>Current version: {VERSION} -> {up_version}</i>', 'system-software-update').show()
    
    # Run the App
    app = App()

    app.open_main_window('playing')
    Gtk.main()