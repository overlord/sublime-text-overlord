# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
# ------------------------------
if sublime.version() >= '3000':
	from sublime_overlord.lib import (st2api, winclip)
else:
	from lib import (st2api, winclip)
# ------------------------------
from os import urandom
# ------------------------------------------------------------------------------------------
PASS_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789abcdefghjkmnpqrstuvwxyz23456789'
# ------------------------------------------------------------------------------------------
VOWELS = 'AEU' + 'aeiu'
CONSONANTS = 'BCDFGHJKLMNPQRSTVWXYZ' + 'bcdfghjkmnpqrstvwxyz'
DIGITS = '123456789'
# ------------------------------------------------------------------------------------------
class overlord_pass_generate(sublime_plugin.WindowCommand):
	'''
	Window Command: генерация пароля с запросом длины.
	'''
	# ------------------------------
	def run(self, length = None):
		if not length:
			self.window.show_input_panel('Password length:', '12', lambda length: self.generate_password(length), None, None)
		else:
			self.generate_password(length)
	# ------------------------------
	def generate_password(self, length):
		password = self.get_password(int(length))
		# winclip.Paste(password)
		st2api.insert_in_active_view(self, password)

	# ------------------------------
	def get_password(self, length):
		password = ''

		for i in range(0, length):
			password = password + ''.join(CONSONANTS[i % len(CONSONANTS)] for i in urandom(1))
			password = password + ''.join(VOWELS[i % len(VOWELS)] for i in urandom(1))
			if i % 2 == 0:
				password = password + ''.join(DIGITS[i % len(DIGITS)] for i in urandom(1))

		return password[:length]
# ------------------------------------------------------------------------------------------
class overlord_pass_generate2(sublime_plugin.WindowCommand):
	'''
	Window Command: генерация пароля с запросом длины.
	'''
	# ------------------------------
	def run(self, length = None):
		if not length:
			self.window.show_input_panel('Password length:', '12', lambda length: self.generate_password(length), None, None)
		else:
			self.generate_password(length)
	# ------------------------------
	def generate_password(self, length):
		password = ''.join(PASS_CHARS[i % len(PASS_CHARS)] for i in urandom(int(length)))
		# winclip.Paste(password)
		st2api.insert_in_active_view(self, password)
# ------------------------------------------------------------------------------------------
