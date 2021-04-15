#!/usr/bin/env python3

if __name__ == '__main__':
	import gi
	import argparse
	import socket
	import util
	import sys
	import requests

	gi.require_version('Gtk', '3.0')
	gi.require_version('Notify', '0.7')

	from gi.repository import Notify, Gtk
	from app import App

	# Argument parser
	parser = argparse.ArgumentParser(prog='spotifytools', description='A GTK application written in Python that displays song lyrics and mutes Spotify advertisements', epilog='flag names may change in the future')

	# parser.add_argument('-c', '--config', nargs=1, help='use an alternative config file')
	parser.add_argument('-l', '--launch-spotify', action='store_true', help='launch Spotify on program start')
	parser.add_argument('-t', '--tray-only', action='store_true', help='don\'t show the main window on startup, useful if you want to start spotifytools when you log in')

	flags = parser.parse_args()


	# Check if another instance is already running
	def get_lock():
		get_lock._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

		try: get_lock._lock_socket.bind('\0spotifytools')
		except socket.error:
			util.Logger.error('Another instance is already running')
			sys.exit(1)


	get_lock()

	# Version check
	util.Logger.info('Checking version')
	Notify.init('SpotifyTools')

	version = open(f'{util.get_dirname(__file__)}/version').read() or '1.0'
	up_version = requests.get('https://raw.githubusercontent.com/XECortex/spotifytools/main/version').text

	# Show a desktop notification if a new version is available
	if version != up_version:
		util.Logger.warn(f'Not up to date, current version: {version}, up version: {up_version}')
		Notify.Notification.new('Update', f'A new version of SpotifyTools is available on GitHub, check out\n<tt>https://github.com/XECortex/spotifytools</tt>\n\n<i>Current version: {version} -> {up_version}</i>', 'system-software-update').show()

	# Run the App
	if flags.launch_spotify: util.launch_spotify()

	app = App()

	if not flags.tray_only: app.open_main_window('playing')
	Gtk.main()