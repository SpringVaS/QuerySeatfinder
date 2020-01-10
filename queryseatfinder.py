from serverquerymodel import Model, URL
from parameterui import ViewController

if __name__ == "__main__":
	m = Model(URL, 'data.xlsx')
	c = ViewController(m)