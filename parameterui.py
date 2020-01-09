import queryseatfinder as qsf

import tkinter as tk
from tkinter import ttk
import tkcalendar
import mytkwidgets as mw

import datetime as dt
from datetime import datetime

import tkinter.font as tkFont

import pandas as pd
import numpy as np

class ViewController(qsf.Observer):
	
	def __init__(self, model):
		self.model = model
		# subscribe to model updates
		self.model.attach(self)
		self.__build_gui()

	def __del__(self):
		# unsubscribe from model updates
		self.model.detach(self)

	def update(self, subject: qsf.Subject) -> None:
		print("ConcreteObserverA: Reacted to the event " + str(self.model.get_progress()))
		self.progressbar["value"] = self.model.get_progress()
		self.progressbar.update()

	def __build_gui(self):
		self.window = tk.Tk()
		self.window.title("Query Seatfinder")

		self.gui_pane = tk.Frame(self.window)
		self.gui_pane.rowconfigure(0, weight=1)
		self.gui_pane.columnconfigure(0, weight=1)

		self.label = tk.Label(self.window, text = "Select a period of time for the query", font = ('Segoe UI', 12))
		self.label.pack(padx = 10, pady = 10, side = tk.TOP, anchor= tk.W)
		self.button_send_query = tk.Button(self.gui_pane, text = 'OK', command = self.button_pressed)

		self.__interval_selection()

		self.label_from	= tk.Label(self.gui_pane, text = "from:")
		self.label_to	= tk.Label(self.gui_pane, text = "to:")

		self.dateentry_from = tkcalendar.DateEntry(self.gui_pane, width=12, background='darkblue', 
			foreground='white', borderwidth=2)
		self.dateentry_to = tkcalendar.DateEntry(self.gui_pane, width=12, background='darkblue', 
			foreground='white', borderwidth=2)

		self.timeentry_from = mw.TimeEntry(self.gui_pane)
		self.timeentry_to = mw.TimeEntry(self.gui_pane)
		
		self.progressbar = ttk.Progressbar(self.window, mode = 'determinate')
		self.progressbar["maximum"] = 100

	
		self.gui_pane.pack(fill=tk.X, expand=0)
		self.progressbar.pack(padx = 10, pady = 10, side = tk.BOTTOM, fill=tk.X, expand=0)

		self.timeentry_from.set_time(datetime.now() - dt.timedelta(hours = 2))
		self.timeentry_to.set_time(datetime.now())

		self.dateentry_from.set_date(self.dateentry_to.get_date() - dt.timedelta(days = 1))

		self.__layout()

		for widget in self.gui_pane.winfo_children():
			self.__change_font_size(widget, 12)

		self.window.mainloop()

	def __interval_selection(self):
		self.resampling_intervals = {	'15 min'	: '15Min', 
										'30 min'	: '30Min',
										'1 hour' 	: '1H',
										'2 hours'	: '2H',
										'1 day'		: '1D',
										'1 week'	: '1W'}
		self.label_interval = tk.Label(self.gui_pane, text='sampling interval:')
		self.interval_selection = ttk.Combobox(self.gui_pane, 
			values = list(self.resampling_intervals.keys()))
		self.interval_selection.current(0)

	def __layout(self):
		#self.label.grid(row = 0, columnspan = 2, padx = 10, pady = 10, sticky = 'w')
		self.button_send_query.grid(row = 4, column = 1, columnspan = 2, padx = 10, pady = 10, sticky = 'we')
		self.label_from.grid(row = 1, column = 0, padx = 10, pady = 10,sticky = 'w')
		self.dateentry_from.grid(row = 1, column = 1, padx = 10, pady = 10,sticky = 'w')
		self.timeentry_from.grid(row = 1, column = 2, padx = 10, pady = 10,sticky = 'e')
		self.label_to.grid(row = 2, column = 0, padx = 10, pady = 10,sticky = 'w')
		self.dateentry_to.grid(row = 2, column = 1, padx = 10, pady = 10,sticky = 'w')
		self.timeentry_to.grid(row = 2, column = 2, padx = 10, pady = 10,sticky = 'e')

		self.label_interval.grid(row = 3, column = 0, padx = 10, pady = 10, sticky = 'w')
		self.interval_selection.grid(row = 3, column = 1, columnspan = 2, padx = 10, pady = 10, sticky = 'we')

		self.window.resizable(False, False)


	def button_pressed(self):

		# reset progressbar
		self.progressbar["value"] = 0
		self.progressbar.update()

		# gather datetime input

		time_period = self.__get_entered_time_period()
		self.model.set_resampling_interval(self.resampling_intervals[self.interval_selection.get()])

		print(time_period[0])
		print(time_period[-1])

		occupancy = self.model.get_info('seatestimate',time_period[0], time_period[-1])
		self.model.write_to_excel(occupancy, "Seat Occupancy")

	def __get_entered_time_period(self):
		date_entered_from 	= self.dateentry_from.get_date()
		time_entered_from 	= self.timeentry_from.get_time()

		date_entered_to		= self.dateentry_to.get_date()
		time_entered_to		= self.timeentry_to.get_time()

		timebegin = pd.Timestamp(str(date_entered_from) + ' ' + time_entered_from)
		timeend   = pd.Timestamp(str(date_entered_to)   + ' ' + time_entered_to)
		return (timebegin, timeend)

	def __change_font_size(self, tk_elem, font_size):
		new_font = tkFont.Font(font = tk_elem.cget("font"))
		size = new_font.actual()["size"]
		new_font.configure(size=font_size)
		tk_elem.configure(font=new_font)


if __name__ == "__main__":
	m = qsf.Model(qsf.URL, 'data.xlsx')
	c = ViewController(m)