import errno
import json
import os
import subprocess
import threading
import time
import pickle
from tkinter import *
from tkinter.ttk import *

VERSION = '1.6.2'
LOGGING = False
PRINTING = False
PREBUILD = True


class DATA():

	def __init__(self):
		self.app_data = os.getenv('LOCALAPPDATA')
		self.log_path = os.path.join(self.app_data, 'log.json')
		self.app_data_path = os.path.join(self.app_data, 'eDrawingFinder')
		if not os.path.exists(self.app_data_path):
			try:
				os.makedirs(self.app_data_path)
			except OSError as exception:
				self.app_data_path = os.getcwd()
				if exception.errno != errno.EEXIST:
					raise

	def resource_path(self, relative_path):
		""" Get absolute path to resource, works for dev and for PyInstaller """
		try:
			# PyInstaller creates a temp folder and stores path in _MEIPASS
			base_path = sys._MEIPASS
		except Exception:
			base_path = os.path.abspath(".")

		return os.path.join(base_path, relative_path)
	    
	def log(self, outcome):

		if not os.path.exists(self.log_path):
			data = {}
			data['Computer'] = os.environ['COMPUTERNAME']
			data['Searched'] = 0
			data['Found'] = 0
			data['Opened'] = 0
			data['Invalid'] = 0

			with open(self.log_path, 'w') as f:
				json.dump(data, f, indent=4)

		with open(self.log_path, 'r+') as f:
			raw = json.load(f)

		if outcome == 'Searched':
			raw['Searched'] += 1
		elif outcome == 'Found':
			raw['Found'] += 1
		elif outcome == 'Opened':
			raw['Opened'] += 1
		elif outcome == 'Invalid':
			raw['Invalid'] += 1

		with open(self.log_path, 'w') as f:
			json.dump(raw, f, indent=4)


