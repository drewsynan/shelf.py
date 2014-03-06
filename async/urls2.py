import concurrent.futures
import urllib2
from PyZ3950 import zoom, zmarc
import datetime
import time
import csv
import uuid

################################################
################################################
##### SAMPLE AND TEST DATA #####################
test_searchISBNS = ['0226422801',
					'0226423743',
					'0226423808',
					'0226424243',
					'0226425169',
					'0226425193',
					'0226425746',
					'0226425770',
					'0226428486',
					'0226428761',
					'0226429636',
					'0226428761',
					'0226429636',
					'0226429652',
					'0226429849',
					'0226430804',
					'0226431568',
					'0226431630',
					'0226432017',
					'0226434737',
					'0226435091',
					'0226435334',
					'0226437205',
					'0226437191',
					'0226437213',
					'0226437221',
					'0226437248',
					'0226437256',
					'0226437655',
					'0226437329',
					'0226437779',
					'0226438295',
					'0226439607',
					'0226439569',
					'0226439461',
					'0226439992',
					'0226442217',
					'0226448487',
					'0226450201',
					'0226450023',
					'0226450252',
					'0226450392',
					'0226450384',
					'0226450422',
					'0226451143',
					'0226451348',
					'0226451410',
					'0226452360',
					'0226077683',
					'0226453499',
					'0226453006',
					'0226454924',
					'0226454932',
					'0226454940',
					'0226454959',
					'0226455009',
					'0226458059',
					'0226462013',
					'0226464016',
					'0226464040',
					'0226463931',
					'0226464776',
					'0226465667',
					'0226465837',
					'0226467260',
					'0226473252',
					'0226473287',
					'0226467910',
					'0226468089',
					'0226468690',
					'0226468739',
					'0226468720',
					'0226468755',
					'0226469085',
					'0226469115',
					'0226469212',
					'0226668452',
					'0226469468',
					'0226469549',
					'0226469662',
					'0226469735',
					'0226469905',
					'0226470865',
					'0226472612',
					'0226472663',
					'0226473074',
					'0226474178',
					'0226475212',
					'0226475662',
					'0226475514',
					'0226475654',
					'0226474895',
					'0226476081',
					'0226477215',
					'0226476979',
					'0226481166',
					'0226481166',
					'0226481166',
					'0226481166',
					'0226482359']

'''test_searchISBNS = ['9780226922843',
					'9780226699080',
					'9780226701011',
					'9780226701707',
					'9780226036915',
					'9780226703145',
					'9780226701516',
					'9780226701462',
					'9780226701479',
					'9780226150772',
					'9780226701981',
					'9780226701967',
					'9780226702230',
					'9780226702247',
					'9780226702278',
					'9780226041001',
					'9780226702285',
					'9780226702360',
					'9780226702667',
					'9780226702650',
					'9780826331755',
					'9780226702704',
					'9780226702704',
					'9780226702704',
					'9780226702681',
					'9780226702711',
					'9780226702728',
					'9780226924007',
					'9780226702773',
					'9780226702759']'''

'''test_searchISBNS = []
try:
	with open('bigtest.csv','rb') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			test_searchISBNS.append(row[0])
except Exception as e:
	print e'''


URLS = ['http://www.google.com/',
		'http://www.cnn.com/',
		'http://europe.wsj.com/',
		'http://www.bbc.co.uk/',
		'http://fake-ass-domain-na.me']

#test_z3950Servers = []
#
#try:
#	with open('servers.csv','rb') as csvfile:
#		reader = csv.reader(csvfile)
#		for row in reader:
#			d = {}
#			d['host'] = row[0]
#			d['port'] = int(row[1])
#			d['databaseName'] = row[2]
#			test_z3950Servers.append(d)
#except Exception as e:
#	print e

