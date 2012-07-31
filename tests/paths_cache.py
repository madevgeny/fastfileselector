import os
from os.path import getctime, getmtime
from collections import defaultdict

import sqlite3

def getModTime(path):
	return max(getctime(path), getmtime(path))

class PathsCache(object):
	def __init__(self, pathToCache, caseSensitivePaths):
		self.caseSensitivePaths = caseSensitivePaths

		if self.caseSensitivePaths:
			self.caseSelectAddon = u''
		else:
			self.caseSelectAddon = u'COLLATE NOCASE'

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
				c.executescript(u"""
					CREATE TABLE roots (id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, modtime INTEGER);
					CREATE TABLE paths (id INTEGER PRIMARY KEY AUTOINCREMENT, root_id INTEGER SECONDARY KEY, path TEXT, modtime INTEGER);
					CREATE TABLE files (path_id INTEGER PRIMARY KEY, file_name TEXT);
				""")
				conn.commit()
				c.close()

	# Returns unicoded list of files
	# ((path, mod_time), (files))
	def getCachedPaths(self, root):
		if self.conn == None:
			return []

		c = self.conn.cursor()

		# get cached paths
		c.execute(u'''
			SELECT paths.path, paths.modtime, files.file_name FROM roots 
			JOIN paths ON (roots.id == paths.root_id)
			JOIN files ON (paths.id == files.path_id)
			WHERE path = "%s" %s
		''' % (path, self.caseSelectAddon))

		res = defaultdict(list)

		paths = c.fetchmany()
		while len(paths):
			for i in paths
			res += paths
			paths = c.fetchmany()

		files = []
		for i in res:
			c.execute(u'SELECT file_name FROM files WHERE path_id = %s' % (i[0]))
			fs = c.fetchmany()
			while True:
				r = c.fetchmany()
				if not len(r):
					break

				fs += r
			files.append(fs)

		c.close()
		
		res = zip([(x[1], x[2]) for x in res], files)
		res.sort(key = lambda x: x[0][0])

		return res

	# root, paths mustbe in unicode
	def updateCachedPaths(self, root, paths):
		if self.conn == None:
			return

		c = self.conn.cursor()

		# root must have separator at the end
		if root[-1] != os.pathsep:
			root += os.pathsep

		# get root id
		c.execute(u'SELECT id FROM roots WHERE path = "%s" %s' % (root, self.caseSelectAddon))

		res = c.fetchone()
		if res == None:
			c.execute(u"INSERT OR REPLACE INTO roots VALUES(NULL, '%s', %s)" % (root, getModTime(root)))
			c.execute(u'SELECT id FROM roots WHERE path = "%s" %s' % (root, self.caseSelectAddon))
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
			c.execute(u"INSERT OR REPLACE INTO paths VALUES(NULL, %s, '%s', %s)" % (root_id, i[0], i[1]))
		self.conn.commit()

		# insert files
		# TODO: Batch insert
		for i in paths:
			c.execute(u'SELECT id FROM paths WHERE root_id = %s, path = "%s" %s' % (root_id, i[0], self.caseSelectAddon))
			path_id = c.fetchone()
			if path_id == None:
				continue
			
			# delete old files
			c.execute(u'DELETE FROM files WHERE path_id)
			for j in i[2]:
				c.execute("INSERT OR REPLACE INTO files VALUES(%s, '%s')" % (path_id[0], j))

		self.conn.commit()

		c.close()
