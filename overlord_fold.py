# -*- coding: utf-8 -*-
import sublime
import sublime_plugin

OVERLORD_FOLD_LEVEL_INDEX = {}

class overlord_fold_dec(sublime_plugin.WindowCommand):
	def run(self):
		view = self.window.active_view()
		if view:
			level = max(1, OVERLORD_FOLD_LEVEL_INDEX.get(view, 1) - 1)
			# print(f"Fold to level {level}.")
			view.run_command("fold_by_level", { "level": level })
			OVERLORD_FOLD_LEVEL_INDEX[view] = level

class overlord_fold_inc(sublime_plugin.WindowCommand):
	def run(self):
		view = self.window.active_view()
		if view and len(view.folded_regions()) > 0:
			level = OVERLORD_FOLD_LEVEL_INDEX.get(view, 1) + 1
			# print(f"Fold to level {level}")
			view.run_command("fold_by_level", { "level": level })
			OVERLORD_FOLD_LEVEL_INDEX[view] = level
