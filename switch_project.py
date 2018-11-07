# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
# ------------------------------
if sublime.version() >= '3000':
	from sublime_overlord.lib import (st2api)
else:
	from lib import (st2api)
# ------------------------------
import subprocess
import sys
import os

# ------------------------------
SETTINGS_FILE = 'switch_project.sublime-settings'

# ------------------------------
C_ADD       = 'add'
C_ITEMS     = 'items'
C_NAME      = 'name'
C_PATHS     = 'paths'
C_PROJECTS  = 'projects'

# ------------------------------
def INFO(message):
	print('[INFO:%s] %s' % (__name__, message))
def ERROR(message):
	print('[ERROR:%s] %s' % (__name__, message))
# ------------------------------
def select(items, converter):
	return list(map(converter, items))
# ------------------------------
class overlord_switch_project(sublime_plugin.WindowCommand):

	def append_to_command(self, command, paths):
		for path in paths or []:
			path_custom = st2api.apply_custom_replace(path)
			if os.path.exists(path_custom):
				command.append(path_custom)
			else:
				ERROR('Path "%s" is not found.' % path_custom)

	def on_item_selected(self, project, item):
		command = [st2api.executable_path()]
		# ------------------------------
		self.append_to_command(command, item.get(C_PATHS, []) if item else [])
		self.append_to_command(command, project.get(C_ADD, []))
		# ------------------------------
		if not self.in_new_instance:
			for view in self.window.views():
				if view.file_name() and not view.is_scratch():
					command.append(view.file_name())
					self.window.focus_view(view)
					self.window.run_command('close')
			if len(self.window.folders()) > 0:
				self.window.run_command('close_folder_list')
		# ------------------------------
		command = [st2api.to_os_encoding(i) for i in command]
		# ------------------------------
		# print(command)
		# ------------------------------
		subprocess.Popen(command)

	def walk_items(self, project, items):
		if len(items) == 0:
			self.on_item_selected(project, None)
		elif len(items) == 1:
			self.on_item_selected(project, items[0])
		else:
			menu = select(items, lambda z: z.get(C_NAME, "?"))
			st2api.show_quick_panel(self, menu, lambda i: self.on_item_selected(project, items[i]), sublime.MONOSPACE_FONT)

	def on_project_selected(self, project):
		self.walk_items(project, project.get(C_ITEMS, []))

	def walk_projects(self, projects):
		if len(projects) == 1:
			self.on_project_selected(projects[0])
		else:
			menu = select(projects, lambda z: z.get(C_NAME, "?"))
			st2api.show_quick_panel(self, menu, lambda i: self.on_project_selected(projects[i]), sublime.MONOSPACE_FONT)

	def run(self, in_new_instance=False):
		self.in_new_instance = in_new_instance
		projects = sublime.load_settings(SETTINGS_FILE).get(C_PROJECTS)
		self.walk_projects(projects)

# ------------------------------
