# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
# ------------------------------
if sublime.version() >= '3000':
	from sublime_overlord.lib import (st2api)
else:
	from lib import (st2api)
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
def first_or_default(p_list, p_default):
	return p_list[0] if p_list else p_default

# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
class TotalRecallManager():
	# ------------------------------
	_back_steps = []
	_forw_steps = []
	_real_prev_step = None, None
	# ------------------------------
	_enabled = True
	allow_same_line = True
	max_lines = 3
	max_step_count = 50
	# ------------------------------
	def set_enabled(self, value):
		self._enabled = value
	# ------------------------------
	def is_enabled(self):
		return self._enabled
	# ------------------------------
	def _add_step(self, target, view_id, row):
		step = view_id, row
		if not self.allow_same_line and step in target:
			target.remove(step)
		target.insert(0, step)
	# ------------------------------
	def add_back_step(self, view):
		if not (self.is_enabled() and view and view.window() and st2api.get_view_by_id(view.id())):
			return
		# --
		pview_id, prow = first_or_default(self._back_steps, (None, None))
		view_id, row = view.id(), st2api.selected_row_single_or_default(view, None)
		real_pview_id, real_prow = self._real_prev_step
		# --
		if not row:
			return
		# --
		if real_pview_id == view_id and abs(row - real_prow) <= self.max_lines:
			self._real_prev_step = view_id, row
		else:
			self._real_prev_step = view_id, row
			# --
			if pview_id != view_id or prow != row:
				self._add_step(self._back_steps, view_id, row)
				# --
				self._forw_steps = []
				# --
				if len(self._back_steps) > self.max_step_count:
					self._back_steps = self._back_steps[0 : self.max_step_count]
	# ------------------------------
	def _pop_step(self, source, cur_view_id, cur_row, target):
		while True:
			if not source:
				return None, None
			step = view_id, row = source.pop(0)
			if st2api.get_view_by_id(view_id):
				target.insert(0, step)
				if cur_view_id != view_id or cur_row != row:
					return step
	# ------------------------------
	def _make_step(self, cur_view, source, target):
		return self._pop_step(source, cur_view.id(), st2api.selected_row_single_or_default(cur_view, -1), target)
	# ------------------------------
	def step_back(self, view):
		return self._make_step(view, self._back_steps, self._forw_steps)
	# ------------------------------
	def step_forw(self, view):
		return self._make_step(view, self._forw_steps, self._back_steps)

# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
manager = TotalRecallManager()
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
class TotalRecallEventListener(sublime_plugin.EventListener):
	def on_selection_modified(self, view):
		manager.add_back_step(view)
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
class overlord_total_recall(sublime_plugin.TextCommand):
	# ------------------------------
	def run(self, edit, mode):
		if not manager.is_enabled():
			return
		# --
		try:
			view_id, row = None, None
			manager.set_enabled(False)
			# --
			if mode == 'back':
				view_id, row = manager.step_back(self.view)
			elif mode == 'forw':
				view_id, row = manager.step_forw(self.view)
			# --
			if view_id:
				view = st2api.get_view_by_id(view_id)
				window = st2api.get_window_for_view_id(view_id)
				window.focus_view(view)
				view.run_command('goto_line', { 'line': row + 1 } )
			# --
		finally:
			sublime.set_timeout(lambda: manager.set_enabled(True), 50)

# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