'''
test_z3950Servers = [{"host":"z3950.loc.gov", "port":7090, "databaseName":'VOYAGER'},
			{"host":"libcat.uchicago.edu", "port":210, "databaseName":'uofc'},
			{"host":"catalog.princeton.edu", "port":7090, "databaseName": 'voyager'},
			{"host":"janus.uoregon.edu","port":210, "databaseName":"innopac"},
			{"host":"libdb.lib.upenn.edu","port":7090, "databaseName":'voyager'},
			{"host":"library.mit.edu","port":9909,"databaseName":'mit01'},
			{"host":"prodorbis.library.yale.edu","port":7090,"databaseName":'voyager'},
			{"host":"clio-db.cc.columbia.edu","port":7090,"databaseName":'VOYAGER'},
			{"host":"library.ua.edu","port":7090,"databaseName":"VOYAGER"},
			{"host":"library.bu.edu","port":210,"databaseName":"INNOPAC"},
			{"host":"clas.caltech.edu","port":210,"databaseName":"INNOPAC"}]

'''



test_z3950Servers = [
					#{"config" : {"host":"libcat.uchicago.edu","port":210,"databaseName":'uofc'}, "threads" : 2},
					{"config" : {"host":"z3950.loc.gov", "port":7090, "databaseName":'VOYAGER'}, "threads" : 5},
					{"config" : {"host":"prodorbis.library.yale.edu","port":7090,"databaseName":'voyager'}, "threads" : 3},
					{"config" : {"host":"catalog.princeton.edu", "port":7090, "databaseName": 'voyager'}, "threads": 15},
					{"config" : {"host":"libdb.lib.upenn.edu","port":7090, "databaseName":'voyager'}, "threads" : 15},
					{"config" : {"host":"clio-db.cc.columbia.edu","port":7090,"databaseName":'VOYAGER'}, "threads" : 10}
					]

###########################################################################
###########################################################################
###########################################################################

def load_url(url, timeout):
	return urllib2.urlopen(url, timeout=timeout).read()

def connect(dbDict):
	try:
		conn = zoom.Connection(dbDict["host"], dbDict["port"], databaseName=dbDict["databaseName"])
	except:
		raise Exception("Could Not Connect")
	return conn

class searcherNotReady(Exception):
	def __init__(self,msg,hostname):
		super(searcherNotReady, self).__init__(msg)
		self.hostname = hostname

class noRecordsFound(Exception):
	def __init__(self,msg,hostname,searchKey,searchValue,hostUid):
		super(noRecordsFound, self).__init__(msg)
		self.hostUid = hostUid
		self.hostname = hostname
		self.searchKey = searchKey
		self.searchValue = searchValue

class couldNotConnect(Exception):
	def __init__(self,msg,hostname,hostUid):
		super(couldNotConnect, self).__init__(msg)
		self.hostname = hostname
		self.hostUid = hostUid

class searchFailed(Exception):
	def __init__(self,msg,hostname,searchKey,searchValue,hostUid):
		super(searchFailed, self).__init__(msg)
		self.hostUid = hostUid
		self.hostname = hostname
		self.searchKey = searchKey
		self.searchValue = searchValue

class searcher:
	def __init__(self, dbDict, minBreakTime=100):
		self.breakSeconds = minBreakTime/1000
		self.minBreakTime = datetime.timedelta(seconds=self.breakSeconds)
		self.hostname = dbDict["host"]
		self.port = dbDict["port"]
		self.databaseName = dbDict["databaseName"]
		self.cnxn = zoom.Connection(self.hostname, self.port, databaseName=self.databaseName, connect=0)

		self.uid = self.hostname + "_" + uuid.uuid4().hex

		try:
			self.cnxn.connect()
		except:
			raise couldNotConnect("Could not connect to database.",self.hostname,self.uid)

		self._LastSearch = None
	def __str__(self):
		return self.hostname

	def aSearch(self,searchKey, searchValue):
		beginTime = datetime.datetime.now()
		try:
			res = self.search(searchKey, searchValue)
			endTime = datetime.datetime.now()

			returnD = { 'hostname': self.hostname,
						'hostUid': self.uid,
						'searchTime': endTime-beginTime,
						'searchKey': searchKey,
						'searchValue': searchValue,
						'results': None} #'results': res}

			time.sleep(self.breakSeconds)
			return returnD
		except noRecordsFound as e:
			time.sleep(self.breakSeconds)
			raise e
	def setUID(self,uid):
		self.uid = uid;

	def search(self, searchKey, searchValue):
		
		if not self.isReady():
			raise searcherNotReady("Searcher not ready", self.hostname)
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
				raise searchFailed("Search failed",self.hostname,searchKey,searchValue,self.uid)
		if len(res) > 0:
			return self.toMARC(res)
		else:
			raise noRecordsFound("No Records Found",self.hostname,searchKey,searchValue,self.uid)

	def isReady(self):
		if self._LastSearch == None:
			return True
		elif (datetime.datetime.now() - self._LastSearch) > self.minBreakTime:
			return True
		else:
			return False

	def toMARC(self, resultSet):
		try:
			marc = zmarc.MARC(resultSet[0].data)
			parsedMarc = marc.fields
			return parsedMarc
		except:
			raise Exception()

