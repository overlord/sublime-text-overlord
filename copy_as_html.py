# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
# ------------------------------
if sublime.version() >= '3000':
	from sublime_overlord.lib import (st2api, winclip)
else:
	from lib import (st2api, winclip)
# ------------------------------
import datetime
import os
import plistlib
import re
import sys
import tempfile
# ------------------------------------------------------------------------------------------
HEADER = \
"""<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
	<meta http-equiv="content-type" content="text/html; charset=UTF-8">
	<title>%(fname)s</title>
"""
# ------------------------------------------------------------------------------------------
def get_element(element_name, fgcolor, bgcolor, font):
	return '<%s %s>' % (element_name, get_style(fgcolor, bgcolor, font))
# ------------------------------------------------------------------------------------------
def get_style(fgcolor, bgcolor, font):
	styles = []
	# styles = ['border: 0', 'margin: 0', 'padding: 0', 'display: inline']
	if fgcolor:
		styles.append('color: %s' % fgcolor)
	if bgcolor:
		styles.append('background-color: %s' % bgcolor)
	if font:
		font_face, font_size = font
		styles.append("font: %dpt '%s'" % (font_size, font_face))
	# ------------------------------
	return 'style="' + '; '.join(styles) + ';"'
# ------------------------------------------------------------------------------------------
def dt_stamp():
	return datetime.datetime.now().strftime("%d/%m %H:%M")
# ------------------------------------------------------------------------------------------
def escape_html(text, reverse=False):
	if reverse:
		return text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
	else:
		return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
# ------------------------------------------------------------------------------------------
def append_encoded(items, s):
	if sublime.version() >= '3000':
		items.append(s)
	else:
		items.append(unicode(s))
