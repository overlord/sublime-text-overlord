# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
# ------------------------------
class overlord_add_caret(sublime_plugin.TextCommand):
	'''
	Text Command: Умеет ставить новые курсоры через строчку
	'''
	def run(self, edit, skip_lines):
		view = self.view
		sels = view.sel()
		rowcols = [view.rowcol(sel.begin()) for sel in sels]
		row, col = rowcols[-1] if(skip_lines > 0) else rowcols[0]
		pt = view.text_point(row + skip_lines, col)
		sels.add(sublime.Region(pt))

# ------------------------------
