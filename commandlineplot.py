import datamodel as dm
from servercomm import URL
from parameterui import ViewController
from excelprinter import ExcelPrinter
from plotting import Plotter, colors
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt


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

		pressure = self.model.data_processor.compute_pressure(occupancy)
		pressure = pressure[self.model.all_libs]
		#pressure = pressure.mean(axis=1)
		#pressure = pressure.reset_index(name = "All").set_index(['timestamp'])


		print(occupancy)

		sum_occupancy = occupancy.sum(axis=1)
		sum_occupancy = sum_occupancy.reset_index(name = "All").set_index(['timestamp'])

		print(pd.to_timedelta(pd.Timestamp(year=2015, month=1, day=1) - pd.Timestamp(year=1970, month=1, day=1)))


		whole = pd.DataFrame()
		
		for i in range(2015, 2020):
			tdoffset =pd.to_timedelta(pd.Timestamp(year=i, month=1, day=1) - pd.Timestamp(year=1970, month=1, day=1))
			mean_mod_year = sum_occupancy[sum_occupancy.index.year == i].shift(freq=-tdoffset)
			whole = whole.append(mean_mod_year)


		whole = whole.groupby(whole.index).mean()

		plotdata = whole.resample('1D', label='left').mean()
		#plotdata = whole.resample('7D', label='left').mean()

		#plotdata = plotdata.resample('1D').interpolate()

		print(plotdata)
	

		#plotdata = plotdata.resample('1D').interpolate()

		self.model.printer.clean_plot(self.model.printer.export_data(plotdata,
			"Mittelwert belegter Sitzplätze aller Bibliotheken auf dem Campus: 2015-2019", "Anzahl belegter Sitzplätze"))

		self.model.printer.finish_up()


	def week_overview(self, filename):
		occupancy = pd.read_pickle(filename);

		occupancy = occupancy[occupancy.index < pd.Timestamp(year=2020, month=1, day=1)]

		pressure = self.model.data_processor.compute_grouped_pressure(occupancy)
		#pressure = pressure[self.model.all_libs]
		#pressure = pressure.mean(axis=1)
		#pressure = pressure.reset_index(name = "All").set_index(['timestamp'])

		#pressure = pd.merge(pressure[(self.model.slibs)].sort_index(axis=1)

		whole = pd.DataFrame()

		for i in range(2015, 2020):
			tdoffset =pd.to_timedelta(pd.Timestamp(year=i, month=1, day=1) - pd.Timestamp(year=1970, month=1, day=1))
			mean_mod_year = pressure[pressure.index.year == i].shift(freq=-tdoffset)
			whole = whole.append(mean_mod_year)

		whole = whole.loc['1970-01-15':'1970-03-15']
		whole = whole.groupby(whole.index).mean()

		print(whole)

		#self.model.printer.finish_up()



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
		#occupancy = pd.read_pickle(filename);

		self.model.set_resampling_interval('1D')

		occupancy = self.model.get_info('seatestimate', pd.Timestamp("2020-01-01 00:00:00"), pd.Timestamp("2020-01-31 00:00:00"))
		
		mainlib_pressure = self.model.data_processor.compute_mainlib_pressure(occupancy)
		speclib_pressure = self.model.data_processor.compute_speclibs_pressure(occupancy)
		mainlib_pressure_vs_speclib_pressure  = pd.merge(mainlib_pressure, speclib_pressure, on='timestamp')

		grouped_occupancy = self.model.grouped_seat_info(occupancy)

		sum_occupancy = grouped_occupancy.sum(axis = 1)
		max_value = sum_occupancy.max()

		print(sum_occupancy)
		print(max_value)

		maxpoints = grouped_occupancy[sum_occupancy.values == max_value]

		maxrel = mainlib_pressure_vs_speclib_pressure[sum_occupancy.values == max_value]

		print(maxpoints)

	
		#mask = grouped_occupancy.transform(lambda x: x==x.max()).astype('bool')
		#grouped_occupancy.loc[mask]

		pressure_ratio_description = "Anteil belegter Sitzplätze"
		"""
		self.printer.export_data(self.__grouped_seat_info(occupancy),
			"Absolute Anzahl belegter Sitzplätze in den Bibliotheken auf dem Campus",
			"Absolute Anzahl belegter Sitzplätze")
		"""
		self.model.printer.set_ylimits(0,-10)
		self.model.printer.export_data(mainlib_pressure, "Sitzplatzdruck in der Hauptbibliothek",
			pressure_ratio_description)
		self.model.printer.export_data(mainlib_pressure_vs_speclib_pressure,
			"Sitzplatzdruck in den Bibliotheken auf dem Campus", pressure_ratio_description)
		ax = self.model.printer.export_data(grouped_occupancy,
			"Absolute Anzahl belegter Sitzplätze in den Bibliotheken auf dem Campus",
			"Absolute Anzahl belegter Sitzplätze")
		#self.printer.export_data(mainlib_pressure_vs_speclib_pressure, "Pressure in campus libraries")

		maxpoints.plot(ax=ax, marker='o', markersize=8, linestyle = 'None', color = [colors.get(x, 'Red') for x in maxpoints.columns], legend=False)


		for tick in ax.xaxis.get_minor_ticks():
			tick.label1.set_horizontalalignment('left')
		
		self.model.printer.finish_up()


if __name__ == "__main__":
	printer = Plotter(True)
	m = dm.Model(URL, printer)
	c = CommandLineController(m)

	#c.save_data_to_disc(pd.Timestamp("2014-01-01 00:00:00"), pd.		Timestamp("2020-01-31 00:00:00"), 'data.pkl')

	#c.local_editing('data.pkl')
	c.week_overview('data.pkl')