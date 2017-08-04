#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import requests
from multiprocessing.dummy import Pool as ThreadPool 

import time
import sys
import os
sys.path.append(os.path.abspath("/home/joseph/bin"))
from EveMarketLib import OrderSeparator
from EveMarketLib import cleanCrest, clean2string, AnalyzeCleanCrestData, QueryCrest4ItemPrices, GetCrestWorth
from EveMarketLib import file2string, Rlookup, IDlookupTable, NamelookupTable

MAXNUM_TO_INSERT = -1
DUPLICATE_ROWS = 0
NEW_ROWS = 0

##############################################
# BEGIN Functions
##############################################
def ReadUserAndPwFromFile(filename):
	return file2string(filename).split('\n')

def is_int(string):
	try:
		int(string)
		return True
	except:
		return False
		
def is_float(string):
	try:
		float(string)
		return True
	except:
		return False
		
def PrepareBasicInsertInto(modifiedcsv, form, table): #string parameters
# Returns a mySQL insert command as a string, given formatted data to insert via "form"
	return "INSERT INTO "+table+" ("+form+") VALUES "+modifiedcsv;

def PrepareItemInsertInto(values, form, table): #string parameters
# Returns a mySQL insert command as a string, given formatted data to insert via "form"
	return "INSERT INTO "+table+" ("+form+") VALUES ("+values+");"

def PrepareInsertInto(xml, table, form): #string parameters
# Returns a mySQL command string to be executed
	transactionID = 0
	array = xml.split("\" ")
	temp = array[0].split("<row ")
	if len(temp) > 1:
		array[0] = temp[1] #Split the first entry and throw away first piece, which contains only whitespace and xml row tag
	else:
		#~ print("the offender:<"+temp[0]+">\n");
		print("Not a data row.")
		return ""

	array[len(array)-1] = None	#Throw away last entry, is also only xml syntax

	theFormat = ""
	theData = ""
	
	for elt in array:
		if elt == None:
			break;
		#~ print(elt);
		elarray = elt.split("=\"")

		theFormat = theFormat + elarray[0]+","
		datum = " " #Fix up what happens if a field is blank for some (hopefully good) reason
		if len(elarray) > 1:
			datum = elarray[1]

		if not is_float( datum ): #Strings get quoted in a mySQL call
			datum = '\"'+datum+'\"'
		theData = theData + datum+","
		
		if elarray[0] == "transactionID":
			transactionID = long(elarray[1])

	if theFormat[:-1] == form: #-1 drops the last (and unwanted) comma
		return "INSERT INTO " + table +" ("+form+") VALUES ("+theData[:-1]+")"
	else:
		#~ print(format)
		#~ print(theFormat[:-1])
		return ""

def myGetUrlQueryResult(url): # string parameter
# Returns web response as a string
	result = requests.get(url)
	return result.text

def shardProcess(shard, depth = 0): # parameter: range of job indices to complete
	# For parallelization of CREST API query/response I/O
	failed = []
	for item in shard:
		try:
			DoIt(item)
			
		except IOError:
			continue
		except ValueError:
			break
		except requests.exceptions.ConnectionError:
			print('Connection timed out on "%s"' % item[1])
			failed.append(item)
		#~ except ConnectionResetError:
			#~ print('Connection was reset on "%s"' % item[1])
			#~ failed.append(item)
		except:
			print('Something bad happened to "%s"' % item[1])
			failed.append(item)

	if depth < 3: # retry failed calls a few times in case there were connection issues
		shardProcess(failed,depth+1)

def DoIt(item):
	# Writes CREST prices into recordResults in mySQL "INSERT INTO ... FROM" format
	# For data processing schema (of sorts)
	global X_DICT
	global colnames
	
	#parallelized record keeping storage
	global recordDict
	global recordResults

	ID = str(item[X_DICT["typeID"]])
	name = item[X_DICT["typeName"]]
	quantity = item[X_DICT["InStock"]]
	print '\t'.join([str(quantity), "of item with typeid", str(ID), "named", name])

	if ID == "":
		print("Blank column, continuing")
		raise IOError("Blank column, continuing")

	data = QueryCrest4ItemPrices(region,ID,[True, True])

	if data == None:
		print( "Some sort of query problem")
		exit(1)

	cleandata = cleanCrest(data)
	if cleandata == None:
		print("no orders for item", i)
		worth = 0
		raise IOError("no orders for item: "+str(typeid)+" == "+name)

	try:
		[fullworth, q] = GetCrestWorth(cleandata,[int(quantity),int(quantity)]) #this is two sets of two numbers: buy and sell prices and quants
		[singleworth, dummyQ] = GetCrestWorth(cleandata,[1,1]) #this is two sets of two numbers: buy and sell prices and quants
		#dummyQ[i]==0 if no orders of type 'i' are active
	except:
		print( "something went wrong at typeid='"+ID+"'")
		print( "Presumed end of typeID row")
		raise ValueError("Presumed end of typeID row")

	#~ cols = ["typeID",	"cashOut",		"buyMax",		"sellMin",		"purchaseIn" ]
	vals = [ID, 		fullworth[0],	singleworth[0], singleworth[1],	fullworth[1] ]
	for i in range(len(vals)):
		vals[i] = str(vals[i])

	recordResults[recordDict[item]] = "(" + ",".join(vals) + ")"

