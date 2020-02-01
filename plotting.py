from printers import Printer

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

colors =   {	'KIT-BIB':	'#32A189FF',
				'FBC' : '#1c3e5eff',      # Chemie
				'FBP': '#a0acffff',      # Physik
				'LAF': '#294EFFFF',      # Lernzentrum am Fasanenschloesschen}
				'FBA' : 'Gray',      # Architektur
				'FBI' : 'Orange',      # Informatik
				'FBM' : '#ffa0dfff',

				'LSG' : '#1c3e5eff',      
				'LSM' : '#a0acffff',      
				'LST' : '#294EFFFF', 
				'LSN' : 'Gray', 
				'LSW' : 'Orange',
				'LBS' : '#ffa0dfff'} 

class Plotter(Printer):

	def __init__(self, block_on_finish = False):
		self.plot_index = 1
		self.pass_index = 0
		self.ylimit_min = 0
		self.ylimit_max = -10
		self.block_on_finish = block_on_finish
		#plt.xkcd()
		
	
	def __del__(self):
		pass

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

		print(title)

		fig = plt.figure()
		fig.set_size_inches(8.5, 6)
		ax = fig.gca(ylabel=quantity_description)

		data.plot(title = title, ax = ax, x_compat=False,  linewidth=2,
		 color = [colors.get(x, 'Purple') for x in data.columns])
		ax.set_xlabel('')
		ax.legend(loc='upper left')
		#plt.legend(handles=[line1], loc='upper left')
		if (self.ylimit_max > - 1):
			ax.set_ylim(ymin = self.ylimit_min, ymax = self.ylimit_max)
		else:
			autoscale = ax.get_ylim()
			ax.set_ylim(ymin = 0, ymax = autoscale[1])

		self.plot_index += 1
		return ax

	def clean_plot(self, ax):
		ax.set_xlabel('')
		ax.legend(loc='upper left')

	def finish_up(self):
		self.pass_index += 1
		plt.show(block = self.block_on_finish)