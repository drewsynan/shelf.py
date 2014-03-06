from PyZ3950 import zoom, zmarc
import datetime, time, uuid, concurrent.futures, urllib2
import csv

class aSearchFactory:
	def __init__():
		pass
	def aListSearch():
		pass

class aSearcher:

	class searcherNotReady(Exception):
		pass

	class noRecordsFound(Exception):
		pass

	class couldNotConnect(Exception):
		pass

	class searchFailed(Exception):
		pass

	def __init__():
		pass
	def aSearch():
		pass

	def _convert13To10(self, isbn13):
		trimmed = str(isbn13)[3:-1]

		checkDigit = 0
		multiplier = 10
		for digit in trimmed:
			checkDigit = checkDigit + multiplier * int(digit)
			multiplier = multiplier - 1

		checkDigit = (11 - (checkDigit % 11)) % 11

		if checkDigit == 10:
			checkDigit = "X"

		return trimmed + str(checkDigit)

	def _convert10To13(self, isbn10):
		trimmed = str(isbn10)[:-1]
		prepped = "978" + trimmed

		sum = 0
		for i in range(len(prepped)):
			c = int(prepped[i])
			if i % 2: w = 3
			else: w = 1
			sum += w * c
		checkDigit = (10 - (sum % 10)) % 10

		return prepped + str(checkDigit)


