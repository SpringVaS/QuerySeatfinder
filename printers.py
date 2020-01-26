from __future__ import annotations
from abc import ABC, abstractmethod

class Printer(ABC):
	
	@abstractmethod
	def export_lib_metadata(self, metadata):
		pass

	@abstractmethod
	def export_data(self, data, name):
		pass

	def set_lib_identifier(self, mainlib, slibs):
		self.mainlib = mainlib
		self.slibs = slibs

