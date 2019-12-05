import requests
import json
import csv
import datetime

from openpyxl import Workbook

import pandas as pd

URL = "https://seatfinder.bibliothek.kit.edu/karlsruhe/getdata.php"

location = 'FBI, LSW'
values =  'location, manualcount'
before = 'now'
limit = 10

PARAMS = {'location[]' : location, 'values' : values, 'before' : before, 'limit' : limit}

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

	def __del__(self):
		pass

	def __defineWeekdayNames(self):
		mon = datetime.datetime.strptime("2013-05-13 09:00:00.000000", "%Y-%m-%d %H:%M:%S.%f");
		print((mon + 1).strftime("%A"))

	def getLibSpecTable(self):
		r = requests.get(url = self.url_sf, params = {'location[]' : self.mainlib, 'sublocs' : 1, 'values' : 'location', 'before' : 'now'})
		data = r.json()
		with open('libdata.json', 'w+') as ld:
			ld.write(r.text)
		sheet1 = self.workbook.create_sheet('Libraries')
		cindex = 1
		for location in data:
			self.__parseJSONrecursively(location, sheet1, 1, cindex, 0, {'timestamp' : self.__parseTimeStamps, 'opening_hours' : self.__parseOpeningHours})
			cindex += 2
		self.workbook.save(self.dstpath)

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
			return datetime.datetime.strptime(data['date'], "%Y-%m-%d %H:%M:%S.%f")

	def obtainDataFromServer(self, parameters):
		r = requests.get(url = self.url_sf, params = parameters)
		data = r.json()
		print(r)
		with open(self.dstpath, 'w+') as csv_file:
			csv_data = csv.writer(csv_file)
			#self.__parseJSONrecursively(data, csv_data)

	def __parseJSONrecursively(self, json_data, sheet, row, column, level, callback):
		if (isinstance(json_data, list)):
			for element in json_data:
				self.__parseJSONrecursively(element, sheet, row, column, level + 1, callback)
		elif (isinstance(json_data, dict)):
			addoff = 0
			for key in json_data.keys():
				addoff = addoff + 1
				sheet.cell(row + addoff, column).value = key
				if (keybreak in callback.keys()):
					fcn = callback[keybreak]
					value = fcn(json_data[keybreak])
					sheet.cell(row + addoff, column + 1).value = str(value)
				else:
					self.__parseJSONrecursively(json_data[key], sheet, row + addoff, column, level + 1, callback)
		else:
			value = sheet.cell(row, column + 1).value
			if (not value):
				sheet.cell(row, column + 1).value = json_data
			elif (isinstance(value, str)):
				sheet.cell(row, column + 1).value = value + ", " + str(json_data)


class ViewController(object):
	def __init__(self, pModel):
		self.model = pModel

	def buildParameters(self):
		PARAMS = {'location[]' : self.model.mainlib, 'values' : 'location', 'before' : 'now', 'limit' : 20}
		return PARAMS

m = Model(URL, 'data.xlsx')
c = ViewController(m)
m.getLibSpecTable()