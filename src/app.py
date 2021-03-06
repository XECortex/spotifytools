
import gi
import threading
import util
import sys
import time
import requests
import os

gi.require_version('Notify', '0.7')
gi.require_version('Gtk', '3.0')

from config import Config
from gi.repository import Notify, Gtk
from queue import Queue
from tray_icon import TrayIcon
from main_window import MainWindow


class App():
    def __init__(self):
        # Version check
        util.get_lock()
        util.Logger.info('Checking version')

        with open(f'{util.get_dirname(__file__)}/version', 'r') as version_file:
            version = version_file.read() or '0.0.0'

            try:
                up_version = requests.get('https://raw.githubusercontent.com/XECortex/spotifytools/main/version').text
            except Exception:
                dialog = Gtk.MessageDialog(flags=0, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.CANCEL, text="Please check your internet connection")

                dialog.format_secondary_text("Error while retrieving version file from GitHub.")
                dialog.run()
                dialog.destroy()

                self.main_quit(pre=True)

            if version != up_version:
                util.Logger.warn(f'Not up to date, current version: {version}, up version: {up_version}')

                Notify.init('SpotifyTools')
                Notify.Notification.new('A new version of SpotifyTools is available!', 'Run “<tt>sudo spotifytools update</tt>“ to download &amp; install the update', 'system-software-update').show()

                self.update_available = True
            else:
                self.update_available = False

        self.config = Config()
        self.window_open = False
        self.request_update = False
        self.queue = Queue()

        # Create the system tray icon
        self.tray_icon = TrayIcon(self)

        # Start the main thread
        self.main_thread = threading.Thread(target=self._main, daemon=True)

        self.main_thread.start()

        if self.config.values['launch_spotify'] and not util.process_running('spotify'):
            util.launch_spotify()

        if not self.config.values['hide_window']:
            self.open_main_window('playing')

    def main_quit(self, pre=False):
        # Stop the main thread, unmute Spotify and quit
        util.Logger.info('Stopping main thread')

        if not pre:
            self.config.stop_file_watcher()
            Gtk.main_quit()

            self.main_thread.running = False

            self.main_thread.join()

        util.spotify_pactl(False)
        sys.exit()

    def open_main_window(self, page):
        util.Logger.info(f'Opening main window on stack page "{page}"')

        # Open the main window
        if not self.window_open:
            self.main_window = MainWindow(self, page, self.config)
        else:
            self.main_window.switch_page(page)

    def _main(self):
        util.Logger.info('Started main thread')

        metadata = util.get_spotify_metadata()
        old_metadata = metadata
        update_timout = False
        mute_update = 0
        mute_update_delta = 1


        def _update(requested=False):
            if metadata['running']:
                if f'{metadata["title"]} {metadata["artist"][0]}' == 'Unknown Unknown' and not requested:
                    return
            else:
                util.spotify_pactl(False)

            util.Logger.debug('Song metadata updated')
            util.Logger.hidebug(metadata)

            if self.window_open:
                self.queue.put(metadata)


        while getattr(threading.currentThread(), 'running', True):
            metadata = util.get_spotify_metadata()

            # If the playing song changed
            if metadata != old_metadata:
                if not mute_update_delta == 200:
                    mute_update_delta = 1

                    if metadata['running'] and old_metadata['running']:
                        if old_metadata['is_ad'] and not metadata['is_ad']:
                            mute_update = time.time()
                            mute_update_delta = 200

                if update_timout:
                    update_timout.cancel()

                update_timout = threading.Timer(0.2, _update)
                old_metadata = metadata

                update_timout.start()

            if self.request_update:
                self.request_update = False

                _update(True)

            if metadata['running'] and time.time() - mute_update > mute_update_delta / 100 and (mute_update_delta <= 64 or mute_update_delta == 200):
                if mute_update_delta == 200:
                    mute_update_delta = 1

                mute_update_delta *= 2
                mute_update = time.time()

                util.spotify_pactl(metadata['is_ad'])