import sublime_plugin
import os
import re
import webbrowser

REX_URL = re.compile(r'''(?xi) \s* url \s* = \s* (.*) ''')
REX_BRANCH = re.compile(r'''(?xi) \[ branch \s+ \" (.*) \" \] ''')

DEBUG = False
# DEBUG = True

def traced(message):
	if DEBUG:
		print('[OVR]', message)

class OverlordOpenGitlabCommand(sublime_plugin.TextCommand):

	def find_repo_dir(self):
		file_name = self.view.file_name() or ""
		cur_dir = os.path.dirname(file_name)
		while cur_dir:
			git_dir = os.path.join(cur_dir, '.git')
			if os.path.isdir(git_dir):
				return cur_dir

			new_dir = os.path.dirname(cur_dir)
			if cur_dir == new_dir:
				break
			cur_dir = new_dir

		return None

	def find_git_config(self):
		repo_dir = self.find_repo_dir()
		if not repo_dir:
			return None
		git_config = os.path.join(repo_dir, '.git', 'config')
		if os.path.isfile(git_config):
			return git_config

	def get_origin_url(self):
		view = self.view
		file_name = view.file_name() or ""
		repo_dir = self.find_repo_dir()
		git_config = self.find_git_config()
		traced(f'{file_name=}')
		traced(f'{repo_dir=}')
		traced(f'{git_config=}')
		if not git_config:
			return None

		rel_file_name = file_name.replace(repo_dir, '').replace('\\', '/').strip('/')
		traced(f'{rel_file_name=}')

		with open(git_config, 'r', encoding='utf-8') as f:
			data = f.read()
			match = REX_URL.search(data)
			if not match:
				return None
			url = match.group(1).strip('/')

			match = REX_BRANCH.search(data)
			traced(match)
			branch = match.group(1) if match else "master"

		if url.endswith('.git'):
			url = url[:-4]

		if 'github.com' in url: # https://github.com/overlord/sublime-text-overlord/blob/master/README.md
			url = url + f'/blob/{branch}/{rel_file_name}'
		elif 'gitlab.services.mts.ru' in url: # https://gitlab.services.mts.ru/path/to/project/-/blob/develop/README.md
			url = url + f'/-/blob/{branch}/{rel_file_name}'
			row, _ = view.rowcol(view.sel()[0].a)
			if row:
				url += f'#L{row + 1}'

		traced(f'{url=}')

		return url

	# ------------------------------

	def run(self, edit):
		url = self.get_origin_url()
		webbrowser.open_new_tab(url)

	def is_visible(self):
		return self.get_origin_url() is not None

	def description(self):
		url = self.get_origin_url()
		if len(url) > 64:
			url = url[:32] + '<...>' + url[-32:]
		return f'Open git {url}'
