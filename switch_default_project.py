# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
# ------------------------------
if sublime.version() >= '3000':
	from sublime_overlord.lib import (st2api)
else:
	from lib import (st2api)
# ------------------------------
import subprocess
import sys

# ------------------------------
SETTINGS_FILE = 'switch_default_project.sublime-settings'

# ------------------------------
def select(items, converter):
	return list(map(converter, items))

# ------------------------------
class overlord_switch_project_file(sublime_plugin.WindowCommand):

	def construct(self, file_name, source, target):
		i = file_name.lower().find(source.lower())
		file_name = file_name[0:i] + target + file_name[i+len(source):]
		row, col = self.selection
		file_w_position = "%s:%s:%s" % (file_name.replace(u'→ ', ''), row, col)
		self.window.open_file(file_w_position, sublime.ENCODED_POSITION)

	def select_match(self, match, file_name):
		source, targets = match
		targets = select(targets, lambda i: u'→ ' + i if source in i else i)
		st2api.show_quick_panel(self, targets, lambda i: self.construct(file_name, source, targets[i]), sublime.MONOSPACE_FONT)

	def run(self):
		path_blocks = sublime.load_settings(SETTINGS_FILE).get("path_blocks", [])

		view = self.window.active_view()
		if view is None or view.file_name() is None: return

		file_name = view.file_name().replace('\\', '/')
		self.selection = view.rowcol(view.sel()[0].begin())

		matched_blocks = {}
		for block in path_blocks:
			for item in block:
				if item.lower() in file_name.lower():
					matched_blocks[item] = block

		matches = list(matched_blocks.items())

		if len(matches) == 1:
			self.select_match(matches[0], file_name)
		elif len(matches) > 1:
			labels = select(matches, lambda i: i[0])
			st2api.show_quick_panel(self, labels, lambda i: self.select_match(matches[i], file_name))

# ------------------------------
