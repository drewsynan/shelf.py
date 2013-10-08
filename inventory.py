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
		print 'inventory.py -i <inputfile> -o <outputfile>'
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

def demo():
	#### INTERNAL DEMO ######
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

def csvInventory(inventoryFile):

	shelfList = []
	global infoPrompting
	global interactiveShelfReport
	global desktopPath
	global csvFileName

	infoPrompting = False
	interactiveShelfReport = False
	desktopPath = os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + "\\Desktop"
	csvFileName = desktopPath + "\\inventory_batch.csv"

	with open(inventoryFile, 'rb') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			if row[0] == "<ENDSHELF>":
				try:
					processShelfList(shelfList)

					shelfList = []
					barcodeList = []
				except:
					raise
			elif row[0] == "<ENDCASE>":
				if shelfList:
					processShelfList(shelfList)
					processBarcodeList(barcodeList)
					writeCaseEndMarker()
				else:
					writeCaseEndMarker()
			elif row[0] == "<DELPREV>":
				try:
					delb = shelfList.pop()
				except:
					pass
			else:
				clean = row[0].replace("-","")
				cb = shelf.book(clean)
				shelfList.append(cb)
	#check to see if there are any books left on the list (maybe no ending endshelf tag)
	if shelfList:
		processShelfList(shelfList)

def writeCaseEndMarker():
	with open(csvFileName, 'ab') as csvfile:
		csvWriter = csv.writer(csvfile)
		endCaseRow = ['endofcase', 'endofcase', 'endofcase', 'endofcase', 'endofcase', 'endofcase', 'endofcase', 'endofcase','endofcase']
		csvWriter.writerow([s.encode("utf-8") for s in endCaseRow])

