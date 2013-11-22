from twisted.internet import defer, threads, reactor
from PyZ3950 import zoom, zmarc


def connect(host,port,db):
	try:
		conn = zoom.Connection(host,port,db)
		conn.databaseName = db
		#global cnxn 
		#cnxn = conn
	except:
		raise Exception
	return conn

def a_connect(host,port,db):
	return threads.deferToThread(connect(host,port,db))

def search(conn):
	query = zoom.Query('CCL', 'isbn=9780521388849')
	res = conn.search(query)
	print res[0]
	#reactor.stop()

def a_search(conn):
	return threads.deferToThread(search(conn))

print "Connecting"
d = a_connect('z3950.loc.gov',7090,'VOYAGER')
d.addCallback(a_search)


print "next line"
#reactor.run()
#d.callback(cnxn)
