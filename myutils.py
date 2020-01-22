import pandas as pd

def as_text(value):
	if value is None:
		return ""
	else:
		return str(value)

def index_to_letter(index):
	return chr(64 + (index % 26))

def parse_timestamps(data):
	if (not isinstance(data, dict)):
		return data
	keylist = list(data.keys());
	if (keylist[0] == 'date'):
		return pd.Timestamp(data['date'])

def parse_openinghours(data):
	oh_intervals = []
	for interval in data['weekly_opening_hours']:
		opening = parse_timestamps(interval[0])
		closing = parse_timestamps(interval[1])
		oh_intervals.append(pd.Interval(opening, closing))
	return oh_intervals