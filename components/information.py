import tkinter as tk
from tkinter import ttk

class Help():

	def __init__(self, data):
		self.frame = tk.Toplevel()
		self.frame.wm_title('Help')
		self.data = data

		self.frame.iconbitmap(self.data.resource_path('components\\resources\\info.ico'))

		self.titleLabel = ttk.Label(self.frame, text='--Instructions--', font=("Default", 10))
		self.titleLabel.pack(padx=35, pady=2)
