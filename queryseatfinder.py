from datamodel import Model
from servercomm import URL
from parameterui import ViewController

if __name__ == "__main__":
	m = Model(URL, 'data.xlsx')
	c = ViewController(m)