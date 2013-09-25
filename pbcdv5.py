"""
Microsoft Access ODBC bindings to connect to production database.
Needs hella work... might consider using the info here to suppliment books not found in Google Books
"""

import pyodbc

#Hart/Storycraft paperback
#isbn13string = "978-0-226-31816-5"

#Kuhn/Structure of Scientific Revolutions
isbn13string = "978-0-226-45811-3"

impressionString = "1"

Title = None
Author = None
TextPrinter = None
CoverPrinter = None
Typesetter = None
Paper = None
Binding = None



cnxn = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\\Users\\dsynan\Desktop\\sand.mdb;')
cursor = cnxn.cursor()

sqlString = """
SELECT Books.[BookID] AS bid, Books.[Title] as title, Books.[Author] as author
FROM Books WHERE """
sqlStringPaper = sqlString + "Books.[ISBN-13 Paper]='" + isbn13string + "'"
sqlStringCloth = sqlString + "Books.[ISBN-13 Cloth] = '" + isbn13string + "'"
sqlStringEbook = sqlString + "Books.[ISBN-13 Electronic] = '" + isbn13string + "'"

#print sqlString

##See if isbn returns a paper result
cursor.execute(sqlStringPaper)
row = cursor.fetchone()
if row:
	Binding = "Paper"
	searchBookID = str(row[0])
	Title = str(row[1])
	Author = str(row[2])
## see if isbn returns a cloth result
cursor.execute(sqlStringCloth)
row = cursor.fetchone()
if row:
	Binding = "Cloth"
	searchBookID = str(row[0])
	Title = str(row[1])
	Author = str(row[2])

## see if isbn returns only an ebook result
cursor.execute(sqlStringEbook)
row = cursor.fetchone()
if Binding is None:
	print "NO BINDING"


cursor.execute("""
	SELECT Impression.[ImpressionID] as impid, Impression.[Impression] as num, Impression.[Text stock] as textStock
	FROM Impression WHERE
	Impression.BookId="""+searchBookID+" and Impression.Impression = '"+impressionString+"'")
#rows = cursor.fetchall()
#for row in rows:
#	print row
row = cursor.fetchone()
if row:
	searchImpID = row[0]
	Paper = row[2]

cursor.execute("""
	SELECT [Printing Costs].[Printer] as TextPrinter, [Printing Costs].[Cover printer] as CoverPrinter
	FROM [Printing Costs]
	WHERE [Printing Costs].[ImpressionID]=""" + str(searchImpID))
row = cursor.fetchone()
if row:
	TextPrinter = row[0]
	CoverPrinter = row[1]

print """-===Book Summary ===--

ISBN-13: """ + isbn13string + """

Title: """ + str(Title) + """
Author: """ + str(Author) + """
Impression Number: """ + str(impressionString) + """
Text Printer: """ + str(TextPrinter) + """
Cover Printer: """ + str(CoverPrinter) + """
Text Stock: """ + str(Paper)