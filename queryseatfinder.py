import requests
import json
import csv

from openpyxl import Workbook

import pandas as pd

URL = "https://seatfinder.bibliothek.kit.edu/karlsruhe/getdata.php"

location = 'FBI, LSW'
values =  'location, manualcount'
before = 'now'
limit = 10

PARAMS = {'location[]' : location, 'values' : values, 'before' : before, 'limit' : limit}

def identityFunction(data):
	return data

class Model(object):

	def __init__(self, url_seatfinder, dstpath):
		self.url_sf = url_seatfinder
		self.dstpath = dstpath
		self.workbook = Workbook()
		# Reading halls LS
		self.mainlib = {'LSG', 		# Gesellschaftswissenschaften
						'LSM', 		# Medienzentrum
						'LST', 		# Technik
						'LSN', 		# Naturwissenschaften
						'LSW', 		# Wiwi und Informatik
						'LBS', 		# Lehrbuchsammlung
						'BIB-N'} 	# KIT-Bibliothek Nord
		# Specific Libraries
		self.slibs =   {'FBC', 		# Chemie
						'FBP',		# Physik
						'LAF',		# Lernzentrum am Fasanenschloesschen}
						'FBA',		# Architektur
						'FBI',		# Informatik
						'FBM',		# Mathematik
						'FBW'}		# Wiwi

		self.vtypes = {'location[]', 'sublocs'}

		self.timeSeriesKeys = {'seatestimate' : 'occupied_seats', 'manualcount' : 'occupied_seats'}

	def __del__(self):
		pass

	def __defineWeekdayNames(self):
		mon = datetime.datetime.strptime("2013-05-13 09:00:00.000000", "%Y-%m-%d %H:%M:%S.%f");
		print((mon + 1).strftime("%A"))

	def getLibSpecTable(self):
		queryparams =	{'location[]'	: [self.mainlib, self.slibs], 
						 'sublocs'		: 1,
						 'values'		: 'location',
						 'before'		: 'now'}
		r = requests.get(url = self.url_sf, params = queryparams)
		data = r.json()
		# write back the json from server to local hard drive for debugging purposes
		with open('libdata.json', 'w+') as ld:
			ld.write(r.text)
		sheet1 = self.workbook.create_sheet('Libraries')
		callbacks = {'timestamp' : self.__parseTimeStamps, 'opening_hours' : self.__parseOpeningHours}
		cindex = 1
		self.__parseKeysRecursively(data[0]['location'][list(data[0]
			['location'].keys())[0]], sheet1, 1, 1, 0, callbacks.keys())
		cindex += 1
		for location in data:
			self.__parseJSONrecursively(location['location'][list(location['location'].keys())[0]], sheet1, 1, cindex, 0, callbacks)
			cindex += 1
		self.workbook.save(self.dstpath)

	def getInfo(self, kind, timebegin, timeend):
		queryparams =	{'location[]' 	: [self.mainlib, self.slibs], 
						 'sublocs' 		: 0,
						 'values' 		: kind,
						 'before' 		: '-5day',
						 'limit' 		: 1000}
		r = requests.get(url = self.url_sf, params = queryparams)
		data = r.json()
		# write back the json from server to local hard drive for debugging purposes
		with open('libdata.json', 'w+') as ld:
			ld.write(r.text)
		sheet = self.workbook.create_sheet(kind)
		cindex = 1
		callbacks = {kind : self.__parseTimeSeries, 'timestamp' : self.__parseTimeStamps}
		self.__parseKeysRecursively(data, sheet, 1, 1, 0, callbacks.keys())
		timeSeries = {}
		for location in data:
			# pass callbacks for parsing the timestamps and the opening hours in the library data
			# callbacks = {'timestamp' : self.__parseTimeStamps}
			# self.__parseJSONrecursively(location[kind], sheetSeats, 1, cindex, 0, callbacks)
			locationData = location[kind]
			locationKey = next(iter(locationData))
			timeSeries[locationKey] =  self.__parseTimeSeries(kind, locationData[locationKey])
			#timeSeries[locationKey].rename(str(locationKey))
			cindex += 2
		#print(timeSeries)
		twoBibs = timeSeries['LSW'].merge(timeSeries['FBI'], how='inner', on='timestamp')
		print(twoBibs)
		self.workbook.save(self.dstpath)

	def __parseTimeSeries(self, kind, data):
		timestamp_list = [self.__parseTimeStamps(pointInTime['timestamp']) for pointInTime in data]
		value_list = [pointInTime[self.timeSeriesKeys[kind]] for pointInTime in data]

		value_dict = {"timestamp" : timestamp_list, "occupied_seats" : value_list}
		timeSeriesDataFrame = pd.DataFrame(value_dict)
		return timeSeriesDataFrame

	def __parseOpeningHours(self, data):
		ohlist = []
		# weekly opening hours
		#print(data[keylist[1]])
		for interval in data['weekly_opening_hours']:
			openingHours_str = ""
			opening = self.__parseTimeStamps(interval[0])
			closing = self.__parseTimeStamps(interval[1])
			weekday_opening = opening.strftime("%A")
			weekday_closing = closing.strftime("%A")
			time_opening = opening.strftime("%H:%M")
			time_closing = closing.strftime("%H:%M")
			if (weekday_opening == weekday_closing):
				openingHours_str = weekday_opening + ": " + time_opening + " - " + time_closing
			else:
				openingHours_str = weekday_opening + ": " + time_opening + " - " + weekday_closing + ": " + time_closing
			#print(opening)
			ohlist.append(openingHours_str)
		return ohlist

	def __parseTimeStamps(self, data):
		#sheet.write(row, column, str(data))
		if (not isinstance(data, dict)):
			return data
		keylist = list(data.keys());
		if (keylist[0] == 'date'):
			return pd.Timestamp(data['date'])

	def obtainDataFromServer(self, parameters):
		r = requests.get(url = self.url_sf, params = parameters)
		data = r.json()
		print(r)
		with open(self.dstpath, 'w+') as csv_file:
			csv_data = csv.writer(csv_file)
			#self.__parseJSONrecursively(data, csv_data)

	# parse an entry identified as value with given callback function
	def __addValue(self, sheet, row, column, data, callback):
		oldCellValue = sheet.cell(row, column).value
		newValue = callback(data)
		if (not oldCellValue):
			sheet.cell(row, column).value = str(newValue)
		elif (isinstance(oldCellValue, str)):
			sheet.cell(row, column).value += ", " + str(newValue)

	# It is possible to pass a dict of callbacks, the key is the key in the data the callback should parse
	def __parseKeysRecursively(self, json_data, sheet, row, column, level, keysbreak):
		if (isinstance(json_data, list)):
			for element in json_data:
				self.__parseKeysRecursively(element, sheet, row, column, level + 1, keysbreak)
		elif (isinstance(json_data, dict)):
			addoff = 1
			for key in json_data.keys():
				sheet.cell(row + addoff, column).value = key
				if (key not in keysbreak):
					self.__parseKeysRecursively(json_data[key], sheet, row + addoff, column, level + 1, keysbreak)
				addoff = addoff + 1

	def __parseJSONrecursively(self, json_data, sheet, row, column, level, callback):
		if (isinstance(json_data, list)):
			for element in json_data:
				self.__parseJSONrecursively(element, sheet, row, column, level + 1, callback)
		elif (isinstance(json_data, dict)):
			addoff = 1
			#isect = intersection(json_data.keys(), callback.keys())
			for key in json_data.keys():
				if key in callback.keys():
					self.__addValue(sheet, row + addoff, column + 1, json_data[key], callback[key])
				else:
					self.__parseJSONrecursively(json_data[key], sheet, row + addoff, column, level + 1, callback)
				addoff = addoff + 1
		else:
			self.__addValue(sheet, row, column + 1, json_data, identityFunction)


class ViewController(object):
	def __init__(self, pModel):
		self.model = pModel

	def buildParameters(self):
		PARAMS = {'location[]' : self.model.mainlib, 'values' : 'location', 'before' : 'now', 'limit' : 20}
		return PARAMS

m = Model(URL, 'data.xlsx')
c = ViewController(m)
m.getLibSpecTable()
m.getInfo('seatestimate', [],[])