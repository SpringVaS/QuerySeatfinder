from datamodel import Model
from servercomm import URL
from parameterui import ViewController
from excelprinter import ExcelPrinter
from plotting import Plotter

if __name__ == "__main__":
	ep = ExcelPrinter('data.xlsx')
	pp = Plotter()
	m = Model(URL, pp)
	c = ViewController(m)