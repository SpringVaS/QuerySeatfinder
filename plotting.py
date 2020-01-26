from printers import Printer

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class Plotter(Printer):

	def __init__(self):
		pass

	def __del__(self):
		pass
		#plt.show(block=False)

	def export_lib_metadata(self, metadata):
		pass

	def export_data(self, data, name):
		data.sort_index(ascending=True)
		data.plot()

	def finish_up(self):
		plt.show(block = False)