
import gi
import os
import threading
import util
import webbrowser
import shutil
import requests
import tempfile

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
from datetime import timedelta
from math import floor


class MainWindow():
    def __init__(self, app, page, config):
        self.lyrics_searched = False
        self.app = app
        self.config = config
        self.app.window_open = True
        self.cover_cache = os.path.join(os.getenv('XDG_CACHE_HOME', os.path.expanduser('~/.cache')), 'spotifytools')
        self.tmp_cover_path = False
        self.lyric_update_threads = 0

        self._build_window()
        self.switch_page(page)

        # Start the window main thread
        self.window_main_thread = threading.Thread(target=self._window_main, daemon=True)

        self.app.request_update = True
        self.window_main_thread.start()


    def switch_page(self, page):
        self.builder.get_object('window').present()

        if not page in ['playing', 'lyrics', 'preferences']:
            util.Logger.warn(f'Invalid page name "{page}"')
            return

        self.builder.get_object('content').set_visible_child_name(page)

        # Focus the lyric search box
        if page == 'lyrics':
            self.builder.get_object('lyric_search').grab_focus()


    def _build_window(self):
        util.Logger.debug('Building main window')

        # Build the window from the glade file
        self.builder = Gtk.Builder()
        handlers = {
            # Window
            'destroy': lambda window: self._destroy(),
            'page_change': lambda stack, visible_child: self._page_change(stack, visible_child),

            # Playing
            'launch_spotify': lambda button: util.launch_spotify(),
            'open_cover': lambda event_box, event_button: webbrowser.open(self.metadata['cover'], 0, True),
            'player_previous': lambda button: util.spotify_player().Previous(),
            'player_play_pause': lambda button: self._play_pause(button),
            'player_next': lambda button: util.spotify_player().Next(),
            'copy_song_info': lambda button: Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(f'{self.metadata["title"]}\n{self.metadata["artist"][0]}\n{self.metadata["url"]}', -1),

            # Lyrics
            'search_lyrics': lambda entry: threading.Thread(target=self._search_lyrics, args={ entry }).start(),
            'spotify_lyrics': lambda button: threading.Thread(target=self._spotify_lyrics).start(),

            # Preferences
            'update_preferences_hide_window': lambda switch, state: self.config.update_option('config', 'hide-window', str(state).lower()),
            'update_preferences_launch_spotify': lambda switch, state: self.config.update_option('config', 'launch-spotify', str(state).lower()),
            'update_preferences_cache_covers': lambda switch, state: self.config.update_option('config', 'cache-covers', str(state).lower()),
            'clear_cache': lambda button: self._clear_cache(),
            'update_preferences_tray_icon': lambda file_chooser: self.config.update_option('config', 'tray-icon', file_chooser.get_filename() or '/opt/spotifytools/assets/spotifytools.svg'),
            'about': lambda button: self._show_about_dialog(),
            'quit': lambda button: self.app.main_quit()
        }

        self.builder.add_from_file(f'{util.get_dirname(__file__)}/assets/glade/main_window.glade')

        if self.app.update_available:
            self.builder.get_object('update_info').show()
            self.builder.get_object('content').child_set_property(self.builder.get_object('content').get_child_by_name('preferences'), 'needs_attention', True)

        self.builder.get_object('preferences_hide_window').set_active(self.config.values['hide_window'])
        self.builder.get_object('preferences_launch_spotify').set_active(self.config.values['launch_spotify'])
        self.builder.get_object('preferences_cache_covers').set_active(self.config.values['cache_covers'])

        self.builder.connect_signals(handlers)
        self.builder.get_object('window').show_all()


    def _window_main(self):
        # Run while the window is opened
        util.Logger.debug('Started window thread')

        old_playback_status = 'Paused'
        old_config_changes = 0

        while getattr(threading.currentThread(), 'running', True):
            if self.config.changes != old_config_changes:
                old_config_changes = self.config.changes

                GLib.idle_add(self.builder.get_object('preferences_hide_window').set_active, self.config.values['hide_window'])
                GLib.idle_add(self.builder.get_object('preferences_launch_spotify').set_active, self.config.values['launch_spotify'])
                GLib.idle_add(self.builder.get_object('preferences_cache_covers').set_active, self.config.values['cache_covers'])

                self._update_preferences_cache_size()


            playback_status = util.get_playback_status()

            if old_playback_status != playback_status:
                old_playback_status = playback_status

                self._update_play_pause_indicator()

            # Wait for data in the queue
            if self.app.queue.empty():
                continue

            self.metadata = self.app.queue.get_nowait()

            # If Spotify is running
            if self.metadata['running']:
                # Reveal the info bar if an ad is palying
                GLib.idle_add(self.builder.get_object('ad_playing_info').set_revealed, self.metadata['is_ad'])
                GLib.idle_add(self.builder.get_object('playing_info').set_sensitive, not self.metadata['is_ad'])
                GLib.idle_add(self.builder.get_object('player_previous').set_sensitive, not self.metadata['is_ad'])
                GLib.idle_add(self.builder.get_object('player_next').set_sensitive, not self.metadata['is_ad'])
                GLib.idle_add(self.builder.get_object('copy_song_info').set_sensitive, not self.metadata['is_ad'])

                # Update the song info
                GLib.idle_add(self.builder.get_object('not_running').hide)
                GLib.idle_add(self.builder.get_object('playing').show)
                GLib.idle_add(self.builder.get_object('playing_info').set_markup, f'<big>{GLib.markup_escape_text(self.metadata["title"])}</big>\n<small>by</small> {GLib.markup_escape_text(", ".join(self.metadata["artist"]))}\n<small>on</small> {GLib.markup_escape_text(self.metadata["album"])}')

                track_length = str(timedelta(seconds=floor(self.metadata['length'] / 1e+6)))

                if int(track_length[0:track_length.index(':')]) < 1:
                    track_length = track_length[track_length.index(':') + 1:]

                GLib.idle_add(self.builder.get_object('track_length').set_text, track_length)

                # Update the cover image and lyrics
                threading.Thread(target=self._set_cover, args={ self.metadata['cover'] }).start()

                if not self.lyrics_searched and not self.metadata['is_ad']:
                    threading.Thread(target=self._update_lyrics).start()
                else:
                    GLib.idle_add(self.builder.get_object('spotify_lyrics_button').set_sensitive, True)

                self._update_play_pause_indicator()
            else:
                GLib.idle_add(self.builder.get_object('ad_playing_info').set_revealed, False)
                GLib.idle_add(self.builder.get_object('playing').hide)
                GLib.idle_add(self.builder.get_object('not_running').show)
                GLib.idle_add(self.builder.get_object('spotify_lyrics_button').set_sensitive, False)


    def _destroy(self):
        util.Logger.debug('Stopping window thread')

        self.window_main_thread.running = False

        self.window_main_thread.join()

        self.app.window_open = False
        del self.app.main_window


    def _page_change(self, stack, visible_child):
        pass


    def _play_pause(self, button):
        if util.get_playback_status() == 'Paused':
            util.spotify_player().Play()
        else:
            util.spotify_player().Pause()

        self._update_play_pause_indicator()


    def _search_lyrics(self, entry):
        self.lyrics_searched = True

        self._update_lyrics(entry.get_text())
        GLib.idle_add(entry.set_text, '')


    def _spotify_lyrics(self):
        self.lyrics_searched = False

        self._update_lyrics()


    def _clear_cache(self):
        util.Logger.info('Clearing cache directory')
        shutil.rmtree(self.cover_cache, ignore_errors=True)
        self._update_preferences_cache_size()


    def _show_about_dialog(self):
        # Same as building the main window
        util.Logger.debug('Showing about dialog')

        builder = Gtk.Builder()

        builder.add_from_file(f'{util.get_dirname(__file__)}/assets/glade/about_dialog.glade')

        about_dialog = builder.get_object('about_dialog')

        about_dialog.run()
        about_dialog.destroy()


    def _update_preferences_cache_size(self):
        GLib.idle_add(self.builder.get_object('preferences_cache_size').set_text, util.human_readable_size(util.get_dir_size(self.cover_cache)) if os.path.exists(self.cover_cache) else '0.0 B')


    def _update_play_pause_indicator(self):
        GLib.idle_add(self.builder.get_object('play_pause_indicator').set_from_icon_name, f'media-playback-{"start" if util.get_playback_status() == "Paused" else "pause"}', Gtk.IconSize.BUTTON)


    def _set_cover(self, url):
        delete_tmp_file = False

        try:
            if url.startswith('https://'):
                if self.config.values['cache_covers']:
                    if not os.path.isdir(self.cover_cache):
                        util.Logger.warn(f'Cache directory "{self.cover_cache}" does not exist, attempting to create')
                        os.makedirs(self.cover_cache)

                    cover_path = os.path.join(self.cover_cache, f'{url[24:]}.png')

                    if not os.path.isfile(cover_path):
                        util.Logger.debug(f'Downloading cover from "{url}"')

                        response = requests.get(url)

                        with open(cover_path, 'wb') as f: f.write(response.content)

                        self._update_preferences_cache_size()
                    else:
                        util.Logger.debug(f'Loading cached cover from "{cover_path}"')
                else:
                    util.Logger.debug(f'Downloading cover from "{url}"')

                    delete_tmp_file = True
                    tmp_cover_fd, cover_path = tempfile.mkstemp()
                    response = requests.get(url)

                    with os.fdopen(tmp_cover_fd, 'wb') as tmp: tmp.write(response.content)
            else:
                cover_path = url

            GLib.idle_add(self.builder.get_object('cover').set_from_pixbuf, GdkPixbuf.Pixbuf.new_from_file(cover_path).scale_simple(128, 128, 1))
        finally:
            if delete_tmp_file and os.path.isfile(cover_path): os.unlink(cover_path)


    def _update_lyrics(self, query=False):
        self.lyric_update_threads += 1
        lyric_update_thread_id = self.lyric_update_threads

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

        if self.lyric_update_threads != lyric_update_thread_id:
            return util.Logger.warn('Lyric search cancelled: detected another thread')

        GLib.idle_add(self.builder.get_object('lyrics_loading').stop)
        GLib.idle_add(self.builder.get_object('lyrics_loading').hide)

        if text == 'No lyrics available' or not self.metadata['running'] and not self.lyrics_searched:
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
