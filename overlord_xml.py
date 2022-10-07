# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import html
import sys
# ------------------------------
class overlord_xml_escape(sublime_plugin.TextCommand):
	def run(self, edit):
		for sel in reversed(self.view.sel()):
			text = html.escape(self.view.substr(sel))
			self.view.replace(edit, sel, text)

class overlord_xml_unescape(sublime_plugin.TextCommand):
	def run(self, edit):
		for sel in reversed(self.view.sel()):
			text = html.unescape(self.view.substr(sel))
			self.view.replace(edit, sel, text)

# ------------------------------
