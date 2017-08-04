#!/usr/bin/env python3

import requests
#~ import string
#~ from math import sqrt

Brokertax=.0259
Salestax=.012

OrderSeparator = ",#,"

#Derived from "read_crest_market.py" by printing 'labels'
CrestOrderDetails = ['buy', 'issued', 'price', 'volumeEntered', 'minVolume', 'volume', 'range', 'href', 'duration_str', 'location', 'href', 'id', 'name', 'duration', 'minVolume_str', 'volumeEntered_str', 'type', 'href', 'id', 'name', 'id', 'id_str']
CREST_COL = {}
for n in range(len(CrestOrderDetails)):
	CREST_COL[CrestOrderDetails[n]] = n

def printblah():
	print("blah")
	print (Brokertax)

def LoadDelimPairs2Dict(text,dictry,delim):
	text = text.split('\n')
	for line in text:
		line = line.split(delim)
		if len(line) < 2:
			#~ print "breaking at line ", line
			continue
		entry = line[0]
		key = ','.join(line[1:])
		dictry[key] = entry

def LoadIDFileList2Dict(fnames,dictry,delim):
	for fname in fnames:
		EVEIDSfile = open(fname)
		EVEIDS = EVEIDSfile.read()
		EVEIDSfile.close()
		EVEIDS = EVEIDS.lower()
		LoadDelimPairs2Dict(EVEIDS,dictry,delim)

#BEGIN DICTIONARY CREATION
#BEGIN Creation of 'IDlookupTable' dictionary ##############
IDlookupTable = {}
LoadIDFileList2Dict(["EVE-TypeID-newitems.csv","EVE-TypeID-trimmed.csv","EVE-TypeID.csv"],IDlookupTable,',')

# REVERSE DICTIONARY
NamelookupTable = dict((v,k) for k,v in IDlookupTable.items())	
#END Creation of 'IDlookupTable' dictionary ################

#for getting name of an item from a typeID:

types_fix = 'types/'

marketprefix = 'https://crest-tq.eveonline.com/market/'
midfix = '/orders/'
#~ BUY = 'buy'
#~ SELL = 'sell'
IDprefix = '/?type=https://crest-tq.eveonline.com/inventory/types/'
#~ typeID = '44142'



def file2string(file_name):
	file_lines = []
	try:
		datafile = open(file_name)
	except IOError:
		print("File "+file_name+" does not exist; try another one.")
		return None

	i = 0
	for line in datafile:
		file_lines.append(line)
		i = i + 1

	datafile.close()
	return "".join(file_lines)

def ExtractDataFromText(text, begintag, endtag):
	try:
		text = text.split(begintag)[1]
	except IndexError:
		return None
	try:
		text = text.split(  endtag)[0]
	except IndexError:
		return None
	return text

def ExtractDataFromText_Improved(text, begintag, endtag, instance):
	#instance should be in {1, 2, 3, ..., -1}
	try:
		text = text.split(begintag)[instance]
	except IndexError:
		return None
	try:
		text = text.split(  endtag)[0]
	except IndexError:
		return None
	return text

def ExtractLastDataFromText(text, begintag, endtag):
	return ExtractDataFromText_Improved(text, begintag, endtag, -1)

def getTypeIDs(items):
	typenumlist = []

	for item in items:
		num = IDlookupTable.get(item.lower())
		if num != None:
			typenumlist.append(num)
		else:
			print( "found no match for item %s" % item )

	#~ print(typenumlist)
	return typenumlist

def getTypeIDs_fillgaps(items):
	typenumlist = []

	for item in items:
		num = IDlookupTable.get(item.lower())
		if num != None:
			typenumlist.append(num)
		else:
			typenumlist.append("")
			print( "found no match for item %s" % item )

	#~ print(typenumlist)
	return typenumlist

def string2int(string):
	try:
		i = int(string)
		return i
	except ValueError:
		#Handle the exception
		return None

def processMarketHist(string,numDays):#,savef=None):
	history = ExtractDataFromText(string,'[{','}]')
	if history == None:
		print (string[:100])
		return (None, None,None,None,None,None,None)
	days = history.split("}, {")
	days = days[-1*numDays:]
	daysprocessed = []

	for day in days:
		thisday = ''.join( day.split('"') )
		thisday = ''.join( thisday.split(' ') )
		thisday = thisday.split(',')
		daysprocessed.append( thisday )

