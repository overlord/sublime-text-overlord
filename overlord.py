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
class overlord_insert_xyz(sublime_plugin.TextCommand):
	def run(self, edit, content, index):
		self.view.insert(edit, index, content)

# ------------------------------------------------------------------------------------------------------------------------
class ShowEncodingEventListener(sublime_plugin.EventListener):
	'''
	Listener: shows current file encoding in status bar on activation of view.
	'''
	def on_activated(self, view):
		sublime.status_message(view.encoding())

# ------------------------------------------------------------------------------------------------------------------------
class overlord_tab(sublime_plugin.TextCommand):
	'''
	Text Command: aligns selected regions with TAB or SPACE character in one vertical line.
	'''
	def run(self, edit, indent_type = "tab"):
		sel = self.view.sel()
		max_col = 0

		for r in sel:
			max_col = max(max_col, indentation.normed_indentation_pt(self.view, r))

		for r in sel:
			start = indentation.normed_indentation_pt(self.view, r)
			if start < max_col:
				gap = abs(start - max_col)

				if(indent_type == "tab"):
					count = gap / indentation.get_tab_size(self.view)
					char = '\t'
				elif(indent_type == "space"):
					count = gap
					char = ' '
				else:
					raise Exception("Unexpected indent_type '%s'" % indent_type)

				self.view.insert(edit, r.a, char * int(round(count, 1)))

# ------------------------------------------------------------------------------------------------------------------------
class overlord_diff(sublime_plugin.WindowCommand):
	'''
	Window Command: launches external diff tool to show diff between CURRENT and NEXT view.
	'''
	# ------------------------------
	def __run_diff(self, path, file1, file2, line):
		command = path.replace("'", '"').format(file1, file2, line).replace("\\", "/")
		print("[OVR] diff: %s" % command)
		subprocess.Popen(st2api.to_os_encoding(command))
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

# ------------------------------------------------------------------------------------------------------------------------
class overlord_number_items(sublime_plugin.TextCommand):
	'''
	Text Command: Вставляет нумерацию в текущие положения курсоров.
	'''
	def run(self, edit):
		sel = self.view.sel()
		total = len(sel)
		width = len(str(total))

		i = 1
		for r in sel:
			self.view.insert(edit, r.a, str(i).zfill(width))
			i += 1

# ------------------------------------------------------------------------------------------------------------------------
class overlord_insert_timestamp(sublime_plugin.TextCommand):
	'''
	Text Command: Вставляет слепок времени YYYYMMDDHHmmss.
	'''
	def run(self, edit):
		timestamp = '{:%Y%m%d%H%M%S}'.format(datetime.now())
		for r in self.view.sel():
			self.view.insert(edit, r.a, timestamp)

# ------------------------------------------------------------------------------------------------------------------------
class overlord_insert_datetime(sublime_plugin.TextCommand):
	'''
	Text Command: Вставляет слепок времени YYYY-MM-DD HH:mm:ss.
	'''
	def run(self, edit):
		timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
		for r in self.view.sel():
			self.view.insert(edit, r.a, timestamp)

# ------------------------------------------------------------------------------------------------------------------------
class overlord_insert_stairs(sublime_plugin.TextCommand):
	# ------------------------------
	def run(self, edit):
		i = 0
		for r in self.view.sel():
			self.view.insert(edit, r.a, '\t' * i)
			i += 1
# ------------------------------------------------------------------------------------------------------------------------
class overlord_clear_regions(sublime_plugin.TextCommand):
	'''
	Text Command: убирает в каждой строке символы, удовлетворяющие regex-у в pattern. По умолчанию удаляет пробелы в конце строк.
	'''
	def run(self, edit, pattern = r'[ \t]+$'):
		self.view.sel().clear()
		for r in self.view.find_all(pattern, sublime.IGNORECASE):
			for rs in self.view.split_by_newlines(r):
				self.view.sel().add(rs)
		self.view.run_command("right_delete")

