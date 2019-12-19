import queryseatfinder as qsf

import tkinter as tk
from tkinter import ttk
import tkcalendar
import mytkwidgets as mw

import pandas as pd
import numpy as np

class ViewController(qsf.Observer):
	
	def __init__(self, model):
		self.model = model
		self.model.attach(self)
		self.__buildGUI()

	def update(self, subject: qsf.Subject) -> None:
		print("ConcreteObserverA: Reacted to the event " + str(self.model.getQueryProgess()))
		self.progressbar["value"] = self.model.getQueryProgess()
		self.progressbar.update()

	def __buildGUI(self):
		self.window = tk.Tk()
		self.window.title("Query Seatfinder")

		guiPane = tk.Frame(self.window)

		label = tk.Label(guiPane, text = "Select a period of time", font = ('Segoe UI', 12))
		label.grid(row = 0, columnspan = 2, padx = 10, pady = 10)
		button_send_query = tk.Button(guiPane, text = 'OK', command = self.buttonPressed)
		button_send_query.grid(row = 3, column = 0, columnspan = 2, padx = 10, pady = 10, sticky = 'we')

		self.dateEntryFrom = tkcalendar.DateEntry(guiPane, width=12, background='darkblue', 
			foreground='white', borderwidth=2, font = ('Segoe UI', 12))
		self.dateEntryTo = tkcalendar.DateEntry(guiPane, width=12, background='darkblue', 
			foreground='white', borderwidth=2, font = ('Segoe UI', 12))

		self.timeEntryFrom = mw.TimeEntry(guiPane, font = ('Segoe UI', 12))
		self.timeEntryTo = mw.TimeEntry(guiPane, font = ('Segoe UI', 12))
		
		self.progressbar = ttk.Progressbar(guiPane)

		self.progressbar["maximum"] = 100
		#self.progressbar.after(500, self.progress())

		self.dateEntryFrom.grid(row = 1, column = 0, padx = 10, pady = 10)
		self.timeEntryFrom.grid(row = 1, column = 1, padx = 10, pady = 10)
		self.dateEntryTo.grid(row = 2, column = 0, padx = 10, pady = 10)
		self.timeEntryTo.grid(row = 2, column = 1, padx = 10, pady = 10)
		self.progressbar.grid(row = 4, column = 0, columnspan = 2, padx = 10, pady = 10, sticky = 'we')

		guiPane.pack()

		self.window.mainloop()

	def buttonPressed(self):

		self.progressbar["value"] = 0
		self.progressbar.update()

		timebegin = pd.Timestamp(str(self.dateEntryFrom.get_date()) + ' ' + self.timeEntryFrom.get_time())
		timeend   = pd.Timestamp(str(self.dateEntryTo.get_date()) + ' ' + self.timeEntryTo.get_time())

		print(timebegin)
		print(timeend)

		occupancy = self.model.getInfo('seatestimate',timebegin, timeend)
		self.model.writeInfoToExcel(occupancy, "Seat Occupancy")


if __name__ == "__main__":
	m = qsf.Model(qsf.URL, 'data.xlsx')
	c = ViewController(m)