import win32com.client
import win32api
import os
from time import sleep as time_sleep
from codecs import decode

class Converter():
	def __init__(self, core_app):
		self.app = core_app
		self.dll = 'KergeriabPQNP.ergeriabPQNP'[::-1]
		self.converter = win32com.client.Dispatch(decode(self.dll, '31_tor'[::-1]))

	def toPDF(self):
		src_path = self.app.selectedDrawing.get()
		dest_file = src_path.split('\\')[-1].split('.')[0] + '.pdf'
		dest_path = os.path.join(self.app.data.temp_files, dest_file)

		self.converter.convert(src_path, dest_path, f'-WithoutBorder:on -c PDF ')
		
		return dest_path

	def printPDF(self, src):
		win32api.ShellExecute(0, "print", src, None, ".", 0)
		errorRaise = True
		time_sleep(2)
		print('sleeping')
		while errorRaise:
			try:
				os.remove(src)
				errorRaise = False
			except:
				time_sleep(1)
				print('slept after error')
			finally:
				os.system("TASKKILL /F /IM FoxitReader.exe")