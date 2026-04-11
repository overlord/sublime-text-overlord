# -*- coding: utf-8 -*-
import sublime
import sublime_plugin

OVERLORD_FOLD_LEVEL_INDEX = {}

class overlord_fold(sublime_plugin.WindowCommand):
	def has_folded(self):
		view = self.window.active_view()
		return len(view.folded_regions()) > 0

	def get_folded_size(self):
		view = self.window.active_view()
		return sum(region.size() for region in view.folded_regions())

	def get_indent(self):
		view = self.window.active_view()
		point = view.sel()[0].begin()
		return view.indentation_level(point)

	def get_level(self):
		view = self.window.active_view()
		return OVERLORD_FOLD_LEVEL_INDEX.get(view, None)

	def set_level(self, level):
		view = self.window.active_view()
		OVERLORD_FOLD_LEVEL_INDEX[view] = level

	def fold(self, level):
		view = self.window.active_view()
		view.run_command("fold_by_level", { "level": level })

class overlord_fold_dec(overlord_fold):
	def run(self):
		level = self.get_level() or (self.get_indent() + 1)
		level = max(1, level - 1)

		folded_before = self.get_folded_size()
		self.fold(level)
		folded_after = self.get_folded_size()

		if folded_before != folded_after:
			self.set_level(level)

		# print(f"DEC: {level=}; {folded_before} -> {folded_after}")

class overlord_fold_inc(overlord_fold):
	def run(self):
		if not self.has_folded(): return

		level = (self.get_level() or 0) + 1

		self.fold(level)
		self.set_level(level)

		# print(f"INC: {level=}")
