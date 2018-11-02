# Sublime Overlord Package

Essential Sublime Text toolbox **v.0.1**

## New Syntaxes

See examples [here](https://bitbucket.org/DarkOverlord/sublime_overlord/src/master/README_syntaxes.md)

- **SQL Ex.sublime-syntax**
	- optimal for Oracle PL/SQL script files
	- fix for `ctrl+r` hotkey (in package files)

		![sql_ex_ctrl_r](https://bytebucket.org/DarkOverlord/sublime_overlord/raw/master/images/sql_ex_ctrl_r.png)

	- fix multiline dynamic-sql highlight, see examples [here](https://bitbucket.org/DarkOverlord/sublime_overlord/src/master/README_syntaxes.md)

- **Highlighted Text.tmLanguage**
	- bring some highlight into plain-text file

- **[VCard.tmLanguage](http://en.wikipedia.org/wiki/VCard)**

- **Chorder.tmLanguage**

## Improved Color Schemes

- **Cobalt Ex.tmTheme**
	- a lot of various fixes

- **Solarized Ex (Light).tmTheme**
	- fix for `selection` scope

- **Visual Studio Ex.tmTheme**
	- fix for `error` scope

## Commands

### In Main.sublime-menu

- **overlord_align_table**
	- By default aligns tab-separated table by spaces and vertical | columns separator

	![overlord_align_table](https://bytebucket.org/DarkOverlord/sublime_overlord/raw/master/images/align_table.gif)

- **overlord_auto_indent**
	- Based on <https://github.com/alek-sys/sublimetext_indentxml>

- **overlord_clear_regions**
	- Removes regions by given regex-pattern

- **overlord_file_attribute_manager**

- **overlord_number_items**

- **overlord_save_all**
	- Mass `Save all` command with given `encoding` parameter.

- **overlord_close_all_force**
	- Close all open files without saving. Can be useful when changes are NOT needed to be saved.

- **overlord_open_recently_closed_file**

- **overlord_switch_project**
	- Allows quickly switch between projects (FOLDERS)

- **overlord_switch_project_file**

### In Context.sublime-menu

- **overlord_copy_as_html**
	- Simplified version of <https://github.com/agibsonsw/PrintHtml>

### In Tab Context.sublime-menu

- **overlord_rename_path**
	- Command to rename current file by clicking on view tab.

### Other

- **overlord_detect_syntax**
	- Currently can autodetect:
		- XML
		- Python
		- SQL
		- Powershell

- **overlord_diff**
	- Launches external diff tool to compare two nearest views.
	- Out of the box supports:
		- TortoiseSVN
		- WinMerge
		- AraxisMerge
		- KDiff3
	- Can be configured to support any other external diff tool.

- **overlord_find_all**

- **overlord_insert_string**

- **overlord_replace**

- **overlord_tab**
	- Aligns selected cursor positions verticaly by tabs or spaces

	![overlord_tab](https://bytebucket.org/DarkOverlord/sublime_overlord/raw/master/images/overlord_tab.gif)

- **overlord_total_recall**

- **overlord_close**
	- Changes default `close` behaviour. First closes all views, then clear folder-panel, finally closes sublime window itself.

- **overlord_open_custom_file**

- **overlord_cleanup_file_history**

## Settings files

### switch_project.sublime-settings

```
"projects" := [:project]

:project :=
	"name" := :string          - display name of project
	"items" := [:project_item] - items in project
	"add" := [:string]         - additional folder list to add to sublime project

:project_item :=
	"name" := :string    - display name of project item
	"paths" := [:string] - folder list to add to sublime project
```

### switch_default_project.sublime-settings

```
"path_blocks" := [:path_block]

:path_block := [:string]
```

## Links

- [Sublime Overlord Main](https://bitbucket.org/DarkOverlord/sublime_overlord)
- [Sublime Overlord FORIS Package](https://bitbucket.org/DarkOverlord/sublime_overlord_foris) (private)
- [Sublime Overlord Settings Package](https://bitbucket.org/DarkOverlord/sublime_overlord_settings) (private)