# ------------------------------------------------------------------------------------------
class overlord_copy_as_html(sublime_plugin.TextCommand):
	# ------------------------------
	def setup(self):
		# ------------------------------
		path_packages = sublime.packages_path()
		# ------------------------------
		self.file_name = self.view.file_name()
		if self.file_name == None or not os.path.exists(self.file_name):
			self.file_name = "Untitled"
		# ------------------------------ Get general document preferences from sublime preferences
		settings = sublime.load_settings('Preferences.sublime-settings')
		self.font = settings.get('font_face', 'Consolas'), self.config.get('font_size', settings.get('font_size', 10))
		self.tab_size = self.config.get('tab_size', settings.get('tab_size', 4))
		# ------------------------------ Get color scheme
		scheme_file = self.config.get("color_scheme", self.view.settings().get('color_scheme'))
		colour_scheme = os.path.normpath(scheme_file)
		plist_file = plistlib.readPlist(path_packages + colour_scheme.replace('Packages', ''))
		color_settings = plist_file["settings"][0]["settings"]
		# ------------------------------ Get general theme colors from color scheme file
		self.bgcolor = color_settings.get('background', '#FFFFFF')
		self.bgcolor = self.config.get('white_bgcolor', '#FFFFFF') if self.bgcolor == '#FFFFFF' else self.bgcolor
		self.fgcolor = color_settings.get('foreground', '#000000')
		# ------------------------------ Determine start and end points and whether to parse whole file or selection
		curr_sel = self.view.sel()[0]
		if curr_sel.empty() or len(self.view.lines(curr_sel)) < 2:              # don't print just 1 line
			self.size = self.view.size()
			self.pt, self.end = (0, 1)   # partial = False: print entire view
		else:
			self.size = curr_sel.end()
			self.pt = curr_sel.begin()
			self.end = self.pt + 1
		# ------------------------------ Create scope colour-mapping from colour-scheme file
		self.colors = { self.view.scope_name(self.end).split(' ')[0]: self.fgcolor }
		for item in plist_file["settings"]:
			scope = item.get('scope', None)
			if 'settings' in item and 'foreground' in item['settings']:
				colour = item['settings']['foreground']
			else:
				colour = None
			if scope != None and colour != None:
				self.colors[scope] = colour
	# ------------------------------
	def guess_color(self, the_key):
		the_color = None
		if the_key in self.colors:
			the_color = self.colors[the_key]
		else:
			best_match = 0
			for key in self.colors:
				if self.view.score_selector(self.pt, key) > best_match:
					best_match = self.view.score_selector(self.pt, key)
					the_color = self.colors[key]
			self.colors[the_key] = the_color or self.fgcolor
		# ------------------------------
		return the_color or self.fgcolor
	# ------------------------------
	def write_header(self, formatted_text):
		append_encoded(formatted_text, HEADER % {"fname": self.file_name})
		append_encoded(formatted_text, '</head>\n<body>\n<br />\n')
	# ------------------------------
	def write_body(self, formatted_text, plain_text):
		if self.config.get('include_file_name', False):
			append_encoded(formatted_text, get_element('pre', self.fgcolor, self.bgcolor, self.font))
			append_encoded(formatted_text, '%s - %s</pre>' % (self.file_name, dt_stamp()))
		self.convert_view_to_html(formatted_text, plain_text)         # convert view to HTML
	# ------------------------------
	def write_footer(self, formatted_text):
		append_encoded(formatted_text, '</body>\n</html>')
	# ------------------------------
	def convert_view_to_html(self, formatted_text, plain_text):
		# ------------------------------
		selection = list(map(lambda i: i, self.view.sel()))
		if (len(selection) == 1) and (selection[0].size() == 0): # nothing selected - just cursor
			selection = [sublime.Region(0, self.view.size())]
		# ------------------------------
		for region in selection:
			append_encoded(formatted_text, get_element('pre', self.fgcolor, self.bgcolor, None))
			append_encoded(plain_text, self.view.substr(region).strip('\r\n') + '\n\n')
			# ------------------------------
			for line in self.view.split_by_newlines(region):
				self.pt = line.begin()
				self.end = self.pt + 1
				if line.empty():
					append_encoded(formatted_text, '\n')
					continue
				self.line_end = line.end()
				line_items = []
				# ------------------------------
				while self.end <= self.line_end:
					scope_name = self.view.scope_name(self.pt)
					while (self.end < self.line_end
						and (
							self.view.scope_name(self.end) == scope_name
							or (self.view.substr(self.end) in ('\t', ' ', ''))
						)
					):
						self.end += 1
					# ------------------------------
					region = sublime.Region(self.pt, self.end)
					if region.empty():
						self.pt = self.end
						self.end = self.pt + 1
						continue
					# ------------------------------
					the_color = self.guess_color(scope_name.strip())
					the_text = self.view.substr(region)
					the_text = escape_html(the_text).replace('\t', ' ' * self.tab_size).strip('\r\n')
					line_items.append((the_color, the_text))
					# ------------------------------
					self.pt = self.end
					self.end = self.pt + 1
				# ------------------------------
				if line_items:
					html_line = ''
					for (the_color, the_text) in line_items:
						html_line += get_element('span', the_color, None, self.font) + the_text + '</span>'
						# html_line += get_element('span', the_color, self.bgcolor, self.font) + the_text + '</span>'
					append_encoded(formatted_text, html_line + '\n')
					line_items[:] = []
			# ------------------------------
			append_encoded(formatted_text, '</pre>\n')
			append_encoded(formatted_text, '<br />\n')
	# ------------------------------
	def run(self, edit):
		# ------------------------------
		self.config = sublime.load_settings("copy_as_html.sublime-settings")
		window = sublime.active_window()
		view = window.active_view() if window != None else None
		if view is None or view.id() != self.view.id():
			sublime.status_message('Click into the view/tab first.')
			return
		# ------------------------------
		self.setup()
		# ------------------------------
		formatted_text = []
		plain_text = []
		self.write_header(formatted_text)
		self.write_body(formatted_text, plain_text)
		self.write_footer(formatted_text)
		html_content = ''.join(formatted_text)
		flat_content = ''.join(plain_text)
		# ------------------------------
		winclip.Paste(html_content, 'html', flat_content)
		# ------------------------------ for debug purpose
		# new_view = st2api.new_file(window, html_content, True)
		# new_view.set_syntax_file('Packages/HTML/HTML.tmLanguage')
	# ------------------------------
# ------------------------------------------------------------------------------------------
