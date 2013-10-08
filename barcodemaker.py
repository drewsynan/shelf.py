import os, sys, csv, shelf


#isbnString = "9780226301686"

def makeBarCode(isbnString):

	cwd = os.getcwd()
	imageDir = "barcodeimages"

	# -g wxh (in points)
	os.system("barcode -b " + isbnString + " -g 90x54 -o temp_" + isbnString + "output.ps")
	os.system("ps2pdf temp_" + isbnString + "output.ps")
	#/CropBox [LeftEdge BottomEdge RightEdge TopEdge]   all in points
	os.system("gswin32c -o temp_" + isbnString + "cropped.pdf -sDEVICE=pdfwrite -c \"[/CropBox [10 0 112 76] /PAGES pdfmark\" -f temp_" + isbnString + "output.pdf")
	os.system("gswin32c -dNOPAUSE -q -r300 -g430x300 -sDEVICE=tiffg4 -dBATCH -sOutputFile=" + imageDir + "/" + isbnString + ".tif temp_" + isbnString + "cropped.pdf")
	os.system("del temp_" + isbnString + "*")

	imageFileName = cwd + "\\" + imageDir + "\\" + isbnString + ".tif"
	escaped = imageFileName.replace("\\", "/")
	return escaped

def csvReader(csvFile):
	isbnList = []
	with open(csvFile, 'rb') as csvFile:
		reader = csv.reader(csvFile)
		for row in reader:
			isbn = row[0]
			isbnList.append(shelf.book(isbn))
	return isbnList

def process(inputFile, outputFile):

	pathToBarcode = "C:\\Users\\dsynan\\Documents\\gnu-barcode-bin"
	pathToGhostScript = "C:\\Users\\dsynan\\Documents\\PortableApps\\CommonFiles\\Ghostscript"

	startingPath = os.environ["PATH"]
	newPath = startingPath + ";" + pathToBarcode + ";" + pathToGhostScript + "\\bin;" + pathToGhostScript + "\\lib"
	os.environ["PATH"] = newPath

	try:
		os.mkdir("barcodeimages")
	except:
		pass

	books = csvReader(inputFile)
	
	#write header
	with open(outputFile, 'wb') as csvfile:
		csvWriter = csv.writer(csvfile)
		csvWriter.writerow(['isbn', 'author', 'title', 'isbn_filename','book_found'])

	#write results to csv file
	#isbn,author,title,isbn_filename
	for book in books:
		row = []
		row.append(book.isbnSearch)
		if book.found:
			#row.append(book.authors[0])
			row.append(book.simpleLastName)
		else:
			row.append("")
		row.append(book.title)
		row.append(makeBarCode(book.isbn13))
		row.append(str(book.found))
		with open(outputFile, 'ab') as csvfile:
			csvWriter = csv.writer(csvfile)
			csvWriter.writerow([s.encode("utf-8") for s in row])

if __name__ == "__main__":
	if len(sys.argv) >= 3:
		process(sys.argv[1], sys.argv[2])
	else:
		print "usage:"
		print "barcodemaker.py inputfile.csv outputfile.csv"