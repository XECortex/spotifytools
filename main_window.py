
import gi
import os
import threading
import requests
import util

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from pathlib import Path
from gi.repository import Gtk, GLib, Gio, GdkPixbuf, Pango
from gi.repository import AppIndicator3


class MainWindow():
    def __init__(self, app, page):
        self.lyrics_searched = False
        self.app = app
        self.app.window_open = True
        
        self._build_window()        
        self.switch_page(page)
        
        # Start the window main thread
        self.window_main_thread = threading.Thread(target=self._window_main, daemon=True)
        
        self.app.request_update = True
        self.window_main_thread.start()
    
    
    def switch_page(self, page):
        if not page in ['playing', 'lyrics', 'preferences']:
            print(f'[WARN] Invalid page name "{page}"')
            return
        
        self.builder.get_object('content').set_visible_child_name(page)
        
        # Focus the lyric search box
        if page == 'lyrics':
            self.builder.get_object('lyric_search').grab_focus()
    
    
    def _build_window(self):
        print('[INFO] Building main window')
        
        # Build the window from the glade file
        self.builder = Gtk.Builder()
        handlers = {
            'destroy': lambda window: threading.Thread(target=self._destroy, args={ window }).start(),
            'launch_spotify': lambda button: threading.Thread(target=self._launch_spotify, args={ button }).start(),
            'search_lyrics': lambda entry: threading.Thread(target=self._search_lyrics, args={ entry }).start(),
            'spotify_lyrics': lambda button: threading.Thread(target=self._spotify_lyrics, args={ button }).start()
        }
        
        self.builder.add_from_file('assets/glade/main_window.glade')
        self.builder.connect_signals(handlers)
        
        self.builder.get_object('window').show_all()
        self.builder.get_object('icon').set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file('assets/icons/spotifytools.svg').scale_simple(22, 22, 1))
    
    
    def _window_main(self):
        # Run while the window is opened
        print('[INFO] Started window thread')
        thread = threading.currentThread()

        while getattr(thread, 'running', True):
            # Wait for data in the queue
            if self.app.queue.empty():
                continue
            
            self.metadata = self.app.queue.get_nowait()

            # If Spotify is running
            if self.metadata['running']:
                # Reveal the info bar if an ad is palying
                GLib.idle_add(self.builder.get_object('ad_playing_info').set_revealed, self.metadata['is_ad'])
                
                # Update the song info
                GLib.idle_add(self.builder.get_object('not_running').hide)
                GLib.idle_add(self.builder.get_object('playing').show)
                GLib.idle_add(self.builder.get_object('playing_info').set_markup, f'<big>{GLib.markup_escape_text(self.metadata["title"])}</big>\n{GLib.markup_escape_text(", ".join(self.metadata["artist"]))}\n{GLib.markup_escape_text(self.metadata["album"])}')
                
                # Update the cover image and lyrics
                threading.Thread(target=self._set_cover, args={ self.metadata['cover'] }).start()
                
                if not self.lyrics_searched:                
                    threading.Thread(target=self._update_lyrics).start()
                else:
                    GLib.idle_add(self.builder.get_object('spotify_lyrics_button').set_sensitive, True)
            else:
                GLib.idle_add(self.builder.get_object('ad_playing_info').set_revealed, False)
                GLib.idle_add(self.builder.get_object('playing').hide)
                GLib.idle_add(self.builder.get_object('not_running').show)
                GLib.idle_add(self.builder.get_object('spotify_lyrics_button').set_sensitive, False)
    
    
    def _set_cover(self, url):
        if url.startswith('https://'):
            cover_cache = str(Path.home()) + '/.cache/spotifytools/covers'
        
            if not os.path.isdir(cover_cache):
                print(f'[INFO] Attempting to create cache directory "{cover_cache}"')
                os.makedirs(cover_cache)
        
            if not os.path.isfile(cover_cache + f'/{url[24:]}.png'):
                print(f'[INFO] Downloading cover from "{url}"')

                response = requests.get(url)

                f = open(cover_cache + f'/{url[24:]}.png', 'wb')
                f.write(response.content)
                f.close()
            else:
                print(f'[INFO] Loading cached cover from "{cover_cache}/{url[24:]}.png"')
            
            cover_path = cover_cache + f'/{url[24:]}.png'
        else:
            cover_path = url
        
        GLib.idle_add(self.builder.get_object('cover').set_from_pixbuf, GdkPixbuf.Pixbuf.new_from_file(cover_path).scale_simple(100, 100, 1))
    
    
    def _update_lyrics(self, query=False):
        GLib.idle_add(self.builder.get_object('spotify_lyrics_button').set_sensitive, self.lyrics_searched and self.metadata['running'])
        
        if query == False:
            if self.metadata['running']:
                query = f'{self.metadata["title"]} {self.metadata["artist"][0]}'
            else:
                return
        
        GLib.idle_add(self.builder.get_object('lyrics_info').hide)
        GLib.idle_add(self.builder.get_object('lyric_view').hide)
        GLib.idle_add(self.builder.get_object('no_lyrics_available').hide)
        GLib.idle_add(self.builder.get_object('lyrics_loading').show)
        GLib.idle_add(self.builder.get_object('lyrics_loading').start)
        
        text = util.google_lyrics(query)
        
        GLib.idle_add(self.builder.get_object('lyrics_loading').stop)
        GLib.idle_add(self.builder.get_object('lyrics_loading').hide)
        
        if text == 'No lyrics available':
            GLib.idle_add(self.builder.get_object('no_lyrics_available').show)
        else:
            GLib.idle_add(self.builder.get_object('lyrics_info').show)
            
            if self.lyrics_searched:
                GLib.idle_add(self.builder.get_object('lyrics_info').set_markup, f'<big>{GLib.markup_escape_text(query)}</big>')
            else:
                GLib.idle_add(self.builder.get_object('lyrics_info').set_markup, f'<big>{GLib.markup_escape_text(self.metadata["title"])}</big>\n{GLib.markup_escape_text(self.metadata["artist"][0])}')
            
            textbuffer = self.builder.get_object('lyrics').get_buffer()
            
            GLib.idle_add(self.builder.get_object('lyric_view').show)
            GLib.idle_add(textbuffer.set_text, text)
    
    
    def _destroy(self, window):
        print('[INFO] Stopping window thread')
        
        self.window_main_thread.running = False
        
        self.window_main_thread.join()
        
        self.app.window_open = False
        del self.app.main_window
    
    
    def _launch_spotify(self, button):
        util.launch_spotify()
    
    
    def _search_lyrics(self, entry):
        self.lyrics_searched = True
        
        self._update_lyrics(entry.get_text())
        GLib.idle_add(entry.set_text, '')
    
    
    def _spotify_lyrics(self, button):
        self.lyrics_searched = False
        
        self._update_lyrics()