# ------------------------------------------------------------------------------------------------------------------------
class overlord_open_custom_file(sublime_plugin.WindowCommand):
	def run(self, file_name):
		self.window.open_file(st2api.apply_custom_replace(file_name))

# ------------------------------------------------------------------------------------------------------------------------
class overlord_insert_string(sublime_plugin.TextCommand):
	'''
	Text Command: вставляет указанную строчку в текущие курсоры
	'''
	def run(self, edit, s, mutate = False):
		for r in self.view.sel():
			self.view.erase(edit, r)
			self.view.insert(edit, r.begin(), st2api.apply_custom_replace(s) if mutate else s)

# ------------------------------------------------------------------------------------------------------------------------
class overlord_testregex(sublime_plugin.TextCommand):
	def run(self, edit):
		r_content = sublime.Region(0, self.view.size())
		content = self.view.substr(r_content)
		# content = re.sub(ur'(\w)', ur'\1', content)

		content = re.sub(r'([ \t]*(#|;)+.*)\n', r'<!--\1-->\n', content)
		content = re.sub(r'\[(.*?)\].*(\n[^\[]*)', r'<element name="\1"> \2 </element>\n', content)
		content = re.sub(r'[ \t]*(\w+)\s*=\s*(\w+).*\n', r'<add name="\1" value="\2"/>\n', content)
		content = re.sub(r'((.|\n)*)', r'<root>\n\1</root>', content)

		self.view.erase(edit, r_content)
		self.view.insert(edit, 0, content)

# ------------------------------------------------------------------------------------------------------------------------
class overlord_rename_path(sublime_plugin.WindowCommand):
	'''
	Window Command: переименовывает текущий файл, запрашивая имя у пользователя
	'''
	def run(self):
		if self.is_visible():
			self.window.run_command('rename_path', {'paths': [self.window.active_view().file_name()]})
	def is_visible(self):
		view = self.window.active_view()
		return True if view and view.file_name() else False

# ------------------------------------------------------------------------------------------------------------------------
class overlord_duplicate_file(sublime_plugin.WindowCommand):
	'''
	Window Command: создает копию текущего файла, запрашивая имя у пользователя
	'''
	def run(self):
		if self.is_visible():
			self.target_item = self.get_target()
			self.execute()
	def is_visible(self):
		return self.get_target() is not None
	def get_target(self):
		if self.window and self.window.active_view() and self.window.active_view().file_name():
			return self.window.active_view().file_name()
		return None
	# ------------------------------
	def execute(self):
		if self.target_item:
			self.dir, self.file_name = os.path.split(self.target_item)
			self.window.show_input_panel('New name', self.file_name, self.__on_done, None, None)
	def __on_done(self, new_name):
		try:
			new_file_name = os.path.join(self.dir, new_name)
			if(not os.path.exists(new_file_name)):
				shutil.copyfile(self.target_item, new_file_name)
			self.window.open_file(new_file_name)
		except Exception as e:
			sublime.error_message("%s" % e)

# ------------------------------------------------------------------------------------------------------------------------
class overlord_duplicate_file2(overlord_duplicate_file):
	'''
	Window Command: создает копию текущего файла, запрашивая имя у пользователя
	'''
	def run(self, files):
		if self.is_visible(files):
			self.target_item = self.get_target(files)
			self.execute()
	def is_visible(self, files):
		return True if self.get_target(files) else False
	def get_target(self, files):
		if files:
			return files[0]
		return None

# ------------------------------------------------------------------------------------------------------------------------
class overlord_close(sublime_plugin.WindowCommand):
	'''
	Window Command: Заменяет штатный [close] по ctrl+w. Исправляет последовательность закрытий. Закрываются [все view] -> [folders] -> [st2].
	'''
	def run(self):
		window = self.window
		if len(window.views()) > 0:
			window.run_command('close')
		elif len(window.folders()) > 0:
			window.run_command('close_folder_list')
		else:
			window.run_command('close')

