#!/usr/bin/python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------------------
# Based off of http://stackoverflow.com/a/3429034/334717
# and http://pywin32.hg.sourceforge.net/hgweb/pywin32/pywin32/file/4c7503da2658/win32/src/win32clipboardmodule.cpp
# ------------------------------------------------------------------------------------------
import ctypes
import sys
import time
# ------------------------------------------------------------------------------------------
# привет, я русский буков
GHND = 0x0042
GMEM_MOVEABLE = 0x0002
# ------------------------------------------------------------------------------------------
kernel32 = ctypes.windll.kernel32
msvcrt = ctypes.CDLL('msvcrt')
user32 = ctypes.windll.user32
# ------------------------------------------------------------------------------------------
CF_TEXT = 1
CF_UNICODETEXT = 13
CF_HTML = user32.RegisterClipboardFormatA(b"HTML Format")
CF_RTF = user32.RegisterClipboardFormatA(b"Rich Text Format")
CF_RTFWO = user32.RegisterClipboardFormatA(b"Rich Text Format Without Objects")
# ------------------------------------------------------------------------------------------
TRACE = True
# ------------------------------------------------------------------------------------------
def printd(value):
	if TRACE:
		print("[WINCLIP] %s\n" % value)
# ------------------------------------------------------------------------------------------
def OpenClipboard(hwnd):
	# We may not get the clipboard handle immediately because
	# some other application is accessing it (?)
	# We try for at least 500ms to get the clipboard.
	t = time.time() + 0.5
	success = False
	while time.time() < t:
		success = user32.OpenClipboard(hwnd)
		if success:
			break
		time.sleep(0.01)
		if not success:
			raise Exception("Error calling OpenClipboard")
# ------------------------------------------------------------------------------------------
def Get():
	try:
		hwnd = user32.CreateWindowExA(0, b"STATIC", None, 0, 0, 0, 0, 0, None, None, None, None)
		OpenClipboard(hwnd)
		pcontents = user32.GetClipboardData(CF_TEXT)
		return ctypes.c_char_p(pcontents).value
	finally:
		user32.CloseClipboard()
		user32.DestroyWindow(hwnd)
# ------------------------------------------------------------------------------------------
def Paste(data, paste_type='text', plaintext=None):

	printd("type(Paste.data): %s" % type(data))

	if plaintext is None:
		plaintext = data

	try:
		hwnd = user32.CreateWindowExA(0, b"STATIC", None, 0, 0, 0, 0, 0, None, None, None, None)
		OpenClipboard(hwnd)
		user32.EmptyClipboard()

		if paste_type == 'rtf':
			Put(data, CF_RTF, 'cp1251')
			Put(data, CF_RTFWO, 'cp1251')
		elif paste_type == 'html':
			Put(wrap_html(data), CF_HTML, 'utf-8')

		Put(plaintext, CF_TEXT, 'cp1251')
		Put(plaintext, CF_UNICODETEXT, 'utf_16')
	finally:
		user32.CloseClipboard()
		user32.DestroyWindow(hwnd)

# ------------------------------------------------------------------------------------------
def to_bytes(data, codepage):
	if sys.version_info > (3, 0):
		b_data = bytes(data, codepage)
	else:
		b_data = bytes(data.encode(codepage))
	return b_data

# ------------------------------------------------------------------------------------------
def Put(data, clipboard_format, codepage):

	printd("%s - type(Put.data) = %s" % (clipboard_format, type(data)))
	printd("repr(Put.data) = %s" % repr(data))

	b_data = to_bytes(data, codepage)

	printd("type(Put.b_data) = %s" % type(b_data))
	printd("repr(Put.b_data) = %s" % repr(b_data))

	size = len(b_data) + ctypes.sizeof(ctypes.c_wchar)
	handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, size)
	locked_handle = kernel32.GlobalLock(handle)
	printd("codepage: %s; clipboard_format: %s; size: %s; handle: %s; locked_handle: %s" % (codepage, clipboard_format, size, handle, locked_handle))
	msvcrt.wcscpy(ctypes.c_wchar_p(locked_handle), b_data)

	# if clipboard_format in (CF_UNICODETEXT, ):
	# 	size = len(b_data) + ctypes.sizeof(ctypes.c_wchar)
	# 	handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, size)
	# 	locked_handle = kernel32.GlobalLock(handle)
	# 	printd("codepage: %s; clipboard_format: %s; size: %s; handle: %s; locked_handle: %s" % (codepage, clipboard_format, size, handle, locked_handle))
	# 	msvcrt.wcscpy(ctypes.c_wchar_p(locked_handle), b_data)
	# else:
	# 	size = len(b_data) + ctypes.sizeof(ctypes.c_char)
	# 	handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, size)
	# 	locked_handle = kernel32.GlobalLock(handle)
	# 	printd("codepage: %s; clipboard_format: %s; size: %s; handle: %s; locked_handle: %s" % (codepage, clipboard_format, size, handle, locked_handle))
	# 	msvcrt.strcpy(ctypes.c_char_p(locked_handle), b_data)

	kernel32.GlobalUnlock(handle)
	user32.SetClipboardData(ctypes.c_int(clipboard_format), handle)

# ------------------------------------------------------------------------------------------
# Based off of http://code.activestate.com/recipes/474121-getting-html-from-the-windows-clipboard/
def wrap_html(fragment):

	METADATA = '''Version:0.9
StartHTML:%09d
EndHTML:%09d
StartFragment:%09d
EndFragment:%09d'''
	CONTEXT_BEGIN = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN"><HTML><HEAD></HEAD><BODY><!--StartFragment-->'
	CONTEXT_END = '<!--EndFragment--></BODY></HTML>'

	b_fragment = to_bytes(fragment, 'utf-8')

	metadata_length = len(METADATA % (0, 0, 0, 0))
	context_begin_length = len(CONTEXT_BEGIN)
	fragment_length = len(b_fragment)
	html_length = context_begin_length + len(CONTEXT_END) + fragment_length

	startHtml = metadata_length
	endHtml = startHtml + html_length
	startFragment = metadata_length + len(CONTEXT_BEGIN)
	endFragment = startFragment + fragment_length

	result = METADATA % (startHtml, endHtml, startFragment, endFragment) + CONTEXT_BEGIN + fragment + CONTEXT_END

	return result
# ------------------------------------------------------------------------------------------