def connectionCompletedCallback(connectionFuture):
	try:
		server = connectionFuture.result()
		print "Connected successfully to " + server.hostname
		connectionPool[server.uid] = server
	except couldNotConnect as c:
		print "Could not connect to " + c.hostname
		outTheGame.append(c.hostUid)
	except Exception as e:
		print e


connectionPool = {}
outTheGame = []

neededThreads = 1
for server in test_z3950Servers:
	neededThreads = neededThreads + server['threads']

with concurrent.futures.ThreadPoolExecutor(max_workers=neededThreads) as connExecutor:
	#future_to_cnxn = {executor.submit(searcher, server): server for server in test_z3950Servers}
	print "connecting to servers...."
	future_to_cnxn = {}

	for server in test_z3950Servers:
		for x in range(0,server['threads']):
			future = None
			future = connExecutor.submit(searcher, server['config'])
			#print server
			future.add_done_callback(connectionCompletedCallback)
			future_key = server['config']['host'] + "_" + uuid.uuid4().hex
			future_to_cnxn[future_key] = future

def searchCompletedCallback(searchFuture):
	try:
		records = searchFuture.result()
		rawResults[records['searchValue']] = records
		searchResults[records['searchValue']] = records['results']
		availableSearchers.append(records['hostUid'])
		#print "          returning " + records['hostUid']
	except noRecordsFound as nrf:
		#print nrf.searchValue + " not found"
		noRecordsFoundList[nrf.searchValue] = nrf.hostname
		availableSearchers.append(nrf.hostUid)
	except searchFailed as sf:
		failedList.append(sf.hostUid)


noRecordsFoundList = {}
failedList = []
searchResults = {}
rawResults = {}

availableSearchers = connectionPool.keys()

searchStart = datetime.datetime.now()

with concurrent.futures.ThreadPoolExecutor(max_workers=len(availableSearchers)) as searchExecutor:
	searchFutures = {}
	while True:
		try:
			nextSearcher = availableSearchers.pop()
			try:
				nextISBN = test_searchISBNS.pop()
				#print "     Searching " + str(nextISBN) + " on " + nextSearcher
				print str(len(test_searchISBNS)) + " searches left"
			except IndexError as e:
				print e
				break

			try:
				f = searchExecutor.submit(connectionPool[nextSearcher].aSearch, 'isbn', str(nextISBN))
				f.add_done_callback(searchCompletedCallback)
				searchFutures[nextISBN] = f
			except IndexError:
				print "reached end of search list"
			except:
				print e
		except IndexError:
			#print "sleeping for searchers... " + str(len(test_searchISBNS)) + " searches left"
			time.sleep(0.1)
	print "Waiting for final searches to complete..."

searchEnd = datetime.datetime.now()
searchDuration = searchEnd - searchStart

def closeAll():
	closures = []
	with concurrent.futures.ThreadPoolExecutor(max_workers=len(connectionPool.keys())) as executor:
		for searcher in connectionPool.keys():
			print "Closing " + searcher
			closures.append(executor.submit(connectionPool[searcher].cnxn.close))
	#print closures

