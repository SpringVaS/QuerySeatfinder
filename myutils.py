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

def resample_gaussian(resampler, sigma, loffset):
	resampled_dataframe = pd.DataFrame()
	for group in resampler:
		label_time = group[0] + loffset
		values = group[1]
		weights = np.zeros(len(values))
		for i in range(len(values)):
			distance = np.abs(values.index[i] - label_time)
			#print(values.index[i])
			d = distance.seconds
			weights[i] = np.exp(- 0.5 * np.power((d / sigma), 2))
		normalization_factor = 1 / np.sum(weights)
		weights = normalization_factor * weights

		#group_rep = np.multiply(weights, values)

		resampled_dataframe.append

	return resampled_dataframe