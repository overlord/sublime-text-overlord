import sublime_plugin
import os
import re
import webbrowser

rex = r'(?xi) \s* url \s* = \s* (.*)'

class OverlordOpenGitlabCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		url = self.get_origin_url()
		webbrowser.open_new_tab(url)

	def is_visible(self):
		return self.get_origin_url() is not None

	def find_git_config(self):
		initial = self.view.file_name()
		cur_dir = os.path.dirname(self.view.file_name() or "")
		while cur_dir:
			git = os.path.join(cur_dir, '.git')
			if os.path.isdir(git):
				config = os.path.join(git, 'config')
				if os.path.isfile(config):
					return None if config == initial else config

			new_dir = os.path.dirname(cur_dir)
			if cur_dir == new_dir:
				break
			cur_dir = new_dir

		return None

	def get_origin_url(self):
		config = self.find_git_config()
		if not config:
			return None

		with open(config, 'r', encoding='utf-8') as f:
			data = f.read()
			match = re.search(rex, data)
			return match.group(1) if match else None

	def description(self):
		url = self.get_origin_url()
		return f'Open git origin - {os.path.basename(url)}...'
