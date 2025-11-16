# Sublime Overlord Package

Essential Sublime Text Overlord toolbox.

**Table of Content:**

[[_TOC_]]

# New Syntaxes

See examples [here](https://github.com/overlord/sublime-text-overlord/-/blob/master/README_syntaxes.md)

- **SQL Ex.sublime-syntax**
	- optimal for Oracle PL/SQL script files
	- fix for `ctrl+r` hotkey (in package files)
		![sql_ex_ctrl_r](https://github.com/overlord/sublime-text-overlord/raw/master/images/sql_ex_ctrl_r.png)
	- fix multiline dynamic-sql highlight, see examples.
- **Highlighted Text.tmLanguage**
	- bring some highlight into plain-text file
- **[VCard.tmLanguage](http://en.wikipedia.org/wiki/VCard)**
- **Chorder.tmLanguage**

# Improved Color Schemes

- **Cobalt Ex.tmTheme**
	- a lot of various fixes
- **Solarized Ex (Light).tmTheme**
	- fix for `selection` scope
- **Visual Studio Ex.tmTheme**
	- fix for `error` scope

# Commands

## In Main.sublime-menu

- **overlord_align_table**
	- By default aligns tab-separated table by spaces and vertical | columns separator
	![overlord_align_table](https://github.com/overlord/sublime-text-overlord/raw/master/images/align_table.gif)
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

## In Tab Context.sublime-menu

- **overlord_rename_path**
	- Command to rename current file by clicking on view tab.

## Other

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
	![overlord_tab](https://github.com/overlord/sublime-text-overlord/raw/master/images/overlord_tab.gif)
- **overlord_total_recall**
- **overlord_close**
	- Changes default `close` behaviour. First closes all views, then clear folder-panel, finally closes sublime window itself.
- **overlord_open_custom_file**
- **overlord_cleanup_file_history**

# Settings files

## switch_project.sublime-settings

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

## switch_default_project.sublime-settings

```
"path_blocks" := [:path_block]

:path_block := [:string]
```

# Links

**On GitHub:**

- https://github.com/overlord/sublime-text-overlord.git
- https://github.com/overlord/sublime-text-overlord-settings.git [private]
- https://github.com/overlord/sublime-merge-overlord.git


**On Assembla [Obsolete]:**

- [Obsolete] https://git.assembla.com/overlord_repo.sm_overlord.git


**On BitBucket [Obsolete]:**

- [Obsolete] https://bitbucket.org/DarkOverlord/sublime_overlord
- [Obsolete] https://bitbucket.org/DarkOverlord/sublime_overlord_settings [private]
