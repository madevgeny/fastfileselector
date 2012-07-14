"====================================================================================
" Author:		Evgeny V. Podjachev <evNgeny.poOdjSacPhev@gAmail.cMom-NOSPAM>
"
" License:		This program is free software: you can redistribute it and/or modify
"				it under the terms of the GNU General Public License as published by
"				the Free Software Foundation, either version 3 of the License, or
"				any later version.
"				
"				This program is distributed in the hope that it will be useful,
"				but WITHOUT ANY WARRANTY; without even the implied warranty of
"				MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
"				GNU General Public License for more details
"				(http://www.gnu.org/copyleft/gpl.txt).
"
" Description:	
"
" Installation:	Just drop this file in your plugin directory.
"
" Usage:		Command :FFS toggles visibility of fast file selector buffer.
" 				Parameter g:FFS_window_height sets height of search buffer. Default = 15.
" 				Parameter g:FFS_ignore_list sets list of dirs/files to ignore use Unix shell-style wildcards. Default = ['.*', '*.bak', '~*', '*.obj', '*.pdb', '*.res', '*.dll', '*.idb', '*.exe', '*.lib', '*.so'].
"				Parameter g:FFS_ignore_case, if set letters case will be ignored during search. On windows default = 1, on unix default = 0.
"
" Version:		1.0.0
"
" ChangeLog:	1.0.0:	 Initial version.
"====================================================================================

" TODO:
" Add list of known file extentions.
" Show files only with symbols in right order.

if exists( "g:loaded_FAST_FILE_SELECTOR" )
	finish
endif

let g:loaded_FAST_FILE_SELECTOR = 1

" Check to make sure the Vim version 700 or greater.
if v:version < 700
  echo "Sorry, FastFileSelector only runs with Vim 7.0 and greater"
  finish
endif

if !has('python')
    echo "Error: Required vim compiled with +python"
    finish
endif

if !exists("g:FFS_window_height")
	let g:FFS_window_height = 15
endif

if !exists("g:FFS_ignore_case")
	if has('win32') || has('win64')
		let g:FFS_ignore_case = 1
	else
		let g:FFS_ignore_case = 0
	endif
endif

if !exists("g:FFS_ignore_list")
	let g:FFS_ignore_list = ['.*', '*.bak', '~*', '*.obj', '*.pdb', '*.res', '*.dll', '*.idb', '*.exe', '*.lib', '*.so']
endif

if !exists("s:file_list")
	let s:file_list = []
endif

if !exists("s:filtered_file_list")
	let s:filtered_file_list = s:file_list
endif

if !exists("s:user_line")
	let s:user_line = ''
endif

command! -bang FFS :call <SID>ToggleFastFileSelectorBuffer()

fun <SID>GenFileList()
python << EOF

from os import walk, getcwdu
from os.path import join, isfile, abspath, split
from fnmatch import fnmatch

import vim

if vim.eval("g:FFS_ignore_case"):
	caseMod = lambda x: x.lower()
else:
	caseMod = lambda x: x

def find_tags(path):
	p = abspath(path)

	# need to remove last / for right splitting
	if p[-1] == '/' or p[-1] == '\\':
		p = path[:-1]
	
	while not isfile(join(p, 'tags')):
		p, h = split(p)
		if p == '' or h == '':
			return None

	return p

def scan_dir(path, ignoreList):
	def in_ignore_list(f):
		for i in ignoreList:
			if fnmatch(caseMod(f), caseMod(i)):
				return True

		return False

	fileList = []
	for root, dirs, files in walk(path):
		fileList += [join(root, f) for f in filter(lambda x: not in_ignore_list(x), files)]

		for j in dirs:
			if in_ignore_list(j):
				dirs.remove(j)

	return fileList

wd = getcwdu()
path = find_tags(wd)
if path == None:
	fileList = scan_dir(wd, vim.eval("g:FFS_ignore_list"))
else:
	fileList = scan_dir(path, vim.eval("g:FFS_ignore_list"))

if len(fileList) != 0:
	vim.command("let s:file_list = ['%s']" % "','".join(map(lambda x: x.encode("utf-8"), fileList)))
else:
	vim.command("let s:file_list = []")
EOF
let s:filtered_file_list = s:file_list
endfun

fun <SID>OnRefresh()
	autocmd! CursorMovedI <buffer>
	setlocal nocul
	setlocal ma

	" clear buffer
	exe 'normal ggdG'

	cal append(0,s:user_line)
	exe 'normal dd$'
	cal append(1,s:filtered_file_list)
	autocmd CursorMovedI <buffer> call <SID>OnCursorMovedI()
