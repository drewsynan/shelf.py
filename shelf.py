
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

		#create new searcher
		#import google
		#mySearcher = google.googleSearcher()
		import z3950
		mySearcher = z3950.z3950Searcher()

		bookInfo = mySearcher.search(self.isbnSearch)

		#print bookInfo

		self.isbn13 = bookInfo['isbn13']
		self.isbn10 = bookInfo['isbn10']
		
		self.authors = bookInfo['authors']
		self.title = bookInfo['title']

		self.simpleLastName = bookInfo['simpleLastName']
		self.simpleFirstName = bookInfo['simpleFirstName']
		self.simpleTitle = bookInfo['simpleTitle']

		self.found = bookInfo['found']
		self.jsonError = bookInfo['jsonError']
		self.format = bookInfo['format']


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

