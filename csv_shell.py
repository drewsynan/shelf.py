import sys, getopt, shelf
def main(argv):

	"""
	Check to see if a "shelf" of books (ISBNS) from scanning is out of order.
	The algorithm works by transforming each array of ISBNs in to an array of
	book objects. The longest increasing subsequence of books is then extracted from
	this array, and all books not in this subsequence are deemed to be "out of order."

	First input value is a csv file of isbns (with no header)
	The second (optional) parameter is an output csv file name.
	If no csv file name is given, the report will be printed to the screen
	"""

	inputfile = ''
	outputfile = ''
	printtoscreen = True

	try:
		opts, args = getopt.getopt(argv,"hi:o",["ifile=","ofile="])
	except getopt.GetoptError:
		print 'shelfreader.py -i <inputfile> -o <outputfile>'
		sys.exit(2)

	for opt, arg in opts:
		if opt == "-h":
			print "shelfreader.py -i <inputfile> -o <outputfile>"
			sys.exit()
		elif opt in ("-i", "--ifile"):
			inputfile = arg
		elif opt in ("-o", "--ofile"):
			outputfile = arg
			printtoscreen = False

	book = shelf.book
	#populate a test array of book objects
	shelf1 = [book("9780226922843"), book("9780226699080"), book("9780226701011"), 
			  book("9780226701707"), book("9780226036915"), book("9780226703145"),
			  book("9780226701516"), book("9780226701462"), book("9780226701479"),
			  book("9780226150772"), book("9780226701981"), book("9780226701967"),
			  book("9780226702230"), book("9780226702247"), book("9780226702278"),
			  book("9780226041001"), book("9780226702285"), book("9780226702360"),
			  book("9780226702667"), book("9780226702650"), book("9780826331755"),
			  book("9780226702704"), book("9780226702704"), book("9780226702704"),
			  book("9780226702681")]

	processShelfList(shelf1)

def processShelfList(shelfList):
	# extract all books that were found in Google Books
	found = [book for book in shelfList if book.found == True]

	#find the longest increasing subsequence of the found books
	LISS = shelf.LongestIncreasingSubsequence(found)

	# find all books in the "found" books that are not in the longest increasing subsequence
	# these are the "out of order" books for the shelf
	OutOfOrder = [book for book in found if book not in LISS]

	# loop through the initial array of book objects and print if each book was found
	# and if each book was is out of order

	print "------------------------------------------------"

	for book in shelfList:
		marker = "  " #creates spaces for the left hand first column
		foundLeft = "" #variable for marking books if they weren't found
		foundRight = ""

		if book in OutOfOrder:
			# print books that are out of order with a * in the first column
			marker = "* "
		if book not in found:
			# print books that weren't found as (ISBN) since no other info is available
			foundLeft = "("
			foundRight = ")"
			book.simpleLastName = book.isbn13
			book.title = book.isbn13

		print marker + foundLeft + book.simpleLastName + ": " + book.title + foundRight
	
	print "REPORT------------------------------------------"
	print " " + str(len(OutOfOrder)) + "  books out of order (marked with an '*')"

def interactive():
	shelfList = []
	while True:
		currentValue = raw_input('ISBN> ')
		if currentValue == "<ENDSHELF>":
			print "Reached End of shelf... processing"
			processShelfList(shelfList)
			shelfList = []
		elif currentValue == "<ENDCASE>":
			print "Reached End of Case.. processing"
		elif currentValue == "<DELPREV>":
			try:
				delb = shelfList.pop()
				print "Deleting " + delb.title
			except:
				print "Cannot Delete!"
		elif currentValue == "q":
			break
		elif currentValue == "l" or currentValue == "ls" or currentValue == "L" or currentValue == "LS":
			print "Items Scanned for this Shelf"
			print "----------------------------"
			for book in shelfList:
				print book.simpleLastName + ": " + book.title
			print "----------------------------"
			print "scan or type <ENDOFSHELF> for shelf reading report"
		else:
			clean = currentValue.replace("-","")
			cb = shelf.book(clean)
			print cb.title
			shelfList.append(cb)



if __name__ == "__main__":
	if len(sys.argv) == 1:
		print "INTERACTIVE / begin scanning books; type q to quit"
		interactive()
	elif len(sys.argv) == 2 and sys.argv[1] == "demo":
		print sys.argv
		print "Internal Data Demo"
		main([])
	else:
		print "CSV processing"
		main(sys.argv[1:])