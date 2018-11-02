# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
# ------------------------------
import re
# ------------------------------

LOOK_BACK, LOOK_FORTH = 0, 10
SYNTAXES = [
	(r'<(/)?(\w+:)?\w+(\s+(\w+:)?\w+\s*=\s*"[^"]*")*(\s+/)?>',                'Packages/XML/XML.tmLanguage'),
	(r'(?i)(\$\w+|\[(\w+\.)*\w+\]::\w+|foreach\s*\{|@[(]|\s+-\w+|<[#]|[#]>)', 'Packages/PowerShell/Support/PowershellSyntax.tmLanguage'),
	(r'(^\s*(def|class))|(\):\s*)',                                           'Packages/Python/Python.tmLanguage'),
	(r'(?i)\b(select|update|from|inner|where|join)\b',                        'Packages/sublime_overlord/syntaxes/SQL Ex.tmLanguage'),
]

# ------------------------------

class overlord_detect_syntax(sublime_plugin.TextCommand):

	def detect_syntax(self, view):
		point = view.sel()[0].a
		(row, col) = view.rowcol(point)

		region = view.line(sublime.Region(view.text_point(row - LOOK_BACK, 0), view.text_point(row + LOOK_FORTH, 0)))
		s = view.substr(region)

		selected_syntax, count = '', 0
		for pattern, syntax in SYNTAXES:
			qty = len(re.findall(pattern, s))
			if qty > count:
				selected_syntax, count = syntax, qty

		if count > 0:
			view.set_syntax_file(selected_syntax)

		return region

	def run(self, edit):
		region = self.detect_syntax(self.view)

# ------------------------------
