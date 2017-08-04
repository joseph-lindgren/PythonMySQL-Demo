#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys
import requests

MAXNUM_TO_INSERT = -1
DUPLICATE_ROWS = 0
NEW_ROWS = 0

##############################################
# BEGIN Functions
##############################################
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
		
def UpdateWalletTransactions(con,maxTransacts = -1): #database connection object parameter
	fileName = "secret.txt"
	fileContents = file2string(fileName)
	lines = fileContents.split("\n")
	keyID = lines[0]
	vCode = lines[1]
	eveApiUrl = "https://api.eveonline.com/char/WalletTransactions.xml.aspx?keyID="+keyID+"&vCode="+vCode
	#~ print(eveApiUrl)
	result = myGetUrlQueryResult(eveApiUrl)
	#~ print(result[:800])
	columns = "transactionDateTime,transactionID,quantity,typeName,typeID,price,"+						"clientID,clientName,stationID,stationName,"+						"transactionType,transactionFor,journalTransactionID,clientTypeID"
	lines = result.split("\n")
	if maxTransacts < 0:
		maxTransacts = len(lines)
	for line in lines:
		data = line	#Example: "    <row transactionDateTime=\"2017-05-17 13:25:23\" transactionID=\"4614998944\" quantity=\"340\" typeName=\"Dread Guristas Inferno Light Missile\" typeID=\"27369\" price=\"79884.84\" clientID=\"93101038\" clientName=\"ZeroPoint Shi\" stationID=\"60003760\" stationName=\"Jita IV - Moon 4 - Caldari Navy Assembly Plant\" transactionType=\"sell\" transactionFor=\"personal\" journalTransactionID=\"14113123141\" clientTypeID=\"1383\" />";
		#~ insertIntoString = PrepareInsertIntoTransaction(data, columns)
		#~ print( insertIntoString )
		if WalletTransactionInsertIntoDB( con, data, columns):
			maxTransacts = maxTransacts - 1
			if maxTransacts <= 0:
				break

def file2string(file_name): #string parameter
	file_lines = []
	try:
		datafile = open(file_name)
	except IOError:
		print("File "+file_name+" does not exist; try another one.")
		return None

	i = 0
	for line in datafile:
		#~ data = line.rstrip()
		#~ file_lines.append(data)
		file_lines.append(line)
		i = i + 1

	datafile.close()
	return "".join(file_lines)
	
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

def WalletTransactionInsertIntoDB(con, xml, form):# connection, string, string
# Returns a bool indicating success or failure (Not an int of how many rows were affected)
	global DUPLICATE_ROWS
	global NEW_ROWS
	sqlInsertInto = PrepareInsertInto(xml,"Transactions", form)
	if sqlInsertInto=="":
		print("No data! Aborting data row insertion.")
		return False
	
	#~ print(sqlInsertInto)
	try:
		cur = con.cursor()
		numRowsAffected = cur.execute(sqlInsertInto)
		print(str(numRowsAffected)+" rows affected")
		print("Successful insertion into the database")
		NEW_ROWS = NEW_ROWS + 1
		return True

	except mdb.Error, e:
		if e.args[0] == 1062:
			DUPLICATE_ROWS = DUPLICATE_ROWS + 1
		else:
			print( "Error %d: %s" % (e.args[0],e.args[1]))
		#~ sys.exit(1)
	except MySQLError:
		print("OOPS! mySQL database exception thrown! (probably duplicate entry)")
		#~ print("SQLException: "+ex.getMessage())
		#~ return False

def myGetUrlQueryResult(url): # string parameter
# Returns web response as a string
	result = requests.get(url)
	return result.text

def createBaselineQuant(con): # database connection parameter
# prints out the approximate mySQL command(s) to baseline quantity of previously untracked item(s)
# quantity output is sufficient to zero out inventory. BE SURE TO ADD HOW MANY ARE ACTUALLY ON HAND!
	script = file2string("GetItemsNeedingBaseline.sql")
	cur = con.cursor()
	cur.execute(script)
	
	resultrows = cur.fetchall()
	for row in resultrows:
		r = []
		for elt in row[:-1]:
			r.append(str(elt))
		r.append(str(-1*row[-1]))
		r[0] = '"'+r[0]+'"'
		values = ",".join(r)+","
		insertCommand = PrepareItemInsertInto(values, "typeName,typeID,quantity,transactionID", "Transactions")
		print(insertCommand)

def ReadUserAndPwFromFile(filename):
	return file2string(filename).split('\n')
##############################################
# END Functions
##############################################
def main():
	User, Passwd = ReadUserAndPwFromFile("REDACTED_FILE")
	#~ print "'"+User+"','"+Passwd+"'"

	argnum = len(sys.argv)
	if argnum > 1 and is_int(sys.argv[1]):
		MAXNUM_TO_INSERT = int(sys.argv[1])
		print( "Copying in (at most)",MAXNUM_TO_INSERT,"transactions from character's EVE wallet." )
	else:
		print( "Copying in as many transactions from character's EVE wallet as possible." )


	try:
		con = mdb.connect(host='localhost', user=User, passwd=Passwd, db='Eve');

		cur = con.cursor()
		cur.execute("SELECT VERSION()")

		ver = cur.fetchone()
		
		print( "Database version : %s " % ver)
		
		if True:
			UpdateWalletTransactions(con)
			con.commit()
			print("And we are updating current inventory")
			createBaselineQuant(con)
		if False:
			# adds "typeID"s from file to "Eve.typeids" database table
			contents = file2string(args[0])
			query = PrepareBasicInsertInto( contents, "typeid,item,query","typeids")
			print(query[:1000])
			cur.execute("use Eve")
			cur.execute(query+";")
		if False:
			cur.execute('SELECT typeName,SUM(price*quantity* CASE WHEN transactionType = "buy" THEN -1 ELSE 1 END ) FROM Transactions WHERE typeName = "Guristas Brass Tag";')
			rows = cur.fetchall()
			for row in rows:
				print row[0], row[1]
		
	except mdb.Error, e:
		print( "Error %d: %s" % (e.args[0],e.args[1]))
		sys.exit(1)
		
	finally:    
		if con:
			con.close()

	print( "%d rows added. %d duplicate rows skipped" % (NEW_ROWS, DUPLICATE_ROWS))

	return 0

if __name__ == '__main__':
	main()
