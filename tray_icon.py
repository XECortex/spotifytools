
import gi
import util

gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')

from gi.repository import AppIndicator3
from gi.repository import Gtk


APPINDICATOR_ID = 'spotifytools-tray'


class TrayIcon():
    def __init__(self, app):
        self.app = app
        
        # Create the system tray icon
        self.indicator = AppIndicator3.Indicator.new(APPINDICATOR_ID, 'audio-card', AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)
        
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self._build_tray_menu())
    
    
    def _build_tray_menu(self):
        # Build the system tray menu from the glade file
        builder = Gtk.Builder()
        handlers = {
            'open': self._open_main_window,
            'open_lyrics': self._open_lyrics,
            'open_preferences': self._open_preferences,
            'launch_spotify': self._launch_spotify,
            'quit': self._quit
        }
        
        builder.add_from_file('assets/glade/tray_menu.glade')
        builder.connect_signals(handlers)
        
        menu = builder.get_object('tray_menu')
        menu.show_all()
        
        return menu

    
    def _open_main_window(self, menu_item):
        self.app.open_main_window('playing')
    
    
    def _open_lyrics(self, menu_item):
        self.app.open_main_window('lyrics')
    
    
    def _open_preferences(self, menu_item):
        self.app.open_main_window('preferences')
    
    
    def _launch_spotify(self, menu_item):
        util.launch_spotify()
    
    
    def _quit(self, menu_item):
        self.app.main_quit()