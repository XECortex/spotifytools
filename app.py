
import threading
import gi
import util

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from queue import Queue
from tray_icon import TrayIcon
from main_window import MainWindow


class App():
    def __init__(self):
        self.window_open = False
        self.queue = Queue()
        
        # Create the system tray icon
        self.tray_icon = TrayIcon(self)
        
        # Start the main thread
        self.main_thread = threading.Thread(target=self._main, daemon=True)
        
        self.main_thread.start()
    
    
    def main_quit(self):
        print('[INFO] Stopping main thread')
        
        # Stop the main threaad, unmute Spotify and quit        
        util.spotify_pactl(False)
        Gtk.main_quit()
        
        self.main_thread.running = False
        
        self.main_thread.join()
    
    
    def open_main_window(self, page):
        print(f'[INFO] Opening main window on stack page "{page}"')
        
        if not self.window_open:
            # Open the main window
            self.main_window = MainWindow(self, page)
        else:
            self.main_window.switch_page(page)
    
    
    def _main(self):
        print('[INFO] Started main thread')
        
        thread = threading.currentThread()
        old_metadata = {}

        while getattr(thread, 'running', True):
            metadata = util.get_spotify_metadata()

            # If the playing song changed
            if metadata != old_metadata or self.request_update:
                print('[INFO] Song metadata updated')
                
                if self.window_open:
                    self.queue.put(metadata)
                
                # Mute Spotify if an ad is playing
                if metadata['running']:
                    if metadata['is_ad']:
                        print('[INFO] Advertisement detected')
                    
                    util.spotify_pactl(metadata['is_ad'])
                else:
                    util.spotify_pactl(False)
                
                old_metadata = metadata
                self.request_update = False