import sublime_plugin
import re

rex = r'''(?xi)
    [a-z] \: \\
    (?:
        [ \. \w _ ! # \( \) \- ]+ \\?
    )+
'''

# C:\Portable\
# C:\Portable\Sublime Text\Data\Index\039569.ldb

class OverlordOpenContextFileCommand(sublime_plugin.TextCommand):
	def run(self, edit, event):
		file = self.find_file(event)
		self.view.window().open_file(file)

	def is_visible(self, event):
		return self.find_file(event) is not None

	def find_file(self, event):
		pt = self.view.window_to_text((event['x'], event['y']))
		line = self.view.line(pt)
		line.a = max(line.a, pt - 1024)
		line.b = min(line.b, pt + 1024)

		text = self.view.substr(line)
		match = re.search(rex, text)

		return match.group(0) if match else None

	def description(self, event):
		file = self.find_file(event)
		if len(file) > 64:
			file = file[:32] + '<...>' + file[-32:]
		return 'Open ' + file

	def want_event(self):
		return True
