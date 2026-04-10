import sublime_plugin
import os
import re

rex = re.compile(r'''
(?xi)
(\s | $ | ^)
(
	[a-z] : ( \\ | / ) |
	\\ \\ |
	//
)
(
	[ \. \w _ = \? ! & \# \( \) \- ]+ [ \\ / ]?
)+
''')

# v - C:\Portable\
# v - C:/Portable/Reflector/
# v - C:\Portable\Sublime Text\Data\Index\039569.ldb
# v - \\software-hub\portable\sublime_text\data\index\098581.ldb
# x - Https://tfs.mtsit.com/STS/FORIS_Mobile/_build?definitionId=6187&_a=summary

class OverlordOpenContextFileCommand(sublime_plugin.TextCommand):
	def run(self, edit, event):
		file = self.find_file(event)
		if file.startswith('\\\\'): # путь в сетевой папке
			os.startfile(file)
		else:
			self.view.window().open_file(file)

	def is_visible(self, event):
		return self.find_file(event) is not None

	def find_file(self, event):
		pt = self.view.window_to_text((event['x'], event['y']))
		line = self.view.line(pt)
		# line.a = max(line.a, pt - 1024)
		# line.b = min(line.b, pt + 1024)
		text = self.view.substr(line)
		match = rex.search(text)
		return match.group(0).strip() if match else None

	def description(self, event):
		file = self.find_file(event)
		if len(file) > 64:
			file = file[:32] + '<...>' + file[-32:]
		return 'Open file: ' + file

	def want_event(self):
		return True
