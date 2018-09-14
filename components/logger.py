import logging

VERSION = '1.6.7'
LOG_ = { 
	'disabled': logging.NOTSET,
	'debug': logging.DEBUG,
	'info': logging.INFO,
	'warning': logging.WARNING,
	'error': logging.ERROR,
	'critical': logging.CRITICAL
      	}
LOGLEVEL = LOG_['debug']

class Logger():
	def __init__(self, d):
		self.data = d
		self.writter = logging.getLogger('main')
		self.writter.setLevel(LOGLEVEL)
		self.filehandler = logging.FileHandler(self.data.log_path)
		self.consolehandler = logging.StreamHandler()
		self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m-%d-%Y %I:%M:%S%p')
		self.filehandler.setFormatter(self.formatter)
		self.consolehandler.setFormatter(self.formatter)
		if self.writter.level >= LOG_['warning']:
			self.writter.addHandler(self.filehandler)
		if self.writter.level < LOG_['warning']:
			self.writter.addHandler(self.consolehandler)