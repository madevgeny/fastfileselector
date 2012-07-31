import time

import os
from os import walk, getcwdu
from os.path import join, getctime, getmtime, exists
from fnmatch import fnmatch
import operator

import sqlite3

if 1:
	import string
	caseMod = string.lower
else:
	caseMod = lambda x: x

def getModTime(path):
	return max(getctime(path), getmtime(path))

class PathsCache(object):
	def __init__(self, pathToCache, caseSensitivePaths):
		self.caseSensitivePaths = caseSensitivePaths

		# Check if database file exists and creates all needed paths.
		createTable = False
		if not exists(pathToCache):
			createTable = True
			try:
				os.makedirs(os.path.split(pathToCache)[0])
			except OSError:
				pass

		self.conn = None
		with sqlite3.connect(pathToCache) as conn:
			self.conn = conn
			if createTable:
				c = conn.cursor()
				c.executescript("""
					CREATE TABLE roots (id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, modtime INTEGER);
					CREATE TABLE paths (id INTEGER PRIMARY KEY AUTOINCREMENT, root_id INTEGER SECONDARY KEY, path TEXT, modtime INTEGER);
					CREATE TABLE files (path_id INTEGER PRIMARY KEY, file_name TEXT);
				""")
				conn.commit()
				c.close()

	def getCachedPaths(self, root):
		if self.conn == None:
			return []

		if self.caseSensitivePaths:
			addon = ''
		else:
			addon = 'COLLATE NOCASE'

		c = self.conn.cursor()

		# get parent id
		c.execute('SELECT id FROM roots WHERE path = "%s" %s' % (path, addon))
		res = c.fetchone()
		if res == None:
			c.close()
			return []
		
		root_id = res[0]

		# get cached paths
		res = []
		c.execute('SELECT id, path, modtime FROM paths WHERE root_id = %s' % (root_id))
		paths = c.fetchmany()
		while len(paths):
			res += paths
			paths = c.fetchmany()

		files = []
		for i in res:
			c.execute('SELECT file_name FROM files WHERE path_id = %s' % (i[0]))
			fs = c.fetchmany()
			while True:
				r = c.fetchmany()
				if not len(r):
					break

				fs += r
			files += fs

		c.close()
		
		res = zip([(x[1], x[2]) for x in res], files)

		return res

	def updateCachedPaths(self, root, paths):
		if self.conn == None:
			return

		if self.caseSensitivePaths:
			addon = ''
		else:
			addon = 'COLLATE NOCASE'

		c = self.conn.cursor()

		# root must have separator at the end
		if root[-1] != os.pathsep:
			root += os.pathsep

		# get root id
		c.execute('SELECT id FROM roots WHERE path = "%s" %s' % (root, addon))

		res = c.fetchone()
		if res == None:
			c.execute("INSERT OR REPLACE INTO roots VALUES(NULL, '%s', %s)" % (root, getModTime(root)))
			c.execute('SELECT id FROM roots WHERE path = "%s" %s' % (root, addon))
			res = c.fetchone()
			if res == None:
				return

		root_id = res[0]
		
		# remove root from paths
		rootLength = len(root)
		paths = [(x[0][rootLength:], x[1], x[2]) for x in paths]

		# insert paths
		# TODO: Batch insert
		for i in paths:
			c.execute("INSERT OR REPLACE INTO paths VALUES(NULL, %s, '%s', %s)" % (root_id, i[0], i[1]))
		self.conn.commit()

		# insert files
		# TODO: Batch insert
		for i in paths:
			c.execute('SELECT id FROM paths WHERE root_id = %s, path = "%s" %s' % (root_id, i[0], addon))
			path_id = c.fetchone()
			if path_id == None:
				continue
			
			for j in i[2]:
				c.execute("INSERT OR REPLACE INTO files VALUES(%s, '%s')" % (path_id[0], j))

		self.conn.commit()

		c.close()

def scan_dir(path, ignoreList, cache):
	path = os.abspath(path)
	ignoreList = map(caseMod, ignoreList)
	def in_ignore_list(f):
		for i in ignoreList:
			if fnmatch(caseMod(f), i):
				return True
		return False

	cachedPaths = cache.getCachedPaths(path)

	fileList = []
	addToCache = []
	for root, dirs, files in walk(path):
		fileList += [join(root, f) for f in files if not in_ignore_list(f)]
		
		toRemove = filter(in_ignore_list, dirs)
		for j in toRemove:
			dirs.remove(j)

		toRemove = []
		for i in dirs:
			fp = join(root, dirs)
			fpmt = getModTime(fp)
			
			for j in cachedPaths:
				if fpmt == j[1] and fp == j[0]:
					toRemove.append(i)
					fileList += [join(root, f) for f in files if not in_ignore_list(f)]
					break
			if (fp, getModTime(fp)) in cachedPaths:
				toRemove.append(i)
				fileList += [join(root, f) for f in files if not in_ignore_list(f)]


	n = len(path.encode("utf-8"))

	fileList = map(lambda x: x.encode("utf-8"), fileList)
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
