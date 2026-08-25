import sublime
import sublime_plugin
# ------------------------------
import json
import os
import re
import xml.dom.minidom
# ------------------------------
from sublime_overlord import overlord_json
# ------------------------------
DEBUG = False
def _trace(s):
	if DEBUG:
		print(f'[OVERLORD_INDENT] {s}')
# ------------------------------
class overlord_indent(sublime_plugin.TextCommand):
	def __init__(self, view):
		self.view = view
		self.language = self.get_language()

	def get_language(self):
		syntax_path = self.view.settings().get('syntax')
		syntax = os.path.basename(syntax_path).replace('.tmLanguage', '').replace('.sublime-syntax', '').lower()
		language = syntax if syntax else "plain text"
		_trace(f'{syntax=}, {language=}')
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

		enabled = self.check_enabled(self.language)
		_trace(f"{enabled=}")
		return enabled

	def run(self, edit):
		"""
		Main plugin logic for the 'indent' command.
		"""
		view = self.view
		regions = view.sel()
		first_line = view.line(regions[0]).begin()
		if len(regions) > 1 or not regions[0].empty():
			# if there are more than 1 region or region one and it's not empty
			for region in view.sel():
				if not region.empty():
					s = view.substr(region).strip()
					s = self.indent(s)
					view.replace(edit, region, s)
		else:
			# format all text
			alltextreg = sublime.Region(0, view.size())
			s = view.substr(alltextreg).strip()
			s = self.indent(s)
			view.replace(edit, alltextreg, s)
		view.show(first_line)
# ------------------------------
class overlord_auto_indent(overlord_indent):
	def get_text_type(self, s):
		if self.language == 'xml':
			return 'xml', s
		if self.language == 'json':
			return 'json', s
		# ------------------------------
		if not s:
			return 'unknown', s
		# ------------------------------
		if s.startswith('<'):
			return 'xml', s
		# ------------------------------
		s1, ok1 = overlord_json.try_json_unescape(s)
		if ok1 and s1.startswith('<'):
			return 'xml', s1
		# ------------------------------
		return 'json', s
		# ------------------------------
	# ------------------------------
	def indent(self, s):
		# ------------------------------
		text_type, s = self.get_text_type(s)
		# ------------------------------
		if text_type == 'unknown':
			return s
		# ------------------------------
		if text_type == 'xml':
			command = overlord_indent_xml(self.view)
		if text_type == 'json':
			command = overlord_indent_json(self.view)
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
		return (language == "xml") or ("plain text" in language)
# ------------------------------
class overlord_indent_json(overlord_indent):
	def check_enabled(self, language):
		return ((language == "json") or ("plain text" in language))

	def indent(self, s):
		parsed = json.loads(s)
		pretty = json.dumps(parsed, sort_keys=False, indent=4, separators=(',', ': '), ensure_ascii=False)

		try:
			inner_string = json.loads(s)
			if isinstance(inner_string, str):
				return inner_string
		except:
			pass

		return pretty
# ------------------------------
class overlord_indent_json_mixed(overlord_indent):

	DECODER = json.JSONDecoder()

	def check_enabled(self, language):
		return ((language == "json") or ("plain text" in language))

	def indent(self, s):
		parsed = json.loads(s)
		processed = self.__extract(parsed)
		pretty = json.dumps(processed, sort_keys=False, indent=4, separators=(',', ': '), ensure_ascii=False)
		return pretty

	def __extract(self, obj):
		if isinstance(obj, dict):
			return {k:self.__extract(v) for k, v in obj.items()}
		elif isinstance(obj, list):
			return [self.__extract(v)for v in obj]
		elif isinstance(obj, str) and ("{" in obj and "}" in obj):
			for i, c in enumerate(obj):
				if c == "{":
					try:
						p, e = self.DECODER.raw_decode(obj, i)
						pre = obj[:i].strip()
						if pre:
							return { "*text": pre, "*json": self.__extract(p) }
						return self.__extract(p)
					except:
						continue
		else:
			return obj
# ------------------------------
