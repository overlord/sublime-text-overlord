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
class overlord_replace(sublime_plugin.WindowCommand):
	'''
	Window Command: применяет ряд Regex-переименований к контенту текущего view,
	замены берутся из json-config-файла в формате [[regex_source, plain_target]+]
	или запрашиваются у пользователя в формате [regex_source-->target] (разделитель -->)
	'''
	# ------------------------------
	def run(self, config_path=None, config_json=None, scratch=True, in_all_open_files=False):
		# ------------------------------
		TReplaceOptions = collections.namedtuple("_", ['window', 'scratch', 'in_all_open_files'])
		options = TReplaceOptions(self.window, scratch, in_all_open_files)
		# ------------------------------
		if config_path:
			with open(st2api.apply_custom_replace(config_path), encoding='utf8') as config_file:
				config_json = json.load(config_file)
		# ------------------------------
		if config_json:
			self.__apply_replace(config_json, options)
		else:
			self.window.show_input_panel('Input replace data:', '', lambda replace_data: self.__on_done(replace_data, options), None, None)
	# ------------------------------
	def description(self, config_path=None, config_json=None, scratch=True, in_all_open_files=False):
		head, tail = os.path.split(st2api.apply_custom_replace(config_path))
		return 'Replace using "%s"' % tail
	# ------------------------------
	def __on_done(self, replace_data, options):
		lines = [x.strip() for x in replace_data.split('\n')]
		not_empty_lines = [x for x in lines if x]
		config_json = [x.split('-->') for x in not_empty_lines]
		self.__apply_replace(config_json, options)
	# ------------------------------
	def __apply_replace(self, data, options):
		if options.in_all_open_files:
			for view in options.window.views():
				self.__apply_replace_to_view(view, data, options)
		else:
			view = options.window.active_view()
			self.__apply_replace_to_view(view, data, options)
	# ------------------------------
	def __apply_replace_to_view(self, view, data, options):
		# ------------------------------
		cleanup_data = [x for x in data if x]
		# ------------------------------
		content = initial_content = st2api.get_text(view)
		for source, target in cleanup_data:
			content = re.sub(source, target, content)
		# ------------------------------
		if options.scratch:
			st2api.new_file(options.window, content, True)
		else:
			if content == initial_content:
				return
			pos = st2api.get_cursor_position(view)
			view.run_command("overlord_set_content", { "content": content })
			# while(st2api.get_text(view) != content): None
			if view.settings().get('syntax') == 'Packages/Text/Plain text.tmLanguage':
				view.set_syntax_file('Packages/sublime_overlord/syntaxes/Highlighted Text.tmLanguage')
			st2api.set_cursor_position(view, pos)

# ------------------------------------------------------------------------------------------
class overlord_set_content(sublime_plugin.TextCommand):
	def run(self, edit, content):
		st2api.set_text(self.view, edit, content)
