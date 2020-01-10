import numpy as np
import pandas as pd

def as_text(value):
	if value is None:
		return ""
	else:
		return str(value)

def index_to_letter(index):
	return chr(64 + (index % 26))

def gaussian_weighted_mean(array_like, exp_decay):
	return np.mean(array_like)

def calculate_derivation(max_dist, min_weight):
	return (max_dist / (np.sqrt(- 2 * np.log(min_weight))))

def resample_gaussian(resampler, sigma):
	#resampled_dataframe = pd.DataFrame()
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
	#resampled_dataframe = pd.DataFrame()
	resampled_dataframe = resampled_dataframe.set_index(['timestamp'])
	return resampled_dataframe

