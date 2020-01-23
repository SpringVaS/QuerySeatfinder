from datamodel import Model
from servercomm import URL
from parameterui import ViewController
import printers as pnt

if __name__ == "__main__":
	p = pnt.ExcelPrinter('data.xlsx')
	m = Model(URL, p)
	c = ViewController(m)