class aZ3950Searcher(aSearcher):

	class searcherNotReady(Exception):
		def __init__(self,msg,hostname):
			super(aZ3950Searcher.searcherNotReady, self).__init__(msg)
			self.hostname = hostname

	class noRecordsFound(Exception):
		def __init__(self,msg,hostname,searchKey,searchValue,hostUid):
			super(aZ3950Searcher.noRecordsFound, self).__init__(msg)
			self.hostUid = hostUid
			self.hostname = hostname
			self.searchKey = searchKey
			self.searchValue = searchValue

	class couldNotConnect(Exception):
		def __init__(self,msg,hostname,hostUid):
			super(aZ3950Searcher.couldNotConnect, self).__init__(msg)
			self.hostname = hostname
			self.hostUid = hostUid

	class searchFailed(Exception):
		def __init__(self,msg,hostname,searchKey,searchValue,hostUid):
			super(aZ3950Searcher.searchFailed, self).__init__(msg)
			self.hostUid = hostUid
			self.hostname = hostname
			self.searchKey = searchKey
			self.searchValue = searchValue

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
			raise self.couldNotConnect("Could not connect to database.",self.hostname,self.uid)

		self._LastSearch = None
	def __str__(self):
		return "Asynchronous z3940 searcher on " + self.hostname

	def aSearch(self,searchKey, searchValue):

		beginTime = datetime.datetime.now()
		try:
			res = self._search(searchKey, searchValue)
			endTime = datetime.datetime.now()

			returnD = { 'hostname': self.hostname,
						'hostUid': self.uid,
						'searchTime': endTime - beginTime,
						'searchKey': searchKey,
						'searchValue': searchValue,
						'results': res}

			time.sleep(self.breakSeconds)

			return returnD
		except aZ3950Searcher.noRecordsFound as e:
			time.sleep(self.breakSeconds)
			raise e
	def setUID(self,uid):
		self.uid = uid;

	def _search(self, searchKey, searchValue):
		
		if not self.isReady():
			raise self.searcherNotReady("Searcher not ready", self.hostname)
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
				raise self.searchFailed("Search failed",self.hostname,searchKey,searchValue,self.uid)
		if len(res) > 0:
			return self.__processResults(self.__toMARC(res), searchKey, searchValue)
		else:
			raise self.noRecordsFound("No Records Found",self.hostname,searchKey,searchValue,self.uid)

	def isReady(self):
		if self._LastSearch == None:
			return True
		elif (datetime.datetime.now() - self._LastSearch) > self.minBreakTime:
			return True
		else:
			return False

	def __processResults(self, resultMARC, searchKey, searchValue):
		returnDict = {}

		returnDict['found'] = True

		if "ISBN" in searchKey.upper():
			if len(searchValue) == 10:
				returnDict['isbn10'] = searchValue
				returnDict['isbn10'] = self._convert10To13(searchValue)
			elif len(searchValue) == 13:
				returnDict['isbn13'] = searchValue
				returnDict['isbn10'] = self._convert13To10(searchValue)

		### Parse Authors
		authors = []

		try: #try 100 field
			authorField = resultMARC.fields[100] # http://www.loc.gov/marc/bibliographic/concise/bd100.html
			for subfield in authorField[0][2]:
				if subfield[0] == 'a':
					#check to see if last character is a comma (will be if there is also a $d subfield)
					if subfield[1][-1] == ",":
						authors.append(subfield[1][:-1]) # trim last comma
					else:
						authors.append(subfield[1])
		except KeyError:
			try:
				authorField = resultMARC.fields[700] #try 700 field (used for editors, not authors) http://www.loc.gov/marc/bibliographic/concise/bd700.html
				for subfield in authorField[0][2]:
					if subfield[0] == 'a':
						#check to see if last character is a comma (will be if there is also a $d subfield)
						if subfield[1][-1] == ",":
							authors.append(subfield[1][:-1]) # trim last comma
						else:
							authors.append(subfield[1])
			except KeyError:
				print "No author could be determined from MARC record"
				authors = [""]
		if len(authors) == 0:
			authors = [""]
		returnDict['authors'] = authors



		### Parse Title
		titleField = resultMARC.fields[245][0] # http://www.loc.gov/marc/bibliographic/concise/bd245.html
		titleSubFields = titleField[2]
		# $a is the title
		# $b is the subtitle
		# $c is the author / statement of responsiblity

		for subfield in titleSubFields:
			if subfield[0] == 'a':
				# check for semicolon in the subtitle
				if len(subfield[1].split(' :')) > 1:
					returnDict['title'] = subfield[1].split(' :')[0]
				else:
					returnDict['title'] = subfield[1].split(' /')[0]
			if subfield[0] == 'b': #fill in the subtitle
				returnDict['subtitle'] = subfield[1].split(' /')[0]

		### Parse Format
		identifiersField = resultMARC.fields[20] # http://www.loc.gov/marc/bibliographic/concise/bd020.html
		formatsDict = {}
		isbn10 = returnDict['isbn10']

		for field in identifiersField:
			subfields = field[2]
			for subfield in subfields:
				if (subfield[0] == 'a' or subfield[0] == 'z'): # ISBN
					parts = subfield[1].split(" (")
					extractedIsbn = parts[0]
					if len(parts) > 1: # see if there is format information
						format = parts[1].split(")")[0]
						splitFormat = format.split(" : ")
						if len(splitFormat) > 1 :
							if splitFormat[0] == 'paper' or splitFormat[0] == 'pbk':
								formatsDict[extractedIsbn] = 'paper'
							elif splitFormat[0] == 'cloth' or splitFormat[0] == 'hardcover':
								formatsDict[extractedIsbn] = 'cloth'
							else:
								formatsDict[extractedIsbn] = 'unknown'
						elif format == "pbk.":
							formatsDict[extractedIsbn] = 'paper'
						else:
							formatsDict[extractedIsbn] = 'unknown'
		try:
			returnDict['format'] = formatsDict[returnDict['isbn10']]
		except KeyError:
			returnDict['format'] = 'unknown'

		### Set simple strings
		returnDict = self.__setSimpleStrings(returnDict)

		return returnDict


	def __toMARC(self, resultSet):
		try:
			marc = zmarc.MARC(resultSet[0].data)
			return marc
		except:
			raise Exception("MARC conversion error")

	def __setSimpleStrings(self, lookupDict):
		import string

		firstAuthor = lookupDict['authors'][0]
		#print "First Author: " + firstAuthor

		split = firstAuthor.split(", ")
		if len(split) >1 :
			lookupDict['simpleLastName'] = ''.join(c for c in split[0].upper().replace(" ", "") if c not in string.punctuation)
			lookupDict['simpleFirstName'] = ''.join(c for c in split[1].upper().replace(" ","") if c not in string.punctuation)

		originalTitle = lookupDict['title']
		lookupDict['simpleTitle'] = ''.join(c for c in [word for word in originalTitle.split(":")[0].upper().split() if word not in ["AN", "A", "THE"]] if c not in string.punctuation)

		return lookupDict

