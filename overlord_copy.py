# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
# --
import os
import shutil

# ----------------------------------!---------------------------------------------
GLOBAL_LAST_DIR_TO = ''

# ----------------------------------!---------------------------------------------
class overlord_copy_active_file_to(sublime_plugin.WindowCommand):
	'''
	Window Command: копирует текущий файл в выбраную папку.
	'''
	def run(self):
		global GLOBAL_LAST_DIR_TO
		self.window.show_input_panel('Target directory:', GLOBAL_LAST_DIR_TO, self.on_target_path_selected, None, None)

	def on_target_path_selected(self, target_dir):
		global GLOBAL_LAST_DIR_TO
		file_name = self.window.active_view().file_name()
		if os.path.isdir(target_dir) and os.path.exists(target_dir) and os.path.exists(file_name):
			GLOBAL_LAST_DIR_TO = target_dir
			folder, file_name = os.path.split(file_name)
			shutil.copyfile(os.path.join(folder, file_name), os.path.join(target_dir, file_name))

# ----------------------------------!---------------------------------------------
class overlord_copy_open_file_to(sublime_plugin.WindowCommand):
	'''
	Window Command: копирует открытые файлы в выбраную папку.
	'''
	def run(self):
		global GLOBAL_LAST_DIR_TO
		self.window.show_input_panel('Target directory:', GLOBAL_LAST_DIR_TO, self.on_target_path_selected, None, None)

	def on_target_path_selected(self, target_dir):
		global GLOBAL_LAST_DIR_TO
		if os.path.isdir(target_dir) and os.path.exists(target_dir):
			GLOBAL_LAST_DIR_TO = target_dir
			for (folder, file_name) in [os.path.split(view.file_name()) for view in self.window.views() if view.file_name()]:
				shutil.copyfile(os.path.join(folder, file_name), os.path.join(target_dir, file_name))

# ----------------------------------!---------------------------------------------
class overlord_copy_open_file_path(sublime_plugin.WindowCommand):
	'''
	Window Command: копирует список открытых файлов в clipboard.
	'''
	def run(self):
		data = '\n'.join([view.file_name() for view in self.window.views() if view.file_name()])
		if data:
			sublime.set_clipboard(data)

# ----------------------------------!---------------------------------------------
class overlord_copy_file_path(sublime_plugin.WindowCommand):
	'''
	Window Command: копирует пути к выбранным объектам в clipboard.
	'''
	def get_paths(self, files = None, dirs = None):
		return (files or []) + (dirs or [])

	def run(self, files = None, dirs = None):
		paths = self.get_paths(files, dirs)
		if paths:
			sublime.set_clipboard('\n'.join(paths))

	def is_visible(self, files = None, dirs = None):
		return len(self.get_paths(files, dirs)) > 0

# ----------------------------------!---------------------------------------------
class overlord_copy_file_name(sublime_plugin.WindowCommand):
	'''
	Window Command: копирует названия выбраннх объектов в clipboard.
	'''
	def get_paths(self, files = None, dirs = None):
		return (files or []) + (dirs or [])

	def run(self, files = None, dirs = None):
		paths = self.get_paths(files, dirs)
		if paths:
			names = [os.path.basename(path) for path in paths]
			sublime.set_clipboard('\n'.join(names))

	def is_visible(self, files = None, dirs = None) -> bool:
		return len(self.get_paths(files, dirs)) > 0

