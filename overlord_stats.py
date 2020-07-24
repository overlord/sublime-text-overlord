# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
# ------------------------------
if sublime.version() >= '3000':
	from sublime_overlord.lib import (st2api)
else:
	from lib import (st2api)
# ------------------------------------------------------------------------------------------
def trace(s):
	print(s)
# ------------------------------------------------------------------------------------------
class overlord_line_stats(sublime_plugin.WindowCommand):
	# ------------------------------
	def run(self):
		window = self.window
		if window and window.active_view():
			view = window.active_view()
			if view:
				counter = {}
				for line_region in view.split_by_newlines(sublime.Region(0, view.size())):
					value = view.substr(line_region)
					if(value not in counter):
						counter[value] = 0
					counter[value] = counter[value]+1;

				content = "\n".join(["% 6d\t%s" % (counter[key], key) for key in counter])

				st2api.new_file(window, content, is_scratch=True, name=None)
# ------------------------------------------------------------------------------------------
