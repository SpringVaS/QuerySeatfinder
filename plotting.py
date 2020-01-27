from printers import Printer

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class Plotter(Printer):

	def __init__(self):
		self.plot_index = 1
	
	def __del__(self):
		plt.close()

	def export_lib_metadata(self, metadata):
		pass

	def export_data(self, data, name):
		"""
			reverse order of dataframe for plot. Original begins with newest values
		"""
		plt.figure(0)
		data.sort_index(ascending=True)
		#data[::-1] 
		print(name)
		data.plot(title = name)

	def finish_up(self):
		plt.show(block = False)