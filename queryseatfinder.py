from datamodel import Model
from servercomm import URL
from parameterui import ViewController
from excelprinter import ExcelPrinter

if __name__ == "__main__":
	p = ExcelPrinter('data.xlsx')
	m = Model(URL, p)
	c = ViewController(m)