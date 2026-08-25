# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
# --
import json
# ------------------------------
def to_json_str(s):
	return json.dumps(s, sort_keys=False, indent=4, separators=(',', ': '), ensure_ascii=False)
# ------------------------------
def json_unescape(s):
	s = s.strip()
	# --
	# люди любят случайно выделять еще и запятую в конце
	tail = ''
	if s.endswith(','):
		s = s[:-1].strip()
		tail = ','
	# --
	# может прийти строка без открывающих/закрывающих кавычек
	if not s.startswith('"'):
		s = '"' + s
	if not s.endswith('"'):
		s = s + '"'
	# --
	return json.loads(s) + tail
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
			text = to_json_str(self.view.substr(sel))
			self.view.replace(edit, sel, text)
# ------------------------------
class overlord_json_unescape(sublime_plugin.TextCommand):
	def run(self, edit):
		for sel in reversed(self.view.sel()):
			text = json_unescape(self.view.substr(sel))
			self.view.replace(edit, sel, text)
# ------------------------------