endfun

fun <SID>OnCursorMoved()
	let l = getpos(".")[1]
	if l > 1
		setlocal cul
		setlocal noma
	else
		setlocal nocul
		setlocal ma
	endif
endfun

fun <SID>UpdateSyntax(str)
	" Apply color changes
	exe 'syn off | syn on'
	if a:str != ''
		if g:FFS_ignore_case == 0
			exe 'syn match Identifier #['.a:str.']#'
		else
			exe 'syn match Identifier #['.tolower(a:str).toupper(a:str).']#'
		endif
	else
		exe 'syn match Identifier #^$#'
	endif
endfun

fun <SID>OnCursorMovedI()
	let l = getpos(".")[1]
	if l > 1
		setlocal cul
		setlocal noma
	else
		setlocal nocul
		setlocal ma

		let str=getline('.')
		if s:user_line!=str
			call <SID>UpdateSyntax(str)
			let save_cursor = winsaveview()
python << EOF
import vim
import operator

def longest_substring_size(str1, str2):
	n1 = len(str1)
	n2 = len(str2)

	L = [0] * n1 * n2

	res = 0
	for i in range(n1):
		for j in range(n2):
			if str1[i] == str2[j]:
				ind = i * n2 + j
				if i == 0 or j == 0:
					L[ind] = 1
				else:
					L[ind] = L[(i - 1) * n2 + (j - 1)] + 1
				if L[ind] > res:
					res = L[ind]
	return res

def check_symbols(s, symbols):
	res = 0
	for i in symbols:
		if s.find(i) == -1:
			return res

	res -= 1

	res -= (longest_substring_size(s, symbols) - 1)

	return res

if vim.eval("g:FFS_ignore_case"):
	caseMod = lambda x: x.lower()
else:
	caseMod = lambda x: x

symbols = caseMod(vim.eval('str'))
if len(symbols) != 0:
	fileList = map(lambda x: (check_symbols(caseMod(x), symbols), x), vim.eval('s:file_list'))
	fileList = filter(lambda x: x[0] != 0, fileList)
	fileList.sort(key=operator.itemgetter(0))

	if len(fileList) != 0:
		vim.command("let s:filtered_file_list = ['%s']" % "','".join(map(lambda x: x[1], fileList)))
	else:
		vim.command("let s:filtered_file_list = []")
else:
	vim.command("let s:filtered_file_list = s:file_list")
EOF
			let s:user_line=str
			call <SID>OnRefresh()
			cal winrestview(save_cursor)
		endif
	endif
endfun

fun <SID>GotoFile()
	if !len(s:filtered_file_list) || line('.') == 1
		return
	endif
	
	let str=getline('.')

	exe ':wincmd p'
	exe ':'.s:tm_winnr.'bd!'
	let s:tm_winnr=-1
	exe ':e '.str
	" Without it you should press Enter once again some times.
	exe 'normal Q'
endfun

fun! <SID>ToggleFastFileSelectorBuffer()
	if !exists("s:tm_winnr") || s:tm_winnr==-1
		exe "bo".g:FFS_window_height."sp FastFileSelector"

		exe "inoremap <expr> <buffer> <Enter> pumvisible() ? '<CR><C-O>:cal <SID>GotoFile()<CR>' : '<C-O>:cal <SID>GotoFile()<CR>'"
		exe "noremap <silent> <buffer> <Enter> :cal <SID>GotoFile()<CR>"

		let s:tm_winnr=bufnr("FastFileSelector")
		
		setlocal buftype=nofile
		setlocal noswapfile
		setlocal insertmode

		let s:user_line=''
		if !exists("s:first_time")
			let s:first_time=1

			autocmd BufUnload <buffer> exe 'let s:tm_winnr=-1'
			autocmd CursorMoved <buffer> call <SID>OnCursorMoved()
			autocmd CursorMovedI <buffer> call <SID>OnCursorMovedI()
			autocmd VimResized <buffer> call <SID>OnRefresh()
			autocmd BufEnter <buffer> call <SID>OnRefresh()
		endif
		
		cal <SID>GenFileList()
		cal <SID>OnRefresh()
	else
		exe ':wincmd p'
		exe ':'.s:tm_winnr.'bd!'
		let s:tm_winnr=-1
	endif
endfun