class aZ3950SearchFactory(aSearchFactory):
	
	def __init__(self, configList):
		self.found = {}
		self.notFound = {}
		self.failed = []

		self.configList = configList

		self.connectionPool = {}
		self.availableSearchers = []
		self.outTheGameSearchers = []

		self.results = {}


		self.__connectToServers(self.configList)

	def __connectToServers(self, configList):

		neededThreads = 1
		for server in configList:
			neededThreads = neededThreads + server['threads']

		with concurrent.futures.ThreadPoolExecutor(max_workers=neededThreads) as connExecutor:
			#future_to_cnxn = {executor.submit(searcher, server): server for server in test_z3950Servers}
			print "connecting to servers...."
			future_to_cnxn = {}

			for server in configList:
				for x in range(0,server['threads']):
					future = None
					future = connExecutor.submit(aZ3950Searcher, server['config'])
					#print server
					future.add_done_callback(self.__connectionCompletedCallback)
					future_key = server['config']['host'] + "_" + uuid.uuid4().hex
					future_to_cnxn[future_key] = future

		self.availableSearchers = self.connectionPool.keys()
		self.CONNECTION_STATE = "on"

	def __connectionCompletedCallback(self, connectionFuture):
		try:
			server = connectionFuture.result()
			print "Connected successfully to " + server.hostname
			self.connectionPool[server.uid] = server
		except aZ3950Searcher.couldNotConnect as c:
			print "Could not connect to " + c.hostname
			self.outTheGameSearchers.append(c.hostUid)
		except Exception as e:
			print e

	def listSearch(self, searchList):
		self.found = {}
		self.notFound = {}
		self.failed = []
		self.results = {}

		self.searchStart = datetime.datetime.now()

		with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.availableSearchers)) as searchExecutor:
			self.searchFutures = {}
			while True:
				try:
					nextSearcher = self.availableSearchers.pop()
					try:
						nextISBN = searchList.pop()
						#print "     Searching " + str(nextISBN) + " on " + nextSearcher
						print str(len(searchList)) + " searches left"
					except IndexError as e:
						print e
						break

					try:
						f = searchExecutor.submit(self.connectionPool[nextSearcher].aSearch, 'isbn', str(nextISBN))
						f.add_done_callback(self.__searchCompletedCallback)
						self.searchFutures[nextISBN] = f
					except IndexError:
						print "reached end of search list"
					except:
						print e
				except IndexError:
					#print "sleeping for searchers... " + str(len(test_searchISBNS)) + " searches left"
					time.sleep(0.1)
			print "Waiting for final searches to complete..."

		self.searchEnd = datetime.datetime.now()
		self.searchDuration = self.searchEnd - self.searchStart

		results = {'found': self.found, 'notFound': self.notFound}

		self.results = results

		return results


	def __searchCompletedCallback(self, searchFuture):
		try:
			records = searchFuture.result()
			#rawResults[records['searchValue']] = records
			self.found[records['searchValue']] = records['results']
			self.availableSearchers.append(records['hostUid'])
			#print "          returning " + records['hostUid']
		except aZ3950Searcher.noRecordsFound as nrf:
			#print nrf.searchValue + " not found"
			self.notFound[nrf.searchValue] = nrf.hostname
			self.availableSearchers.append(nrf.hostUid)
		except aZ3950Searcher.searchFailed as sf:
			self.failed.append(sf.hostUid)
		except Exception as e:
			print e
			raise e

	def closeConnections(self):
		self.CONNECTION_STATE = "off"
		closures = []
		with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.connectionPool.keys())) as executor:
			for searcher in self.connectionPool.keys():
				print "Closing " + searcher
				closures.append(executor.submit(self.connectionPool[searcher].cnxn.close))
				if searcher in self.availableSearchers: self.availableSearchers.remove(searcher)
		#print closures
	def openConnections(self):
		if self.CONNECTION_STATE == "off":
			self.__connectToServers(self.configList)
		else:
			return

