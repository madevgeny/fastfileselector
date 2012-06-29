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
" Usage:		
"
" Version:		0.0.1
"
" ChangeLog:	0.0.1:	 Started development.
"====================================================================================

if exists( "g:loaded_TAG_MANAGER" )
	finish
endif

let g:loaded_TAG_MANAGER = 1

  echo "Sorry, YATE only runs with Vim 7.0 and greater"
" Check to make sure the Vim version 700 or greater.
if v:version < 700
  echo "Sorry, YATE only runs with Vim 7.0 and greater"
  finish
endif

command! -bang TM :call <SID>ToggleTagManagerBuffer()

fun <SID>PrintTagsList()
	autocmd! CursorMovedI <buffer>

	setlocal nocul
	setlocal ma

	" clear buffer
	exe 'normal ggdG'

	cal append(0,s:user_line)
	exe 'normal dd$'

	if (!exists("s:tags_list")) || (!len(s:tags_list))
		autocmd CursorMovedI <buffer> call <SID>OnCursorMovedI()
		return
	endif

	" find the longest name, kind
	let lname=0
	let lkind=0

	for i in s:tags_list
		let lnm=strlen(i['name'])
		let lk=strlen(i['kind'])

		if lnm>lname
			let lname=lnm
		endif
		if lk>lkind
			let lkind=lk
		endif
	endfor

	let max_counter_len = strlen(len(s:tags_list))

	let printf_str=printf("%%-%dd | %%-%ds | %%-%ds | %%s",max_counter_len,lname,lkind)
	let fn_width=winwidth('$')-(max_counter_len+lname+lkind+15)

	if fn_width < 16
		let fn_width = 16
	endif

	let counter=0
	for i in s:tags_list
		let filename = i["filename"]

		if g:YATE_strip_long_paths
			if strlen(filename)>fn_width
				let filename='...'.strpart(filename,strlen(filename)-fn_width)
			endif
		endif

		let str=printf(printf_str,counter,i["name"],i["kind"],filename)
		
		let counter=counter+1

		cal append(counter,str)
	endfor

	autocmd CursorMovedI <buffer> call <SID>OnCursorMovedI()
endfun

fun <SID>OnCursorMoved()
	let l = getpos(".")[1]
	if l > 1
		setlocal cul
		setlocal noma
		
		setlocal completefunc=''
	else
		setlocal nocul
		setlocal ma
		
		setlocal completefunc=CompleteYATEHistory
	endif
endfun

fun <SID>OnCursorMovedI()
	let l = getpos(".")[1]
	if l > 1
		setlocal cul
		setlocal noma
		
		setlocal completefunc=''
	else
		setlocal nocul
		setlocal ma

		setlocal completefunc=CompleteYATEHistory

		if g:YATE_enable_real_time_search
			let str=getline('.')
			if s:user_line!=str 
				if strlen(str)>=g:YATE_min_symbols_to_search
					let save_cursor = winsaveview()
					cal <SID>GenerateTagsList(str,0)
					cal winrestview(save_cursor)
				else
					let s:user_line=str
				endif
			endif
		endif
	endif
endfun

fun! <SID>ToggleTagManagerBuffer()
	if !exists("s:tm_winnr") || s:tm_winnr==-1
		exe "bo".g:YATE_window_height."sp YATE"

		" TODO: color output	
		let s:tm_winnr=bufnr("YATE")
		
		setlocal buftype=nofile
		setlocal noswapfile

		if !exists("s:first_time")
			let s:user_line=''
			let s:first_time=1

			autocmd BufUnload <buffer> exe 'let s:tm_winnr=-1'
			autocmd CursorMoved <buffer> call <SID>OnCursorMoved()
			autocmd CursorMovedI <buffer> call <SID>OnCursorMovedI()
			autocmd VimResized <buffer> call <SID>PrintTagsList()
			autocmd BufEnter <buffer> call <SID>PrintTagsList()
		endif
		
		cal <SID>PrintTagsList()
	else
		exe ':wincmd p'
		exe ':'.s:tm_winnr.'bd!'
		let s:tm_winnr=-1
	endif
endfun
