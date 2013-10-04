import sys, getopt, shelf, os, datetime, csv
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

def writeShelfEndMarker():
	desktopPath = os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + "\\Desktop"
	csvFileName = desktopPath + "\\inventory.csv"

	with open(csvFileName, 'ab') as csvfile:
		csvWriter = csv.writer(csvfile)
		endCaseRow = ['endofcase', 'endofcase', 'endofcase', 'endofcase', 'endofcase', 'endofcase']
		csvWriter.writerow([s.encode("utf-8") for s in beginCaseRow])

def processBarcodeList(barcodeList):
	desktopPath = os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + "\\Desktop"
	csvFileName = desktopPath + "\\inventory_barcodelist.csv"

	with open(csvFileName, 'ab') as csvfile:
		csvWriter = csv.writer(csvfile)
		for barcode in barcodeList:
			csvWriter.writerow([barcodeList[0].isbn13,datetime.datetime.now().strftime("%m/%d/%Y")])

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

	# add each book to the inventory.csv file
	# isbn,author,authorlastname,title,outoforder,date

	#check to see if inventory.csv exists on the desktop
	desktopPath = os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + "\\Desktop"
	csvFileName = desktopPath + "\\inventory.csv"

	with open(csvFileName, 'ab') as csvfile:
		csvWriter = csv.writer(csvfile)
		# write
		# beginshelf,beginshelf,beginshelf,beginshelf,beginshelf,beginshelf
		# to the csv file to mark the start of a shelf
		beginShelfRow = ['beginshelf', 'beginshelf', 'beginshelf', 'beginshelf', 'beginshelf', 'beginshelf']
		csvWriter.writerow([s.encode("utf-8") for s in beginShelfRow])

		for book in shelfList:
			#create csv string
			csvRow = []

			marker = "  " #creates spaces for the left hand first column
			foundLeft = "" #variable for marking books if they weren't found
			foundRight = ""

			if book in OutOfOrder:
				# print books that are out of order with a * in the first column
				marker = "* "
				csvRow.append(book.isbn13)
				csvRow.append(book.authors[0])
				csvRow.append(book.simpleLastName)
				csvRow.append(book.title)
				csvRow.append('outoforder')
				csvRow.append(datetime.datetime.now().strftime("%m/%d/%Y"))

			elif book not in found:
				# print books that weren't found as (ISBN) since no other info is available
				foundLeft = "("
				foundRight = ")"
				if book.simpleLastName == "":
					book.simpleLastName = book.isbn13
				if book.title == "":
					book.title = book.isbn13
				if book.authors == [""]:
					book.author = "notfound"
					book.simpleLastName = "notfound"

				csvRow.append(book.isbn13)
				csvRow.append(book.authors[0])
				csvRow.append(book.simpleLastName)
				csvRow.append(book.title)
				csvRow.append('notfound')
				csvRow.append(datetime.datetime.now().strftime("%m/%d/%Y"))
			else:
				#book found, not out of order
				csvRow.append(book.isbn13)
				csvRow.append(book.authors[0])
				csvRow.append(book.simpleLastName)
				csvRow.append(book.title)
				csvRow.append('inorder')
				csvRow.append(datetime.datetime.now().strftime("%m/%d/%Y"))

			print marker + foundLeft + book.simpleLastName + ": " + book.title + foundRight
			#write line in csv file
			csvWriter.writerow([s.encode("utf-8") for s in csvRow])

		#write endshelf,endshelf,endshelf,endshelf,endshelf,endshelf
		endShelfRow = ['endshelf', 'endshelf', 'endshelf', 'endshelf', 'endshelf', 'endshelf']
		csvWriter.writerow([s.encode("utf-8") for s in endShelfRow])

		print "-REPORT-----------------------------------------"
		print "  " + str(len(OutOfOrder)) + "  books out of order (marked with an '*')   ( ) = not found"

def interactive():
	shelfList = []
	barcodeList = []

	infoPrompting = False;

	while True:
		currentValue = raw_input('ISBN> ')
		if currentValue == "<ENDSHELF>":
			print "Reached End of shelf... processing"
			processShelfList(shelfList)
			processBarcodeList(barcodeList)

			shelfList = []
			barcodeList = []
		elif currentValue == "<ENDCASE>":
			print "Reached End of Case.. processing"
			#write end of case marker in csv file
		elif currentValue == "<DELPREV>":
			try:
				delb = shelfList.pop()
				print "Deleting " + delb.title
			except:
				print "Cannot Delete!"
		elif currentValue == "<TEST>":
			print "Success! The scanner is working"
		elif currentValue == "b" or currentValue == "B":
			print "      Type barcode (a label will be generated later), or c to cancel"
			neededBarcode = raw_input('----> ')
			cleaned = neededBarcode.replace("-","")
			if cleaned == "c" or cleaned == "C":
				pass
			elif cleaned == "q" or cleaned =="Q":
				break
			else:
				b = shelf.book(cleaned)
				if b.found:
					print b.title
				else:
					print "BOOK NOT FOUND: enter book information"
					newTitle = raw_input("Title: ")
					newAuthorLname = raw_input("Author last name: ")
					newAuthorFname = raw_input("Author first name: ")
					b.simpleLastName = newAuthorLname.upper().replace(" ","")
					b.title = newTitle
					combinedAuthor = newAuthorFname + ' ' + newAuthorLname
					b.authors = [combinedAuthor]
				shelfList.append(b)
				barcodeList.append(b)
		elif currentValue == "q" or currentValue == "Q":
			# Need to create some sort of confirmation to quit without saving, or save and quit
			break
		elif currentValue == "l" or currentValue == "ls" or currentValue == "L" or currentValue == "LS":
			print "Items Scanned for this Shelf"
			print "----------------------------"
			for book in shelfList:
				print book.simpleLastName + ": " + book.title
			print "----------------------------"
			print "scan or type <ENDOFSHELF> for shelf reading report"
		elif currentValue == "p" or currentValue == "P":
			infoPrompting = not infoPrompting
			if infoPrompting:
				print "Info prompting enabled"
			else:
				print "Info prompting disabled"
		else:
			clean = currentValue.replace("-","")
			cb = shelf.book(clean)
			if cb.found:
				print cb.title
			else:
				if infoPrompting:
					print "BOOK NOT FOUND: enter book information"
					newTitle = raw_input("Title: ")
					newAuthorLname = raw_input("Author last name: ")
					newAuthorFname = raw_input("Author first name: ")
					cb.simpleLastName = newAuthorLname.upper().replace(" ","")
					cb.title = newTitle
					combinedAuthor = newAuthorFname + ' ' + newAuthorLname
					cb.authors = [combinedAuthor]
			shelfList.append(cb)



if __name__ == "__main__":
	if len(sys.argv) == 1:
		print "Interactive Inventory"
		print "type q to quit | b to enter a barcodeless book | p to enable info prompting | ls to see shelf list so far"
		print "Begin scanning books."
		interactive()
	elif len(sys.argv) == 2 and sys.argv[1] == "demo":
		print sys.argv
		print "Internal Data Demo"
		main([])
	else:
		print "CSV processing"
		main(sys.argv[1:])