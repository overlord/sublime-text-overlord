# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
# ------------------------------
if sublime.version() >= '3000':
	from sublime_overlord.lib import (st2api)
else:
	from lib import (st2api)
# ------------------------------
import re
# ------------------------------------------------------------------------------------------
def first_or_default(p_list, p_default):
	return p_list[0] if p_list else p_default
# ------------------------------------------------------------------------------------------
def trace(s):
	print(s)
# ------------------------------------------------------------------------------------------
class overlord_goto_definition_plsql(sublime_plugin.WindowCommand):
	PLSQL_PATTERN = '''(?xi)
		^[ \t]*
		(
			( ( procedure | function ) \s+ {0} [ \t]* ($ | \() ) |
			( {0} \s+ constant \s+ ) |
			( type \s+ {0} \s+ is )
		)
		'''
	# ------------------------------
	def pick_item(self, items):
		if items:
			if len(items) == 1:
				return items[0]
			elif len(items) == 2:
				return items[1]
		return None
	# ------------------------------
	def run(self):
		# trace('plsql.py/overlord_goto_definition_plsql.run')
		window = self.window
		if window and window.active_view():
			view = window.active_view()
			sel0 = st2api.get_sel0(view)
			# trace('sel0: %s' % sel0)
			word = st2api.word_substr(view, sel0)
			# trace('word: %s' % word)
			if word:
				split_by_dot = word.split('.')
				if len(split_by_dot) == 2:
					package, method = split_by_dot
					# trace('package, method: %s; %s' % (package, method))
					st2api.show_file_overlay(window, package)
					st2api.insert_in_active_view(window, '#')
					st2api.insert_in_active_view(window, method)
				else:
					pattern = self.PLSQL_PATTERN.replace('{0}', re.escape(word))
					# trace('pattern: %s' % pattern)
					item = self.pick_item(view.find_all(pattern))
					if item:
						st2api.select_region_begin(view, item)
						st2api.goto_region_begin(view, item)
# ------------------------------------------------------------------------------------------
class overlord_goto_line_plsql(sublime_plugin.TextCommand):
	PLSQL_PATTERN = '(?xi) create \s+ or \s+ replace \s+ (package) \s+ body'
	# ------------------------------
	def run(self, edit):
		view = self.view
		window = view.window()
		window.show_input_panel('Line number:', "", lambda line_number: self.__on_done(line_number, view), None, None)
	# ------------------------------
	def __on_done(self, s_line_number, view):
		if s_line_number and s_line_number.isdigit() and view:
			line_number = int(s_line_number)
			rg0 = first_or_default(view.find_all(self.PLSQL_PATTERN), None)
			if rg0:
				row, _ = view.rowcol(rg0.begin())
				line_number = line_number + row
			view.run_command("goto_line", { "line": line_number })
# ------------------------------------------------------------------------------------------
class overlord_plsql_select_keywords(sublime_plugin.TextCommand):
	PATTERN = '''(?xi)
		\\b
		(
			add |
			all |
			alter |
			and |
			apply |
			as |
			asc |
			begin |
			bigint |
			bit |
			bulk |
			by |
			case |
			cast |
			char |
			clob |
			close |
			clustered |
			coalesce |
			collect |
			column |
			comment |
			commit |
			concat |
			connect |
			constraint |
			convert |
			count |
			create |
			cross |
			date |
			dateadd |
			datediff |
			datetime |
			datetime2 |
			deallocate |
			declare |
			default |
			delete |
			desc |
			distinct |
			drop |
			drop_object |
			else |
			end |
			exception |
			exec |
			execute |
			exists |
			exit |
			fetch |
			for |
			foreign |
			format |
			from |
			function |
			getdate |
			getutcdate |
			global |
			go |
			group |
			identity_insert |
			if |
			iif |
			immediate |
			in |
			increment |
			index |
			inner |
			insert |
			int |
			into |
			is |
			isnull |
			join |
			key |
			lead |
			left |
			len |
			length |
			level |
			like |
			loop |
			matched |
			max |
			merge |
			min |
			modify |
			nocount |
			nolock |
			not |
			null |
			nullif |
			number |
			numeric |
			nvarchar |
			nvarchar2 |
			nvl |
			object |
			object_id |
			of |
			off |
			on |
			open |
			or |
			order |
			out |
			outer |
			output |
			over |
			partition |
			pivot |
			preserve |
			primary |
			proc |
			procedure |
			readonly |
			references |
			rename |
			replace |
			return |
			returns |
			row_number |
			rows |
			schemabinding |
			select |
			sequence |
			set |
			start |
			substring |
			sum |
			sys_refcursor |
			sysdate |
			table |
			tablespace |
			target |
			temporary |
			then |
			timestamp |
			to_char |
			top |
			type |
			union |
			update |
			using |
			values |
			varbinary |
			varchar |
			varchar2 |
			when |
			where |
			while |
			with
		)
		\\b
	'''
	# ------------------------------
	def run(self, edit):
		view = self.view
		regions = view.find_all(self.PATTERN)
		if regions:
			view.sel().clear()
			for r in regions:
				view.sel().add(r)
# ------------------------------------------------------------------------------------------
class overlord_plsql_flip_equal(sublime_plugin.TextCommand):
	PATTERN = r'''(?xi)
		^
		( [ \t]* (?: -- [ \t]* | --!!! [ \t]* | --!_! [ \t]* )? )
		( on \s+ |  and \s+ | or \s+ | where \s+ )
		( [^\=\n]+ )
		\=
		( [^\=\n]+ )
		$
	'''
	REX = re.compile(PATTERN)
	# ------------------------------
	def run(self, edit):
		view = self.view
		for sel0 in reversed(view.sel()):
			for sel in reversed(view.lines(sel0)):
				sel_line = view.full_line(sel)
				found = re.search(self.PATTERN, view.substr(sel_line))
				if found:
					flipped = found.group(1) + found.group(2) + found.group(4).strip() + " = " + found.group(3).strip() + "\n"
					view.replace(edit, sel_line, flipped)
# ------------------------------------------------------------------------------------------
class overlord_sql_outline(sublime_plugin.TextCommand):
	C_KEY = 'overlord_sql_outline'
	C_START = '--{'
	C_FINISH = '--}'
	# ------------------------------
	def run(self, edit):
		view = self.view

		start_point = 0
		start_pos = self.find_mark(self.C_START, start_point)

		while start_pos:
			start_point = start_pos.a + 1
			finish_pos = self.find_mark(self.C_FINISH, start_point)
			if finish_pos:
				fold_region = sublime.Region(start_pos.b, finish_pos.a + 2)
				view.fold(fold_region)
			start_pos = self.find_mark(self.C_START, start_point)

	def find_mark(self, mark, start_point):
		return self.view.find(mark, start_point)
# ------------------------------------------------------------------------------------------


# sublime.DRAW_EMPTY
# sublime.DRAW_EMPTY_AS_OVERWRITE
# sublime.DRAW_NO_FILL
# sublime.DRAW_NO_OUTLINE
# sublime.DRAW_SOLID_UNDERLINE
# sublime.DRAW_SQUIGGLY_UNDERLINE
# sublime.DRAW_STIPPLED_UNDERLINE
# sublime.HIDDEN
# sublime.HIDE_ON_MINIMAP
# sublime.PERSISTENT
