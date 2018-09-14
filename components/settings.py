import yaml

import tkinter as tk
from tkinter import ttk

VERSION = '1.7.0'

class Settings():

	def __init__(self, core_app):
		self.app = core_app
		self.yaml = self.app.data.config_path
		
		self.default_settings = {'fullfilepath': 'True'}

		self.app.data.check_config(self.default_settings)
		self.compile_settings()

	def display(self, core_app):
		self.frame = tk.Toplevel()
		self.frame.wm_title('Settings')
		
		self.frame.iconbitmap(self.app.data.resource_path('components\\resources\\settings.ico'))

		self.titleLabel = ttk.Label(self.frame, text="--Optional Settings--", font=("Default", 10))
		self.titleLabel.grid(row=0, column=0, columnspan=10, padx=10, pady=1)

		self.fullfilepath_bool = tk.IntVar()
		self.fullfilepath_bool.set(self.fullfilepath)
		self.resultPathToggle = ttk.Checkbutton(self.frame, text='Show Full Filepath', offvalue=0, onvalue=1, variable=self.fullfilepath_bool)
		self.resultPathToggle.grid(row=1, column=0, columnspan=10, padx=10, pady=1)

		self.saveButton = ttk.Button(self.frame, text='Save', command=self.save_settings)
		self.saveButton.grid(row=2, column=3, columnspan=2, padx=10, pady=4)

		self.cancelButton = ttk.Button(self.frame, text='Cancel', command=self.frame.destroy)
		self.cancelButton.grid(row=2, column=5, columnspan=2, padx=10, pady=4)

	def compile_settings(self):
		self.inplace_settings = self.load_settings()
		self.fullfilepath = self.inplace_settings['fullfilepath']

	def save_settings(self):
		config = self.load_settings()
		config['fullfilepath'] = self.fullfilepath_bool.get()

		with open(self.yaml, 'w+') as file:
			yaml.dump(config, file, default_flow_style=False)

		self.compile_settings()

		self.app.log.writter.info('Confuration Save Succesful.')
		self.app.log.writter.info(f'{config}')

		self.frame.destroy()

	def load_settings(self):
		with open(self.yaml) as file:
			config = yaml.load(file)
		return config

	def test(self):
		print(self.fullfilepath)