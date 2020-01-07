import numpy as np

def as_text(value):
	if value is None:
		return ""
	else:
		return str(value)

def index_to_letter(index):
	return chr(64 + (index % 26))

def gaussian_weighted_mean(exp_decay, array_like):
	weights = np.zeros(len(array_like))
	print(weights)
	for timestamp in array_like.keys():
		print(timestamp)
	return np.mean(array_like)