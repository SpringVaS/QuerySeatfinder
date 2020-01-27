from datamodel import Model
from servercomm import URL
from parameterui import ViewController
from excelprinter import ExcelPrinter
from plotting import Plotter

if __name__ == "__main__":
	excelPrinter = ExcelPrinter('data.xlsx')
	plotter = Plotter()
	m = Model(URL, plotter)
	c = ViewController(m)