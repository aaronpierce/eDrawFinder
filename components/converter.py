import win32com.client
import win32api
from os.path import join
from os import remove
import time

class Converter():
	def __init__(self, core_app):
		self.app = core_app
		self.converter = win32com.client.Dispatch("CADConverter.CADConverterX")

	def toPDF(self):
		src_path = self.app.selectedDrawing.get()
		dest_file = src_path.split('\\')[-1].split('.')[0] + '.pdf'
		dest_path = join(self.app.data.app_data_path, dest_file)

		self.converter.convert(src_path, dest_path, '-c PDF')

		return dest_path

	def printPDF(self, src):
		win32api.ShellExecute(0, "print", src, None, ".", 0)
		errorRaise = True
		time.sleep(2)
		print('sleeping')
		while errorRaise:
			try:
				remove(src)
				errorRaise = False
			except:
				time.sleep(1)
				print('sleeping after error')

	# Need to figure out timing for the wait to delete the printed file.
			
