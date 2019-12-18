import requests
import json
import functools

from openpyxl import Workbook, load_workbook

import pandas as pd
import numpy as np

import myutils


URL = "https://seatfinder.bibliothek.kit.edu/karlsruhe/getdata.php"

def identityFunction(data):
    return data

class Model(object):

    def __init__(self, url_seatfinder, dstpath):
        self.url_sf = url_seatfinder
        self.dstpath = dstpath
        # Reading halls LS
        self.mainlib = {'LSG',      # Gesellschaftswissenschaften
                        'LSM',      # Medienzentrum
                        'LST',      # Technik
                        'LSN',      # Naturwissenschaften
                        'LSW',      # Wiwi und Informatik
                        'LBS',}         # Lehrbuchsammlung
                        #'BIB-N'}   # KIT-Bibliothek Nord. Am Campus Nord
        # Specific Libraires
        self.slibs =   {'FBC',      # Chemie
                        'FBP',      # Physik
                        'LAF',      # Lernzentrum am Fasanenschloesschen}
                        'FBA',      # Architektur
                        'FBI',      # Informatik
                        'FBM',}     # Mathematik
                        #'FBW'}     # Wiwi - zur Zeit geschlossen

        self.vtypes = {'location[]', 'sublocs'}

        self.timeSeriesKeys = {'seatestimate' : 'occupied_seats', 'manualcount' : 'occupied_seats'}

        self.staticLibData = {}

        # Create Exel File
        workbook = Workbook()
        workbook.save(dstpath)

    def __del__(self):
        pass

    def getLibSpecTable(self):
        queryparams =   {'location[]'   : [self.mainlib, self.slibs], 
                         'sublocs'      : 1,
                         'values'       : 'location',
                         'before'       : 'now'}
        r = requests.get(url = self.url_sf, params = queryparams)
        data = r.json()
        # write back the json from server to local hard drive for debugging purposes
        with open('staticlibdata.json', 'w+') as ld:
            ld.write(r.text)

        excel_workbook = load_workbook(self.dstpath)
        sheet1 = excel_workbook.create_sheet('Libraries')
        callbacks = {'timestamp' : self.__parseTimeStamps, 'opening_hours' : self.__parseOpeningHours}
        cindex = 0
        self.__parseKeysRecursively(data[0]['location'][list(data[0]
            ['location'].keys())[0]], sheet1, 0, 1, 0, callbacks.keys())
        cindex += 1
        for location in data:
            self.__parseJSONrecursively(location['location'][list(location['location'].keys())[0]], sheet1, 0, cindex, 0, callbacks)
            cindex += 1

        sheet1.column_dimensions['A'].width = 25
        list_column_names = [chr(i) for i in range(ord('B'),ord('Z')+1)]

        for colletter in list_column_names:
            sheet1.column_dimensions[colletter].width = 50
        excel_workbook.save(self.dstpath)

    def getInfo(self, kind, timebegin, timeend):
        data = self.__queryServer(kind, [self.mainlib, self.slibs], timebegin, timeend)
        resampled = {}
        for location in data:
            locationData = location[kind]
            locationKey = next(iter(locationData))
            pddf =  self.__parseTimeSeries(kind, locationData, locationKey)

            oldestTime = pddf.iloc[0].name 
            while oldestTime > timebegin:
                reload_data = self.__queryServer(kind, locationKey, timebegin, oldestTime)
                for locationr in reload_data:
                    pddfr =  self.__parseTimeSeries(kind, locationr[kind], next(iter(locationr[kind])))
                    #print(pddfr)
                    pddf = pddf.append(pddfr)
                    oldestTime = pddfr.iloc[0].name
            pddf = pddf[pddf.index >= timebegin]

            sampleddf = pddf.resample('15Min').mean()
            resampled[locationKey] = sampleddf.round()
        #print(resampled)
        combinedData = functools.reduce(lambda left,right: 
            pd.merge(left,right,on='timestamp', how = 'outer').fillna(0), 
            resampled.values())
        combinedData = combinedData.sort_index(ascending = False)
        return combinedData

    def getStaticLibData(self):
        queryparams =    {'location[]'   : [self.mainlib, self.slibs], 
                         'sublocs'      : 1,
                         'values'       : 'location',
                         'before'       : 'now'}
        r = requests.get(url = self.url_sf, params = queryparams)
        data = r.json()
        # write back the json from server to local hard drive for debugging purposes
        with open('staticlibdata.json', 'w+') as ld:
            ld.write(r.text)

        """data = {}
        with open('staticlibdata.json', 'r') as datafile:
            data = json.load(datafile)"""


        callbacks = {'timestamp' : self.__parseTimeStamps, 'opening_hours' : self.__parseOpeningHours}

        staticlibdata = {}
        for location in data:
            metadata = location['location']
            locationKey = next(iter(metadata))
            parsedMetaInfo = metadata[locationKey][0]
            for key in parsedMetaInfo.keys():
                if key in callbacks.keys():
                    parsedMetaInfo[key] = callbacks[key](parsedMetaInfo[key])
            staticlibdata[locationKey] = parsedMetaInfo

        return pd.DataFrame(staticlibdata)

    def writeInfoToExcel(self, dataframe, sheet_name):
        excel_workbook = load_workbook(self.dstpath)
        writer = pd.ExcelWriter(self.dstpath, engine = 'openpyxl')
        writer.book = excel_workbook
        dataframe.to_excel(writer, sheet_name = sheet_name)
        sheet = writer.sheets[sheet_name]
        sheet.column_dimensions['A'].width = 30
        writer.save()
        writer.close()

    def autoFormatSheet(self, sheet_name):
        excel_workbook = load_workbook(self.dstpath)
        sheet = excel_workbook[sheet_name]

        for column in sheet.columns:
            length = max(len(myutils.as_text(cell.value)) for cell in column)
            sheet.column_dimensions[myutils.letterFromIndex(column[0].column)].width = length
        excel_workbook.save(self.dstpath)

    def __parseTimeSeries(self, kind, data, locationKey):
        data_list = data[locationKey]
        timestamp_list = [self.__parseTimeStamps(pointInTime['timestamp']) for pointInTime in data_list]
        value_list = [pointInTime[self.timeSeriesKeys[kind]] for pointInTime in data_list]

        value_dict = {'timestamp' : timestamp_list, locationKey : value_list}
        timeSeriesDataFrame = pd.DataFrame(value_dict)
        timeSeriesDataFrame = timeSeriesDataFrame.set_index(['timestamp'])
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

    def __queryServer(self, kind, location_list, timebegin, timeend):
        queryparams =   {'location[]'   : location_list, 
                         'sublocs'      : 0,
                         'values'       : kind,
                         'before'       : timeend,
                         'limit'        : 1000}
        r = requests.get(url = self.url_sf, params = queryparams)
        data = r.json()
        # write back the json from server to local hard drive for debugging purposes
        with open('libdata.json', 'w+') as ld:
            ld.write(r.text)
        return data

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

    def __defineWeekdayNames(self):
        mon = datetime.datetime.strptime("2013-05-13 09:00:00.000000", "%Y-%m-%d %H:%M:%S.%f");
        print((mon + 1).strftime("%A"))


class ViewController(object):
    def __init__(self, pModel):
        self.model = pModel

    def buildParameters(self):
        PARAMS = {'location[]' : self.model.mainlib, 'values' : 'location', 'before' : 'now', 'limit' : 20}
        return PARAMS

m = Model(URL, 'data.xlsx')
c = ViewController(m)

m.writeInfoToExcel(m.getStaticLibData(), "Libraries")
m.autoFormatSheet("Libraries")

timebegin = pd.Timestamp('2018-10-15 07:00:00')
timeend   = pd.Timestamp('2019-03-31 22:15:00')

m.writeInfoToExcel(m.getInfo('seatestimate',timebegin, timeend), "occupied seats")