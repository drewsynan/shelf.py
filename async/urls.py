import concurrent.futures
import urllib2
from PyZ3950 import zoom, zmarc
import datetime

URLS = ['http://www.google.com/',
		'http://www.cnn.com/',
		'http://europe.wsj.com/',
		'http://www.bbc.co.uk/',
		'http://fake-ass-domain-na.me']

z3950Servers = [{"host":"z3950.loc.gov", "port":7090, "databaseName":'VOYAGER'},
			{"host":"libca.uchicago.edu", "port":210, "databaseName":'uofc'},
			{"host":"grammy.mit.edu", "port":9909, "databaseName":'mit01'}]

def load_url(url, timeout):
	return urllib2.urlopen(url, timeout=timeout).read()

def connect(dbDict):
	try:
		conn = zoom.Connection(dbDict["host"], dbDict["port"], databaseName=dbDict["databaseName"])
	except:
		raise Exception("Could Not Connect")
	return conn

class searcherNotReady(Exception):
	pass
class noRecordsFound(Exception):
	pass
class couldNotConnect(Exception):
	pass
class searchFailed(Exception):
	pass

class searcher:
	def __init__(self, dbDict, minBreakTime=2000):
		breakSeconds = minBreakTime/1000
		self.minBreakTime = datetime.timedelta(seconds=breakSeconds)
		self.hostname = dbDict["host"]
		self.port = dbDict["port"]
		self.databaseName = dbDict["databaseName"]
		self.cnxn = zoom.Connection(self.hostname, self.port, databaseName=self.databaseName, connect=0)

		try:
			self.cnxn.connect()
		except:
			raise couldNotConnect("Could not connect to database.")

		self._LastSearch = None
	def __str__(self):
		return self.hostname

	def search(self, searchKey, searchValue):
		
		if not self.isReady():
			raise searcherNotReady()
		else:
			query = zoom.Query('CCL', searchKey + "=" + str(searchValue))

		try:
			self._LastSearch = datetime.datetime.now()
			res = self.cnxn.search(query)
		except:
			try:
				self.cnxn.close()
				self.cnxn.connect()

				res = self.cnxn.search(query)
			except:
				raise searchFailed()
		if len(res) > 0:
			return res
		else:
			raise noRecordsFound()

	def isReady(self):
		if self._LastSearch == None:
			return True
		elif (datetime.datetime.now() - self._LastSearch) > self.minBreakTime:
			return True
		else:
			return False



with concurrent.futures.ThreadPoolExecutor(max_workers=len(z3950Servers)) as executor:
	future_to_cnxn = {executor.submit(searcher, server): server for server in z3950Servers}

	connectionPool = []
	for future in concurrent.futures.as_completed(future_to_cnxn):
		cnxn = future_to_cnxn[future]
		try:
			data = future.result()
		except Exception as exc:
			print "%r generated an exception: %s" % (cnxn, exc)
		else:
			print "Connected to %s" % data.cnxn.host
			connectionPool.append(data)

def closeAll():
	for searcher in connectionPool:
		searcher.cnxn.close()
