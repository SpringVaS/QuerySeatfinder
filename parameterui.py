import queryseatfinder as qsf

import tkinter as tk
from tkinter import ttk
import tkcalendar
import mytkwidgets as mw

import tkinter.font as tkFont

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
		guiPane.rowconfigure(0, weight=1)
		guiPane.columnconfigure(0, weight=1)

		label = tk.Label(guiPane, text = "Select a period of time", font = ('Segoe UI', 12))
		label.grid(row = 0, columnspan = 2, padx = 10, pady = 10, sticky = 'w')
		button_send_query = tk.Button(guiPane, text = 'OK', command = self.buttonPressed)
		button_send_query.grid(row = 3, column = 0, columnspan = 2, padx = 10, pady = 10, sticky = 'we')

		self.dateEntryFrom = tkcalendar.DateEntry(guiPane, width=12, background='darkblue', 
			foreground='white', borderwidth=2)
		self.dateEntryTo = tkcalendar.DateEntry(guiPane, width=12, background='darkblue', 
			foreground='white', borderwidth=2)

		self.timeEntryFrom = mw.TimeEntry(guiPane)
		self.timeEntryTo = mw.TimeEntry(guiPane)
		
		self.progressbar = ttk.Progressbar(self.window)

		self.progressbar["maximum"] = 100
		#self.progressbar.after(500, self.progress())

		self.dateEntryFrom.grid(row = 1, column = 0, padx = 10, pady = 10,sticky = 'w')
		self.timeEntryFrom.grid(row = 1, column = 1, padx = 10, pady = 10,sticky = 'e')
		self.dateEntryTo.grid(row = 2, column = 0, padx = 10, pady = 10,sticky = 'w')
		self.timeEntryTo.grid(row = 2, column = 1, padx = 10, pady = 10,sticky = 'e')
		#self.progressbar.grid(row = 4, column = 0, columnspan = 2, padx = 10, pady = 10, sticky = 'we')

		guiPane.pack(fill=tk.BOTH, expand=1)
		self.progressbar.pack(padx = 10, pady = 10, fill=tk.X, expand=1)

		for widget in guiPane.winfo_children():
			self.__changeFontSize(widget, 12)

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

	def __changeFontSize(self, tk_elem, font_size):
		new_font = tkFont.Font(font = tk_elem.cget("font"))
		size = new_font.actual()["size"]
		new_font.configure(size=font_size)
		tk_elem.configure(font=new_font)


if __name__ == "__main__":
	m = qsf.Model(qsf.URL, 'data.xlsx')
	c = ViewController(m)