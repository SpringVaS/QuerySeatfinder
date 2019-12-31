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
		self.model.attach(self)
		self.__build_gui()

	def update(self, subject: qsf.Subject) -> None:
		print("ConcreteObserverA: Reacted to the event " + str(self.model.get_progress()))
		self.progressbar["value"] = self.model.get_progress()
		self.progressbar.update()

	def __build_gui(self):
		self.window = tk.Tk()
		self.window.title("Query Seatfinder")

		gui_pane = tk.Frame(self.window)
		gui_pane.rowconfigure(0, weight=1)
		gui_pane.columnconfigure(0, weight=1)

		label = tk.Label(gui_pane, text = "Select a period of time", font = ('Segoe UI', 12))
		label.grid(row = 0, columnspan = 2, padx = 10, pady = 10, sticky = 'w')
		button_send_query = tk.Button(gui_pane, text = 'OK', command = self.button_pressed)
		button_send_query.grid(row = 3, column = 0, columnspan = 2, padx = 10, pady = 10, sticky = 'we')

		self.dateentry_from = tkcalendar.DateEntry(gui_pane, width=12, background='darkblue', 
			foreground='white', borderwidth=2)
		self.dateentry_to = tkcalendar.DateEntry(gui_pane, width=12, background='darkblue', 
			foreground='white', borderwidth=2)

		self.timeentry_from = mw.TimeEntry(gui_pane)
		self.timeentry_to = mw.TimeEntry(gui_pane)
		
		self.progressbar = ttk.Progressbar(self.window, mode = 'determinate')
		self.progressbar["maximum"] = 100

		self.dateentry_from.grid(row = 1, column = 0, padx = 10, pady = 10,sticky = 'w')
		self.timeentry_from.grid(row = 1, column = 1, padx = 10, pady = 10,sticky = 'e')
		self.dateentry_to.grid(row = 2, column = 0, padx = 10, pady = 10,sticky = 'w')
		self.timeentry_to.grid(row = 2, column = 1, padx = 10, pady = 10,sticky = 'e')

		gui_pane.pack(fill=tk.BOTH, expand=1)
		self.progressbar.pack(padx = 10, pady = 10, fill=tk.X, expand=1)

		self.timeentry_from.set_time(datetime.now() - dt.timedelta(hours = 2))
		self.timeentry_to.set_time(datetime.now())

		self.dateentry_from.set_date(self.dateentry_to.get_date() - dt.timedelta(days = 1))

		for widget in gui_pane.winfo_children():
			self.__change_font_size(widget, 12)

		self.window.mainloop()

	def button_pressed(self):

		self.progressbar["value"] = 0
		self.progressbar.update()

		timebegin = pd.Timestamp(str(self.dateentry_from.get_date()) + ' ' + self.timeentry_from.get_time())
		timeend   = pd.Timestamp(str(self.dateentry_to.get_date()) + ' ' + self.timeentry_to.get_time())

		print(timebegin)
		print(timeend)

		occupancy = self.model.get_info('seatestimate',timebegin, timeend)
		self.model.write_to_excel(occupancy, "Seat Occupancy")

	def __change_font_size(self, tk_elem, font_size):
		new_font = tkFont.Font(font = tk_elem.cget("font"))
		size = new_font.actual()["size"]
		new_font.configure(size=font_size)
		tk_elem.configure(font=new_font)


if __name__ == "__main__":
	m = qsf.Model(qsf.URL, 'data.xlsx')
	c = ViewController(m)