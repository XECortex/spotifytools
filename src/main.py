#!/usr/bin/python3

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from app import App
from util import Logger

if __name__ == '__main__':
    try:
        app = App()

        Gtk.main()
    except KeyboardInterrupt:
        print('')
        Logger.error('Stopping (KeyboardInterrupt)')
        app.main_quit()