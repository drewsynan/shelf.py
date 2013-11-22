class nuZ3950Searcher:
	def __init__(self):
		#self.server = 'z3950.loc.gov' #library of congress
		self.server = 'libcat.uchicago.edu'
		#self.port = 7090
		self.port = 210
		#self.databaseName = 'VOYAGER'
		self.databaseName = 'uofc'

		self.preferredRecordSyntax = 'USMARC'

	def search(self, isbn13):

		returnDict = {}
		returnDict['found'] = False
		returnDict['authors'] = [""]
		returnDict['title'] = ""
		returnDict['subtitle'] = "" ######<<<<< update other searchers to include this
		returnDict['searchIsbn'] = isbn13
		returnDict['isbn10'] = ""
		returnDict['isbn13'] = ""
		returnDict['format'] = ""
		returnDict['simpleFirstName'] = ""
		returnDict['simpleLastName'] = ""
		returnDict['simpleTitle'] = ""
		returnDict['jsonError'] = False

		print "  Looking up book " + str(isbn13) + "...", #log the search to the console

		from PyZ3950 import zoom, zmarc
		try:
			conn = zoom.Connection(self.server, self.port)
			conn.databaseName = self.databaseName
			conn.preferredRecordSyntax = self.preferredRecordSyntax
		except:
			print "Could not connect"
			return
		queryString = 'isbn=' + str(isbn13)
		query = zoom.Query('CCL', queryString)

		res = conn.search(query)
		resultMARC = None

		if len(res) == 0:
			print "Searching ISBN-10"
			query = zoom.Query('CCL', 'isbn=' + self.__convert13To10(isbn13))
			res2 = conn.search(query)
			if len(res2) == 0:
				print "   [!]" #log to the console that the book was not found
				return returnDict
			else:
				resultMARC = zmarc.MARC(res2[0].data)
		else:
			resultMARC = zmarc.MARC(res[0].data)

		print "   [OK]"

		conn.close()
		returnDict['found'] = True
		returnDict['isbn13'] = isbn13
		returnDict['isbn10'] = self.__convert13To10(isbn13)

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
				authorField = resultMARC.fields[700] #try 700 field (used for editors, not authors)
				for subfield in authorField[0][2]:
					if subfield[0] == 'a':
						#check to see if last character is a comma (will be if there is also a $d subfield)
						if subfield[1][-1] == ",":
							authors.append(subfield[1][:-1]) # trim last comma
						else:
							authors.append(subfield[1])
			except KeyError:
				print "multiple key errors"
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

	def __convert13To10(self, isbn13):
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

#myNewSearcher = nuZ3950Searcher()
#mySearch = myNewSearcher.search("9780226720821")