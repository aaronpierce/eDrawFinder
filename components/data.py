import os

class Data():

	def __init__(self):
		self.app_data = os.getenv('LOCALAPPDATA')
		self.app_data_path = os.path.join(self.app_data, 'eDrawingFinder')
		self.log_path = os.path.join(self.app_data_path, 'eDrawLog.log')
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
