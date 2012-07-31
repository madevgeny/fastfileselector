import os
from os.path import getctime, getmtime

import sqlite3

def getModTime(path):
	return max(getctime(path), getmtime(path))

class PathsCache(object):
	def __init__(self, pathToCache, caseSensitivePaths):
		self.caseSensitivePaths = caseSensitivePaths

		if self.caseSensitivePaths:
			self.caseSelectAddon = ''
		else:
			self.caseSelectAddon = 'COLLATE NOCASE'

		# Check if database file exists and creates all needed paths.
		createTable = False
		if not os.path.exists(pathToCache):
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

		c = self.conn.cursor()

		# get parent id
		c.execute('SELECT id FROM roots WHERE path = "%s" %s' % (path, self.caseSelectAddon))
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

		c = self.conn.cursor()

		# root must have separator at the end
		if root[-1] != os.pathsep:
			root += os.pathsep

		# get root id
		c.execute('SELECT id FROM roots WHERE path = "%s" %s' % (root, self.caseSelectAddon))

		res = c.fetchone()
		if res == None:
			c.execute("INSERT OR REPLACE INTO roots VALUES(NULL, '%s', %s)" % (root, getModTime(root)))
			c.execute('SELECT id FROM roots WHERE path = "%s" %s' % (root, self.caseSelectAddon))
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
			c.execute('SELECT id FROM paths WHERE root_id = %s, path = "%s" %s' % (root_id, i[0], self.caseSelectAddon))
			path_id = c.fetchone()
			if path_id == None:
				continue
			
			for j in i[2]:
				c.execute("INSERT OR REPLACE INTO files VALUES(%s, '%s')" % (path_id[0], j))

		self.conn.commit()

		c.close()
