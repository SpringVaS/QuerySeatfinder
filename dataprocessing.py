import pandas as pd
import numpy as np

import myutils

def calculate_derivation(max_dist, min_weight):
	return (max_dist / (np.sqrt(- 2 * np.log(min_weight))))

def resample_gaussian(resampler, sigma):
	labels = []
	reps = []
	loffset = resampler.loffset
	for group in resampler:
		label_time = group[0] + loffset
		labels.append(label_time)
		values = group[1]
		weights = np.zeros(len(values))
		for i in range(len(values)):
			distance = np.abs(values.index[i] - label_time)
			d = distance.seconds
			weights[i] = np.exp((-1 * d * d) / (2 * sigma * sigma))
		sum_weights = np.sum(weights)
		if (sum_weights == 0):
			normalization_factor = 1
		else:
			normalization_factor = 1 / sum_weights
		weights = normalization_factor * weights
		group_rep = 0
		for i in range(len(weights)):
			group_rep += weights[i] * values.values[i][0]
		reps.append(group_rep)
	
	""" location_id is to be found in group like this
		the first key of the first line of the secend element of the passed touple
	"""
	loc_id = (next(iter(values.iloc[0].keys())))

	value_dict = {'timestamp' : labels, loc_id : reps}
	resampled_dataframe = pd.DataFrame(value_dict)
	resampled_dataframe = resampled_dataframe.set_index(['timestamp'])
	return resampled_dataframe

def resample_opening_hours(array_like, opening_hours):
	sum_entries = 0
	for entry in array_like.index:
		#print(entry.day_name())
		opened = False;
		for interval in opening_hours:
			if entry.dayofweek in range(interval.left.dayofweek, interval.right.dayofweek + 1):
				if (entry.time() >= interval.left.time() and entry.time() <= interval.right.time()):
					opened = True;
			else:
				pass
		print(opened)
		print(opening_hours)
		print(entry)
		print(entry.day_name())

class DataProcessor(object):

	def __init__(self, mainlib, slibs, lib_metadata):
		self.lib_metadata = lib_metadata
		self.slibs = slibs
		self.mainlib = mainlib

	def __del__(self):
		pass


	def resample(self, data, sampling_interval, sampling_method):
		""" Without additional parameters, the pandas datframe resample function
			aggregates the values between the two labels. To simulate a moving average
			the actual label ticks are moved half the resampling interval.
			The label names are also offset half the resampling interval.
		"""
		timedelta = pd.Timedelta(sampling_interval)
		interval_seconds = str(timedelta.seconds) + 'S'
		offset_delta = pd.Timedelta(0)
		if (timedelta < pd.Timedelta('1D')):
			offset_delta = timedelta / 2
		
		"""
		Apply custom aggregarion function. Use functools to include parameter.
		"""
		if (timedelta >= pd.Timedelta('1W')):
			''' Use monday as base label
			'''
			resampler = data.resample(sampling_interval, label = 'left', loffset='1D')
		# 1D
		elif (offset_delta.seconds == 0):
			resampler = data.resample(sampling_interval)
		else:
			resampler = data.resample(interval_seconds, base=offset_delta.seconds, loffset=offset_delta)

		
		#resampler = data.resample(self.resampling_interval)

		location_data = pd.DataFrame()

		if (sampling_method == 'Mean'):
			location_data = resampler.mean()
		elif (sampling_method == 'Gauss'):
			sigma = calculate_derivation(offset_delta.seconds, 0.2)
			location_data = resample_gaussian(resampler, sigma)
		
		location_data = location_data.sort_index(ascending = False)
		return location_data


	def compute_mainlib_pressure(self, occupancy_data):
		mainlib_capacity = self.lib_metadata[self.mainlib].loc['available_seats'].sum()
		mainlib_pressure = occupancy_data[self.mainlib].sum(axis = 1) / mainlib_capacity
		mainlib_pressure.name = "KIT-BIB"

		return mainlib_pressure

	def compute_reading_halls_pressure(self, occupancy_data):
		capacity = self.lib_metadata[self.mainlib].loc['available_seats']
		halls_pressure = occupancy_data[self.mainlib] / capacity

		return halls_pressure

	def compute_speclibs_pressure(self, occupancy_data):
		speclib_capacities = self.lib_metadata[self.slibs].loc['available_seats']
		speclib_pressure = occupancy_data[self.slibs] / speclib_capacities

		return speclib_pressure


	def compute_pressure(self, occupancy_data):
		mainlib_pressure = self.compute_mainlib_pressure(occupancy_data)
		halls_pressure = self.compute_reading_halls_pressure(occupancy_data)
		speclib_pressure = self.compute_speclibs_pressure(occupancy_data)

		pressure = pd.merge(mainlib_pressure, halls_pressure.sort_index(axis=1), on='timestamp')		

		pressure = pd.merge(pressure, speclib_pressure.sort_index(axis=1), on='timestamp')

		return pressure