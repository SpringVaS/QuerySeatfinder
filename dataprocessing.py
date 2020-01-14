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
			print(weights)
			print(group)
		else:
			normalization_factor = 1 / np.sum(weights)
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

class DataProcessor(object):

	def __init__(self, mainlib, slibs, lib_meatadata):
		self.lib_meatadata = lib_meatadata
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



	def compute_pressure(self, data):
		mainlib_capacity = self.lib_meatadata[self.mainlib].loc['available_seats'].sum()
		mainlib_pressure = data[self.mainlib].sum(axis = 1) / mainlib_capacity
		mainlib_pressure.name = "KIT-BIB"

		speclib_capacities = self.lib_meatadata[self.slibs].loc['available_seats']
		speclib_pressure = data[self.slibs] / speclib_capacities
		pressure = pd.merge(mainlib_pressure, speclib_pressure, on='timestamp')

		return pressure