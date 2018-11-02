import sublime
import sublime_plugin
# ------------------------------
import json
import os
import re
import xml.dom.minidom
# ------------------------------
class overlord_indent(sublime_plugin.TextCommand):
	def __init__(self, view):
		self.view = view
		self.language = self.get_language()

	def get_language(self):
		syntax = self.view.settings().get('syntax')
		language = os.path.basename(syntax).replace('.tmLanguage', '').lower() if syntax != None else "plain text"
		return language

	def check_enabled(self, lang):
		return True

	def is_enabled(self):
		"""
		Enables or disables the 'indent' command.
		Command will be disabled if there are currently no text selections and current file is not 'XML' or 'Plain Text'.
		This helps clarify to the user about when the command can be executed, especially useful for UI controls.
		"""
		if self.view == None:
			return False

		return self.check_enabled(self.get_language())

	def run(self, edit):
		"""
		Main plugin logic for the 'indent' command.
		"""
		view = self.view
		regions = view.sel()
		first_line = view.line(regions[0]).begin()
		# if there are more than 1 region or region one and it's not empty
		if len(regions) > 1 or not regions[0].empty():
			for region in view.sel():
				if not region.empty():
					s = view.substr(region).strip()
					s = self.indent(s)
					view.replace(edit, region, s)
		else:   #format all text
			alltextreg = sublime.Region(0, view.size())
			s = view.substr(alltextreg).strip()
			s = self.indent(s)
			view.replace(edit, alltextreg, s)
		view.show(first_line)
# ------------------------------
class overlord_auto_indent(overlord_indent):
	def get_text_type(self, s):
		# ------------------------------
		if self.language == 'xml':
			return 'xml'
		if self.language == 'json':
			return 'json'
		# ------------------------------
		if s:
			if s[0] == '<':
				return 'xml'
			if s[0] == '{' or s[0] == '[':
				return 'json'
		# ------------------------------
		return 'notsupported'
	# ------------------------------
	def indent(self, s):
		# ------------------------------
		text_type = self.get_text_type(s)
		# ------------------------------
		if text_type == 'xml':
			command = overlord_indent_xml(self.view)
		if text_type == 'json':
			command = overlord_indent_json(self.view)
		if text_type == 'notsupported':
			return s
		# ------------------------------
		return command.indent(s)
	# ------------------------------
	def check_enabled(self, lang):
		return True
# ------------------------------
class overlord_indent_xml(overlord_indent):

	def indent(self, s):
		xmlheader = re.compile("<\?.*\?>").match(s)
		# convert to plain string without indents and spaces
		s = re.compile('>\s+([^\s])', re.DOTALL).sub('>\g<1>', s)
		# replace tags to convince minidom process cdata as text
		s = s.replace('<![CDATA[', '%CDATAESTART%').replace(']]>', '%CDATAEEND%')

		s = xml.dom.minidom.parseString(s).toprettyxml()

		# remove line breaks
		s = re.compile('>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL).sub('>\g<1></', s)
		# restore cdata
		s = s.replace('%CDATAESTART%', '<![CDATA[').replace('%CDATAEEND%', ']]>')
		# remove xml header
		s = s.replace("<?xml version=\"1.0\" ?>", "").strip()
		if xmlheader:
			s = xmlheader.group() + "\n" + s

		return s

	def check_enabled(self, language):
		return (language == "xml") or (language == "plain text")
# ------------------------------
class overlord_indent_json(overlord_indent):
	def check_enabled(self, language):
		return ((language == "json") or (language == "plain text"))

	def indent(self, s):
		parsed = json.loads(s)
		pretty = json.dumps(parsed, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
		return pretty
# ------------------------------
