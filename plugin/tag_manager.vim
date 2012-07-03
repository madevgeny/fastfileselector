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
" Usage:		Command :TAGM toggles visibility of tag manager buffer.
"				Command :TAGM_RebuildActive rebuilds all loaded tags files.
"				Command :TAGM_RebuildAll rebuilds all registered tags files.
"				Command :TAGM toggles visibility of tag manager buffer.
" 				Parameter g:TAGM_window_height sets height of search buffer. Default = 15.
" 				Parameter g:TAGM_tags sets height of search buffer. Default = 15.
"
" Version:		0.0.1
"
" ChangeLog:	0.0.1:	 Started development.
"====================================================================================

if exists( "g:loaded_TAG_MANAGER" )
	finish
endif

let g:loaded_TAG_MANAGER = 1

" Check to make sure the Vim version 700 or greater.
if v:version < 700
  echo "Sorry, TagManager only runs with Vim 7.0 and greater"
  finish
endif

if !exists("g:TAGM_window_height")
	let g:TAGM_window_height = 15
endif

if !exists("g:TAGM_tags")
	let g:TAGM_tags = {}
endif

command! -bang TAGM :call <SID>ToggleTagManagerBuffer()
command! -bang TAGMRebuildActive :call <SID>RebuildActiveTags()
command! -bang TAGMRebuildAll :call <SID>RebuildAllTags()

fun <SID>NormalizePath(path)
	return simplify(resolve(expand(a:path)))
endfun

fun GenTagFilesList()
	" normalize tags paths
"	let keysToDelete = []
"	for key in keys(g:TAGM_tags)
"		nkey = NormalizePath(key)
"		if nkey != key
"			g:TAGM_tags[nkey] = g:TAGM_tags[key]
"			append(keysToDelete, key)
"		endif
"	endfor

	" validate properties

	" add content of tags to g:TAGM_tags
	"
endfun

fun <SID>OnRefresh()
	autocmd! CursorMovedI <buffer>
	setlocal nocul
	setlocal ma

	" clear buffer
	exe 'normal ggdG'

	" print tags files
	for key in sort(keys(g:TAGM_tags))
		let str=printf('%s',key)
		call append(line('$'), <SID>AbsPath(str))
	endfor

	call append(line('$'), 'Loaded tags:')

	for i in tagfiles()
		let str=printf('%s',i)
		call append(line('$'), <SID>AbsPath(str))
	endfor
	exe 'normal dd$'
	autocmd CursorMovedI <buffer> call <SID>OnCursorMovedI()
endfun

fun <SID>OnCursorMoved()
endfun

fun <SID>OnCursorMovedI()
endfun

fun! <SID>RebuildActiveTags()
endfun

fun! <SID>RebuildAllTags()
endfun

fun! <SID>ToggleTagManagerBuffer()
	if !exists("s:tm_winnr") || s:tm_winnr==-1
		exe "bo".g:TAGM_window_height."sp TagManager"

		" TODO: color output	
		let s:tm_winnr=bufnr("TagManager")
		
		setlocal buftype=nofile
		setlocal noswapfile

		if !exists("s:first_time")
			let s:user_line=''
			let s:first_time=1

			autocmd BufUnload <buffer> exe 'let s:tm_winnr=-1'
			autocmd CursorMoved <buffer> call <SID>OnCursorMoved()
			autocmd CursorMovedI <buffer> call <SID>OnCursorMovedI()
			autocmd VimResized <buffer> call <SID>OnRefresh()
			autocmd BufEnter <buffer> call <SID>OnRefresh()
		endif
		
		cal <SID>OnRefresh()
	else
		exe ':wincmd p'
		exe ':'.s:tm_winnr.'bd!'
		let s:tm_winnr=-1
	endif
endfun
