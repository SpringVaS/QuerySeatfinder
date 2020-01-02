import tkinter as tk
from datetime import datetime
# found at https://stackoverflow.com/questions/57034118/time-picker-for-tkinter 19.12.2019

class TimeEntry(tk.Frame):
    def __init__(self, parent, font = None):
        super().__init__(parent)
        self.hourstr=tk.StringVar(self,'10')
        # TO DO sanitize entry
        self.hour = tk.Spinbox(self,from_=0,to=23,wrap=True,textvariable=self.hourstr,width=2,state="readonly",
            font = font, format="%02.0f")
        self.minstr=tk.StringVar(self,'30')
        self.minstr.trace("w",self.trace_var)
        self.last_value = ""
        self.min = tk.Spinbox(self,from_=0,to=59,wrap=True,textvariable=self.minstr,width=2,state="readonly",
            font = font, format="%02.0f")
        self.hour.grid()
        self.min.grid(row=0,column=1)

    def trace_var(self,*args):
        if self.last_value == "59" and self.minstr.get() == "00":
            self.hourstr.set((int(self.hourstr.get())+1) if self.hourstr.get() !="23" else 0)
            self.hour.config(format="%02.0f")
        elif self.last_value == "00" and self.minstr.get() == "59":
            self.hourstr.set((int(self.hourstr.get())-1) if self.hourstr.get() !="00" else 23)
            self.hour.config(format="%02.0f")
        self.last_value = self.minstr.get()

    def set_time(self, pTime):
        hours = pTime.strftime("%H")
        minutes = pTime.strftime("%M")
        self.hourstr.set(hours)
        self.minstr.set(minutes)


    def get_time(self):
        timestr = str(self.hourstr.get()) + ':' + str(self.minstr.get()) + ':00'
        return timestr

    def cget(self, option):
        return self.hour.cget(option)

    def configure(self, font):
        self.hour.configure(font = font)
        self.min.configure(font = font)