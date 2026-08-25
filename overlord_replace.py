# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
# --
import json
import os
import re
# --
from sublime_overlord.lib import st2api
# ----------------------------------!---------------------------------------------
SEP_PLAIN = '--R->'
# ----------------------------------!---------------------------------------------
DEBUG = False
def _trace(s, verbose=False):
	if DEBUG or verbose:
		print('[OVERLORD_REPLACE]', s)
# ----------------------------------!---------------------------------------------
class overlord_replace_core(sublime_plugin.WindowCommand):
	# ------------------------------
	def replace_in_window(self, data, options):
		window = options['window']
		views = window.views() if options['in_all_open_files'] else [window.active_view()]
		for view in views:
			self.replace_in_view(view, data, options)
	# ------------------------------
	def replace_in_view(self, view, data, options):
		# ------------------------------
		cleanup_data = [x for x in data if x]
		# ------------------------------
		content = initial_content = st2api.get_text(view)
		_trace(f'[+] ------------------------------')
		for source, target in cleanup_data:
			source = source.strip().replace('`s', ' ').replace('`EMPTY', '')
			target = target.strip().replace('`s', ' ').replace('`EMPTY', '')
			_trace(f'[+] Replace "{source}" to "{target}"')
			content = re.sub(source, target, content)
		# ------------------------------
		if options['scratch']:
			new_view = st2api.new_file(options['window'], content, True)
			syntax = view.settings().get('syntax')
			if syntax:
				new_view.set_syntax_file(syntax)
		else:
			if content == initial_content:
				return
			pos = st2api.get_cursor_position(view)
			view.run_command('overlord_set_content', { 'content': content })
			syntax = (view.settings().get('syntax') or '').lower()
			_trace(f'Current syntax: {syntax}')
			if 'text' in syntax:
				view.set_syntax_file('Packages/sublime_overlord/syntaxes/Highlighted Text.sublime-syntax')
			st2api.set_cursor_position(view, pos)
	# ------------------------------
	def parse_lines(self, lines, sep):
		config_json = []
		for line in lines:
			if line and not line.startswith('#'):
				try:
					src, dst = line.split(sep)
					config_json.append((src, dst))
				except ValueError as e:
					_trace(f'line: {line}; error: {e}', verbose=True)
					raise
		return config_json
# ----------------------------------!---------------------------------------------
class overlord_replace(overlord_replace_core):
	'''
	Window Command: применяет ряд Regex-переименований к контенту текущего view,
	замены берутся из json-config-файла в формате [[regex_source, plain_target]+]
	или запрашиваются у пользователя в формате [regex_source-->target] (разделитель -->)
	'''
	# ------------------------------
	def run(self, config_path=None, config_json=None, scratch=True, in_all_open_files=False):
		# ------------------------------
		options = {
			'window': self.window,
			'scratch': scratch,
			'in_all_open_files': in_all_open_files,
		}
		# ------------------------------
		if config_path:
			expanded_path = st2api.apply_custom_replace(config_path)
			with open(expanded_path, encoding='utf8') as config_file:
				config_json = json.load(config_file)
		# ------------------------------
		if config_json:
			self.replace_in_window(config_json, options)
		else:
			self.window.show_input_panel('Input replace data:', '', lambda replace_data: self.__on_done(replace_data, options), None, None)
	# ------------------------------
	def description(self, config_path=None, config_json=None, scratch=True, in_all_open_files=False):
		head, tail = os.path.split(st2api.apply_custom_replace(config_path))
		return 'Replace using "%s"' % tail
	# ------------------------------
	def __on_done(self, replace_data, options):
		lines = [x.strip() for x in replace_data.split('\n')]
		config_json = self.parse_lines(lines, '-->')
		self.replace_in_window(config_json, options)
# ----------------------------------!---------------------------------------------
class overlord_replace_plain(overlord_replace_core):
	'''
	Window Command: применяет ряд Regex-переименований к контенту текущего view,
	замены берутся из json-config-файла в формате [[regex_source, plain_target]+]
	или запрашиваются у пользователя в формате [regex_source-->target] (разделитель -->)
	'''
	# ------------------------------
	def run(self, config_path=None, config_json=None, scratch=True, in_all_open_files=False):
		# ------------------------------
		options = {
			'window': self.window,
			'scratch': scratch,
			'in_all_open_files': in_all_open_files,
		}
		# ------------------------------
		if config_path:
			expanded_path = st2api.apply_custom_replace(config_path)
			with open(expanded_path, encoding='utf8') as config_file:
				_trace({'config_file': expanded_path})
				lines = [x.strip() for x in config_file.readlines()]
				config_json = self.parse_lines(lines, SEP_PLAIN)
				_trace({'config_json': config_json})
		# ------------------------------
		if config_json:
			self.replace_in_window(config_json, options)
		else:
			self.window.show_input_panel('Input replace data:', '', lambda replace_data: self.__on_done(replace_data, options), None, None)
	# ------------------------------
	def description(self, config_path=None, config_json=None, scratch=True, in_all_open_files=False):
		head, tail = os.path.split(st2api.apply_custom_replace(config_path))
		return 'Replace using "%s"' % tail
	# ------------------------------
	def __on_done(self, replace_data, options):
		lines = [x.strip() for x in replace_data.split('\n')]
		config_json = self.parse_lines(lines, SEP_PLAIN)
		self.replace_in_window(config_json, options)
# ----------------------------------!---------------------------------------------
class overlord_set_content(sublime_plugin.TextCommand):
	def run(self, edit, content):
		st2api.set_text(self.view, edit, content)
# ----------------------------------!---------------------------------------------
