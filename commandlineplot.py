import datamodel as dm
from servercomm import URL
from parameterui import ViewController
from excelprinter import ExcelPrinter
from plotting import Plotter, colors
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

import seaborn as sns

from openpyxl import Workbook, load_workbook



import datetime as dt
import pandas as pd

from datetime import datetime

class CommandLineController(dm.Observer):
	def __init__(self, model):
		self.model = model
		# subscribe to model updates
		self.model.attach(self)

	def update(self, subject: dm.Subject) -> None:
		print(self.model.get_progress())

	def save_data_to_disc(self, timebegin, timeend, filename):
		occupancy = self.model.get_info('seatestimate', timebegin, timeend)

		occupancy.to_pickle(path=filename,protocol=2)

	def mean_much_data(self, filename):
		occupancy = pd.read_pickle(filename);
		occupancy = occupancy[occupancy.index < pd.Timestamp(year=2020, month=1, day=1)]
		occupancy = occupancy[occupancy.index >= pd.Timestamp(year=2015, month=1, day=1)]

		pressure = self.model.data_processor.compute_pressure(occupancy)
		pressure = pressure[self.model.all_libs]
		#pressure = pressure.mean(axis=1)
		#pressure = pressure.reset_index(name = "All").set_index(['timestamp'])


		print(occupancy)

		sum_occupancy = occupancy.sum(axis=1)
		sum_occupancy = sum_occupancy.reset_index(name = "All").set_index(['timestamp'])

		grouped = sum_occupancy.groupby([sum_occupancy.index.month, sum_occupancy.index.day])

		avg_data = grouped.mean()

		datetimeindex = [pd.Timestamp(year = 1972, month=m, day=d) for (m, d) in avg_data.index]

		idx = pd.DatetimeIndex(datetimeindex)

		avg_data = pd.DataFrame(data = avg_data.values, index=idx, columns=['All'])

		avg_data = avg_data.resample('7D').mean()

		print(avg_data)

		max_points = avg_data.nlargest(2, ['All'])

		print(max_points)

		ax = (self.model.printer.export_data(avg_data,
			"Mittelwert belegter Sitzplätze aller Bibliotheken auf dem Campus: 2015-2019", "Anzahl belegter Sitzplätze"))

		#max_points.plot(ax=ax, marker='o', markersize=8, linestyle = 'None', color = [colors.get(x, 'Red') for x in max_points.columns], legend=False)


		self.model.printer.clean_plot(ax)

		ax.legend(['All'],loc='upper right')

		self.model.printer.finish_up()


	def week_overview(self, filename):
		occupancy = pd.read_pickle(filename);
		occupancy = occupancy[occupancy.index < pd.Timestamp(year=2020, month=1, day=1)]
		occupancy = occupancy[occupancy.index >= pd.Timestamp(year=2015, month=1, day=1)]

		pressure = self.model.data_processor.compute_grouped_pressure(occupancy)

		sum_occupancy = occupancy.sum(axis=1)
		sum_occupancy = sum_occupancy.reset_index(name = "All").set_index(['timestamp'])

		grouped = pressure.groupby([pressure.index.week, pressure.index.weekday, 
									pressure.index.hour, pressure.index.minute])
		avg_data = grouped.mean()
		for data in avg_data.groupby(level=0):
			kw = data[0]
			df = data[1]
			idx = [pd.Timedelta(days=wd, hours=h, minutes = minute) for (w, wd, h, minute) in df.index]
			df_reindexed = pd.DataFrame(data = df.values, index=idx, columns = df.columns)
			#print(df.max())
			fig = plt.figure(figsize=(11, 6))
			ax = sns.heatmap(df_reindexed.transpose(), xticklabels=96, square=False, 
				cmap='Spectral_r', vmin = 0, vmax = 1, cbar_kws={'label': 'Anteil belegter Sitzplätze'})
			
			diff = (ax.get_xticks()[1] - ax.get_xticks()[0]) / 2
			ax.set_xticks(ax.get_xticks() + diff, minor=True)
			ax.set_xticks(np.append(ax.get_xticks(), 
						ax.get_xticks()[len(ax.get_xticks()) - 1] + 2 * diff - (diff / (48))), minor=False)
			ax.set_xticklabels(['MO', 'DI', 'MI', 'DO', 'FR', 'SA', 'SO'], rotation=0, minor=True)
			ax.set_xticklabels([], minor=False)
			for tick in ax.xaxis.get_minor_ticks():
				tick.tick1line.set_markersize(0)
				tick.tick2line.set_markersize(0)
			ax.set_yticklabels(ax.get_yticklabels(), rotation=0, va = 'center')
			plt.savefig('heatmaps/kw{0:02d}.png'.format(kw), dpi=300)
			plt.close()

		#self.model.printer.finish_up()

	def __get_average_by_week(self, data):
		grouped = data.groupby([data.index.week])
		avg_data = grouped.mean()
		return avg_data


	def __get_yearly_average(self, data):
		
		grouped = data.groupby([data.index.month, data.index.day, data.index.hour, data.index.minute])

		avg_data = grouped.mean()

		datetimeindex = [pd.Timestamp(year = 1972, month=m, day=d, hour = h, minute = minute) for (m, d, h, minute) in avg_data.index]

		idx = pd.DatetimeIndex(datetimeindex)

		avg_data = pd.DataFrame(data = avg_data.values, index=idx, columns = avg_data.columns)

		return avg_data

	def large(self, filename):
		occupancy = pd.read_pickle(filename);

		sum_occupancy = occupancy.sum(axis=1)

		sum_occupancy = sum_occupancy.resample('1W').mean()

		max_value = sum_occupancy.max()
		sum_occupancy = sum_occupancy.reset_index(name = "All").set_index(['timestamp'])
		maxpoints = sum_occupancy[sum_occupancy.values == max_value]

		max_values = sum_occupancy.nlargest(5, ['All'])

		print(max_values)


		ax=self.model.printer.export_data(sum_occupancy, "Wochenmittel alle Bibs" , 
			"Anzahl belegter Sitzplätze")

		#plt.scatter(x = max_values.index, y = max_values.values, color = "Red", s= 150, label = 'jaa')

		maxpoints.plot(ax=ax, marker='o', markersize=8, linestyle = 'None', color = [colors.get(x, 'Red') for x in maxpoints.columns], legend=False)


		self.model.printer.clean_plot(ax)

		ax.legend(['All'],loc='upper left')

		self.model.printer.finish_up()


	def local_editing(self, filename):
		occupancy = pd.read_pickle(filename);
		occupancy = occupancy[occupancy.index < pd.Timestamp(year=2020, month=1, day=1)]
		occupancy = occupancy[occupancy.index >= pd.Timestamp(year=2015, month=1, day=1)]

		sum_occupancy = occupancy.sum(axis=1)
		sum_occupancy = sum_occupancy.reset_index(name = "All").set_index(['timestamp'])

		avg_data = self.__get_average_by_week(sum_occupancy)

		print(avg_data.nlargest(5, ['All']))

		ax = (self.model.printer.export_data(avg_data,
			"Mittelwert belegter Sitzplätze aller Bibliotheken auf dem Campus: 2015-2019", "Anzahl belegter Sitzplätze"))


		
		self.model.printer.finish_up()


if __name__ == "__main__":
	printer = Plotter(True)
	m = dm.Model(URL, printer)
	c = CommandLineController(m)

	#c.save_data_to_disc(pd.Timestamp("2014-01-01 00:00:00"), pd.       Timestamp("2020-01-31 00:00:00"), 'data.pkl')

	#c.local_editing('data.pkl')
	#c.week_overview('data.pkl')
	#c.mean_much_data('data.pkl')
	c.local_editing('data.pkl')