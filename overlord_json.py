# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import json
# ------------------------------
def json_unescape(s):
	s = s.strip()
	if not s.startswith('"'):
		s = '"' + s
	if not s.endswith('"'):
		s = s + '"'
	return json.loads(s)
# ------------------------------
def try_json_unescape(s):
	try:
		return json_unescape(s), True
	except:
		return s, False
# ------------------------------
class overlord_json_escape(sublime_plugin.TextCommand):
	def run(self, edit):
		for sel in reversed(self.view.sel()):
			text = json.escape(self.view.substr(sel))
			self.view.replace(edit, sel, text)

class overlord_json_unescape(sublime_plugin.TextCommand):
	def run(self, edit):
		for sel in reversed(self.view.sel()):
			text = json_unescape(self.view.substr(sel))
			self.view.replace(edit, sel, text)

# ------------------------------
