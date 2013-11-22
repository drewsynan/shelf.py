import os, sys, csv

if __name__ == "__main__":
	if len(sys.argv) >= 2:
		pass
		#go(sys.argv[1])
	else:
		print "Usage: "
		print sys.argv[0] + " inputfilename.csv"

def go(csv):

	#create search stack
	searchStack = []
	try:
		with open(csv, 'rb') as csvfile:
			reader = csv.reader(csvfile);
			for row in reader:
				searchStack.append(row[0])
	except:
		print "lol file error or something"

	search(searchStack)

def search(stack):
	from PyZ3950 import zoom, zmarc
	#create connections

class recordsNotFound(Exception):
	pass

class couldNotConnect(Exception):
	pass

class searcher:
	def __init__(self):
		pass
	def search(self, isbn13):
		pass

class z3950Searcher(searcher):

	def __init__(self, hostname='z3950.loc.gov', port=7090, databaseName='VOYAGER', minIntervalTime=2000):
		self.__LOC_hostname = 'z3950.loc.gov'
		self.__LOC_port = 7090
		self.__LOC_databaseName = 'VOYAGER'

		self.__UOFC_hostname = 'libcat.uchicago.edu'
		self.__UOFC_port = 210
		self.__UOFC_databaseName = 'uofc'

		from PyZ3950 import zoom, zmarc

		self.hostname = hostname
		self.port = port
		self.databaseName = databaseName
		self.minIntervalTime = minIntervalTime

		self.__load()

		self.ready = True
	def __load(self):
		from PyZ3950 import zoom, zmarc
		try:
			self.conn = zoom.Connection(self.hostname, self.port)
			self.conn.databaseName = self.databaseName
		except:
			raise couldNotConnect()

	def __ssearch(self, isbn13):
		from PyZ3950 import zoom, zmarc
		query = zoom.Query('CCL', 'isbn=' + str(isbn13))
		try:
			res = self.conn.search(query)
		except:
			print "refreshing connection"
			self.conn.close()
			try:
				self.conn = zoom.Connection(self.hostname, self.port)
				self.conn.databaseName = self.databaseName
			except:
				raise couldNotConnect()

			print "Searching"
			res = self.conn.search(query)
		if len(res) > 0:
			print res[0]
		else:
			raise recordsNotFound()

	def __asearch(self, isbn13):
		pass

	def search(self, isbn13):
		self.__ssearch(isbn13)

	def loc(self):
		#make into loc searcher
		self.conn.close()
		self.hostname = self.__LOC_hostname
		self.port = self.__LOC_port
		self.databaseName = self.__LOC_databaseName

		try:
			self.conn = zoom.Connection(self.hostname, self.port)
		except:
			raise couldNotConnect()
		self.conn.databaseName = self.databaseName

	def uofc(self):
		#make into uofc searcher
		self.conn.close()
		self.hostname = self.__UOFC_hostname
		self.port = self.__UOFC_port
		self.databaseName = self.__UOFC_databaseName

		try:
			self.conn = zoom.Connection(self.hostname, self.port)
		except:
			raise couldNotConnect()
		self.conn.databaseName = self.databaseName