from printers import Printer

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd



colors =   {	'KIT-BIB':	'#32A189FF',
				'FBC' : 'Green',      # Chemie
				'FBP': 'Purple',      # Physik
				'LAF': 'Red',      # Lernzentrum am Fasanenschloesschen}
				'FBA' : 'Blue',      # Architektur
				'FBI' : 'Orange',      # Informatik
				'FBM' : 'Yellow'}     # Mathematik

class Plotter(Printer):

	def __init__(self):
		self.plot_index = 1
		self.pass_index = 0
		self.ylimit_min = 0
		self.ylimit_max = 0

		self.hour_locator = mdates.HourLocator(byhour=range(24), interval = 2)
		
	
	def __del__(self):
		plt.close()

	def export_lib_metadata(self, metadata):
		pass

	def set_ylimits(self, ylimit_min, ylimit_max):
		self.ylimit_min = ylimit_min
		self.ylimit_max = ylimit_max


	def export_data(self, data, title, quantity_description):
		'''
			reverse order of dataframe for plot. Original begins with newest values
		'''
		data.sort_index(ascending=True)
		#data[::-1] 
		print(title)

		keys = (data.keys())

		fig = plt.figure()
		ax = fig.gca(ylabel=quantity_description)
		#ax.plot_date(data.index, data, '-')
		print(data)
		data.plot(title = title, ax = ax, x_compat=True, color = [colors.get(x, '#333333') for x in data.columns])
		ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
		ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
		ax.set_xlabel('')
		if (self.ylimit_max > - 1):
			ax.set_ylim(ymin = self.ylimit_min, ymax = self.ylimit_max)
		else:
			autoscale = ax.get_ylim()
			ax.set_ylim(ymin = 0, ymax = autoscale[1])
		fig.autofmt_xdate(rotation=0, ha='center', which=None)
		self.plot_index += 1

	def finish_up(self):
		self.pass_index += 1
		plt.show(block = False)