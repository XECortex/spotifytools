
import gi
import util

gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')

from gi.repository import AppIndicator3, Gtk


class TrayIcon():
    def __init__(self, app):
        self.app = app

        # Create the system tray icon
        self.indicator = AppIndicator3.Indicator.new('spotifytools-tray', self.app.config.values['tray_icon'], AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)

        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self._build_tray_menu())


    def _build_tray_menu(self):
        # Build the system tray menu from the glade file
        builder = Gtk.Builder()
        handlers = {
            'open': lambda menu_item: self.app.open_main_window('playing'),
            'open_lyrics': lambda menu_item: self.app.open_main_window('lyrics'),
            'open_preferences': lambda menu_item: self.app.open_main_window('preferences'),
            'launch_spotify': lambda menu_item: util.launch_spotify(),
            'quit': lambda menu_item: self.app.main_quit(),
        }

        builder.add_from_file(f'{util.get_dirname(__file__)}/assets/glade/tray_menu.glade')
        builder.connect_signals(handlers)

        # Fallback icon for 'spotify-indicator'
        if not Gtk.IconTheme.get_default().has_icon('spotify-indicator'):
            builder.get_object('spotify-indicator').set_from_icon_name('media-optical', Gtk.IconSize.BUTTON)

        menu = builder.get_object('tray_menu')
        menu.show_all()

        return menu