def processBarcodeList(barcodeList):
	if barcodeList:
		with open(csvBarcodeFileName, 'ab') as csvfile:
			csvWriter = csv.writer(csvfile)
			for barcode in barcodeList:
				csvWriter.writerow([barcodeList[0].isbn13,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
	else:
		pass

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
	# isbnSearch,isbn13,isbn10,author,authorlastname,title,outoforder,date,jsonError

	#check to see if inventory.csv exists on the desktop
	if not os.path.isfile(csvFileName):
		writeHeader = True
	else:
		writeHeader = False

	with open(csvFileName, 'ab') as csvfile:
		csvWriter = csv.writer(csvfile)
		# write
		# beginshelf,beginshelf,beginshelf,beginshelf,beginshelf,beginshelf
		# to the csv file to mark the start of a shelf
		
		# write beginshelf markers... should be moved into a function by itself
		# beginShelfRow = ['beginshelf', 'beginshelf', 'beginshelf', 'beginshelf', 'beginshelf', 'beginshelf', 'beginshelf', 'beginshelf','beginshelf']
		# csvWriter.writerow([s.encode("utf-8") for s in beginShelfRow])

		if writeHeader:
			csvWriter.writerow(['searchIsbn', 'isbn13', 'isbn10', 'author', 'authorlastname', 'title', 'outoforder', 'date', 'jsonError'])

		for book in shelfList:
			#create csv string
			csvRow = []

			marker = "  " #creates spaces for the left hand first column
			foundLeft = "" #variable for marking books if they weren't found
			foundRight = ""

			if book in OutOfOrder:
				# print books that are out of order with a * in the first column
				marker = "* "
				csvRow.append(book.isbnSearch)
				csvRow.append(book.isbn13)
				csvRow.append(book.isbn10)
				csvRow.append(book.authors[0])
				csvRow.append(book.simpleLastName)
				csvRow.append(book.title)
				csvRow.append('outoforder')
				csvRow.append(book.timeStamp)
				csvRow.append(str(book.jsonError))

			elif book not in found:
				# print books that weren't found as (ISBN) since no other info is available
				foundLeft = "("
				foundRight = ")"
				if book.simpleLastName == "":
					book.simpleLastName = book.isbnSearch
				if book.title == "":
					book.title = book.isbnSearch
				if book.authors == [""]:
					book.author = "notfound"
					book.simpleLastName = "notfound"

				csvRow.append(book.isbnSearch)
				csvRow.append(book.isbn13)
				csvRow.append(book.isbn10)
				csvRow.append(book.authors[0])
				csvRow.append(book.simpleLastName)
				csvRow.append(book.title)
				csvRow.append('notfound')
				csvRow.append(book.timeStamp)
				csvRow.append(str(book.jsonError))
			else:
				#book found, not out of order
				csvRow.append(book.isbnSearch)
				csvRow.append(book.isbn13)
				csvRow.append(book.isbn10)
				csvRow.append(book.authors[0])
				csvRow.append(book.simpleLastName)
				csvRow.append(book.title)
				csvRow.append('inorder')
				csvRow.append(book.timeStamp)
				csvRow.append(str(book.jsonError))

			if interactiveShelfReport:
				print marker + foundLeft + book.simpleLastName + ": " + book.title + foundRight
			#write line in csv file
			csvWriter.writerow([s.encode("utf-8") for s in csvRow])

		#write endshelf,endshelf,endshelf,endshelf,endshelf,endshelf
		endShelfRow = ['endshelf', 'endshelf', 'endshelf', 'endshelf', 'endshelf', 'endshelf', 'endshelf', 'endshelf', 'endshelf']
		csvWriter.writerow([s.encode("utf-8") for s in endShelfRow])

		if interactiveShelfReport:
			print "-REPORT-----------------------------------------"
			print "  " + str(len(OutOfOrder)) + "  books out of order (marked with an '*')   ( ) = not found"

def interactive():
	shelfList = []
	barcodeList = []

	global infoPrompting
	global interactiveShelfReport

	global desktopPath
	global csvFileName
	global csvBarcodeFileName

	infoPrompting = False
	interactiveShelfReport = False

	desktopPath = os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + "\\Desktop"
	csvFileName = desktopPath + "\\inventory.csv"
	csvBarcodeFileName = desktopPath + "\\inventory_barcodelist.csv"



	while True:
		currentValue = raw_input('ISBN> ')
		if currentValue == "<ENDSHELF>":
			print "Reached End of shelf... processing"
			try:
				processShelfList(shelfList)
				processBarcodeList(barcodeList)

				shelfList = []
				barcodeList = []
			except IOError as e:
				print "I/O Exception. Is the inventory file currently open?"
			except:
				raise
		elif currentValue == "<ENDCASE>":
			print "Reached End of Case.. processing"
			#write end of case marker in csv file
			if shelfList:
				processShelfList(shelfList)
				processBarcodeList(barcodeList)
				writeCaseEndMarker()
			else:
				writeCaseEndMarker()

		elif currentValue == "<DELPREV>":
			try:
				delb = shelfList.pop()
				print "Deleting " + delb.title
			except:
				print "Cannot Delete!"
		elif currentValue == "<TEST>":
			print "Success! The scanner is working"
		elif currentValue.upper() == "B":
			print "      Type barcode (a label will be generated later), or c to cancel"
			neededBarcode = raw_input('----> ')
			cleaned = neededBarcode.replace("-","")
			if cleaned.upper() == "C":
				pass
			elif cleaned.upper() == "Q":
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
		elif currentValue.upper() == "Q":
			if shelfList:
				print "WARNING: Shelf List Not committed"
				print "         Commit list before quitting?"
				choice = raw_input("Y/N? ")
				if choice.upper() == "Y":
					processShelfList(shelfList)
					processBarcodeList(barcodeList)
					break
				else:
					break
			else:
				break
		elif currentValue.upper() == "L" or currentValue.upper() == "LS":
			print "Items Scanned for this Shelf"
			print "----------------------------"
			for book in shelfList:
				print book.simpleLastName + ": " + book.title
			print "----------------------------"
			print "scan or type <ENDSHELF> for shelf reading report"
		elif currentValue.upper() == "P":
			infoPrompting = not infoPrompting
			if infoPrompting:
				print "Info prompting enabled"
			else:
				print "Info prompting disabled"
		elif currentValue.upper() == "I":
			interactiveShelfReport = not interactiveShelfReport
			if interactiveShelfReport:
				print "Interactive shelf reading report enabled"
			else:
				print "interactive shelf reading report disabled"
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
		print "type q to quit"
		print "     b to enter a barcodeless book"
		print "     p to enable info prompting"
		print "     i to enable interactive shelf report"
		print "     ls to see shelf list so far"
		print "Begin scanning books."
		interactive()
	elif len(sys.argv) == 2 and sys.argv[1] == "demo":
		print sys.argv
		desktopPath = os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + "\\Desktop"
		csvFileName = desktopPath + "\\inventory_demo.csv"
		global interactiveShelfReport
		interactiveShelfReport = True
		print "Internal Data Demo"
		demo()
	else:
		print "CSV processing"
		print sys.argv[1:]
		csvInventory(sys.argv[1])
		#main(sys.argv[1:])