class App():

	def __init__(self):
		self.root = Tk()
		self.frame = Frame(self.root)
		self.frame.master.title(f'eDrawing Finder v{VERSION}')
		self.frame.pack()

		self.root.bind('<Return>', self.search)
		self.root.bind('<Up>', self.pull_history)
		self.root.bind('<Down>', self.pull_history)
		self.root.bind('<Left>', self.change_radio_select)
		self.root.bind('<Right>', self.change_radio_select)
		self.root.iconbitmap(data.resource_path('resources\\logo.ico'))

		self.frame_drawings = Frame(self.root)
		self.frame_drawings.pack()
		self.selectedDrawing = StringVar()
		self.drawings = []
		self.drawingsRadio_instances = []
		self.drawingsOverLimit = False
		self.drawing_limit = 15

		self.appdata_file = data.app_data_path
		self.index_builder = dict()
		self.op_index_path = os.path.join(data.app_data_path, 'op_database.p')
		self.bm_index_path = os.path.join(data.app_data_path, 'bm_database.p')
		self.current_index_path = self.op_index_path
		self.op_index = {}
		self.bm_index = {}
		self.index = {}
		self.update_avaliable = True

		self.inputLabel = Label(self.frame, text="Enter an Item Number Below:")
		self.inputLabel.grid(row=0, column=1, columnspan=12, pady=1)

		self.inputField = Entry(self.frame, width=30)
		self.inputField.grid(row=1, column=1, columnspan=12, padx=35, pady=1)
		self.inputField.focus()

		self.is_search_OP = IntVar()
		self.radioButtonType = Radiobutton(self.frame, text='OP', variable=self.is_search_OP, value=1)
		self.radioButtonType.grid(row=2, column=6)
		self.radioButtonType = Radiobutton(self.frame, text='BM', variable=self.is_search_OP, value=0)
		self.radioButtonType.grid(row=2, column=7)
		self.is_search_OP.set(1)

		self.button_width = 10
		self.searchButton = Button(self.frame, text="Search", width=self.button_width, command=self.search)
		self.searchButton.grid(row=3, column=6, pady=2)

		self.openButton = Button(self.frame, text="Open", width=self.button_width, command=self.openDrawing)
		self.openButton.grid(row=3, column=7, pady=2)

		self.frame_info = Frame(self.root)
		self.frame_info.pack()
		self.infoLabel = Label(self.frame_info, text='')
		self.infoLabel.pack(side=BOTTOM, padx=2)

		# self.testButton = Button(self.frame_info, text="Function", width=self.button_width*2+3, command=self.load_pickle_index)
		# self.testButton.pack(side=BOTTOM, padx=2)

		self.root.update()
		self.root.minsize(self.root.winfo_width(), self.root.winfo_height())
		
		self.threads = []
		self.threading = False
		self.init_op_index = False
		self.init_bm_index = False

		self.previous_search = []
		self.previous_counter = 0

	def displayButtons(self):
		if self.drawingsRadio_instances != []:
			self.clearButtons()

		if len(self.drawings) > self.drawing_limit:
				for drawing in self.drawings[:self.drawing_limit]:
					self.createRadio(drawing)

		else:
			for drawing in self.drawings:
				self.createRadio(drawing)
				
		if self.drawings != []:
			self.selectedDrawing.set(self.drawings[0])

	def createRadio(self, x):
		self.drawingRadioButton = Radiobutton(self.frame_drawings, text=x, variable=self.selectedDrawing, value=x)
		self.drawingRadioButton.pack(anchor=W, padx=5, pady=2)
		self.drawingsRadio_instances.append(self.drawingRadioButton)

	def clearButtons(self):
		for button in self.drawingsRadio_instances:
			button.destroy()

	def change_info(self, message):
		self.infoLabel.config(text = message)
		self.infoLabel.update_idletasks()

	def openDrawing(self):
		if not self.selectedDrawing.get() == '':
			os.startfile(self.selectedDrawing.get(), 'open')
			if LOGGING:
				data.log('Opened')

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
			result = []
			if LOGGING:
				data.log('Invalid')

		else:
			if keyword not in self.previous_search:
				self.previous_search.insert(0, keyword)
				if len(self.previous_search) > 15:
					self.previous_search.pop(-1) 
			else:
				self.previous_search.insert(0, self.previous_search.pop(self.previous_search.index(keyword)))

			results = self.index_search()
			if LOGGING:
				data.log('Searched')

		if results != [] and results != None:
			if LOGGING:
				data.log('Found')

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
		self.inputField.delete(0, END)
		self.displayButtons()

	def create_index(self, index):
		if PRINTING:
			print(f'Building {index[-13::]}')

		if not self.index_exists(index):
			self.change_info('Currently building index... Please wait to search.')

		t1=time.time()
		path = 'H:\\DWG\\'
		if index == self.bm_index_path:
			path += 'BM\\'

		self.file_scan(path)
		pickle_file = open(index , "wb") 
		pickle.dump(self.index_builder, pickle_file) 
		pickle_file.close()
		t2=time.time()
		total =t2-t1

		self.update_avaliable = True

		if PRINTING:
			print(f"\nTime taken to create {index[-13::]}: {round(total, 4)}s")

		if self.init_op_index or self.init_bm_index:
			self.change_info(f'Index database created. [Time Taken: {round(total, 2)}s]')
			if index == self.op_index_path:
				self.init_op_index = False
			else:
				self.init_bm_index = True

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
				self.inputField.delete(0, END)
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

		self.inputField.delete(0, END)

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
			task.start()
			self.threads.append(task)
		self.threading = True

	def file_scan(self, drive):
		if drive == 'H:\\DWG\\':
			for root, dir, files in os.walk(drive, topdown = True):
				if 'OP' in root:
					for file in files:
						if file in self.index_builder:
							pass
						else:
							self.index_builder[file]= root
		else:
			for root, dir, files in os.walk(drive, topdown = True):
				for file in files:
					if file in self.index_builder:
						pass
					else:
						self.index_builder[file]= root

	def thread_running(self):
		running = []
		for ea in self.threads:
			if ea.isAlive():
				running.append(True)
		
		if True in running:
			self.threading = True

		return self.threading

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
				if PRINTING:
					print(e)
				sys.exit()

		keyword = self.inputField.get()
		self.inputField.delete(30, END)

		results = []

		if self.is_search_OP.get():
			self.index = self.op_index
		else:
			self.index = self.bm_index

		for key in self.index:
			if re.search(keyword, key):
				hit = f'{self.index[key]}'+'\\'+f'{key}'
				results.append(hit)
		
		results.sort(key=len, reverse=False)

		if PRINTING:
			print("Path \t\t: File-name")
			for each in results:
				print(each)
				print("---------------------------------")
			t2 = time.time()
			total =t2-t1
			print("Total files are", len(results))
			print(f"Time taken to search: {round(total, 4)}s\n")

		return results

data = DATA()

app = App()
if PREBUILD:
	app.pre_build()

app.root.mainloop()