# ------------------------------------------------------------------------------------------------------------------------
class overlord_close_all_force(sublime_plugin.WindowCommand):
	'''
	Window Command: Закрывает все открытые view без сохранения.
	'''
	def run(self):
		if sublime.ok_cancel_dialog('Are you sure yo want to close all tabs without saving?', 'Yes, I am sure.'):
			for view in self.window.views():
				view.set_scratch(True)
			self.window.run_command('close_all')

# ------------------------------------------------------------------------------------------------------------------------
class overlord_save_all(sublime_plugin.WindowCommand):
	'''
	Window Command: Умеет массово сохранять все открытые view.
	'''
	def run(self, encoding="utf-8"):
		for view in self.window.views():
			# if view.is_dirty():
			view.run_command('save', { "encoding": encoding })

# ------------------------------------------------------------------------------------------------------------------------
class overlord_find_all(sublime_plugin.TextCommand):
	'''
	Text Command: делает find all для всех выделененых фрагментов
	'''
	def expand_region(self, regions):
		result = []
		for r in regions:
			items = map(lambda i: re.escape(i.strip().lower()), self.view.substr(r).split(','))
			result.extend(items)

		return sorted(set(result), key=result.index)

	def run(self, edit):
		initial = self.view.sel()[0]
		find_all_pattern = "\\b(%s)\\b" % '|'.join(self.expand_region(self.view.sel()))
		print(find_all_pattern)
		if find_all_pattern != '\\b()\\b':
			regions = self.view.find_all(find_all_pattern, sublime.IGNORECASE)
			if len(regions) > 0:
				self.view.sel().clear()
				for r in regions:
					self.view.sel().add(r)
				self.view.show(initial)

# ------------------------------------------------------------------------------------------------------------------------
GLOBAL_LAST_DIR_TO = ''

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

# ------------------------------------------------------------------------------------------------------------------------
class overlord_copy_open_file_path(sublime_plugin.WindowCommand):
	'''
	Window Command: копирует список открытых файлов в clipboard.
	'''
	def run(self):
		data = '\n'.join([view.file_name() for view in self.window.views() if view.file_name()])
		#!_!st2api.new_file(self.window, data, True)
		if data:
			sublime.set_clipboard(data)

# ------------------------------------------------------------------------------------------------------------------------
class overlord_copy_file_path(sublime_plugin.WindowCommand):
	'''
	Window Command: копирует пути к выбранным объектам в clipboard.
	'''
	def run(self, files = None, dirs = None):
		data = '\n'.join((files or []) + (dirs or []))
		#!_!st2api.new_file(self.window, data, True)
		if data:
			sublime.set_clipboard(data)

	def is_visible(self, files = None, dirs = None):
		return len(files or []) + len(dirs or []) > 0

class overlord_list_dir(sublime_plugin.WindowCommand):
	'''
	Window Command: выводит все файлы в папке в новое окно.
	'''
	def run(self, dirs = None):
		data = [os.path.join(root, fileName)
			for folder in (dirs or [])
			for (root, subdirs, files) in os.walk(folder)
			for fileName in files
		]
		if data:
			st2api.new_file(self.window, '\n'.join(data), True)

	def is_visible(self, dirs = None):
		return len(dirs or []) > 0

# ------------------------------------------------------------------------------------------------------------------------
class overlord_navigate_to_file(sublime_plugin.WindowCommand):
	def run(self):
		view = self.window.active_view()
		if view and view.file_name():
			subprocess.Popen(st2api.to_os_encoding('explorer /e, /select, "' + view.file_name() + '"'))

