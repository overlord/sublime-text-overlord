# -*- coding: utf-8 -*-
'''
@author Josh Bjornson

This work is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/
or send a letter to Creative Commons, 171 Second Street, Suite 300, San Francisco, California, 94105, USA.
'''
import sublime
import sublime_plugin
# ------------------------------
import os
import json
# ------------------------------

# Plugin to provide access to the history of accessed files:
# https://gist.github.com/1133602
#
# The plugin stores a JSON file with the file history.
#
# Note: I tried checking for file existence in the history but this
# took more time than expected (especially with networked files) and
# made the plugin quite unresponsive.  The compromise is a command
# to cleanup the current project (with the option to clean up the
# global list as well).  The cleanup will remove any files in the
# project history that don't exist.
#
# To run the plugin:
# view.run_command("overlord_open_recently_closed_file")
#
# Keymap entries:
# { "keys": ["ctrl+shift+t"], "command": "overlord_open_recently_closed_file"},
# { "keys": ["ctrl+alt+shift+t"], "command": "overlord_open_recently_closed_file", "args": {"show_quick_panel": false}  },
# { "keys": ["ctrl+alt+shift+t"], "command": "overlord_open_recently_closed_file", "args": { }  },
# { "keys": ["ctrl+alt+shift+c"], "command": "overlord_cleanup_file_history", "args": { }  },
#
# TODO use api function (not yet available) to get the project name/id (rather than using a hash of the project folders)
# TODO Get the settings below from a sublime-settings file?

GLOBAL_MAX_ENTRIES=250
PRINT_DEBUG = False

# Helper methods for "logging" to the console.
def debug(text):
	if PRINT_DEBUG:
		print('[%s] %s' % ('FileHistory', text))

# Class to read and write the file-access history.
class FileHistory(object):

	"""Class to manage the file-access history"""
	def start(self):
		self.history_file = os.path.join(sublime.packages_path(), 'User', 'FileHistory.json')
		self.history = {}
		self.__ensure_project()
		self.__load_history()

	def __load_history(self):
		debug('Loading the history from file ' + self.history_file)
		if not os.path.exists(self.history_file):
			return

		f = open(self.history_file, 'r')
		try:
			self.history = json.load(f)
			self.__ensure_project()
		finally:
			f.close()

	def __save_history(self):
		debug('Saving the history to file ' + self.history_file)
		f = open(self.history_file, mode='w+')
		try:
			json.dump(self.history, f, indent=2)
			f.flush()
		finally:
			f.close()

	def get_history(self):
		"""Return the requested history (global or project-specific): opened files followed by closed files"""
		# Make sure the history is loaded
		if len(self.history) == 0:
			self.__load_history()

		# Return the list of closed and opened files
		return self.history['closed'] + self.history['opened']

	def __ensure_project(self):
		"""Make sure the project nodes exist (including 'opened' and 'closed')"""
		if 'opened' not in self.history:
			self.history['opened'] = []
		if 'closed' not in self.history:
			self.history['closed'] = []

	def add_view(self, view, history_type):
		# Get the file details from the view
		filename = os.path.normpath(view.file_name()) if view.file_name() else None
		# Only keep track of files that exist (that have already been saved)
		if filename != None:
			if os.path.exists(filename):
				self.__add_to_history(history_type, filename)
			else:
				self.__remove(filename)

			self.__save_history()

	def __add_to_history(self, history_type, filename):
		# Make sure the project nodes exist
		self.__ensure_project()

		# Remove the file from the project list then
		# add it to the top (of the opened/closed list)
		self.__remove(filename)
		node = filename
		self.history[history_type].insert(0, node)

		# Make sure we limit the number of history entries
		self.history[history_type] = self.history[history_type][0:GLOBAL_MAX_ENTRIES]

	def __remove(self, filename):
		# Remove any references to this file from the project
		for history_type in ('opened', 'closed'):
			for node in iter(self.history[history_type]):
				if node.lower() == filename.lower():
					self.history[history_type].remove(node)

	def clean_history(self):

		# Remove any non-existent files from the project
		for history_type in ('opened', 'closed'):
			for node in reversed(self.history[history_type]):
				if not os.path.exists(node):
					self.history[history_type].remove(node)

		self.__save_history()

class OpenRecentlyClosedFileEventListener(sublime_plugin.EventListener):
	"""class to keep a history of the files that have been opened and closed"""

	def on_close(self, view):
		hist.add_view(view, 'closed')

	def on_load(self, view):
		hist.add_view(view, 'opened')

class overlord_cleanup_file_history(sublime_plugin.WindowCommand):
	def run(self):
		hist.clean_history()

class overlord_open_recently_closed_file(sublime_plugin.WindowCommand):
	"""class to either open the last closed file or show a quick panel with the recent file history (closed files first)"""

	def run(self, show_quick_panel=True):
		# Prepare the display list with the file name and path separated
		self.history_list = hist.get_history()
		display_list = []
		for node in self.history_list:
			file_path = node
			display_list.append([os.path.basename(file_path), os.path.dirname(file_path)])

		if show_quick_panel:
			self.window.show_quick_panel(display_list, self.open_file)
		else:
			self.open_file(0)

	def open_file(self, selected_index):
		if selected_index >= 0 and selected_index < len(self.history_list):
			node = self.history_list[selected_index]
			new_view = self.window.open_file(node)

# ------------------------------

# Global file history instance
hist = FileHistory()
hist.start()

def plugin_loaded():
	hist.start()
