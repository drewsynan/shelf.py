class z3950Searcher:

	def __init__(self):

		self.baseUrl = "http://z3950.loc.gov:7090/voyager?version=1.1&operation=searchRetrieve&query="
		self.queryString = ""
		self.tail = "&maximumRecords=1&recordSchema=dc"

		demoString = "http://z3950.loc.gov:7090/voyager?version=1.1&operation=searchRetrieve&query=9780226033990&maximumRecords=1"

	def search(self, isbn13):
		import xml.etree.ElementTree as ET
		import urllib2
		import string

		print "  Looking up book " + str(isbn13) + "...", #log the search to the console

		query = isbn13
		requestUrl = self.baseUrl + query + self.tail
		
		skipMe = False
		try:
			markup = urllib2.urlopen(requestUrl).read()
		except:
			markup = ""
			skipMe = True

		if not skipMe: 
			root = ET.fromstring(markup)
			numberOfRecords = root.findall('{http://www.loc.gov/zing/srw/}numberOfRecords')[0].text
		else:
			numberOfRecords = 0

		returnDict = {}

		if int(numberOfRecords) > 0:
			returnDict['found'] = True

			recordSet = root.findall('{http://www.loc.gov/zing/srw/}records')[0]
			firstRecord = recordSet.findall('{http://www.loc.gov/zing/srw/}record')[0]
			recordData = firstRecord.findall('{http://www.loc.gov/zing/srw/}recordData')[0]
			dc = recordData.findall('{info:srw/schema/1/dc-schema}dc')[0]

			title = dc.findall('{http://purl.org/dc/elements/1.1/}title')[0].text
			returnDict['title'] = title.replace(" /","").split(":")[0]

			authors = []

			for creator in dc.findall('{http://purl.org/dc/elements/1.1/}creator'):
				authors.append(creator.text.replace(".",""))

			returnDict['authors'] = authors

			#date = dc.findall('{http://purl.org/dc/elements/1.1/}date')[0].text

			#language = dc.findall('{http://purl.org/dc/elements/1.1/}language')[0].text

			#identifiers
			isbns = {}
			idents = dc.findall('{http://purl.org/dc/elements/1.1/}identifier')
			for ident in idents:
				pieces = ident.text.split("URN:ISBN:")

				if pieces[0] == "":
					subpieces = pieces[1].split(" (")
					currentIsbn = subpieces[0]
					#print "got " + currentIsbn
					#print subpieces
					#print "length: " + str(len(subpieces))
					if len(subpieces) > 1:
						if 'pbk' not in subpieces[1]:
							isbns[currentIsbn] = "cloth"
						else:
							isbns[currentIsbn] = "paper"
					else:
						#isbns[currentIsbn] = "cloth"
						pass
			#print isbns
			converted = self.convert13To10(isbn13)
			try:
				returnDict['format'] = isbns[converted]
			except KeyError:
				returnDict['format'] = ""
			returnDict['isbn10'] = converted
			returnDict['isbn13'] = isbn13

			returnDict = self.setSimpleStrings(returnDict)
			returnDict['jsonError'] = False

			print "   [OK]" #log that the book was found to the console
		else:

			returnDict['found'] = False
			returnDict['authors'] = [""]
			returnDict['title'] = ""
			returnDict['searchIsbn'] = isbn13
			returnDict['isbn10'] = ""
			returnDict['isbn13'] = ""
			returnDict['format'] = ""
			returnDict['simpleFirstName'] = ""
			returnDict['simpleLastName'] = ""
			returnDict['simpleTitle'] = ""
			returnDict['jsonError'] = False

			print "   [!]" #log to the console that the book was not found
			if len(isbn13) == 13:
				newSearch = self.search(self.convert13To10(isbn13))
				print "(searching ISBN-10)"
				if newSearch['found']:
					returnDict = newSearch

		return returnDict
	def setSimpleStrings(self, lookupDict):
		import string

		firstAuthor = lookupDict['authors'][0]
		split = firstAuthor.split(", ")
		lookupDict['simpleLastName'] = ''.join(c for c in split[0].upper().replace(" ", "") if c not in string.punctuation)
		lookupDict['simpleFirstName'] = ''.join(c for c in split[1].upper().replace(" ","") if c not in string.punctuation)

		originalTitle = lookupDict['title']
		lookupDict['simpleTitle'] = ''.join(c for c in [word for word in originalTitle.split(":")[0].upper().split() if word not in ["AN", "A", "THE"]] if c not in string.punctuation)

		return lookupDict



	def convert13To10(self, isbn13):
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

#myLocSearcher = z3950Searcher()
#print myLocSearcher.search("9780226365527")