# -*- coding: utf-8 -*-
import sublime_plugin

# --------------------------------------------------------------------------------------------------------------

def show_scope_name(view):
	return
	sel = view.sel()
	point = sel[0].a
	if(view.prev_point == point):
		return
	name = view.scope_name(point).strip()
	print(name)
	if(name == "source.python"):
		return
	sel.clear()
	sel.add(view.extract_scope(point))
	view.prev_point = point

# --------------------------------------------------------------------------------------------------------------

class ScopeObserverEventListener(sublime_plugin.EventListener):

	def on_selection_modified(self, view): # -> None | Called after the selection has been modified in a view.
		view.prev_point = 0
		show_scope_name(view)

# --------------------------------------------------------------------------------------------------------------
