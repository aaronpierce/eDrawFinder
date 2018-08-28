import errno
import json
import os
import subprocess
import threading
import time
import pickle
from tkinter import *
from tkinter.ttk import *

VERSION = '5.2'
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


	def check_appdata(self):
	    app_data = os.getenv('LOCALAPPDATA')
	    self.path = os.path.join(app_data, 'eDrawingFinder')

	    try:
	        os.makedirs(self.path)

	    except OSError as exception:
	        if exception.errno != errno.EEXIST:
	            raise

	    
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
		self.root.iconbitmap(data.resource_path('resources\\logo.ico'))

		self.frame_drawings = Frame(self.root)
		self.frame_drawings.pack()
		self.selectedDrawing = StringVar()
		self.drawings = []
		self.drawingsRadio_instances = []
		self.drawingsOverLimit = False
		self.drawing_limit = 15

		self.inputLabel = Label(self.frame, text="Enter an Item Number Below:")
		self.inputLabel.grid(row=0, column=1, columnspan=12, pady=1)

		self.inputField = Entry(self.frame, width=30)
		self.inputField.grid(row=1, column=1, columnspan=12, padx=35, pady=1)
		self.inputField.focus()

		# self.selectedType = IntVar()
		# self.radioButtonType = Radiobutton(self.frame, text='OP', variable=self.selectedType, value=0)
		# self.radioButtonType.grid(row=2, column=6)
		# self.radioButtonType = Radiobutton(self.frame, text='BM', variable=self.selectedType, value=1)
		# self.radioButtonType.grid(row=2, column=7)

		self.button_width = 10
		self.searchButton = Button(self.frame, text="Search", width=self.button_width, command=self.search)
		self.searchButton.grid(row=3, column=6, pady=2)

		self.openButton = Button(self.frame, text="Open", width=self.button_width, command=self.openDrawing)
		self.openButton.grid(row=3, column=7, pady=2)

		self.frame_info = Frame(self.root)
		self.frame_info.pack()
		self.infoLabel = Label(self.frame_info, text='')
		self.infoLabel.pack(side=BOTTOM, padx=2)

		# self.testButton = Button(self.frame_info, text="Function", width=self.button_width*2+3, command=self.create_index)
		# self.testButton.pack(side=BOTTOM, padx=2)

		self.root.update()
		self.root.minsize(self.root.winfo_width(), self.root.winfo_height())

		self.appdata_file = data.app_data_path
		self.index_builder = dict()
		self.op_index = os.path.join(data.app_data_path, 'op_database.p')
		self.bm_index = os.path.join(data.app_data_path, 'bm_database.p')
		self.raw_index = self.op_index
		self.index = {}
		self.update_avaliable = True
		
		self.threading = False
		self.task = None
		self.init_index = False

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

	def search(self):
		keyword = self.inputField.get()
		error_state = False
		results = []
		invalid = False
		# self.raw_index = (self.selectedType.get())

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
				self.change_info(f'No results matching {keyword} found.')

		self.drawings = results
		self.inputField.delete(0, END)
		self.displayButtons()

	def create_index(self):
		if PRINTING:
			print('Building Index')

		if not self.index_exists():
			self.change_info('Currently building index... Please wait to search.')

		t1=time.time()
		path = 'H:\\DWG\\'
		self.file_scan(path)
		pickle_file = open(self.raw_index , "wb") 
		pickle.dump(self.index_builder, pickle_file) 
		pickle_file.close()
		t2=time.time()
		total =t2-t1

		self.update_avaliable = True

		if PRINTING:
			print(f"Time taken to create index: {round(total, 4)}s\n")

		if self.init_index:
			self.change_info(f'Index database created. [Time Taken: {round(total, 2)}s]')
			self.init_index = False

	def index_exists(self):
		filepath = os.path.join(os.getcwd(), self.op_index)
		exists = os.path.isfile(filepath)
		if not exists:
			self.init_index = True

		return exists

	def pre_build(self):
		self.task = threading.Thread(target=self.create_index)
		self.task.start()
		self.threading = True

	def file_scan(self, drive):
		for root, dir, files in os.walk(drive, topdown = True):
			if 'OP' in root:
				for file in files:
					if file in self.index_builder:
						pass
					else :
						self.index_builder[file]= root

	def thread_running(self):
		if self.task != None:
			self.threadding = self.task.isAlive()
		else:
			self.threading = False

		return self.threading

	def load_pickle_index(self):
		pickle_file  = open(self.raw_index, "rb")
		self.index = pickle.load(pickle_file)  
		pickle_file.close()
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