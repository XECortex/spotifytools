
import threading
import gi
import time
import util

gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk, Notify
from queue import Queue
from tray_icon import TrayIcon
from main_window import MainWindow


class App():
    def __init__(self):
        self.window_open = False
        self.request_update = False
        self.queue = Queue()
        
        # Create the system tray icon
        self.tray_icon = TrayIcon(self)
        
        # Start the main thread
        self.main_thread = threading.Thread(target=self._main, daemon=True)
        
        self.main_thread.start()
    
    
    def main_quit(self):
        print('[INFO] Stopping main thread')
        
        # Stop the main thread, unmute Spotify and quit
        Gtk.main_quit()
        
        self.main_thread.running = False
        
        self.main_thread.join()
        util.spotify_pactl(False)
    
    
    def open_main_window(self, page):
        print(f'[INFO] Opening main window on stack page "{page}"')
        
        # Open the main window
        if not self.window_open: self.main_window = MainWindow(self, page)
        else: self.main_window.switch_page(page)
    
    
    def _main(self):
        print('[INFO] Started main thread')
        
        thread = threading.currentThread()
        old_metadata = util.get_spotify_metadata()
        tmp = old_metadata
        
        while getattr(thread, 'running', True):
            metadata = util.get_spotify_metadata()
            
            # If the playing song changed
            if metadata == old_metadata:
                last_change = time.time()
            
            if time.time() - last_change > 0.1 or self.request_update:
                if metadata['running'] and f'{metadata["title"]} {metadata["artist"][0]}' == 'Unknown Unknown': continue
                
                print('[INFO] Song metadata updated')
                
                if self.window_open: self.queue.put(metadata)
                
                old_metadata = metadata
                self.request_update = False
            
            # Mute Spotify if an ad is playing
            # TODO: Time this
            if metadata['running']: util.spotify_pactl(metadata['is_ad'])
            else: util.spotify_pactl(False)