#		if savef != None:
#			savef.write(','.join(thisday)+'\n')
	#print daysprocessed

	spread_sum = 0
	raw_sum = 0
	vol_sum = 0
	order_sum = 0
	margin_sum = 0
	avg_sum = 0
	var_sum = 0
	N = len(daysprocessed)
	
	for day in daysprocessed:
		for entry in day:
			pair = entry.split(':')
#			print( pair )
			if pair[0] == "lowPrice":
				low = float(pair[1])
			elif pair[0] == "highPrice":
				high = float(pair[1])
			elif pair[0] == "avgPrice":
				avg = float(pair[1])
			elif pair[0] == "volume":
				vol = float(pair[1])
			elif pair[0] == "orderCount_str":
				order = float(pair[1])
		profit = ( high*(1-Broker-Sales) - low*(1+Broker) )
		
		spread_sum = spread_sum + profit*vol # weighted by volume per day
		raw_sum = raw_sum + profit * vol
		vol_sum = vol_sum + vol
		order_sum = order_sum + order
		margin_sum = margin_sum + float(profit) / avg
		avg_sum = avg_sum + avg
		var_sum = var_sum + avg*avg*vol
	avgvelocity 	= int(float(raw_sum) / N)
	avgvol 			= int(float(vol_sum) / N)  # approx avg speed, divided by number of vendors to filter out high-maintenance sales
	avgspread  		= int(float(spread_sum) / vol_sum) # weighted by volume
	avgmargin  		= int(float(margin_sum) / N)
	avgprice   		= int(float(avg_sum) / N)
	variance   		= int(sqrt(float(var_sum - avg_sum) / N))
#	if savef != None:
#		savef.write(','.join([str(avgspread), str(avgvelocity), str(avgvol), str(avgmargin), str(variance)]))
#		savef.close()
	return (avgprice, avgspread, avgvelocity, avgvol, avgmargin, variance, order_sum)

def processCSVFileAsTypeIDs(data):
	typeIDlist = []
	for line in data.split('\n'):
		typeID = line.split(',')#[0]
		typeIDlist.append(typeID)
	return typeIDlist

def velkey(item):
	return -1*item[4]
def feasiblekey(item):
	return -1*item[4]*(100000000>item[2])

def Profit(buy, sell, buytax, selltax):
	buy = buy*(1+buytax)
	sell = sell*(1-selltax)
	return sell - buy

def readNameFromTypeID(typeid):
	nameurl = marketprefix + types_fix + typeid + '/'
	try:
		response = requests.get(nameurl)
		nameresponse = "".join( (response.text).split('"') )
		templist = nameresponse.split(',')
		name = (templist[6]).split(': ')[1]#get proper elt of list and process it into the item name
		return name
	except:	# item probably doesn't exist
		#~ print (response.headers)
		return None

def RawCRESTQuery(url):
	try:
		crest_response = requests.get(url)
		success_flag = True
	except:
		result = ""
		success_flag = False
		print (requests.response.headers)
	else:
		result = crest_response.text
	
	return (success_flag, result)
	

def QueryCrest4ItemPrices(region,typeID,orderflags):#orderflags should be bools telling whether buy or sell should be recorded
	buyurl  = marketprefix + str(region) + midfix + "buy"  + IDprefix + typeID + "/"
	sellurl = marketprefix + str(region) + midfix + "sell" + IDprefix + typeID + "/"
	if orderflags[0] == True:
		(buyflag, buyresponse) = RawCRESTQuery(buyurl)
	else:
		(buyflag, buyresponse) = (False, "")
	if orderflags[1] == True:
		(sellflag, sellresponse) = RawCRESTQuery(sellurl)
	else:
		(sellflag, sellresponse) = (False, "")
	
	if (sellresponse+buyresponse) == "":
		print("no CREST response for type", typeID)
		datalist = None
	else:
		datalist = [buyresponse, sellresponse]
#~ OrderSeparator.join()
		#~ print(html[:80])

	return datalist

