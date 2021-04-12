
import threading
import time
import gi
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
        
        metadata = util.get_spotify_metadata()
        old_metadata = metadata
        update_timout = False
        mute_update = 0
        mute_update_delta = 1
        
        
        def _update():
            if metadata['running']:
                if f'{metadata["title"]} {metadata["artist"][0]}' == 'Unknown Unknown': return
            else: util.spotify_pactl(False)
                
            print(f'\n\n[INFO] {time.strftime("%H:%M:%S", time.localtime())} Song metadata updated\n')
                
            if self.window_open: self.queue.put(metadata)
            
            update_timout = False
        
        
        while getattr(threading.currentThread(), 'running', True):
            metadata = util.get_spotify_metadata()
            
            # If the playing song changed
            if metadata != old_metadata:
                mute_update_delta = 1
                                
                if update_timout: update_timout.cancel()
                
                update_timout = threading.Timer(0.2, _update)                
                old_metadata = metadata
                
                update_timout.start()
            
            if self.request_update:
                self.request_update = False
                
                _update()
            
            if metadata['running'] and time.time() - mute_update > mute_update_delta / 100 and mute_update_delta <= 64:
                mute_update_delta *= 2
                mute_update = time.time()
                
                util.spotify_pactl(metadata['is_ad'])