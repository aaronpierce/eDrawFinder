import os
import yaml
import sys
import errno
import winreg

from pathlib import Path

class Data():

	def __init__(self, core_app):
		self.app = core_app
		self.app_data = os.getenv('LOCALAPPDATA')
		self.app_data_path = os.path.join(self.app_data, 'eDrawingFinder')
		self.log_path = os.path.join(self.app_data_path, 'log.log')
		self.config_path = os.path.join(self.app_data_path, 'config.yaml')
		self.op_path = os.path.join(self.app_data_path, 'op_database.p')
		self.bm_path = os.path.join(self.app_data_path, 'bm_database.p')

		if not os.path.exists(self.app_data_path):
			try:
				os.makedirs(self.app_data_path)
			except OSError as exception:
				self.app_data_path = os.getcwd()
				if exception.errno != errno.EEXIST:
					raise

	def resource_path(self, relative_path):
		try:
			base_path = sys._MEIPASS
		except Exception:
			base_path = os.path.abspath(".")

		return os.path.join(base_path, relative_path)

	def check_config(self, defaults):
		if not os.path.exists(self.config_path):
			with open(self.config_path, 'w+') as file:
				yaml.dump(defaults, file, default_flow_style=False)

	def get_eDrawing_executable(self):
		
		try:
			key_local = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall')
			key_local_query = winreg.QueryInfoKey(key_local)

			for i in range(key_local_query[0]):
				tmp = winreg.OpenKey(key_local, winreg.EnumKey(key_local, i))
				try:
					location_check = winreg.QueryValueEx(tmp, r'InstallLocation')[0]
					if 'eDrawings' in location_check:
						location = location_check
				except:
					path = Path('.')

			files_in_location = os.listdir(location)
			path = Path(location, [app for app in files_in_location if app == 'eDrawings.exe'][0])

		except:
			path = Path('.')
			
		return path
