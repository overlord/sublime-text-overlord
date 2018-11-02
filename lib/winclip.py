#!/usr/bin/python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------------------
# Based off of http://stackoverflow.com/a/3429034/334717
# and http://pywin32.hg.sourceforge.net/hgweb/pywin32/pywin32/file/4c7503da2658/win32/src/win32clipboardmodule.cpp
# ------------------------------------------------------------------------------------------
import sys
import ctypes
# ------------------------------------------------------------------------------------------
# привет, я русский буков
GHND = 0x0042
# ------------------------------------------------------------------------------------------
msvcrt = ctypes.cdll.msvcrt
kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32
# ------------------------------------------------------------------------------------------
CF_TEXT = 1
CF_UNICODETEXT = 13
CF_HTML  = user32.RegisterClipboardFormatA(b"HTML Format")
CF_RTF   = user32.RegisterClipboardFormatA(b"Rich Text Format")
CF_RTFWO = user32.RegisterClipboardFormatA(b"Rich Text Format Without Objects")
# ------------------------------------------------------------------------------------------
TRACE = True

# ------------------------------------------------------------------------------------------
def printd(value):
	if TRACE:
		print(value)

# ------------------------------------------------------------------------------------------
def last_error(label):
	code = ctypes.GetLastError()
	msg = ctypes.FormatError(code)
	if code == 0:
		msg = ''
	# printd("%s: %s '%s'" % (label, code, msg))

# ------------------------------------------------------------------------------------------
def Get():
	try:
		user32.OpenClipboard(None)
		pcontents = user32.GetClipboardData(CF_TEXT)
		return ctypes.c_char_p(pcontents).value
	finally:
		user32.CloseClipboard()
# ------------------------------------------------------------------------------------------
def Paste(data, paste_type='text', plaintext=None):

	# printd("type(Paste.data) = %s" % type(data))

	if plaintext is None:
		plaintext = data

	try:
		user32.OpenClipboard(None)
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

# ------------------------------------------------------------------------------------------
def to_bytes(data, codepage):
	if sys.version_info > (3, 0):
		b_data = bytes(data, codepage)
	else:
		b_data = bytes(data.encode(codepage))
	return b_data

# ------------------------------------------------------------------------------------------
def Put(data, clipboard_format, codepage):

	# printd("------------------------------")
	# printd("%s - type(Put.data) = %s" % (clipboard_format, type(data)))
	# printd("repr(Put.data) = %s" % repr(data))

	b_data = to_bytes(data, codepage)

	# printd("type(Put.b_data) = %s" % type(b_data))
	# printd("repr(Put.b_data) = %s" % repr(b_data))

	if clipboard_format in (CF_UNICODETEXT, ):
		handle = Put2(b_data, ctypes.c_wchar, ctypes.c_wchar_p, msvcrt.wcscpy)
	else:
		handle = Put2(b_data, ctypes.c_char, ctypes.c_char_p, msvcrt.strcpy)

	user32.SetClipboardData(ctypes.c_int(clipboard_format), handle)

def Put2(b_data, char_type, char_type_pointer, char_copy_function):
	size = len(b_data) + ctypes.sizeof(char_type())
	handle = kernel32.GlobalAlloc(GHND, size)
	pointer = kernel32.GlobalLock(handle)
	char_copy_function(char_type_pointer(pointer), b_data)
	kernel32.GlobalUnlock(handle)
	return handle

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

	# printd(result)

	return result
# ------------------------------------------------------------------------------------------
