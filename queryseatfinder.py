from datamodel import Model
from servercomm import URL
from parameterui import ViewController
from excelprinter import ExcelPrinter
from plotting import Plotter
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-p", "--plot",
                  action="store_true", dest="do_plot", default=False,
                  help="don't print status messages to stdout")


#def set_plot():
#	do_plot = True

if __name__ == "__main__":
	(options, args) = parser.parse_args()
	print(options)
	printer = 0
	if (options.do_plot):
		printer = Plotter()
	else:
		printer = ExcelPrinter('data.xlsx')
	m = Model(URL, printer)
	c = ViewController(m)