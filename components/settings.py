import yaml

from pathlib import Path

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename

VERSION = '1.8.2'

class Settings():

	def __init__(self, core_app):
		self.app = core_app
		self.yaml = self.app.data.config_path
		
		self.default_settings = {'full_filepath': True,
								'auto_open': False,
								'open_with': '.'}

		self.app.data.check_config(self.default_settings)
		self.compile_settings()
		self.settings_open = False


	def display(self):
		self.frame = tk.Toplevel()
		self.frame.wm_title('Settings')
		self.frame.resizable(False, False)
		self.frame.grid_rowconfigure(1, weight=1)
		self.frame.iconbitmap(self.app.data.resource_path('components\\resources\\settings.ico'))

		self.titleSeperator= ttk.Separator(self.frame,)\
			.grid(row=0, columnspan=4, padx=10, pady=8, sticky=tk.EW)

		self.titleLabel= ttk.Label(self.frame, text='Optional Settings')\
			.grid(row=0, column=2, pady=10)

		self.auto_open_bool = tk.BooleanVar()
		self.auto_open_bool.set(self.auto_open)
		self.autoOpenToggle = ttk.Checkbutton(self.frame, text='Auto-Open First Result', offvalue=False, onvalue=True, variable=self.auto_open_bool)\
			.grid(row=1, column=1, columnspan=3, padx=60, sticky=tk.W)

		self.full_filepath_bool = tk.BooleanVar()
		self.full_filepath_bool.set(self.full_filepath)
		self.resultPathToggle = ttk.Checkbutton(self.frame, text='Show Full Filepath', offvalue=False, onvalue=True, variable=self.full_filepath_bool)\
			.grid(row=2, column=1, columnspan=3, padx=60, sticky=tk.W)			

		self.defaultProgramSeperator = ttk.Separator(self.frame,)\
			.grid(row=3, columnspan=4, padx=10, pady=8, sticky=tk.EW)

		self.defaultProgramLabel = ttk.Label(self.frame, text='Default eDrawing Program')\
			.grid(row=3, column=2, pady=10)

		self.open_with_string = tk.StringVar()
		self.open_with_string.set(self.open_with)
		self.currentOpenWithInput = ttk.Entry(self.frame, textvariable=self.open_with_string)\
			.grid(row=5, column=2, columnspan=3, padx=(0, 10), pady=(0, 10), sticky=tk.EW)

		self.openWithButton = ttk.Button(self.frame, text='...', width=10, command=self.change_default_viewer)\
			.grid(row=5, column=1, columnspan=1, padx=(10,0), pady=(0, 10), sticky=tk.W)

		self.saveButton = ttk.Button(self.frame, text='Save', command=self.save_settings)\
			.grid(row=6, column=1, padx=(10,0), pady=6)

		self.cancelButton = ttk.Button(self.frame, text='Cancel', command=self.close_window)\
			.grid(row=6, column=2, padx=2, pady=6)

		self.restoreButton = ttk.Button(self.frame, text='Restore', command=self.restore_defaults)\
			.grid(row=6, column=3, padx=(0,10), pady=6)

		self.frame.protocol("WM_DELETE_WINDOW", self.close_window)

		
	def compile_settings(self):
		self.inplace_settings = self.load_settings()

		configurations = [k for k in self.default_settings.keys()]
		for item in configurations:
			if item not in self.inplace_settings.keys():
				self.inplace_settings[item] = self.default_settings[item]
	
		self.full_filepath = self.inplace_settings['full_filepath']
		self.auto_open = self.inplace_settings['auto_open']
		self.open_with = Path(self.inplace_settings['open_with'])

	def save_settings(self):
		config = self.load_settings()
		config['full_filepath'] = self.full_filepath_bool.get()
		config['auto_open'] = self.auto_open_bool.get()
		config['open_with'] = Path(self.open_with_string.get())

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

	def restore_defaults(self):
		self.full_filepath_bool.set(self.default_settings['full_filepath'])
		self.auto_open_bool.set(self.default_settings['auto_open'])
		self.open_with_string.set(self.default_settings['open_with'])


	def close_window(self):
		self.app.log.writter.info('Settings window has been closed.')
		self.settings_open = False
		self.frame.destroy()

	def change_default_viewer(self):
		program_path = askopenfilename(filetypes=[("Application", "*.exe")])
		if program_path == '':
			pass
		else:
			self.open_with_string.set(program_path)
		self.frame.focus_set()

	def test(self):
		print(self.full_filepath)