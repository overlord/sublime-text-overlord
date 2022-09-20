# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
# ------------------------------
import re
# ------------------------------
LOOK_BACK, LOOK_FORTH = 0, 10

JSON = r'(?xi) ( " \s* : \s* " | \[ \s* { \s* " | " \s* : \s* \[ )'
POWERSHELL = r'(?i)(\$\w+|\[(\w+\.)*\w+\]::\w+|foreach\s*\{|@[(]|\s+-\w+|<[#]|[#]>)'
PYTHON = r'(^\s*(def|class))|(\):\s*)'
SQL = r'(?i)\b(select|update|from|inner|where|join)\b'
XML = r'<(/)?(\w+:)?\w+(\s+(\w+:)?\w+\s*=\s*"[^"]*")*(\s+/)?>'

SYNTAXES = [
	(XML,        'Packages/XML/XML.tmLanguage'),
	(POWERSHELL, 'Packages/PowerShell/Support/PowershellSyntax.tmLanguage'),
	(PYTHON,     'Packages/Python/Python.tmLanguage'),
	(SQL,        'Packages/sublime_overlord/syntaxes/SQL Ex.tmLanguage'),
	(JSON,       'Packages/JSON/JSON.tmLanguage'),
]

# ------------------------------
class overlord_detect_syntax(sublime_plugin.TextCommand):

	def detect_syntax(self, view):
		point = view.sel()[0].a
		row, col = view.rowcol(point)

		region = view.line(sublime.Region(view.text_point(row - LOOK_BACK, 0), view.text_point(row + LOOK_FORTH, 0)))
		s = view.substr(region)

		selected_syntax, count = '', 0
		for pattern, syntax in SYNTAXES:
			qty = len(re.findall(pattern, s))
			if qty > count:
				selected_syntax, count = syntax, qty

		if count > 0:
			print('Detected: %s' % (selected_syntax))
			view.set_syntax_file(selected_syntax)

		return region

	def run(self, edit):
		region = self.detect_syntax(self.view)

