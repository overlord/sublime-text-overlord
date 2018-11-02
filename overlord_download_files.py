# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
# ------------------------------
if sublime.version() >= '3000':
	from sublime_overlord.lib import (st2api)
	from urllib.request import (URLopener)
else:
	from lib import (st2api)
	from urllib import (URLopener)
# ------------------------------
import os
# ------------------------------------------------------------------------------------------
class overlord_URLopener(URLopener):
	version = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
# ------------------------------------------------------------------------------------------
class overlord_download_files(sublime_plugin.WindowCommand):
	folder = None
	opener = overlord_URLopener()
	# ------------------------------
	def run(self):
		view = self.window.active_view()
		if not self.folder and view.file_name():
			self.folder, _ = os.path.split(view.file_name())
		self.window.show_input_panel('Target folder:', self.folder, lambda folder: self.__on_done(folder, view), None, None)
	# ------------------------------
	def __process(self, links):
		if links:
			count = len(links)
			is_error = False
			for i, link in enumerate(links):
				try:
					print("> downloading [%i / %i]: '%s'..." % (i+1, count, link))
					_, file_name = os.path.split(link)
					file_name = file_name.replace('=', '').replace('?', '')
					self.opener.retrieve(link, os.path.join(self.folder, file_name))
				except Exception as e:
					is_error = True
					print("> error: '%s'" % e)
			sublime.message_dialog('Downloading complete!\n\n%s' % self.folder)
			if not is_error:
				self.folder = ""
			return True, 'OK'
	# ------------------------------
	def __on_done(self, folder, view):
		try:
			if view and folder and len(folder.strip()) > 0:
				self.folder = folder
				if not os.path.exists(self.folder):
					os.makedirs(self.folder)
				regions = [view.split_by_newlines(view.line(region)) for region in st2api.get_selection(view)]
				links = [view.substr(region).strip() for sublist in regions for region in sublist]
				# ------------------------------
				thread = st2api.overlord_runner_thread(lambda: self.__process(links))
				thread.start()
				# ------------------------------
		except Exception as e:
			sublime.error_message("%s" % e)
# ------------------------------------------------------------------------------------------
