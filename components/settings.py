import yaml

import tkinter as tk
from tkinter import ttk

VERSION = '1.8.0'

class Settings():

	def __init__(self, core_app):
		self.app = core_app
		self.yaml = self.app.data.config_path
		
		self.default_settings = {'full_filepath': True,
								'auto_open': False}

		self.app.data.check_config(self.default_settings)
		self.compile_settings()
		self.settings_open = False


	def display(self):
		self.frame = tk.Toplevel()
		self.frame.wm_title('Settings')
		self.frame.resizable(False, False)
		
		self.frame.iconbitmap(self.app.data.resource_path('components\\resources\\settings.ico'))

		self.titleLabel = ttk.Label(self.frame, text="--Optional Settings--", font=("Default", 10))
		self.titleLabel.pack(side=tk.TOP, pady=4)

		self.auto_open_bool = tk.BooleanVar()
		self.auto_open_bool.set(self.auto_open)
		self.autoOpenToggle = ttk.Checkbutton(self.frame, text='Auto-Open First Result', offvalue=False, onvalue=True, variable=self.auto_open_bool)
		self.autoOpenToggle.pack(side=tk.TOP, anchor=tk.W, padx=10)

		self.full_filepath_bool = tk.BooleanVar()
		self.full_filepath_bool.set(self.full_filepath)
		self.resultPathToggle = ttk.Checkbutton(self.frame, text='Show Full Filepath', offvalue=False, onvalue=True, variable=self.full_filepath_bool)
		self.resultPathToggle.pack(side=tk.TOP, anchor=tk.W, padx=10)

		self.saveButton = ttk.Button(self.frame, text='Save', command=self.save_settings)
		self.saveButton.pack(side=tk.LEFT, padx=10, pady=6)

		self.cancelButton = ttk.Button(self.frame, text='Cancel', command=self.close_window)
		self.cancelButton.pack(side=tk.RIGHT, padx=10, pady=6)

		self.frame.protocol("WM_DELETE_WINDOW", self.close_window)

	def compile_settings(self):
		self.inplace_settings = self.load_settings()
		self.full_filepath = self.inplace_settings['full_filepath']
		self.auto_open = self.inplace_settings['auto_open']

	def save_settings(self):
		config = self.load_settings()
		config['full_filepath'] = self.full_filepath_bool.get()
		config['auto_open'] = self.auto_open_bool.get()

		with open(self.yaml, 'w+') as file:
			yaml.dump(config, file, default_flow_style=False)

		self.compile_settings()

		self.app.log.writter.info('Confuration Save Succesful.')
		self.app.log.writter.info(f'{config}')

		self.close_window()

	def load_settings(self):
		with open(self.yaml) as file:
			config = yaml.load(file)
		return config

	def close_window(self):
		self.app.log.writter.info('Settings window has been closed.')
		self.settings_open = False
		self.frame.destroy()

	def test(self):
		print(self.full_filepath)