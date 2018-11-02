# -*- coding: utf-8 -*-
# ------------------------------------------------------------
import sublime_plugin
# ------------------------------------------------------------
import os
import stat
# ------------------------------------------------------------
NAME_TO_STAT = {
	"writable": stat.S_IWRITE,
}
# ------------------------------------------------------------
class overlord_file_attribute_manager(sublime_plugin.TextCommand):
	"""
	Text Command: Позволяет устанавливать и снимать атрибуты на файлах.
	"""
	# ------------------------------
	def get_attribute_state(self, file_name, attribute):
		return os.stat(file_name).st_mode & NAME_TO_STAT[attribute] == NAME_TO_STAT[attribute]
	# ------------------------------
	def get_need_set(self, file_name, attribute, mode):
		if mode == 'set':
			return True
		elif mode == 'reset':
			return False
		elif mode == 'toggle':
			return not self.get_attribute_state(file_name, attribute)
		else:
			raise Exception('mode can be set/reset/toggle')
	# ------------------------------
	def apply_attribute(self, file_st_mode, need_set, attribute):
		if need_set:
			file_st_mode |= NAME_TO_STAT[attribute]
		else:
			file_st_mode &= ~NAME_TO_STAT[attribute]
		return file_st_mode
	# ------------------------------
	def run(self, edit, mode, attribute):
		file_name = self.view.file_name()
		if file_name:
			need_set = self.get_need_set(file_name, attribute, mode)
			file_st_mode = self.apply_attribute(os.stat(file_name).st_mode, need_set, attribute)
			# ------------------------------
			os.chmod(file_name, file_st_mode)
			print("Set attribute '%s' to '%s' for file '%s'" % (attribute, str(need_set), file_name))
	# ------------------------------
	def description(self, mode, attribute):
		default = '"%s" attribute - %s' % (attribute.title(), mode.lower())
		return default
	# ------------------------------
	def is_checked(self, mode, attribute):
		file_name = self.view.file_name()
		if file_name:
			return self.get_attribute_state(file_name, attribute)
		else:
			return False
	# ------------------------------