class aGoogleSearcher:

	def __init__(self):
		#self.googleApiKey = "AIzaSyCSH18cCHo6ggNg-XYkrt10GMk3fkFSuhw"
		self.googleApiKey = "AIzaSyAaVCpblCix3LOOu0HtpdG-MXXam5criSI" #alternate key

	class noRecordsFound(Exception):
		def __init__(self,msg,searchKey,searchValue):
			super(aGoogleSearcher.noRecordsFound, self).__init__(msg)
			self.searchKey = searchKey
			self.searchValue = searchValue


	def setApiKey(self, key):
		"""Setter to make the Google Books search API key to something other than the default"""

		self.googleApikey = key

	def search(self, isbn13):
		"""Searches Google Books using the API for the current book using self.isbn13"""

		import json
		import urllib2

		returnDict = {}
		returnDict['isbn10'] = ""
		returnDict['isbn13'] = isbn13

		baseURL = "https://www.googleapis.com/books/v1/volumes?q=isbn:" #Google Books API v 1 base url
		addOn = "&key=" #needed for GET request
		jsonURL = baseURL + str(isbn13) + addOn + self.googleApiKey + "&country=US" #build a URL string for searching

		print "  Looking up book " + str(isbn13) + "...", #log the search to the console
		try:
			googleBook = json.load(urllib2.urlopen(jsonURL)) #attempt to load JSON from Google Books using the URL built above

			returnDict['jsonError'] = False

			if googleBook['totalItems'] > 0: #see if any items were returns from search
				returnDict['found'] = True

				firstVolume = googleBook['items'][0]['volumeInfo'] #get the first volume object from the processed JSON
				returnDict['title'] = firstVolume['title'] #get the title

				idents = firstVolume['industryIdentifiers']
				for ident in idents:
					if ident['type'] == 'ISBN_10':
						returnDict['isbn10'] = ident['identifier']
					elif ident['type'] == 'ISBN_13':
						returnDict['isbn13'] = ident['identifier']

				if 'authors' in firstVolume.keys():
					returnDict['authors'] = firstVolume['authors'] #get the array of authors
				else:
					returnDict['authors'] = [""]

				returnDict = self.setSimpleStrings(returnDict)

				print "   [OK]" #log that the book was found to the console

				returnDict['format'] = ""
				return returnDict
				
			else:
				#no items were found
				returnDict['found'] = False
				returnDict['jsonError'] = False
				returnDict['title'] = ""
				returnDict['authors'] = [""]
				returnDict['isbn13'] = isbn13
				returnDict['isbn10'] = ""
				returnDict['simpleFirstName'] = ""
				returnDict['simpleLastName'] = ""
				returnDict['simpleTitle'] = ""

				print "   [!]" #log to the console that the book was not found
				raise aGoogleSearcher.noRecordsFound("No records found","isbn13",isbn13)

		except aGoogleSearcher.noRecordsFound as nrf:
			raise nrf
		except:
			#google books as probably thrown an API error
			returnDict['found'] = False
			returnDict['title'] = ""
			returnDict['authors'] = [""]
			returnDict['jsonError'] = True
			returnDict['isbn13'] = isbn13
			returnDict['isbn10'] = ""
			returnDict['simpleFirstName'] = ""
			returnDict['simpleLastName'] = ""
			returnDict['simpleTitle'] = ""
			#print "   [HTTP ERROR]"
			print e

		#returnDict['format'] = "" #google books api does not support format info
		#return returnDict

	def setSimpleStrings(self, lookupDict):
		"""
		Sets instance variables with simplified representations of the author and title
		used for searching and seeing which books are out of order.
		Author names are represented like AUTHORFIRSTNAMEMIDDLENAME LASTNAME in all caps with no spaces.
		Similarly, titles are represented INALLCAPSWITHNOSPACES
		"""

		import string #used for stripping punctuation from names and titles

		#initialize temporary variables
		simpleFirstName = ""
		simpleLastName = ""
		simpleTitle = ""

		#check to see if book was found and has info from Google Books
		if lookupDict['found'] and lookupDict['authors'] != [""]: 
			#Get the name of the first author (the first item in the author array)
			firstAuthorName = lookupDict['authors'][0].upper().split(",")[0].split() #get rid of JR or SR if it exists and then split by word

			#the code below extracts the author's last name

			pivot = -1 #set the default last name to be the last word of the author array
			if "DE" in firstAuthorName:
				#Look for "DE" in the name array, if found, make DE -> to the end the last name
				# de
				# de la
				# de los
				# de le
				pivot = firstAuthorName.index("DE")
				lastname = ''.join(c for c in firstAuthorName[pivot:] if c not in string.punctuation)
			elif "DELLA" in firstAuthorName:
				#della
				pivot = firstAuthorName.index("DELLA")
				lastname = ''.join(c for c in firstAuthorName[pivot:] if c not in string.punctuation)
			elif "VAN" in firstAuthorName:
				# van
				# van de
				# van der
				# van den
				pivot = firstAuthorName.index("VAN")
				lastname = ''.join(c for c in firstAuthorName[pivot:] if c not in string.punctuation)
			elif "VON" in firstAuthorName:
				# von
				pivot = firstAuthorName.index("VON")
				lastname = ''.join(c for c in firstAuthorName[pivot:] if c not in string.punctuation)
			else:
				# O' etc
				lastname = ''.join(c for c in firstAuthorName[-1] if c not in string.punctuation)

			#first names are all remaining words unused in last name extraction
			firstnames = firstAuthorName[:pivot]

			for name in firstnames:
				#strip punctuation from first names
				simpleFirstName += ''.join(c for c in name if c not in string.punctuation)

			titleArray = lookupDict['title'].upper().split() #break title into an array of words

			#check to see if first word in title is THE, A, or AN
			if titleArray[0] == "THE" or titleArray[0] == "A" or titleArray[0] == "AN":
				#remove articles from title, for alphabetization purposes
				del titleArray[0]

			#flatten the array into a string of all caps with no spaces or punctuation
			for word in titleArray:
				simpleTitle += ''.join(c for c in word if c not in string.punctuation)

			#set the instance variables to the temporary variable values
			lookupDict['simpleFirstName'] = simpleFirstName
			lookupDict['simpleLastName'] = lastname
			lookupDict['simpleTitle'] = simpleTitle
		else:
			#if book was not found in Google Books, do nothing
			lookupDict['simpleFirstName'] = ""
			lookupDict['simpleLastName'] = ""
			lookupDict['simpleTitle'] = ""
		
		return lookupDict