class aGoogleSearcher(aSearcher):
	def __init__(self, configDict):
		#self.googleApiKey = "AIzaSyCSH18cCHo6ggNg-XYkrt10GMk3fkFSuhw"
		#self.googleApiKey = "AIzaSyAaVCpblCix3LOOu0HtpdG-MXXam5criSI" #alternate key
		self.googleApiKey = configDict['googleApiKey']

	class noRecordsFound(Exception):
		def __init__(self,msg,searchKey,searchValue):
			super(aGoogleSearcher.noRecordsFound, self).__init__(msg)
			self.searchKey = searchKey
			self.searchValue = searchValue
	
	class searchFailed(Exception):
		def __init__(self,msg,searchKey,searchValue):
			super(aGoogleSearcher.searchFailed, self).__init__(msg)
			self.searchKey = searchKey
			self.searchValue = searchValue
			self.msg = msg

	def setApiKey(self, key):
		"""Setter to make the Google Books search API key to something other than the default"""

		self.googleApikey = key

	def aSearch(self, isbn):
		"""Searches Google Books using the API for the current book using self.isbn13"""

		import json
		import urllib2

		searchValue = isbn

		if len(isbn) == 10:
			isbn10 = isbn
			isbn13 = self._convert10To13(isbn)
		elif len(isbn) == 13:
			isbn10 = self._convert13To10(isbn)
			isbn13 = isbn

		returnDict = {}
		returnDict['isbn10'] = ""
		returnDict['isbn13'] = isbn13

		baseURL = "https://www.googleapis.com/books/v1/volumes?q=isbn:" #Google Books API v 1 base url
		addOn = "&key=" #needed for GET request
		jsonURL = baseURL + str(isbn13) + addOn + self.googleApiKey + "&country=US" #build a URL string for searching

		print "Looking up book " + str(isbn13) + "..." #, #log the search to the console
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

				returnDict = self.__setSimpleStrings(returnDict)

				#print "   [OK]" #log that the book was found to the console

				returnDict['format'] = ""
				
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

				#print "   [!]" #log to the console that the book was not found
				raise aGoogleSearcher.noRecordsFound("No records found","isbn",searchValue)

		except aGoogleSearcher.noRecordsFound as nrf:
			raise nrf
		except urllib2.HTTPError as h:
			httpError = h.read()
			#print httpError
			raise aGoogleSearcher.searchFailed(httpError,"isbn",searchValue)
		except Exception as e:
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
			raise e

		#returnDict['format'] = "" #google books api does not support format info
		#return returnDict

		searchResults = {
							"searchValue": searchValue, 
							"results": returnDict
						}
		return searchResults

	def __setSimpleStrings(self, lookupDict):
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

class aGoogleSearchFactory(aSearchFactory):
	def __init__(self, configList):
		configDict = configList[0]
		self.searcher = aGoogleSearcher(configDict['config'])
		self.threads = configDict['threads']

		self.found = {}
		self.notFound = {}
		self.failed = []

		self.results = {}

	def listSearch(self, searchList):
		googleFutures = []
		self.found = {}
		self.notFound = {}
		self.failed = []


		self.searchStart = datetime.datetime.now()
		with concurrent.futures.ThreadPoolExecutor(max_workers=30) as googleExecutor:
			for searchIsbn in searchList:
				f = googleExecutor.submit(self.searcher.aSearch, str(searchIsbn))
				f.add_done_callback(self.__googleCompletedCallback)

				googleFutures.append(f)

		self.searchEnd = datetime.datetime.now()
		self.searchDuration = self.searchEnd - self.searchStart

		searchResults = {'found': self.found, 'notFound': self.notFound}

		self.results = searchResults
		return searchResults

	def __googleCompletedCallback(self, googleFuture):
		try:
			record = googleFuture.result()
			self.found[record['searchValue']] = record['results']

		except aGoogleSearcher.noRecordsFound as gNrf:
			self.notFound[gNrf.searchValue] = 'books.google.com'
		except aGoogleSearcher.searchFailed as sf:
			self.failed.append(sf.searchValue)
			self.notFound[sf.searchValue] = 'FAILED: books.google.com'