# ------------------------------------------------------------------------------------------------------------------------
class overlord_show_file_list(sublime_plugin.WindowCommand):
	'''
	Window Command: показывает панель с открытыми файлами, позволяет перейти на выбраный.
	'''
	def run(self):
		views = [view for view in self.window.views() if view.file_name()]
		views.sort(key = lambda i: os.path.split(i.file_name())[1].lower())
		menu = map(self.create_menu_item, views)
		st2api.show_quick_panel(self, menu, lambda i: self.view_selected(views[i]))
	def create_menu_item(self, view):
		head, tail = os.path.split(view.file_name())
		return [(u'→ ' if view.file_name() == self.window.active_view().file_name() else '') + tail, head]
	def view_selected(self, view):
		self.window.focus_view(view)

# ------------------------------------------------------------------------------------------------------------------------
class overlord_mark_region(sublime_plugin.WindowCommand):
	'''
	Window Command: позволяет размечать цветом выбраные элементы
	'''
	# ------------------------------
	KEY = 'overlord_mark_region'
	# for valid names see http://www.w3schools.com/html/html_colornames.asp
	COLORS = [
		'HotPink',
		'PowderBlue',
		'Turquoise',
		'Yellow',
	]
	# ------------------------------
	def substract(self, from_list, substract_list):
		regions = [i for i in from_list]
		for r in from_list:
			for r2 in substract_list:
				if r.intersects(r2):
					regions.remove(r)
		return regions
	# ------------------------------
	def run(self, command):
		if self.window and self.window.active_view():
			if command == 'add':
				colors = sublime.load_settings(SETTINGS_FILE).get('overlord_mark_region', {}).get('colors', self.COLORS)
				if len(colors) > 1:
					st2api.show_quick_panel(self, colors, lambda i: self.color_selected(colors[i]))
				else:
					self.color_selected(colors[0])
			elif command == 'remove':
				view = self.window.active_view()
				current = view.get_regions(self.KEY)
				regions = self.substract(current, view.sel())
				view.add_regions(self.KEY, regions, self.last_scope, '', sublime.PERSISTENT)
	# ------------------------------
	def color_selected(self, color):
		view = self.window.active_view()
		scope = 'markup.bgcolor.%s' % color
		self.last_scope = scope
		current = view.get_regions(self.KEY)
		regions = [r for r in view.sel()] + current
		view.add_regions(self.KEY, regions, scope, '', sublime.PERSISTENT)

# ------------------------------------------------------------------------------------------------------------------------
class overlord_input_panel_test(sublime_plugin.WindowCommand):
	def on_change(self, s):
		print("changed to: %s" % s)
	def on_done(self, s):
		print("done: %s" % s)
	def on_cancel(self):
		print('cancel')
	def run(self):
		panel = self.window.show_input_panel('caption', 'initial text', self.on_done, self.on_change, self.on_cancel)

# ------------------------------------------------------------------------------------------------------------------------
class overlord_goto_selected_symbol(sublime_plugin.WindowCommand):
	def run(self):
		window = self.window
		view = window.active_view()
		text = st2api.get_first_selected_text(view).strip()
		st2api.show_overlay(window, '@' + text)

# ------------------------------------------------------------------------------------------
class overlord_goto_selected_file(sublime_plugin.WindowCommand):
	def run(self):
		window = self.window
		view = window.active_view()
		text = st2api.get_first_selected_text(view).strip()
		st2api.show_file_overlay(window, text)

# ------------------------------------------------------------------------------------------------------------------------
class overlord_to_camel_case(sublime_plugin.WindowCommand):
	def run(self, capitalize=False):
		view = self.window.active_view()
		selection = reversed(st2api.get_selection(view))

		try:
			edit = view.begin_edit()
			for sel in selection:
				initial_content = content = view.substr(sel)
				if initial_content.find(' ') >= 0 or initial_content.find('_') >= 0:
					content = initial_content.replace('_', ' ')
					content = ''.join(x for x in content.title() if not x.isspace())
				content = content[:1].lower() + content[1:]
				if initial_content != content:
					view.replace(edit, sel, content)
		finally:
			view.end_edit(edit)

