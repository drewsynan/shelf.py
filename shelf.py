
class book:

	"""
	Book class used to populate a "shelf" of books based on ISBN scanning from inventorying
	"""

	def __init__(self, ISBN):
		import datetime

		"""
		Initialize a book with the ISBN (can be 10 or 13, but can't have dashes)
		Use setApiKey(string) to override the default Google Books API key
		"""
		self.timeStamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		self.isbnSearch = ISBN

		self.isbn13 = ""
		self.isbn10 = ""
		
		#self.googleApiKey = "AIzaSyCSH18cCHo6ggNg-XYkrt10GMk3fkFSuhw"
		self.googleApiKey = "AIzaSyAaVCpblCix3LOOu0HtpdG-MXXam5criSI" #alternate key
		self.authors = [""]
		self.__getGoogleBookInfo()
		self.__setNameStrings()

	def setApiKey(self, key):
		"""Setter to make the Google Books search API key to something other than the default"""

		self.googleApikey = key

	def __getGoogleBookInfo(self):
		"""Searches Google Books using the API for the current book using self.isbn13"""

		import json
		import urllib2

		baseURL = "https://www.googleapis.com/books/v1/volumes?q=isbn:" #Google Books API v 1 base url
		addOn = "&key=" #needed for GET request
		jsonURL = baseURL + str(self.isbnSearch) + addOn + self.googleApiKey + "&country=US" #build a URL string for searching

		print "  Looking up book " + str(self.isbnSearch) + "...", #log the search to the console
		try:
			googleBook = json.load(urllib2.urlopen(jsonURL)) #attempt to load JSON from Google Books using the URL built above

			self.jsonError = False

			if googleBook['totalItems'] > 0: #see if any items were returns from search
				self.found = True

				firstVolume = googleBook['items'][0]['volumeInfo'] #get the first volume object from the processed JSON
				self.title = firstVolume['title'] #get the title

				idents = firstVolume['industryIdentifiers']
				for ident in idents:
					if ident['type'] == 'ISBN_10':
						self.isbn10 = ident['identifier']
					elif ident['type'] == 'ISBN_13':
						self.isbn13 = ident['identifier']

				if 'authors' in firstVolume.keys():
					self.authors = firstVolume['authors'] #get the array of authors
				else:
					self.authors = [""]

				print "   [OK]" #log that the book was found to the console
			else:
				#no items were found
				self.found = False
				self.title = ""
				self.authors = [""]

				print "   [!]" #log to the console that the book was not found
		except:
			#google books as probably thrown an API error
			self.found = False
			self.title = ""
			self.authors = [""]
			self.jsonError = True
			print "   [HTTP ERROR]"

	def __setNameStrings(self):

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
		if self.found and self.authors != [""]: 
			#Get the name of the first author (the first item in the author array)
			firstAuthorName = self.authors[0].upper().split()

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

			titleArray = self.title.upper().split() #break title into an array of words

			#check to see if first word in title is THE, A, or AN
			if titleArray[0] == "THE" or titleArray[0] == "A" or titleArray[0] == "AN":
				#remove articles from title, for alphabetization purposes
				del titleArray[0]

			#flatten the array into a string of all caps with no spaces or punctuation
			for word in titleArray:
				simpleTitle += ''.join(c for c in word if c not in string.punctuation)

			#set the instance variables to the temporary variable values
			self.simpleFirstName = simpleFirstName
			self.simpleLastName = lastname
			self.simpleTitle = simpleTitle
		else:
			#if book was not found in Google Books, do nothing
			self.simpleFirstName = ""
			self.simpleLastName = ""
			self.simpleTitle = ""
			pass

	def __eq__(self, other):

		"""
		Checks for equality between two books. Allows for the use of the == operator on two
		book objects. Internally, checks to see if the authors and titles are the same between
		the two book objects. DOES NOT check the ISBNs, allowing to see if hardcover and paperback
		editions of books are the "same". Returns either True or False.
		"""

		return (self.authors[0]==other.authors[0]) and (self.title==other.title) and self.found

	def __ne__(self, other):

		"""
		Checks for inequality between two books. Allows for the use of the <> operator on two
		book objects. Internally, checks to see if the authors and titles are not the same between
		the two book objects. DOES NOT check the ISBNs.
		"""
		return not (self == other)

	def __lt__(self, other):

		"""
		book1 < book 2
		Allows for the use of the < operator on two book objects. Initially checks to see if author of
		book1 is alphabetically before the author of book2. If the authors are the same, it then checks to
		see if the title of book1 is alphabetically before the title of book2. Returns True or False.
		"""

		# process last name character by character self < other
		# process first name character by character
		# process title character by character until a an exception is fount
		if not self.found or not other.found:
			return False
		elif self.simpleLastName < other.simpleLastName:
			return True
		elif (self.simpleLastName == other.simpleLastName) and (self.simpleFirstName < other.simpleFirstName):
			return True
		elif (self.simpleLastName == other.simpleLastName) and (self.simpleFirstName == other.simpleFirstName) and (self.simpleTitle < other.simpleTitle):
			return True
		else:
			return False

	def __le__(self, other):

		"""
		Allow for the <= operator on two book objects (book1 <= book2), to see if the two books are strictly
		in alphabetical order. Checks for < first, then checks for equality. 
		(See documentation on < and == for further details)
		"""

		return (self < other) or (self == other)

	def __gt__(self, other):

		"""
		Allows for the use of the < operator on two book objects (book1 > book2) to see if book2, book1 are
		in alphabetical order first by author, then by title. Initially checks to see if author of
		book1 is alphabetically before the author of book2. If the authors are the same, it then checks to
		see if the title of book1 is alphabetically before the title of book2. Returns True or False.
		"""

		return not (self < other) and not (self == other)

	def __ge__(self, other):

		"""
		Allow for the >= operator on two book objects (book1 >= book2), to see if the two books are strictly
		in alphabetical order. Checks for < first, then checks for equality. 
		(See documentation on < and == for further details)
		"""

		return (self > other) or (self == other)

def LongestIncreasingSubsequence(S):
	import unittest
	from bisect import bisect_left

	"""
	LongestIncreasingSubsequence.py
	
	Find longest increasing subsequence of an input sequence.
	D. Eppstein, April 2004
	"""

	"""
	Find and return longest increasing subsequence of S.
	If multiple increasing subsequences exist, the one that ends
	with the smallest value is preferred, and if multiple
	occurrences of that value can end the sequence, then the
	earliest occurrence is preferred.
	"""
    
    # The main data structures: head[i] is value x from S that
    # terminates a length-i subsequence, and tail[i] is either
    # None (if i=0) or the pair (head[i-1],tail[i-1]) as they
    # existed when x was processed.
	head = []
	tail = [None]

	for x in S:
		i = bisect_left(head,x)
		if i >= len(head):
			head.append(x)
			if i > 0:
				tail.append((head[i-1],tail[i-1]))
			elif head[i] > x:
				head[i] = x
				if i > 0:
					tail[i] = head[i-1],tail[i-1]

	if not head:
		return []

	output = [head[-1]]
	pair = tail[-1]
	while pair:
		x,pair = pair
		output.append(x)

	output.reverse()
	return output