def QueryCrest4TypeNameFromID(typeID):
	typeNameSuffix = "types/"+typeID+"/"
	url = marketprefix+typeNameSuffix
	(flag, response) = RawCRESTQuery(url)
	response.split('"name": "')
	if flag == True:
		return response
	else:
		return "NoName"


def cleanCrest(datalist): #takes html data from "QueryCrest4ItemPrices" and strips off the tags, sorting data into columns instead
	first = 1 #tells how many (useless) left-most columns to cut off (not including the "volume_str" column)
	#~ print(len(data))
#~ datalist = data.split(OrderSeparator)
	#~ n = 0
	labels = []
	cleanlist = []
	for data in datalist:
		tempdata = ExtractDataFromText(data,"[","]")
		if tempdata == None:
			cleanlist.append("")
			#~ print("readable data not found")
			#~ print(data[:80])
			continue
		tempdata = ''.join( tempdata.split('"') )
		cleandata = []
		for order in tempdata.split('{volume_str:'):
			cleanorder = []
			details = order.split(', ')
			for attribute in details:
				#~ temp = ''.join( attribute.split(' ') )
				temp = attribute.split(': ') # split off the tag (1st elt)
				if (len(labels) < len(details)):
					#~ n = n + 1
					labels.append( temp[0] )
				cleanorder.append(':'.join(temp[1:])) 			#cut off the tag and keep just the data
			cleandata.append(cleanorder[first:] )#','.join()) 	# omit the first, useless column
		cleanlist.append(cleandata[1:] )#"\n".join()) 	#there is an empty entry that needs eliminating... 
														#...look into this later and see where it comes from?
	#~ print("datalist is length", len(datalist))
	columnheadings = labels[first+1:] #','.join() # omit the first, useless column plus the one before it
	#~ cleanfile = (OrderSeparator).join(cleanlist)
	#~ cleanfile = OrderSeparator.join([columnheadings,cleanfile])

	return [columnheadings]+cleanlist #cleanfile

def clean2string(crestlistydata): # returns a string (writable file format)
	columnheadings = crestlistydata[0]
	#~ print(len(crestlistydata[1]))
	#~ crelistydata = crestlistydata[1]
	cleanstring = []
	for orderlist in crestlistydata[1:]: #do this for the orders, but not the column headers
		#~ print (orderlist[1])
		newlist = []
		for order in orderlist:
			neworder = ",".join(order)
			newlist.append(neworder)
		newlistything = "\n".join(newlist)
		cleanstring.append(newlistything)
	return (OrderSeparator+'\n').join([','.join(columnheadings)]+cleanstring)

def AnalyzeCleanCrestData(data): #expected format is [column headings, sell orders, buy orders]
	sellorders = data[1]
	buyorders = data[2]
	print( getStats(sellorders,sellsortkey) )
	print( getStats(buyorders,buysortkey) )

def GetCrestWorth(data,quant):
	#ignore the column headings, i.e., data[0]
	buyorders = data[1]
	sellorders = data[2]
	(maxbuy, buyquant) = getStatsQuant(buyorders,buysortkey,quant[0])
	(minsell, sellquant) = getStatsQuant(sellorders,sellsortkey,quant[1])
	#~ maxbuy = getStatsQuant(buyorders,buysortkey,quant[0])
	#~ minsell = getStatsQuant(sellorders,sellsortkey,quant[1])
	return [( maxbuy, minsell ), (buyquant, sellquant)]

def GetCrestQuant(data):
	return GetCrestWorth(data,1000000000000)

#~ def getSellStats(html):
#~ def getBuyStats(html):
def buysortkey(item):
	return -1*float(item[CREST_COL["price"]])

def sellsortkey(item):
	return float(item[CREST_COL["price"]])

def getStats(data,sortkey):
	#~ print( data[0][ CREST_COL["name"] ] )
	data.sort(key=lambda item: sortkey(item))
	#~ for entry in data[:10]:
		#~ print (entry[ CREST_COL["price"] ] )
	return data[0][ CREST_COL["price"] ]

