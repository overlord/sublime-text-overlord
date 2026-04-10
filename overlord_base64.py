# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import base64

# ------------------------------
class overlord_to_base64(sublime_plugin.TextCommand):
	def run(self, edit):
		for sel in reversed(self.view.sel()):
			text = self.view.substr(sel)
			text_b = text.encode('utf-8')
			encoded_b = base64.b64encode(text_b)
			encoded = encoded_b.decode('utf-8')
			self.view.replace(edit, sel, encoded)

class overlord_from_base64(sublime_plugin.TextCommand):
	def run(self, edit):
		for sel in reversed(self.view.sel()):
			text = self.view.substr(sel)
			decoded_b = base64.b64decode(text)
			decoded = decoded_b.decode('utf-8')
			self.view.replace(edit, sel, decoded)

# ------------------------------
