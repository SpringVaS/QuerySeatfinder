import datamodel as dm

import tkinter as tk
from tkinter import ttk
import tkcalendar
import mytkwidgets as mw

import datetime as dt
from datetime import datetime

import tkinter.font as tkFont

from pandas import Timedelta, Timestamp

class ViewController(dm.Observer):
	
	def __init__(self, model):
		self.model = model
		# subscribe to model updates
		self.model.attach(self)
		self.__build_gui()

	def __del__(self):
		# unsubscribe from model updates
		self.model.detach(self)

	def update(self, subject: dm.Subject) -> None:
		self.progressbar["value"] = self.model.get_progress()
		self.progressbar.update()

	def __build_gui(self):
		self.window = tk.Tk()
		self.window.title("Query Seatfinder")

		self.gui_pane = tk.Frame(self.window)
		self.gui_pane.rowconfigure(0, weight=1)
		self.gui_pane.columnconfigure(0, weight=1)

		self.label = tk.Label(self.window, text = "Select a period of time for the query")
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

		self.__mean_option_selection()

		self.gui_pane.pack(fill=tk.X, expand=0)
		self.progressbar.pack(padx = 10, pady = 10, side = tk.BOTTOM, fill=tk.X, expand=0)


		self.timeentry_from.set_time(datetime.now() - dt.timedelta(hours = 2))
		self.timeentry_to.set_time(datetime.now())

		self.dateentry_from.set_date(self.dateentry_to.get_date() - dt.timedelta(days = 1))

		self.__layout()

		for widget in self.gui_pane.winfo_children():
			self.__change_font_size(widget, 12)
		self.__change_font_size(self.label, 12)

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
		self.interval_selection.bind("<<ComboboxSelected>>", self.interval_selected)
		self.interval_selection.current(0)

	def interval_selected(self, event):
		if (Timedelta(self.resampling_intervals[self.interval_selection.get()]) > Timedelta('2H')):
			self.opt_btns[0].select()
			self.opt_btns[1].config(state=tk.DISABLED)
		else:
			self.opt_btns[1].config(state=tk.NORMAL)


	def __mean_option_selection(self):
		options = self.model.get_sampling_method_options()
		self.selected_option = tk.StringVar()
		self.selected_option.set(value =options[0])
		self.mean_option_label = tk.Label(self.gui_pane, text='aggregation method:')
		self.opt_btns = []
		col = 1
		for o in options:
			bt = tk.Radiobutton(self.gui_pane, text = o, variable = self.selected_option, 
				value = o)
			bt.grid(row=4, column=col,padx = 10, pady = 10,sticky = 'w')
			self.__change_font_size(bt, 12)
			self.opt_btns.append(bt)
			col +=1

	def __layout(self):
		#self.label.grid(row = 0, columnspan = 2, padx = 10, pady = 10, sticky = 'w')
		self.button_send_query.grid(row = 5, column = 1, columnspan = 2, padx = 10, pady = 10, sticky = 'we')
		self.label_from.grid(row = 1, column = 0, padx = 10, pady = 10,sticky = 'w')
		self.dateentry_from.grid(row = 1, column = 1, padx = 10, pady = 10,sticky = 'w')
		self.timeentry_from.grid(row = 1, column = 2, padx = 10, pady = 10,sticky = 'e')
		self.label_to.grid(row = 2, column = 0, padx = 10, pady = 10,sticky = 'w')
		self.dateentry_to.grid(row = 2, column = 1, padx = 10, pady = 10,sticky = 'w')
		self.timeentry_to.grid(row = 2, column = 2, padx = 10, pady = 10,sticky = 'e')

		self.label_interval.grid(row = 3, column = 0, padx = 10, pady = 10, sticky = 'w')
		self.interval_selection.grid(row = 3, column = 1, columnspan = 2, padx = 10, pady = 10, sticky = 'we')
		self.mean_option_label.grid(row = 4, column = 0, padx = 10, pady = 10, sticky = 'w')

		self.window.resizable(False, False)


	def button_pressed(self):

		# reset progressbar
		self.progressbar["value"] = 0
		self.progressbar.update()

		# gather datetime input

		time_period = self.__get_entered_time_period()
		self.model.set_resampling_interval(self.resampling_intervals[self.interval_selection.get()])
		self.model.set_sampling_method(self.selected_option.get())

		print(time_period[0])
		print(time_period[-1])

		self.model.output_data(time_period[0], time_period[-1])

	def __get_entered_time_period(self):
		date_entered_from 	= self.dateentry_from.get_date()
		time_entered_from 	= self.timeentry_from.get_time()

		date_entered_to		= self.dateentry_to.get_date()
		time_entered_to		= self.timeentry_to.get_time()

		timebegin = Timestamp(str(date_entered_from) + ' ' + time_entered_from)
		timeend   = Timestamp(str(date_entered_to)   + ' ' + time_entered_to)
		return (timebegin, timeend)

	def __change_font_size(self, tk_elem, font_size):
		new_font = tkFont.Font(font = tk_elem.cget("font"))
		size = new_font.actual()["size"]
		new_font.configure(size=font_size)
		tk_elem.configure(font=new_font)
