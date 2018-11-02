# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------------------
import sublime
import sublime_plugin
# ------------------------------------------------------------------------------------------
# Main.sublime-menu example
# ------------------------------------------------------------------------------------------
#	[
#		{
#			"caption": "Overlord", "mnemonic": "O", "id": "overlord",
#			"children":
#			[
#				{ "caption": "-", "id": "overlord_macro_start" },
#				{
#					"caption": "Macros",
#					"children": [
#						{
#							"caption": "Macro 1",
#							"command": "overlord_macro",
#							"args": {
#								"items": [
#									[ "show_panel", {"panel": "find"} ],
#									[ "insert", { "characters": "ololo!" } ],
#									[ "find_all", { "close_panel": true } ]
#								]
#							}
#						}
#					]
#				},
#				{ "caption": "-", "id": "overlord_macro_end" }
#			]
#		}
#	]
# ------------------------------------------------------------------------------------------
TARGET_WINDOW_COMMAND = 'window'
TARGET_TEXT_COMMAND = 'view'
# ------------------------------------------------------------------------------------------
class overlord_macro(sublime_plugin.WindowCommand):
	# ------------------------------
	def xparse_item(self, item):
		if len(item) == 2:
			command, args = item
			return command, args, TARGET_WINDOW_COMMAND
		elif len(item) == 3:
			command, args, command_type = item
			return command, args, command_type
		else:
			raise Exception("Item '%s' has unexpected length" % item)
	# ------------------------------
	def xget_command_target(self, command_type):
		if command_type == TARGET_WINDOW_COMMAND:
			return self.window
		elif command_type == TARGET_TEXT_COMMAND:
			return self.window.active_view()
		else:
			raise Exception("Unexpected command_type '%s' for command '%s'" % (command_type, command))
	# ------------------------------
	def run(self, items):
		for item in items or []:
			command, args, command_type = self.xparse_item(item)
			target = self.xget_command_target(command_type)
			target.run_command(command, args)
# ------------------------------------------------------------------------------------------
