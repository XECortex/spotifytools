
import configparser
import os
import util
import sys
import argparse

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from shutil import copy


class ConfigUpdateEventHandler(FileSystemEventHandler):
	def __init__(self, config): self.config = config
	def on_any_event(self, event): self.config.load()



class Config():
	def __init__(self):
		self.values = {}
		self.changes = 0
		self.config = configparser.ConfigParser()
		self.file_watcher = Observer()

		self._parse_args()
		self.load()
		self.file_watcher.schedule(ConfigUpdateEventHandler(self), self.config_dir)
		self.file_watcher.start()


	def load(self):
		# Config dir and config file path
		if self.args.config:
			self.config_path = self.args.config[0]

			if not os.path.isfile(self.config_path):
				util.Logger.error(f'No such file: "{self.config_path}"')
				sys.exit(1)

			self.config_dir = util.get_dirname(self.config_path)
		else:
			self.config_dir = os.path.join(os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config')), 'spotifytools')

			# Create the config dir if it doesn't exist
			if not os.path.isdir(self.config_dir):
				util.Logger.warn(f'Config directory "{self.config_dir}" does not exist, attempting to create')
				os.makedirs(self.config_dir)

			self.config_path = os.path.join(self.config_dir, 'config.ini')

			# Create the config file if it doesn't exist
			if not os.path.isfile(self.config_path):
				util.Logger.warn('Config file doesn\'t exist, attempting to create')
				self._write_config()

		self._read_config()

		self.changes += 1


	def _parse_args(self):
		# Argument parser
		parser = argparse.ArgumentParser(prog='spotifytools', description='A GTK application written in Python that displays song lyrics and mutes Spotify advertisements', epilog='flag names may change in the future')

		parser.add_argument('--config', nargs=1, help='path to a configuration file')
		parser.add_argument('--hide-window', action='store_true', help='wheter to show the main window on startup or not')
		parser.add_argument('--show-window', action='store_true')
		parser.add_argument('--launch-spotify', action='store_true', help='launch Spotify on startup')
		parser.add_argument('--dont-launch-spotify', action='store_true')

		self.args = parser.parse_args()


	def _write_config(self):
		with open(self.config_path, 'w') as f:
			default_config_file = open(f'{util.get_dirname(__file__)}/assets/default_config.ini', 'r')

			f.write(default_config_file.read())
			default_config_file.close()
			f.close()


	def _read_config(self, rec=False):
		try:
			self.config.read(self.config_path)

			self.values['hide_window'] = self._overwrite(self._str_to_bool(self._get('config', 'hide-window', 'False')), self.args.hide_window, self.args.show_window)
			self.values['launch_spotify'] = self._overwrite(self._str_to_bool(self._get('config', 'launch-spotify', 'False')), self.args.launch_spotify, self.args.dont_launch_spotify)
		except Exception as e:
			if rec:
				util.Logger.error('Could not create config file')
				sys.exit(1)

			util.Logger.error(e)
			util.Logger.error('Config file is invalid, attempting to recreate')
			util.Logger.info('A backup of your old config file was created as "backup_invalid.ini~"')

			copy(self.config_path, os.path.join(self.config_dir, 'backup_invalid.ini~'))

			os.unlink(self.config_path)
			self._write_config()
			self._read_config(True)


	def _get(self, section, option, fallback): return self.config.get(section, option, fallback=fallback)
	def _str_to_bool(self, str): return str.lower() in ['true', 'on', 'yes']
	def _overwrite(self, a, b, c): return False if c else True if b else a


	def update_option(self, section, option, value):
		if not self.config.has_section(section): self.config.add_section(section)

		with open(self.config_path, 'w') as f:
			self.config.set(section, option, value)
			self.config.write(f)
			f.close()


	def stop_file_watcher(self):
		self.file_watcher.stop()
		self.file_watcher.join()