import queryseatfinder as qsf

import tkinter
from tkinter import ttk
import tkcalendar

import pandas as pd
import numpy as np

class ViewController(object):
	
	def __init__(self, model):
		self.model = model
		self.__buildGUI()

	def __buildGUI(self):
		self.window = tkinter.Tk()
		self.window.title("Query Seatfinder")
		self.window.geometry('400x640')

		label = tkinter.Label(self.window, text = "Please enter a range", font = ('Segoe UI', 18))
		label.grid(row = 0, column = 0)
		button_send_query = tkinter.Button(self.window, text = 'OK', command = self.buttonPressed)
		button_send_query.grid(row = 2, column = 0)

		dateFrom = tkcalendar.DateEntry(self.window, width=12, background='darkblue', 
			foreground='white', borderwidth=2)
		dateFrom.grid(row = 1, column = 0)

		dateTo = tkcalendar.DateEntry(self.window, width=12, background='darkblue', 
			foreground='white', borderwidth=2)

		dateTo.grid(row = 1, column = 1)

		self.window.mainloop()


	def buttonPressed(self):
		timebegin = pd.Timestamp('2018-10-15 07:00:00')
		timeend   = pd.Timestamp('2018-10-15 22:15:00')

		occupancy = self.model.getInfo('seatestimate',timebegin, timeend)
		self.model.writeInfoToExcel(occupancy, "Seat Occupancy")


m = qsf.Model(qsf.URL, 'data.xlsx')

c = ViewController(m)