class aHybridSearchFactory(aSearchFactory):
	def __init__(self, configDict):
		self.CONNECTION_STATE = "off"

		self.googleConfig = configDict['google']
		self.z3950ConfigList = configDict['z3950']

		self.aGoogleSearcher = aGoogleSearcher(self.googleConfig[0]['config'])
		
		self.found = {}
		self.notFound = {}
		self.failed = []

		self.results = {}

		self.connectionPool = {}
		self.availableSearchers = []
		self.outTheGameSearchers = []

		self.__connectToServers(self.z3950ConfigList)

	def __connectToServers(self, configList):

		neededThreads = 1
		for server in configList:
			neededThreads = neededThreads + server['threads']

		with concurrent.futures.ThreadPoolExecutor(max_workers=neededThreads) as connExecutor:
			#future_to_cnxn = {executor.submit(searcher, server): server for server in test_z3950Servers}
			print "connecting to servers...."
			future_to_cnxn = {}

			for server in configList:
				for x in range(0,server['threads']):
					future = None
					future = connExecutor.submit(aZ3950Searcher, server['config'])
					#print server
					future.add_done_callback(self.__connectionCompletedCallback)
					future_key = server['config']['host'] + "_" + uuid.uuid4().hex
					future_to_cnxn[future_key] = future

		self.availableSearchers = self.connectionPool.keys()
		self.CONNECTION_STATE = "on"

	def __connectionCompletedCallback(self, connectionFuture):
		try:
			server = connectionFuture.result()
			print "Connected successfully to " + server.hostname
			self.connectionPool[server.uid] = server
		except aZ3950Searcher.couldNotConnect as c:
			print "Could not connect to " + c.hostname
			self.outTheGameSearchers.append(c.hostUid)
		except Exception as e:
			print e

	def listSearch(self, searchList):
		self.found = {}
		self.notFound = {}
		self.failed = []
		self.results = {}

		self.searchStart = datetime.datetime.now()

		self.googleSearchExecutor = concurrent.futures.ThreadPoolExecutor(max_workers=self.googleConfig[0]['threads'])

		with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.availableSearchers)) as self.searchExecutor:
			self.searchFutures = {}
			self.searchFuturesGoogle = {}

			while True:
				try:
					nextSearcher = self.availableSearchers.pop()
					try:
						nextISBN = searchList.pop()
						#print "     Searching " + str(nextISBN) + " on " + nextSearcher
						print str(len(searchList)) + " searches left"
					except IndexError as e:
						print e
						break

					try:
						f = self.searchExecutor.submit(self.connectionPool[nextSearcher].aSearch, 'isbn', str(nextISBN))
						f.add_done_callback(self.__searchCompletedCallback)
						self.searchFutures[nextISBN] = f
					except IndexError:
						print "reached end of search list"
					except:
						print e
				except IndexError:
					#print "sleeping for searchers... " + str(len(test_searchISBNS)) + " searches left"
					time.sleep(0.1)
			print "Waiting for final searches to complete..."

		self.googleSearchExecutor.shutdown(wait=True)
		del self.googleSearchExecutor

		self.searchEnd = datetime.datetime.now()
		self.searchDuration = self.searchEnd - self.searchStart

		results = {'found': self.found, 'notFound': self.notFound}
		self.results = results

		return results


	def __searchCompletedCallback(self, searchFuture):
		try:
			records = searchFuture.result()
			#rawResults[records['searchValue']] = records
			self.found[records['searchValue']] = records['results']
			self.availableSearchers.append(records['hostUid'])
			#print "          returning " + records['hostUid']
		except aZ3950Searcher.noRecordsFound as nrf:
			#print nrf.searchValue + " not found"
			#Google Search the record
			try:
				gF = self.googleSearchExecutor.submit(self.aGoogleSearcher.aSearch,nrf.searchValue)
				gF.add_done_callback(self.__googleCompletedCallback)
				self.searchFuturesGoogle[nrf.searchValue] = gF
			except Exception as e:
				print e
				raise e

			#self.notFound[nrf.searchValue] = nrf.hostname
			self.availableSearchers.append(nrf.hostUid)
		except aZ3950Searcher.searchFailed as sf:
			self.failed.append(sf.hostUid)
		except Exception as e:
			print e
			raise e

	def __googleCompletedCallback(self, googleFuture):
		try:
			record = googleFuture.result()
			self.found[record['searchValue']] = record['results']

		except aGoogleSearcher.noRecordsFound as gNrf:
			self.notFound[gNrf.searchValue] = 'books.google.com'
		except aGoogleSearcher.searchFailed as sf:
			self.failed.append(sf.searchValue)
			self.notFound[sf.searchValue] = 'FAILED :: books.google.com : ' + sf.msg

	def closeConnections(self):
		self.CONNECTION_STATE = "off"
		closures = []
		with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.connectionPool.keys())) as executor:
			for searcher in self.connectionPool.keys():
				print "Closing " + searcher
				closures.append(executor.submit(self.connectionPool[searcher].cnxn.close))
				if searcher in self.availableSearchers: self.availableSearchers.remove(searcher)
		#print closures
	def openConnections(self):
		if self.CONNECTION_STATE == "off":
			self.__connectToServers(self.configList)
		else:
			return

