import time

from os import walk, getcwdu
from os.path import join, isfile, abspath, split
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

		for j in dirs:
			if in_ignore_list(j):
				dirs.remove(j)

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
	symbols = caseMod('NGModel')

	timing(scan_dir, 5, {'path' : path, 'ignoreList' : ignore_list})
	
	fileList = scan_dir(path, ignore_list)
	fileList = map(lambda x: (check_symbols(caseMod(x), symbols), x), fileList)
	fileList = filter(lambda x: x[0] != 0, fileList)
	fileList.sort(key=operator.itemgetter(0))
