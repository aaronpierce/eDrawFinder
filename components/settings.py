import tkinter as tk
from tkinter import ttk

VERSION = '1.6.7'

class Settings():

	def __init__(self, app_root, data):
		self.frame = tk.Toplevel()
		self.frame.wm_title('Settings')
		self.app_root = app_root
		self.data = data

		self.frame.iconbitmap(self.data.resource_path('components\\resources\\settings.ico'))

		self.titleLabel = ttk.Label(self.frame, text='--Optional Settings--', font=("Default", 10))
		self.titleLabel.pack(padx=35, pady=2)

		self.v = tk.StringVar()
		self.resultPathToggle = ttk.Checkbutton(self.frame, textvariable=self.v, offvalue=True, onvalue=False, variable=self.v)
		self.resultPathToggle.pack(pady=4)