#google the items not
myaGoogleSearcher = aGoogleSearcher()
toSearch = noRecordsFoundList.keys()
googleFutures = []
hopeless = []

def googleCompletedCallback(googleFuture):
	try:
		record = googleFuture.result()
		rawResults[record['isbn13']] = {
			'hostUid' : 'GoogleBooks',
			'hostname' : 'books.google.com',
			'searchKey': 'isbn',
			'searchTime' : 0,
			'results' : None,
			'searchValue' : record['isbn13']
		}

	except aGoogleSearcher.noRecordsFound as gNrf:
		hopeless.append(gNrf.searchValue)
		noRecordsFoundList[gNrf.searchValue] = 'books.google.com'

with concurrent.futures.ThreadPoolExecutor(max_workers=30) as googleExecutor:
	for isbn in toSearch:
		f = googleExecutor.submit(myaGoogleSearcher.search, str(isbn))
		f.add_done_callback(googleCompletedCallback)

		googleFutures.append(f)

def processRawResults():
	timingDict = {}
	countDict = {}
	processed = {}
	for result in rawResults.keys():
		hostname = rawResults[result]['hostname']
		timing = rawResults[result]['searchTime']
		try:
			timingDict[hostname] = timingDict[hostname] + timing
			countDict[hostname] = countDict[hostname] + 1
		except KeyError:
			timingDict[hostname] = timing
			countDict[hostname] = 1

	for key in timingDict.keys():
		processed[key] = timingDict[key] / countDict[key]

	#return processed

	print "-Search Timings---"
	print "Total search time: " + str(searchDuration) + " for " + str(len(noRecordsFoundList.keys()) + len(searchResults.keys())) + " records on " + str(len(availableSearchers)) + " connections"
	print "Averages:"
	for key in processed.keys():
		print "	" + str(processed[key]) + ":	" + key 
	print "------------------"

def processNotFound():
	from collections import Counter
	recordsPerServer = Counter(noRecordsFoundList.values())
	connectionsPerHost = Counter([connectionPool[hostUid].hostname for hostUid in availableSearchers])
	ret = {}
	for hostname in connectionsPerHost.keys():
		ret[hostname] = recordsPerServer[hostname] / connectionsPerHost[hostname]
	#return ret
	print str(len(noRecordsFoundList.keys()) + len(searchResults.keys())) + " records searched / " + str(len(searchResults.keys())) + " found; " + str(len(noRecordsFoundList.keys())) + " not found"
	print "-Not found-------"
	for key in ret.keys():
		print key + ": " + str(ret[key])
	print "-----------------"

closeAll()
print processNotFound()
print processRawResults()


