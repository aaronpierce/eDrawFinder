import tkinter as tk
from tkinter import ttk

from components.settings import VERSION

class Help():

	def __init__(self, core_app):
		self.app = core_app
		self.information_open = False

	def display(self):
		self.frame = tk.Toplevel()
		self.frame.wm_title('Help')

		self.frame.iconbitmap(self.app.data.resource_path('components\\resources\\info.ico'))

		self.titleLabel = ttk.Label(self.frame, text='--Instructions--', font=("Default", 10))
		self.titleLabel.pack(padx=35, pady=2)

		self.footerLabel = ttk.Label(self.frame, text=f'Version {VERSION}', font=("Default", 7))
		self.footerLabel.pack()

		self.frame.protocol("WM_DELETE_WINDOW", self.close_window)

	def close_window(self):
		self.app.log.writter.info('Information window has been closed.')
		self.information_open = False
		self.frame.destroy()