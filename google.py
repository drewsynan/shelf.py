class googleSearcher:

	def __init__(self):
		self.googleApiKey = "AIzaSyCSH18cCHo6ggNg-XYkrt10GMk3fkFSuhw"
		#self.googleApiKey = "AIzaSyAaVCpblCix3LOOu0HtpdG-MXXam5criSI" #alternate key

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
			print "   [HTTP ERROR]"

		returnDict['format'] = "" #google books api does not support format info
		return returnDict

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

#myGoogleSearcher = googleSearcher()
#print myGoogleSearcher.search("9780226702704")