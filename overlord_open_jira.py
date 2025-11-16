import sublime_plugin
import re
import webbrowser

rex = r'''(?xi) TP [A-Z]+ - \d+'''

# TPTECH-1234

class OverlordOpenJiraCommand(sublime_plugin.TextCommand):
	def run(self, edit, event):
		item = self.find_item(event)
		webbrowser.open_new_tab(f"https://jira.mts.ru/browse/{item}")

	def is_visible(self, event):
		return self.find_item(event) is not None

	def find_item(self, event):
		pt = self.view.window_to_text((event['x'], event['y']))
		line = self.view.line(pt)
		text = self.view.substr(line)
		match = re.search(rex, text)
		return match.group(0) if match else None

	def description(self, event):
		item = self.find_item(event)
		return f'Open issue {item}...'

	def want_event(self):
		return True
