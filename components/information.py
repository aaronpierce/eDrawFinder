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
		self.frame.resizable(False, False)

		self.frame.iconbitmap(self.app.data.resource_path('components\\resources\\info.ico'))

		self.text()

		self.footerLabel = ttk.Label(self.frame, text=f'Version {VERSION}', font=("Default", 7))
		self.footerLabel.pack()

		self.frame.protocol("WM_DELETE_WINDOW", self.close_window)

	def close_window(self):
		self.app.log.writter.info('Information window has been closed.')
		self.information_open = False
		self.frame.destroy()

	def text(self):
		strings = [
		'           [<F1>]\t Copies selected item number',
		'        [<Enter>]\t Searches given item number',
		'    [<Ctl-Enter>]\t Opens the selected drawing',
		'   [<Up>\\<Down>]\t Cycles through search history',
		'[<Right>\\<Left>]\t Switches between "OP" & "BM"',
		]

		# self.textBox = tk.Text(self.frame, width=20, height=20)
		# for s in strings:
		# 	self.textBox.insert(tk.END, s)
		# self.textBox.pack()

		for s in strings:
			label = ttk.Label(self.frame, text=s, font=("Default", 9))
			label.pack(anchor=tk.W, padx=10, pady=1)