# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
# ------------------------------
if sublime.version() >= '3000':
	from sublime_overlord.lib import (st2api)
	import Default.indentation as indentation
	from urllib.parse import unquote as unquote
else:
	from lib import (st2api)
	import indentation
	from urllib import unquote_plus as unquote
# ------------------------------
import collections
from datetime import datetime, timedelta
import json
import os
import re
import shutil
import subprocess
# ------------------------------------------------------------------------------------------------------------------------
# Привет, друзья! Я обычный русский букв!
# ------------------------------------------------------------------------------------------------------------------------
SETTINGS_FILE = "overlord.sublime-settings"

# ------------------------------------------------------------------------------------------------------------------------
class overlord_diff(sublime_plugin.WindowCommand):
	'''
	Window Command: launches external diff tool to show diff between CURRENT and NEXT view.
	'''
	# ------------------------------
	def __run_diff(self, path, file1, file2, line):
		command = path.replace("'", '"').format(file1, file2, line).replace("\\", "/")
		command = st2api.to_os_encoding(command)
		command = f'start /MAX "" {command}'
		print("[OVR] diff: %s" % command)
		subprocess.Popen(
			command,
			shell=True,
			creationflags=subprocess.CREATE_NO_WINDOW
		)
	# ------------------------------
	def run_diff(self, tool, file1, file2, line=0):
		# ------------------------------
		tools = sublime.load_settings(SETTINGS_FILE).get('diff_tools', {})
		# ------------------------------
		if tool is None:
			menu = sorted([i for i in tools])
			st2api.show_quick_panel(self, menu, lambda i: self.__run_diff(tools[menu[i]], file1, file2, line))
		elif tool in tools:
			self.__run_diff(tools[tool], file1, file2, line)
		else:
			sublime.error_message('Unable to find diff_tool: "%s" in "%s"' % (tool, SETTINGS_FILE))
	# ------------------------------
	def run(self, tool=None):
		'''
		Valid 'tool' options (CI): TortoiseSVN, AraxisMerge, WinMerge, KDiff
		'''
		# ------------------------------
		view = self.window.active_view()
		sel = st2api.get_selection(view)
		# ------------------------------
		if len(sel) == 2:
			self.run_diff(tool, st2api.tmp_dump_region(view, sel[0]), st2api.tmp_dump_region(view, sel[1]))
			return
		# ------------------------------
		view1, view2 = self.extract_diff_view(view.window(), view)
		# ------------------------------
		if view1 and view2:
			if tool is None:
				tool = view1.settings().get("diff_tool")
			if tool is None:
				tool = sublime.load_settings("Preferences.sublime-settings").get('diff_tool', None)
			file1, file2 = self.extract_diff_content(view1, view2)
			row, col = view.rowcol(sel[0].begin())
			self.run_diff(tool, file1, file2, row)
	# ------------------------------
	def extract_diff_view(self, window, view):
		views = window.views()
		index = window.get_view_index(view)[1]
		index_last = len(views) - 1
		view1, view2 = None, None
		# ------------------------------
		if index_last > 0: # если есть, что сравнивать
			if(index == index_last): # если выбран последний
				view1, view2 = views[index-1], views[index]
			elif(index != index_last): # если выбран не последний
				view1, view2 = views[index], views[index+1]
		# ------------------------------
		return view1, view2
	# ------------------------------
	def extract_diff_content(self, view1, view2):
		sel1 = view1.sel()
		sel2 = view2.sel()
		print(len(sel1[0]))
		print(len(sel2[0]))
		if len(sel1) == 1 and len(sel1[0]) > 0 and len(sel2) == 1 and len(sel2[0]) > 0:
			file1 = st2api.tmp_dump_region(view1, sel1[0])
			file2 = st2api.tmp_dump_region(view2, sel2[0])
		else:
			file1 = st2api.tmp_get_file_name(view1)
			file2 = st2api.tmp_get_file_name(view2)
		return file1, file2
	# ------------------------------
	def is_visible(self, tool=None):
		return True if self.window.active_view() else False
	# ------------------------------
	def description(self, tool=None):
		return "Compare..." if tool is None else "Compare using %s..." % tool

class overlord_diff_unsaved(overlord_diff):
	# ------------------------------
	def run(self, tool=None):
		# ------------------------------
		view = self.window.active_view()
		# ------------------------------
		unsaved_changes_file = st2api.tmp_dump_view(view)
		saved_changes_file = view.file_name()
		# ------------------------------
		row, col = view.rowcol(view.sel()[0].begin())
		self.run_diff(tool, saved_changes_file, unsaved_changes_file, row)
	# ------------------------------
	def is_visible(self, tool=None):
		view = self.window.active_view()
		return True if view and view.file_name() and view.is_dirty() else False
	# ------------------------------
	def description(self, tool=None):
		return "Compare unsaved..." if tool is None else "Compare unsaved using %s..." % tool
