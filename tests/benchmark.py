import time

import os
from os import walk, getcwdu
from os.path import join 
from fnmatch import fnmatch
import operator

from paths_cache import PathsCache, getModTime

if 1:
	import string
	caseMod = string.lower
else:
	caseMod = lambda x: x

def in_ignore_list(f):
	ignoreList = map(caseMod, ignoreList)
	for i in ignoreList:
		if fnmatch(caseMod(f), i):
			return True
	return False

def scan_dir(path, checkOnIgnores, cache):
	path = os.abspath(path)
	pathLen = len(path)

	fileList = []
	cachedPaths = cache.getCachedPaths(path)
	if len(cachedPaths):
		if cachedPaths[0][0][1] == getModTime(fp):
			for i in cachedPaths:
				for j in i[1]:
					fullPath.append(join(path, i[0][0], j))
			return [x]	

	addToCache = []
	for root, dirs, files in walk(path):
		toRemove = []
		for i in dirs:
			fp = join(root, i)
			fpmt = getModTime(fp)
			fp = fp.encode("utf-8")
			fpl = len(fp)
		
			inCache = False
			for j in cachedPaths:
				if fpmt == j[1] and fp == j[0]:
					toRemove.append(i)

					# add cached paths
					for k in cachedPaths:
						if k[0].find(fp) == fpl:
							fileList.append((k[0], k[3]))

					inCache = True

					break

			if not inCache:
				
				fileList.append((root[pathLen : ].encode("utf-8"), [x.encode("utf-8") for x in files]))
					fileList += [join(root, f) for f in files if not in_ignore_list(f)]

		for j in toRemove:
			dirs.remove(j)


	n = len(path.encode("utf-8"))

	fileList = map(lambda x: (caseMod(x[n:]), x), fileList)

	return fileList

def longest_substring_size(str1, str2):
	n1 = len(str1)
	n2 = len(str2)
	n2inc = n2 + 1

	L = [0 for i in range((n1 + 1) * n2inc)]

	res = 0
	for i in range(n1):
		for j in range(n2):
			if str1[i] == str2[j]:
				ind = (i + 1) * n2inc + (j + 1)
				L[ind] = L[i * n2inc + j] + 1
				if L[ind] > res:
					res = L[ind]

	return res

def check_symbols_uni(s, symbols):
	prevPos = 0
	for i in symbols:
		pos = s.find(i, prevPos)
		if pos == -1:
			return 0
		else:
			prevPos = pos + 1

	return -longest_substring_size(s, symbols)

def check_symbols_1(s, symbols):
	if s.find(symbols[0]) == -1:
		return 0
	return -1

def check_symbols_2(s, symbols):
	pos = s.find(symbols[0])
	if pos == -1:
		return 0

	if s.rfind(symbols[1]) < pos:
		return 0

	if s.find(symbols) != -1:
		return -2

	return -1

def check_symbols_3(s, symbols):
	p1 = s.find(symbols[0])
	if p1 == -1:
		return 0

	p2 = s.rfind(symbols[2])
	if p2 < p1:
		return 0

	if s[p1 : p2 + 1].find(symbols[1]) == -1:
		return 0

	if s.find(symbols) != -1:
		return -3
	if s.find(symbols[:2]) != -1 or s.find(symbols[1:]) != -1:
		return -2

	return -1

def timing(f, n, a):
	print f.__name__,
	r = range(n)
	t1 = time.clock()
	for _ in r:
		f(**a); f(**a); f(**a); f(**a); f(**a); f(**a); f(**a); f(**a); f(**a); f(**a)
	t2 = time.clock()
	print round(t2-t1, 3)

if __name__ == '__main__':
	path = getcwdu()
	ignore_list = ['.*', '*.bak', '~*', '*.obj', '*.pdb', '*.res', '*.dll', '*.idb', '*.exe', '*.lib', '*.so']
	filter_string = caseMod('root')

#	timing(scan_dir, 2, {'path' : path, 'ignoreList' : ignore_list})
	
	file_list = scan_dir(path, ignore_list)

	def filterFileList(fileList):
		nSymbols = len(filter_string)
		if nSymbols == 1:
			check_symbols = check_symbols_1
		elif nSymbols == 2:
			check_symbols = check_symbols_2
		elif nSymbols == 3:
			check_symbols = check_symbols_3
		else:
			check_symbols = check_symbols_uni

		fileList = map(lambda x: (check_symbols(x[0], filter_string), x), fileList)
		fileList = filter(operator.itemgetter(0), fileList)
		fileList.sort(key=operator.itemgetter(0, 1))

	#timing(filterFileList, 5, {'fileList':file_list})

	pc = PathsCache('K:/home_projects/fastfileselector/tests/db.db', False)

	pc.updateCachedPaths('K:\\www.av8n.com', [])
