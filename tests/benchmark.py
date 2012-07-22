import time

from os import walk, getcwdu
from os.path import join
from fnmatch import fnmatch
import operator

if 1:
	import string
	caseMod = string.lower
else:
	caseMod = lambda x: x

def scan_dir(path, ignoreList):
	ignoreList = map(caseMod, ignoreList)
	def in_ignore_list(f):
		for i in ignoreList:
			if fnmatch(caseMod(f), i):
				return True

		return False

	fileList = []
	for root, dirs, files in walk(path):
		fileList += [join(root, f) for f in filter(lambda x: not in_ignore_list(x), files)]
		
		toRemove = filter(in_ignore_list, dirs)
		for j in toRemove:
			dirs.remove(j)

	n = len(path.encode("utf-8"))
	fileList = map(lambda x: x.encode("utf-8"), fileList)
	fileList = map(lambda x: (caseMod(x[n:]), x), fileList)

	return fileList

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

def check_symbols_uni(s, symbols):
	prevPos = -1
	for i in symbols:
		pos = s[prevPos + 1 : ].find(i)
		if pos == -1:
			return 0
		else:
			prevPos = pos

	return longest_substring_size(s, symbols)

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
	for i in r:
	    f(**a); f(**a); f(**a); f(**a); f(**a); f(**a); f(**a); f(**a); f(**a); f(**a)
	t2 = time.clock()
	print round(t2-t1, 3)

if __name__=='__main__':
	path = getcwdu()
	ignore_list = ['.*', '*.bak', '~*', '*.obj', '*.pdb', '*.res', '*.dll', '*.idb', '*.exe', '*.lib', '*.so']
	symbols = caseMod('root')

#	timing(scan_dir, 5, {'path' : path, 'ignoreList' : ignore_list})
	
	file_list = scan_dir(path, ignore_list)

	def filterFileList(fileList):
		nSymbols = len(symbols)
		if nSymbols == 1:
			check_symbols = check_symbols_1
		elif nSymbols == 2:
			check_symbols = check_symbols_2
		elif nSymbols == 3:
			check_symbols = check_symbols_3
		else:
			check_symbols = check_symbols_uni

		fileList = map(lambda x: (check_symbols(x[0], symbols), x), fileList)
		fileList = filter(lambda x: x[0] != 0, fileList)
		fileList.sort(key=operator.itemgetter(0, 1))

	timing(filterFileList, 5, {'fileList':file_list})