# ------------------------------------------------------------------------------------------------------------------------
class overlord_unquote_url(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		for sel in reversed(st2api.get_selection(view)):
			initial_content = view.substr(sel)
			content = unquote(initial_content)
			if initial_content != content:
				view.replace(edit, sel, content.replace(' ', '%20'))

# ------------------------------------------------------------------------------------------------------------------------
class overlord_sum_timespan(sublime_plugin.TextCommand):
	def run(self, edit, rxpattern, format, max_length):
		view = self.view
		delta = timedelta()

		selection = list(reversed(st2api.get_selection(view)))

		for sel in selection:
			content = view.substr(sel)
			found = re.search(rxpattern, content)
			if found:
				s = found.group(1) #!_!
				t = datetime.strptime(s[:max_length], format)
				delta += timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)

		view.insert(edit, selection[0].end(), '\n' + str(delta))
# ------------------------------------------------------------------------------------------------------------------------
class overlord_calc_elapsed(sublime_plugin.TextCommand):

	def get_item(self, items, index):
		region = items[index] if len(items) > index else None
		return (region, self.view.substr(region) if region else None)

	def run(self, edit):
		view = self.view
		deltas = []
		for selected_region in st2api.get_selection(view):
			region_lines = view.lines(selected_region)
			for index, line_region in enumerate(region_lines):
				(reg, line) = self.get_item(region_lines, index)
				(reg_next, line_next) = self.get_item(region_lines, index+1)
				if line and line_next:
					line_date = datetime.strptime(line[:19], "%Y-%m-%dT%H:%M:%S") # 2018-03-14T14:41:04
					line_next_date = datetime.strptime(line_next[:19], "%Y-%m-%dT%H:%M:%S") # 2018-03-14T15:41:04
					deltas.append((reg, line, line_next_date - line_date))
		if deltas:
			for (reg, line, delta) in list(reversed(deltas)):
				view.replace(edit, reg, "[%s] %s" % (str(delta), line))
# ------------------------------------------------------------------------------------------------------------------------
class overlord_test(sublime_plugin.WindowCommand):
	def run(self):
		print(__name__)

# ------------------------------------------------------------------------------------------------------------------------
class InsertionListener(sublime_plugin.EventListener):
	# def on_text_command(self, view, command_name, args):
	# 	print(command_name)
	# def on_window_command(self, window, command_name, args):
	# 	print(command_name)
	def on_post_window_command(self, window, command_name, args):
		if command_name in ['goto_symbol_in_project']:
			text = st2api.get_first_selected_text(window.active_view()).strip()
			window.run_command("insert", {"characters": text})

# ------------------------------------------------------------------------------------------------------------------------
# class AnyListener(sublime_plugin.EventListener):
# 	def on_new(self, view): # None	Called when a new buffer is created.
# 		print("on_new")
# 	def on_clone(self, view): # None	Called when a view is cloned from an existing one.
# 		print("on_clone")
# 	def on_load(self, view): # None	Called when the file is finished loading.
# 		print("on_load")
# 	def on_close(self, view): # None	Called when a view is closed (note, there may still be other views into the same buffer).
# 		print("on_close")
# 	def on_pre_save(self, view): # None	Called just before a view is saved.
# 		print("on_pre_save")
# 	def on_post_save(self, view): # None	Called after a view has been saved.
# 		print("on_post_save")
# 	def on_modified(self, view): # None	Called after changes have been made to a view.
# 		print("on_modified")
# 	def on_selection_modified(self, view): # None	Called after the selection has been modified in a view.
# 		print("on_selection_modified")
# 	def on_activated(self, view): # None	Called when a view gains input focus.
# 		print("on_activated")
# 	def on_deactivated(self, view): # None	Called when a view loses input focus.
# 		print("on_deactivated")
# 	def on_query_context(self, view, key, operator, operand, match_all): # bool or None
# 		print("on_query_context")

# ------------------------------------------------------------------------------------------------------------------------
