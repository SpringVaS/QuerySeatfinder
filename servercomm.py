import requests
import json
from warnings import warn
import pandas as pd
import myutils

URL = "https://seatfinder.bibliothek.kit.edu/karlsruhe/getdata.php"

class ServerCommunication(object):

	def __init__(self, url_seatfinder):
		self.url_sf = url_seatfinder
		self.timeseries_keys = {'seatestimate' : 'occupied_seats', 'manualcount' : 'occupied_seats'}

	def __del__(self):
		pass
	
	def get_info_for_location_from_server(self, location_id, kind, timebegin, timeend):
		data = self.__query_server(kind, location_id, timebegin, timeend)
		pddf = pd.DataFrame()
		if (len(data) > 0):
			assert (len(data) == 1), ("Please review location_id parameter " + str(len(data)))
			for location in data:
				locationData = location[kind]
				pddf = pddf.append(self.__parse_timeseries(kind, locationData, location_id))
		return pddf

	"""
	Pass list of libraries for which the static data schould be loaded.
	"""
	def get_static_lib_data(self, libs):
		queryparams =    {'location[]'   : libs, 
						 'sublocs'      : 1,
						 'values'       : 'location',
						 'before'       : 'now'}
		data = {}
		try:
			r = requests.get(url = self.url_sf, params = queryparams)
			data = r.json()
			# write back the json from server to local hard drive for debugging purposes
			with open('staticlibdata.json', 'w+') as ld:
				ld.write(r.text)
			print('Load data from server and write back to file')
		except requests.ConnectionError as e:
			print('Load data from file')
			with open('staticlibdata.json', 'r') as datafile:
				data = json.load(datafile)


		callbacks = {   'timestamp'     : myutils.parse_timestamps, 
						'opening_hours' : myutils.parse_openinghours}

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

	def __parse_timeseries(self, kind, data, locationKey):
		data_list = data[locationKey]
		timestamp_list = [myutils.parse_timestamps(pointInTime['timestamp']) for pointInTime in data_list]
		value_list = [pointInTime[self.timeseries_keys[kind]] for pointInTime in data_list]

		value_dict = {'timestamp' : timestamp_list, locationKey : value_list}
		timeSeriesDataFrame = pd.DataFrame(value_dict)
		timeSeriesDataFrame = timeSeriesDataFrame.set_index(['timestamp'])
		return timeSeriesDataFrame


	def __query_server(self, kind, location_list, timebegin, timeend):
		queryparams =   {'location[]'   : location_list, 
						 'sublocs'      : 0,
						 'values'       : kind,
						 'before'       : timeend,
						 'limit'        : 1000}
		data = {}
		try:
			r = requests.get(url = self.url_sf, params = queryparams)
			data = r.json()
			# write back the json from server to local hard drive for debugging purposes
			with open('libdata.json', 'w+') as ld:
				ld.write(r.text)
		except requests.ConnectionError as e:
			warn('No server connection')

		return data