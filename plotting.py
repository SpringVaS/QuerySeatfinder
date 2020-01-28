from printers import Printer

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class Plotter(Printer):

	def __init__(self):
		self.plot_index = 1
		self.pass_index = 0
	
	def __del__(self):
		plt.close()

	def export_lib_metadata(self, metadata):
		pass

	def set_ylimits(self,ylimit_min, ylimit_max):
		self.ylimit_min = ylimit_min
		self.ylimit_max = ylimit_max

	def export_data(self, data, title, quantity_description):
		"""
			reverse order of dataframe for plot. Original begins with newest values
		"""
		data.sort_index(ascending=True)
		#data[::-1] 
		print(title)

		fig = plt.figure()
		ax = fig.gca(ylabel=quantity_description)
		if (self.ylimit_max > - 1):
			plt.ylim(self.ylimit_min, self.ylimit_max)
		data.plot(title = title, ax = ax)
		self.plot_index += 1

	def finish_up(self):
		self.pass_index += 1
		plt.show(block = False)