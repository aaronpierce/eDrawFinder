import os
import subprocess
import threading
import time
import pickle
import sys

from pathlib import Path

import tkinter as tk
from tkinter import ttk

import components.data as data
import components.settings as settings
import components.logger as logger
import components.information as information


class Application():

	def __init__(self):
		self.root = tk.Tk()
		self.frame = ttk.Frame(self.root)
		self.frame.master.title(f'eDrawing Finder')
		self.frame.pack()
		self.root.resizable(False, False)

		self.data = data.Data(self)
		self.setting = settings.Settings(self)
		self.log = logger.Logger(self)
		self.info = information.Help(self)


		self.root.bind('<Return>', self.search)
		self.root.bind('<Up>', self.pull_history)
		self.root.bind('<Down>', self.pull_history)
		self.root.bind('<Left>', self.change_radio_select)
		self.root.bind('<Right>', self.change_radio_select)
		self.root.bind('<F1>', self.copy_item)
		self.root.bind('<Control-Return>', self.openDrawing)  
		self.root.iconbitmap(self.data.resource_path('components\\resources\\logo.ico'))

		self.menubar = tk.Menu(self.root)
		self.menubar.add_command(label="Settings", command=self.show_settings)
		self.menubar.add_command(label="Help", command=self.show_help)
		self.root.config(menu=self.menubar)

		self.frame_drawings = ttk.Frame(self.root)
		self.frame_drawings.pack()
		self.selectedDrawing = tk.StringVar()
		self.drawings = []
		self.drawingsRadio_instances = []
		self.drawingsOverLimit = False
		self.drawing_limit = 15

		self.appdata_file = self.data.app_data_path
		self.op_index_path = self.data.op_path
		self.bm_index_path = self.data.bm_path
		self.current_index_path = self.op_index_path
		self.op_index = {}
		self.bm_index = {}
		self.index_builder_op = {}
		self.index_builder_bm = {}
		self.index = {}
		self.update_avaliable = True

		self.inputLabel = ttk.Label(self.frame, text="Enter an Item Number Below:")
		self.inputLabel.grid(row=0, column=1, columnspan=12, pady=1)

		self.inputField = ttk.Entry(self.frame, width=30)
		self.inputField.grid(row=1, column=1, columnspan=12, padx=35, pady=1)
		self.inputField.focus()

		self.is_search_OP = tk.IntVar()
		self.radioButtonType = ttk.Radiobutton(self.frame, text='OP', variable=self.is_search_OP, value=1)
		self.radioButtonType.grid(row=2, column=6)
		self.radioButtonType = ttk.Radiobutton(self.frame, text='BM', variable=self.is_search_OP, value=0)
		self.radioButtonType.grid(row=2, column=7)
		self.is_search_OP.set(1)

		self.button_width = 10
		self.searchButton = ttk.Button(self.frame, text="Search", width=self.button_width, command=self.search)
		self.searchButton.grid(row=3, column=6, pady=2)

		self.openButton = ttk.Button(self.frame, text="Open", width=self.button_width, command=self.openDrawing)
		self.openButton.grid(row=3, column=7, pady=2)

		self.frame_info = ttk.Frame(self.root)
		self.frame_info.pack()
		self.infoLabel = ttk.Label(self.frame_info, text='')
		self.infoLabel.pack(side=tk.BOTTOM, padx=2)

		# self.testButton = ttk.Button(self.frame_info, text="Function", width=self.button_width*2+3, command=self.test_function)
		# self.testButton.pack(side=tk.BOTTOM, padx=2)

		self.root.update()
		self.root.minsize(self.root.winfo_width(), self.root.winfo_height())
		
		self.threads = []
		self.threading = False
		self.lock = threading.Lock()
		self.init_op_index = False
		self.init_bm_index = False

		self.previous_search = []
		self.previous_counter = 0

	def show_settings(self, keypress=False):
		if not self.setting.settings_open:
			self.setting.settings_open = True
			self.setting.display()
		else:
			self.setting.frame.focus_force()
		

	def show_help(self, keypress=False):
		if not self.info.information_open:
			self.info.information_open = True
			self.info.display()
		else:
			self.info.frame.focus_force()

	def displayButtons(self):

		if self.drawingsRadio_instances != []:
			self.clearButtons()

		if len(self.drawings) > self.drawing_limit:
			if self.setting.full_filepath:
				for drawing in self.drawings[:self.drawing_limit]:
					self.createRadio(drawing, drawing)
			else:
				for drawing in self.drawings[:self.drawing_limit]:
					item_only = drawing.split('\\')[-1]
					self.createRadio(item_only, drawing)

		else:
			if self.setting.full_filepath:
				for drawing in self.drawings:
					self.createRadio(drawing, drawing)
					self.log.writter.info(f'Full Path - {self.setting.full_filepath}')
			else:
				for drawing in self.drawings:
					item_only = drawing.split('\\')[-1]
					self.createRadio(item_only, drawing)
					self.log.writter.info(f'Item Only - {self.setting.full_filepath}')
					
		if self.drawings != []:
			self.selectedDrawing.set(self.drawings[0])
			if self.setting.auto_open:
				self.openDrawing(keypress=False)
				self.log.writter.info('Auto Opening Enabled at Search Time.')


	def createRadio(self, t, v):
		self.drawingRadioButton = ttk.Radiobutton(self.frame_drawings, text=t, variable=self.selectedDrawing, value=v)
		self.drawingRadioButton.pack(anchor=tk.W, padx=5, pady=2)
		self.drawingsRadio_instances.append(self.drawingRadioButton)

	def clearButtons(self):
		for button in self.drawingsRadio_instances:
			button.destroy()

	def change_info(self, message):
		self.infoLabel.config(text = message)
		self.infoLabel.update_idletasks()

	def openDrawing(self, keypress=False):
		if not self.selectedDrawing.get() == '':
			if self.setting.open_with == Path('.'):
				os.startfile(self.selectedDrawing.get(), 'open')
			else:
				self.log.writter.info(f'Opening via {self.setting.open_with} {self.selectedDrawing.get()}')
				try:
					subprocess.Popen(f'{self.setting.open_with} {self.selectedDrawing.get()}')
				except OSError as e:
					if e.errno == os.errno.ENOENT:
						self.change_info(f"Unable to open using: '{self.setting.open_with}'.")
				
		else:
			self.change_info('No File Selected.')

	def search(self, keypress=False):
		keyword = self.inputField.get().upper()
		self.previous_counter = 0
		error_state = False
		results = []
		invalid = False

		if self.is_search_OP.get():
			self.current_index_path = self.op_index_path
		else:
			self.current_index_path = self.bm_index_path

		for i in range(len(keyword)):
			if keyword[i] in ['\\', '/', '.',] or keyword[0] == ' ' or keyword[-1] == ' ':
				invalid = True

		if invalid == True or keyword == '':
			error_state = True
			self.change_info('Enter a valid part number.')
			self.log.writter.info(f'Invalid Input ["{keyword}"]')
			results = []

		else:
			if keyword not in self.previous_search:
				self.previous_search.insert(0, keyword)
				if len(self.previous_search) > 15:
					self.previous_search.pop(-1) 
			else:
				self.previous_search.insert(0, self.previous_search.pop(self.previous_search.index(keyword)))

			results = self.index_search()

		if results != [] and results != None:

			if len(results) > self.drawing_limit:
				self.drawingsOverLimit = True
				message = f'{str(len(results))} results matching {keyword} found. [First {self.drawing_limit} displayed]'
			else:
				self.drawingsOverLimit = False
				message = f'{str(len(results))} results matching {keyword} found.'
			
			self.change_info(message)

		elif results == None:
			self.change_info('Currently building index... Please wait to search.')
			return

		else:
			if not error_state:
				v = 'OP'
				if not self.is_search_OP.get():
					v = 'BM'
				self.change_info(f'No {v} results matching {keyword} found.')

		self.drawings = results
		self.inputField.delete(0, tk.END)
		self.displayButtons()

	def create_index(self, index):
		self.log.writter.info(f'Building {index[-13::]}')

		if not self.index_exists(index):
			self.change_info('Currently building index... Please wait to search.')

		t1 = time.time()
		path = 'H:\\DWG\\'
		if index == self.bm_index_path:
			path += 'BM\\'

		self.file_scan(path)
		pickle_file = open(index , "wb") 
		if index == self.op_index_path:
			pickle.dump(self.index_builder_op, pickle_file)
		else:
			pickle.dump(self.index_builder_bm, pickle_file)
		t2 = time.time()
		total = t2-t1

		self.update_avaliable = True

		self.log.writter.info(f'{index[-13::]} created. [{round(total, 4)}s]')

		if self.init_op_index or self.init_bm_index:
			self.change_info(f'Index database created. [Time Taken: {round(total, 2)}s]')
			if index == self.op_index_path:
				self.init_op_index = False
			else:
				self.init_bm_index = False

	def index_exists(self, index):
		exists = os.path.isfile(index)
		if not exists:
			if index == self.op_index_path:
				self.init_op_index = True
			else:
				self.init_bm_index = True
		return exists

	def pull_history(self, keypress):
		clear_field = False
		if keypress.keysym == 'Up' and self.previous_search != []:

			if self.previous_search != [] and self.inputField.get() == '' and self.previous_counter == 0:
				self.inputField.delete(0, tk.END)
				self.inputField.insert(0, self.previous_search[self.previous_counter])

			elif (self.previous_counter + 1) < len(self.previous_search):
				self.previous_counter += 1

		elif keypress.keysym == 'Down' and self.previous_search != []:

			if self.previous_counter > 0:
				self.previous_counter -= 1
			else:
				clear_field = True
		else:
			return

		self.inputField.delete(0, tk.END)

		if not clear_field:
			self.inputField.insert(0, self.previous_search[self.previous_counter])
		else:
			self.inputField.insert(0, '')

	def change_radio_select(self, keypress=False):
		if self.is_search_OP.get() == 0:
			self.is_search_OP.set(1)
		else:
			self.is_search_OP.set(0)

	def pre_build(self):
		indexes = [self.op_index_path, self.bm_index_path]
		self.threads = []
		for i in indexes:
			task = threading.Thread(target=self.create_index, args=[i])
			task.setDaemon(True)
			task.start()
			self.threads.append(task)
		self.threading = True

	def file_scan(self, drive):
		exclude = ['BM']

		if drive == 'H:\\DWG\\':
			for root, dirs, files in os.walk(drive, topdown = True):
				dirs[:] = [d for d in dirs if d not in exclude]
				for file in files:
					if file in self.index_builder_op:
						pass
					else:
						self.index_builder_op[file]= root
		else:
			for root, dirs, files in os.walk(drive, topdown = True):
				for file in files:
					if file in self.index_builder_bm:
						pass
					else:
						self.index_builder_bm[file]= root

	def thread_running(self):
		running = []
		for ea in self.threads:
			if ea.isAlive():
				running.append(True)
		
		if True in running:
			self.threading = True

		return self.threading

	def copy_item(self, keypress=False):
		raw = self.selectedDrawing.get()
		item = raw.split('\\')[-1].split('.')[0]

		self.root.clipboard_clear()
		self.root.clipboard_append(item)

	def load_pickle_index(self):
		pickle_file  = open(self.current_index_path, "rb")
		self.index = pickle.load(pickle_file)
		pickle_file.close()
		if self.current_index_path == self.op_index_path:
			self.op_index = self.index
		else:
			self.bm_index = self.index

		self.update_avaliable = False

	def index_search(self):
		t1 = time.time()
		if self.update_avaliable:
			try:
				self.load_pickle_index()

			except IOError:
				if not self.thread_running():
					self.create_index()
					self.load_pickle_index()

				else:
					self.change_info('Currently building index... Please wait.')
					return

			except Exception as e:
				self.log.writter.error(e)
				sys.exit()

		keyword = self.inputField.get()
		self.inputField.delete(30, tk.END)

		results = []

		if self.is_search_OP.get():
			self.index = self.op_index
		else:
			self.index = self.bm_index

		if len(self.index) == 0:
			self.log.writter.warning('Reloading index; Empty list found!')
			self.load_pickle_index()

		for key in self.index:
			if tk.re.search(keyword.lower(), key.lower()):
				hit = f'{self.index[key]}'+'\\'+f'{key}'
				results.append(hit)
		
		results.sort(key=len, reverse=False)

		t2 = time.time()
		total = t2-t1
		self.log.writter.info(f'Total {self.current_index_path.split("_")[0][-2:].upper()} files are {len(results)} [{round(total, 4)}s]')
		return results

	def test_function(self):
		pass
		
