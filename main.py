import errno
import glob
import json
import os
import subprocess
import threading
import time
import pickle
from tkinter import *
from tkinter.ttk import *

VERSION = '5.0'
LOGGING = False
PRINTING = False


class DATA():

	def resource_path(self, relative_path):
		""" Get absolute path to resource, works for dev and for PyInstaller """
		try:
			# PyInstaller creates a temp folder and stores path in _MEIPASS
			base_path = sys._MEIPASS
		except Exception:
			base_path = os.path.abspath(".")

		return os.path.join(base_path, relative_path)

class LOGGER():

	def __init__(self):
		self.log_path = ''

	def check_appdata(self):

	    app_data = os.getenv('LOCALAPPDATA')
	    path = os.path.join(app_data, 'eDrawingFinder')

	    try:
	        os.makedirs(path)

	    except OSError as exception:
	        if exception.errno != errno.EEXIST:
	            raise

	    self.log_path = os.path.join(path, 'log.json')

	def log(self, outcome):

		if self.log_path == '':
			self.check_appdata()

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

		self.root.update()
		self.root.minsize(self.root.winfo_width(), self.root.winfo_height())

		self.index = dict()
		self.op_index = 'op_database.p'
		self.bm_index = 'bm_database.p'
		self.raw_index = self.op_index

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
				Log.log('Opened')

		else:
			self.change_info('No File Selected.')

	def search(self, full_check=False):
		keyword = self.inputField.get()
		self.inputField.delete(30, END)
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
				Log.log('Invalid')

		else:
			results = self.index_search()
			if LOGGING:
				Log.log('Searched')

		if results != []:
			if LOGGING:
				Log.log('Found')

			if len(results) > self.drawing_limit:
				self.drawingsOverLimit = True
				message = f'{str(len(results))} results matching {keyword} found. [First {self.drawing_limit} displayed]'
			else:
				self.drawingsOverLimit = False
				message = f'{str(len(results))} results matching {keyword} found.'
			
			self.change_info(message)

		else:
			if not error_state:
				self.change_info(f'No results matching {keyword} found.')


		self.drawings = results
		self.displayButtons()

	def create_index(self):
		self.change_info('Creating search database... Please Wait.')
		t1=time.time()
		path = 'H:\\DWG\\'
		self.file_scan(path)
		pickle_file = open(self.raw_index , "wb") 
		pickle.dump(self.index, pickle_file) 
		pickle_file.close()
		t2=time.time()
		total =t2-t1
		if PRINTING:
			print("Time taken to create " , total)

	def check_index(self):
		return os.path.isfile(self.raw_index)

	def file_scan(self, drive):
		for root, dir, files in os.walk(drive, topdown = True):
			if 'OP' in root:
				for file in files:
					if file in self.index:
						file = file + "_1"
						self.index[file]= root
					else :
						self.index[file]= root

	def index_search(self):
		t1 = time.time()
		

		try:
			pickle_file  = open(self.raw_index, "rb")
			dict_index = pickle.load(pickle_file)  
			pickle_file.close()

		except IOError:
			self.create_index()
			pickle_file  = open(self.raw_index, "rb")
			dict_index = pickle.load(pickle_file)  
			pickle_file.close()

		except Exception as e:
			if PRINTING:
				print(e)
			sys.exit()

		keyword = self.inputField.get()
		self.inputField.delete(30, END)

		results = []

		for key in dict_index:
			if re.search(keyword, key):
				hit = f'{dict_index[key]}'+'\\'+f'{key}'
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
			print("Time taken to search " , total)

		return results

data = DATA()
Log = LOGGER()

app = App()

<<<<<<< HEAD
app.root.mainloop()
=======
>>>>>>> master
