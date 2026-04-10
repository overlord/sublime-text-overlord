# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
# ------------------------------
import codecs
import getpass
import locale
import os
import stat
import sys
import threading
from uuid import uuid4

# ------------------------------------------------------------------------------------------
# ST CORE WRAPPER FUNCTIONS
# ------------------------------------------------------------------------------------------
def show_overlay(target, text):
	xget_window(target).run_command('show_overlay', { 'overlay': 'goto', 'text': text, 'show_files': False })

def show_file_overlay(target, text):
	xget_window(target).run_command('show_overlay', { 'overlay': 'goto', 'text': text, 'show_files': True })

def insert_in_active_view(target, text):
	xget_window(target).run_command('insert', { 'characters': text } )

# ------------------------------------------------------------------------------------------
def get_view_by_id(p_view_id):
	for window in sublime.windows():
		for view in window.views():
			if view.id() == p_view_id:
				return view
	return None

def get_window_for_view_id(p_view_id):
	for window in sublime.windows():
		for view in window.views():
			if view.id() == p_view_id:
				return window
	return None

# ------------------------------------------------------------------------------------------
def exist(p_item):
	if isinstance(p_item, sublime.Region):
		return p_item is not None #!_! "is not None" is essential for sublime.Region
	else:
		return True if p_item else False

def get_sel0(p_view):
	return p_view.sel()[0] if exist(p_view) else None

def get_sel0_single(p_view):
	if exist(p_view) and len(p_view.sel()) != 1:
		return None
	return get_sel0(p_view)

def word(p_view, p_region):
	if exist(p_view) and exist(p_region):
		return p_view.word(p_region)
	return None

def substr(p_view, p_region):
	if exist(p_view) and exist(p_region):
		return p_view.substr(p_region)
	return None

def word_substr(p_view, p_region):
	return substr(p_view, word(p_view, p_region))

# ------------------------------------------------------------------------------------------
def selected_row_single_or_default(p_view, p_default):
	sel0 = get_sel0_single(p_view)
	if exist(sel0):
		line = p_view.line(sel0)
		row, _ = p_view.rowcol(line.begin())
		return row
	return p_default

# ------------------------------------------------------------------------------------------
def select_region_begin(p_view, p_region):
	if exist(p_view) and exist(p_region):
		p_view.sel().clear()
		p_view.sel().add(p_region.begin())

def goto_region_begin(p_view, p_region):
	if exist(p_view) and exist(p_region):
		p_view.show_at_center(p_region.begin())

# ------------------------------------------------------------------------------------------
def executable_path():
	if sublime.version() >= '3000':
		return sublime.executable_path()
	else:
		return sys.executable

# ------------------------------------------------------------------------------------------
def _region(view, start=0, end=None):
	return sublime.Region(start, end if end else view.size())

def get_region(view, start=0, end=None):
	return _region(view, start, end) if view else None

def get_first_selected_text(view):
	return view.substr(get_sel0(view)) if exist(view) else ''

def get_text(view, start=0, end=None):
	return view.substr(_region(view, start, end)) if view else ''

def set_text(view, edit, content):
	view.replace(edit, _region(view), content)

def get_cursor_position(view):
	return view.rowcol(get_sel0(view).begin())

def set_cursor_position(view, position):
	row, col = position
	point = view.text_point(row, 0)
	r = _region(view, point, point)
	view.sel().clear()
	view.sel().add(r)
	sublime.set_timeout(lambda: view.show(r), 100)

def get_selection(view):
	if not view:
		return []

	actual_selection = view.sel()
	if len(actual_selection) == 1 and actual_selection[0].empty():
		return [_region(view)]

	result = []
	for sel in actual_selection:
		if not sel.empty():
			result.append(sel)

	return result

# def get_selection_split_by_newline(view):
# 	if view:

# 		selection = view.sel()
# 		if len(selection) == 1 and selection[0].empty():
# 			return view.split_by_newline( _region(view)

# 		result = []
# 		for sel in selection:
# 			if not sel.empty():
# 				result.append(sel)

# 	return []


# ------------------------------------------------------------------------------------------
class overlord_runner_thread(threading.Thread):
	# ------------------------------
	def __init__(self, method):
		super(overlord_runner_thread, self).__init__()
		self.method = method
		self.success = False
		self.message = ""
	# ------------------------------
	def run(self):
		self.success, self.message = self.method()

# ------------------------------------------------------------------------------------------
#  HELPERS
# ------------------------------------------------------------------------------------------

def append_content(view, content):
	view.run_command('overlord_insert_xyz', {'content': content, 'index': view.size()})

def new_file(window, content, is_scratch=False, name=None):
	view = window.new_file()
	while(view.is_loading()): pass
	view.set_scratch(is_scratch)
	append_content(view, content)
	if name:
		view.set_name(name)
	return view

def to_os_encoding(content):
	if sublime.version() >= '3000':
		return content
	else:
		return content.encode(locale.getpreferredencoding())

def from_os_encoding(content):
	if sublime.version() >= '3000':
		return content
	else:
		return content.decode(locale.getpreferredencoding())

def xget_window(obj):
	if isinstance(obj, sublime_plugin.WindowCommand):
		return obj.window
	elif isinstance(obj, sublime_plugin.TextCommand):
		return obj.view.window()
	elif isinstance(obj, sublime.View):
		return obj.window() or get_window_for_view_id(obj.id())
	elif isinstance(obj, sublime.Window):
		return obj
	else:
		raise Exception('Unknown obj: %s' % obj)

def show_quick_panel(target, items, on_done, flags=None, on_cancel=None):
	def __on_done(index):
		on_cancel() if index < 0 else on_done(index)
	# ------------------------------
	window = xget_window(target)
	# ------------------------------
	if on_cancel is None:
		on_cancel = lambda: None
	# ------------------------------
	if flags:
		window.show_quick_panel(items, __on_done, flags)
	else:
		window.show_quick_panel(items, __on_done)

def apply_custom_replace(s):
	s = s.replace("${packages}", sublime.packages_path())
	s = s.replace("${guid}", str(uuid4()))
	s = os.path.expandvars(s)
	return s

def tmp_dump(dump_object, temp_root="c:/temp"):
	if isinstance(dump_object, (str, unicode)):
		return tmp_dump_content(dump_object, temp_root)
	elif isinstance(dump_object, sublime.View):
		return tmp_dump_view(dump_object, temp_root)
	else:
		raise TypeError('Unknown type of dump_object=[%s]' % str(type(dump_object)))

def tmp_dump_region(view, region, temp_root="c:/temp"):
	return tmp_dump_content(view.substr(region), temp_root)

def tmp_dump_view(view, temp_root="c:/temp"):
	return tmp_dump_content(get_text(view), temp_root)

def tmp_dump_content(content, temp_root="c:/temp"):
	index = 0
	fileName = ''
	while(True):
		fileName = temp_root + '/temp' + str(index) + '.txt'

		if(not os.path.exists(fileName)):
			break;

		if(index > 500):
			sublime.message_dialog('Cleanup folder "%s/" - remove files "temp*.txt"' % temp_root);
			return None

		index = index + 1;

	tempFile = codecs.open(fileName, "w", "utf-8-sig")
	tempFile.write(content)
	tempFile.close()

	return fileName

def tmp_get_file_name(view):
	return tmp_dump_view(view) if (view.file_name() == None) else view.file_name()

# ------------------------------------------------------------------------------------------

def is_readonly(path):
	try:
		return not os.stat(path)[0] & stat.S_IWRITE
	except WindowsError:
		return None

# ------------------------------------------------------------------------------------------
