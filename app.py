
import gi
import threading
import util
import time

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from queue import Queue
from tray_icon import TrayIcon
from main_window import MainWindow


class App():
	def __init__(self, config):
		self.config = config
		self.window_open = False
		self.request_update = False
		self.queue = Queue()

		# Create the system tray icon
		self.tray_icon = TrayIcon(self)

		# Start the main thread
		self.main_thread = threading.Thread(target=self._main, daemon=True)

		self.main_thread.start()


	def main_quit(self):
		# Stop the main thread, unmute Spotify and quit
		util.Logger.info('Stopping main thread')
		Gtk.main_quit()
		self.config.stop_file_watcher()

		self.main_thread.running = False

		self.main_thread.join()
		util.spotify_pactl(False)


	def open_main_window(self, page):
		util.Logger.info(f'Opening main window on stack page "{page}"')

		# Open the main window
		if not self.window_open: self.main_window = MainWindow(self, page, self.config)
		else: self.main_window.switch_page(page)


	def _main(self):
		util.Logger.info('Started main thread')

		metadata = util.get_spotify_metadata()
		old_metadata = metadata
		update_timout = False
		mute_update = 0
		mute_update_delta = 1


		def _update(requested=False):
			if metadata['running']:
				if f'{metadata["title"]} {metadata["artist"][0]}' == 'Unknown Unknown' and not requested: return
			else: util.spotify_pactl(False)

			util.Logger.debug('Song metadata updated')
			util.Logger.hidebug(metadata)

			if self.window_open: self.queue.put(metadata)


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

				if update_timout: update_timout.cancel()

				update_timout = threading.Timer(0.2, _update)
				old_metadata = metadata

				update_timout.start()

			if self.request_update:
				self.request_update = False

				_update(True)

			if metadata['running'] and time.time() - mute_update > mute_update_delta / 100 and (mute_update_delta <= 64 or mute_update_delta == 200):
				if mute_update_delta == 200: mute_update_delta = 1

				mute_update_delta *= 2
				mute_update = time.time()

				util.spotify_pactl(metadata['is_ad'])