# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
# ------------------------------
if sublime.version() >= '3000':
	from sublime_overlord.lib import (st2api)
else:
	from lib import (st2api)
# ------------------------------
import collections
import json
import os
import re
# ------------------------------------------------------------------------------------------
SPLITTER = '--[ SPLITTER ]--'
# ------------------------------------------------------------------------------------------
class overlord_split_file(sublime_plugin.TextCommand):
	'''
	View Command: разделяет файл на кусочки
	'''
	# ------------------------------
	def get_name(self, splitter):
		return splitter[len(SPLITTER):] if splitter else None
	# ------------------------------
	def dump_content(self, is_scratch, content, splitter):
		if content:
			view = st2api.new_file(self.view.window(), '\n'.join(content), is_scratch, self.get_name(splitter))
			content[:] = []

	# ------------------------------
	def run(self, edit, is_scratch):
		content = []
		splitter = None
		regions = self.view.lines(st2api.get_region(self.view))
		for region in regions:
			line = self.view.substr(region)
			if line.startswith(SPLITTER):
				self.dump_content(is_scratch, content, splitter)
				splitter = line
			else:
				content.append(line)
		self.dump_content(is_scratch, content, splitter)
# ------------------------------------------------------------------------------------------
class overlord_concat_files(sublime_plugin.WindowCommand):
	'''
	Window Command: объединяет выбраные файлы в новое окно.
	'''
	# ------------------------------
	def append_file_content(self, view, path, encodings):
		for encoding in encodings:
			try:
				with open(path, 'r', encoding=encoding) as file:
					content = file.read()
					st2api.append_content(view, "%s%s\n" % (SPLITTER, path))
					st2api.append_content(view, content)
					return
			except UnicodeDecodeError:
				print("Unable to open [%s] in [%s] encoding")
	# ------------------------------
	def run(self, files = None):
		# settings = sublime.load_settings('Preferences.sublime-settings')
		encodings = ["utf-8-sig", "utf-8", 'cp1251']
		if files:
			view = st2api.new_file(self.window, None, True)
			for path in files:
				self.append_file_content(view, path, encodings)
	# ------------------------------
	def is_visible(self, files = None):
		return True if files or [] else False
# ------------------------------------------------------------------------------------------
