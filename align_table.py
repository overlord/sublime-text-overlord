# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
# ------------------------------
if sublime.version() >= '3000':
	from sublime_overlord.lib import (st2api)
else:
	from lib import (st2api)
# ------------------------------------------------------------------------------------------------------------------------
class overlord_align_table(sublime_plugin.TextCommand):
	# ------------------------------
	def run(self, edit):
		view = self.view
		selection = st2api.get_selection(view)
		for sel in reversed(selection): # reversing is essential
			content = self.process_selection(edit, view, sel)
			view.replace(edit, sel, content)
	# ------------------------------
	def process_selection(self, edit, view, sel):
		values = view.substr(sel).split('\n')

		while True:
			max_index = max(list(map(lambda i: i.find('\t'), values)))
			if max_index == -1:
				break
			values = list(map(lambda value: self.align(value, max_index), values))

		return '\n'.join(values).rstrip('\n')
	# ------------------------------
	def align(self, value, max_index):
		tab_index = value.find('\t')
		value = value.replace('\t', ' ' * (max_index - tab_index) + ' | ', 1)
		return value
	# ------------------------------
