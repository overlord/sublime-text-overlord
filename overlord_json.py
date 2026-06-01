# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import json
# ------------------------------
class overlord_json_escape(sublime_plugin.TextCommand):
	def run(self, edit):
		for sel in reversed(self.view.sel()):
			text = json.escape(self.view.substr(sel))
			self.view.replace(edit, sel, text)

class overlord_json_unescape(sublime_plugin.TextCommand):
	def run(self, edit):
		for sel in reversed(self.view.sel()):
			text = self.view.substr(sel)
			if not text.startswith('"'):
				text = '"' + text
			if not text.endswith('"'):
				text = text + '"'
			text = json.loads(text)
			self.view.replace(edit, sel, text)

# ------------------------------
