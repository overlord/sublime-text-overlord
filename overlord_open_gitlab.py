# -*- coding: utf-8 -*-
import sublime_plugin
# --
import os
import re
import webbrowser
# ----------------------------------!---------------------------------------------
REX_URL = re.compile(r'''(?xi) \s* url \s* = \s* (.*) ''')
# ----------------------------------!---------------------------------------------
DEBUG = False
def _trace(s, verbose=False):
	if DEBUG or verbose:
		print('[OVERLORD_GITLAB]', s)
# ----------------------------------!---------------------------------------------
def get_repo_dir(file_name):
	if not file_name:
		return None
	# --
	cur_dir = os.path.dirname(file_name)
	while cur_dir:
		git_dir = os.path.join(cur_dir, '.git')
		if os.path.isdir(git_dir):
			return cur_dir
		# --
		new_dir = os.path.dirname(cur_dir)
		if cur_dir == new_dir:
			break
		cur_dir = new_dir
	# --
	return None
# ----------------------------------!---------------------------------------------
def get_repo_url(repo_dir):
	if not repo_dir:
		return None
	# --
	git_CONFIG = os.path.join(repo_dir, '.git', 'config')
	if not os.path.isfile(git_CONFIG):
		return None
	# --
	with open(git_CONFIG, 'r', encoding='utf-8') as f:
		data = f.read()
		match = REX_URL.search(data)
		if not match:
			return None
		repo_url = match.group(1).strip('/')
		if repo_url.endswith('.git'):
			repo_url = repo_url[:-4]
		return repo_url
# ----------------------------------!---------------------------------------------
def get_repo_ref(repo_dir):
	if not repo_dir:
		return None
	# --
	git_HEAD = os.path.join(repo_dir, '.git', 'HEAD')
	if not os.path.isfile(git_HEAD):
		return None
	# --
	with open(git_HEAD, 'r', encoding='utf-8') as f:
		data = f.read().strip()
		if data.startswith('ref: '):
			return os.path.basename(data[5:])
		return data
# ----------------------------------!---------------------------------------------
def get_origin_url(file_name, line_number):
	if not file_name:
		return None
	# --
	repo_dir = get_repo_dir(file_name)
	repo_url = get_repo_url(repo_dir)
	repo_ref = get_repo_ref(repo_dir)
	_trace(f'{repo_dir=}')
	_trace(f'{repo_url=}')
	_trace(f'{repo_ref=}')
	# --
	if not repo_url or not repo_ref:
		return None
	# --
	file_name = file_name.replace(repo_dir, '').replace('\\', '/').strip('/')
	# --
	if 'github.com' in repo_url:
		#!_! https://github.com/path/to/project/blob/<ref>/README.md#L123
		line = f'#L{line_number + 1}' if line_number else ''
		origin_url = f'{repo_url}/blob/{repo_ref}/{file_name}{line}'
	elif 'gitlab.services.mts.ru' in repo_url:
		#!_! https://gitlab.services.mts.ru/path/to/project/-/blob/<ref>/README.md#L123
		line = f'#L{line_number + 1}' if line_number else ''
		origin_url = f'{repo_url}/-/blob/{repo_ref}/{file_name}{line}'
	else:
		origin_url = repo_url
	# --
	_trace(f'{origin_url=}')
	# --
	return origin_url
# ----------------------------------!---------------------------------------------
class OverlordOpenGitlabCommand(sublime_plugin.TextCommand):
	# ------------------------------
	def __get_origin_url(self):
		file_name = self.view.file_name()
		line_number, _ = self.view.rowcol(self.view.sel()[0].a)
		return get_origin_url(file_name, line_number)
	# ------------------------------
	def run(self, edit):
		url = self.__get_origin_url()
		webbrowser.open_new_tab(url)
	# ------------------------------
	def is_visible(self):
		return self.__get_origin_url() is not None
	# ------------------------------
	def description(self):
		url = self.__get_origin_url()
		if len(url) > 64:
			url = url[:32] + '<...>' + url[-32:]
		return f'Open git {url}'
# ----------------------------------!---------------------------------------------