####### TESTS ########

'''
### Tests for Searcher ###
print "Creating z3950 searcher"
aZS = aZ3950Searcher({"host":"clio-db.cc.columbia.edu","port":7090,"databaseName":'VOYAGER'})

try:
	print aZS.aSearch('isbn',"9780679752554") #Foucault / Discipline and Punish
except Exception as e:
	print e

try: 
	print aZS.aSearch("isbn","02264647260") #Dominick / Emile Durkheim (not in LOC or Goodle)
except aZ3950Searcher.noRecordsFound as e:
	print "No records found for " + e.searchKey + ": " + e.searchValue
###########################
'''


### Tests for Search Factory ###
print "Creating z3950 Search Factory"

test_searchISBNS = []
try:
	with open('bigtest.csv','rb') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			test_searchISBNS.append(row[0])
except Exception as e:
	print e

test_searchISBNS_short = ['9780226922843',
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
					'9780226702759']

factoryConfig = [
					#{"config" : {"host":"libcat.uchicago.edu","port":210,"databaseName":'uofc'}, "threads" : 2},
					{"config" : {"host":"z3950.loc.gov", "port":7090, "databaseName":'VOYAGER'}, "threads" : 5},
					{"config" : {"host":"prodorbis.library.yale.edu","port":7090,"databaseName":'voyager'}, "threads" : 3},
					{"config" : {"host":"catalog.princeton.edu", "port":7090, "databaseName": 'voyager'}, "threads": 15},
					{"config" : {"host":"libdb.lib.upenn.edu","port":7090, "databaseName":'voyager'}, "threads" : 15},
					{"config" : {"host":"clio-db.cc.columbia.edu","port":7090,"databaseName":'VOYAGER'}, "threads" : 10}
				]
'''aZSF = aZ3950SearchFactory(factoryConfig)
#aZSF.closeConnections()
try:
	aZSF_results = aZSF.listSearch(test_searchISBNS)
except Exception as e:
	print e

aZSF.closeConnections()



##### GOOGLE

aGS = aGoogleSearcher({"googleApiKey": "AIzaSyAaVCpblCix3LOOu0HtpdG-MXXam5criSI"})

try:
	aGS_result = aGS.aSearch("9780679752554") # Foucault / Discipline and Punish
except Exception as e:
	print e'''

googleFactoryConfig = [{"config" : {"googleApiKey": "AIzaSyAaVCpblCix3LOOu0HtpdG-MXXam5criSI"}, "threads": 30}]
'''aGSF = aGoogleSearchFactory(googleFactoryConfig)
try:
	aGSF_results = aGSF.listSearch(aZSF_results['notFound'].keys()) #search the ISBNs of the books not found previously
except Exception as e:
	print e'''


##### Hybrid Search Factory
hybridConfig = {'google':googleFactoryConfig, 'z3950': factoryConfig}
try:
	aHSF = aHybridSearchFactory(hybridConfig)
except Exception as e:
	print e
	raise e


try:
	aHSF_results = aHSF.listSearch(test_searchISBNS)
except Exception as e:
	print e
	raise e

aHSF.closeConnections()