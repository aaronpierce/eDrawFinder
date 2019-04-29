import logging

LOG_ = { 
	'disabled': logging.NOTSET,
	'debug': logging.DEBUG,
	'info': logging.INFO,
	'warning': logging.WARNING,
	'error': logging.ERROR,
	'critical': logging.CRITICAL
      	}
LOGLEVEL = LOG_['info']

class Logger():
	def __init__(self, core_app):
		self.data = core_app.data
		self.writter = logging.getLogger('main')
		self.writter.setLevel(LOGLEVEL)
		self.filehandler = logging.FileHandler(self.data.log_path)
		self.consolehandler = logging.StreamHandler()
		self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m-%d-%Y %I:%M:%S%p')
		self.filehandler.setFormatter(self.formatter)
		self.consolehandler.setFormatter(self.formatter)

		if self.writter.level == LOG_['debug']:
			self.writter.addHandler(self.consolehandler)
		if self.writter.level > LOG_['debug']:
			self.writter.addHandler(self.filehandler)