def getStatsQuant(data,sortkey,quant):
	if len(data) == 0:
		return (0,0)
	#~ print( data[0][ CREST_COL["name"] ] )
	data.sort(key=lambda item: sortkey(item))
	#~ for entry in data[:10]:
		#~ print (entry[ CREST_COL["price"] ] )
	worth = 0
	i = 0
	#~ print('--')
	qneed = quant
	while ( (qneed > 0) and (i < len(data)) ):
		qsold = min(qneed,int(data[i][ CREST_COL["volume"] ]) )
		qneed = qneed - qsold
		worth = worth + qsold * float(data[i][ CREST_COL["price"] ])
		i = i + 1
		#~ print(qsold, quant, worth, data[i][ CREST_COL["price"] ])
		if qsold == 0:
			break
	return (worth, quant - qneed)

		
#BEGIN Creation of region dictionary #######################
EVEregions = ['The Forge', 'Domain', 'Lonetrek', 'The Citadel', 'Black Rise', 'The Bleak Lands','Essence','Verge Vendor','Heimatar','Kor-Azor','Metropolis','Sinq Laison','Placid']
EVEregIDs  = [10000002,10000043,10000016,10000033,10000069,10000038,10000064,10000068,10000030,10000065,10000042,10000032,10000048]
#add elts to the dictionary
Rlookup = {}
for num in range(len(EVEregions)):
	Rlookup[EVEregions[num]] = EVEregIDs[num]
Rlookup[None] = Rlookup.get('The Forge')
#END Creation of region dictionary   #######################


#BEGIN Creation of system dictionaries #######################
EVEsystems = ['Jita', 'Amarr', 'Hek', 'Dodixie', 'Onnamon','Usi','Ishomilken','Nisuwa','Rakapas', 'Oerse', 'Maire']
EVEsysIDs  = [30000142,30002187,30002053,30002659, 30045324, 30002755, 30002756, 30045352, 30045349, 30003577, 30003576]
colors     = ['#62AFFA','#E0A25A','#B56770','#74B5A7','#8CB1A1', '#8CB1A1', '#8CB1A1', '#8CB1A1', '#8CB1A1' , '#8CB1A1', '#8CB1A1']
#add elts to the dictionary
Slookup = {}
for num in range(len(EVEsystems)):
	Slookup[EVEsystems[num]] = EVEsysIDs[num]
Slookup[None] = Slookup.get('Jita')
#add elts to the dictionary
Clookup = {}
for num in range(len(EVEsystems)):
	Clookup[EVEsystems[num]] = colors[num]
Clookup[None] = Slookup.get('Jita')
#END Creation of system dictionaries   #######################





#Mainly for EC-spreadsheet utility ("EC" stands for "EVE-Central.com")

def gethtmlchunk( html, flag ):
	if flag == 'buy' or flag == 'sell' or flag == 'volume' or flag == 'avg' or flag == 'max' or flag == 'min':
		flag = flag + ">"
	
	html = html.split("<" + flag )
	if len(html) > 1:
		html = html[1]
		html = html.split("</"+flag )
		return html[0]

	return None
	
def gethtmlchunkImproved( html, flaglist ):
	flag = flaglist[0]
	if flag == 'buy' or flag == 'sell' or flag == 'volume' or flag == 'avg' or flag == 'max' or flag == 'min':
		flag = flag + ">"
	
	html = html.split("<" + flag )
	if len(html) > 1:
		html = html[1]
		html = html.split("</"+flag )

	if len(flaglist) > 1:
		return gethtmlchunkImproved( html[0], flaglist[1:] )
	else:
		return html[0]

	return None

def getmarketstatlisting( html, typeIDnum ):
	
	html = html.split('<type id="' + typeIDnum + '"')
	if len(html) > 1:
		html = html[1]
		html = html.split('</type>')
		return html[0]

	return None

def requestECmarketstatsRegion(typeidstring, regionnum):
	regio = "&regionlimit=" + str(regionnum)
	marketstat = "http://api.eve-central.com/api/marketstat?"
	url = marketstat + typeidstring + regio
	response = urllib2.urlopen(url)
	html = response.read()
	return html

def requestECmarketstatsSystem(typeidstring, system):
	syste = "&usesystem=" + str(system)
	marketstat = "http://api.eve-central.com/api/marketstat?"
	url = marketstat + typeidstring + syste
	response = urllib2.urlopen(url)
	html = response.read()
	return html
