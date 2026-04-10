import sublime_plugin
import re
import webbrowser

rex_jira = re.compile(r'''(?xi)
	TP [A-Z]+ - \d+
''')

rex_tfs = re.compile(r'''(?xi)
	TFS - (\d+)
''')

# TPTECH-1234
# TPSOI-1234
# TFS-1234

class OverlordOpenJiraCommand(sublime_plugin.TextCommand):
	def run(self, edit, event):
		name, url = self.find_item(event)
		webbrowser.open_new_tab(url)

	def is_visible(self, event):
		return self.find_item(event) is not None

	def find_item(self, event):
		pt = self.view.window_to_text((event['x'], event['y']))
		line = self.view.line(pt)
		text = self.view.substr(line)

		match = rex_jira.search(text)
		if match:
			return (
				match.group(0),
				f"https://jira.mts.ru/browse/{match.group(0)}"
			)

		match = rex_tfs.search(text)
		if match:
			return (
				match.group(0),
				f"https://tfs.mtsit.com/STS/FORIS_Mobile/_workitems/edit/{match.group(1)}"
			)

		return None

	def description(self, event):
		name, _ = self.find_item(event)
		return f'Open issue {name}...'

	def want_event(self):
		return True