def GetSqlColNames(script,firstkeyword):
	#Extracts explicit columns from a mySQL string 'script' beginning with 'firstkeyword'
	if "FROM" in script:
		cols = script.split("FROM")[0]
	cols = script.split('\n')[0] # Cut off all but first line
	cols = cols.split(firstkeyword)[1] # Cut off "SELECT " keyword
	cols = ''.join(cols.split(' ')) # Remove spacing
	cols = cols.split(',')
	for n in range(len(cols)): # Remove details that will not show up on query result
		if '.' in cols[n]:
			cols[n] = ( cols[n].split('.') )[1]
		if 'AS' in cols[n]:
			cols[n] = ( cols[n].split('AS') )[1]
	return cols

##############################################
# END Functions
##############################################
User, Passwd = ReadUserAndPwFromFile("REDACTED_FILE")
#~ print "'"+User+"','"+Passwd+"'"

minutesStale = 10
outputFname = "EVEPriceUpdates.sql"
argnum = len(sys.argv)
if argnum > 1:
	minutesStale = int(sys.argv[1])
if argnum > 2:
	outputFname = sys.argv[2]

outputFile = open(outputFname,'w')

region = Rlookup["The Forge"]

try:
	con = mdb.connect(host='localhost', user=User, passwd=Passwd, db='Eve');

	cur = con.cursor()
	cur.execute("SELECT VERSION()")

	ver = cur.fetchone()
	
	print( "Database version : %s " % ver)
	print( time.asctime( time.localtime( time.time() ) ) )
	TABLE = "Pricing2"

	X_DICT = {}
	stalenessQuery = file2string("GetStalePricing.sql")
	stalenessQuery = stalenessQuery.replace("@",str(minutesStale) )
	colnames = GetSqlColNames(stalenessQuery, "SELECT")
	for col in range(len(colnames)):
		X_DICT[colnames[col]] = col
		
	cur.execute( stalenessQuery )
	stale = cur.fetchall()
	
	recordResults = [None]*len(stale) # Write stuff into this and then join it avoid thread writing confusion and other badness
	recordDict = {} # Use this to tell which record gets written into which entry
	for i in range(len(stale)):
		recordDict[stale[i]] = i
	
	if len(stale) > 0:
		print "The following are stale records:"
	else:
		print "No stale records. Exiting!"
		if con:
			con.close()
			con = 0
		sys.exit(0)

	targetCols = ["typeID",	"cashOut",		"buyMax",		"sellMin",		"purchaseIn" ]
	replaceHeader = "REPLACE INTO "+ TABLE + "("+",".join(targetCols)+") VALUES \n"
	outputFile.write(replaceHeader)
	########################
	## Prepare for multi-threaded webquery I/O
	whole = range( len(stale) )
	shardNum = min(40,len(stale))
	print("Processing list of %d items in %d batches:" % (len(stale), int(shardNum)) )
	shardLen = float(len(stale))/shardNum # number of typeIDs each thread gets
	shards = []
	for k in range(shardNum):
		if int(k*shardLen) == int((k+1)*shardLen) and k < (shardNum-1):
			break
		shards.append( stale[int(k*shardLen):int((k+1)*shardLen)] )

	#~ for shard in shards:
		#~ print(shard)

	# make the Pool of workers
	pool = ThreadPool(shardNum) 

	# pool does the work
	pool.map(shardProcess, shards)

	# close the pool and wait for the work to finish 
	pool.close() 
	pool.join()
	## Done with multi-threading now
	########################
	#~ outputFile.write(";")
	outputFile.write( ",\n".join(recordResults)+";" )

	#~ con.commit()
	
except mdb.Error, e:
	print( "Error %d: %s" % (e.args[0],e.args[1]))
	sys.exit(1)

finally:    
	if con:
		con.close()
