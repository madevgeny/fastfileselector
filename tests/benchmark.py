import timeit

from os import walk, getcwdu
from os.path import join, isfile, abspath, split
from fnmatch import fnmatch

if 1
	import string
	caseMod = string.lower
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

import operator

def longest_substring_size(str1, str2):
	n1 = len(str1)
	n2 = len(str2)

	L = [0 for i in range((n1 + 1) * (n2 + 1))]

	res = 0
	for i in range(n1):
		for j in range(n2):
			if str1[i] == str2[j]:
				ind = (i + 1) * n2 + (j + 1)
				L[ind] = L[i * n2 + j] + 1
				if L[ind] > res:
					res = L[ind]
	return res

def check_symbols(s, symbols):
	res = 0
	prevSymbol = None
	prevSymbolPos = -1
	for i in symbols:
		pos = s.find(i)
		if pos == -1:
			return 0
		else:
			if prevSymbol != None:
				if pos < prevSymbolPos:
					pos = s.find(i, pos + 1)
					if pos == -1:
						return 0
					else:
						res -= 1
				else:
					res -= 1

			prevSymbol = i
			prevSymbolPos = pos

	res -= 1

	res -= (longest_substring_size(s, symbols) - 1) * 2

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

