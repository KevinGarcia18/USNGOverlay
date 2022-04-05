from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QGridLayout
from PyQt5.QtCore import QRect, pyqtSlot, pyqtSignal
from QtImageViewer import QtImageViewer
import os
from functools import partial

# This widget is responsible for rendering the page where waypoints can be loaded from save files.
class PrevFilesWidget(QWidget):
	changeWidgetSignal = pyqtSignal(int)
	chosenSaveFileSignal = pyqtSignal(str)
	selectTifSignal = pyqtSignal(str,str)
	def __init__(self):
		super().__init__()
		self.savespath = os.fspath('../../saves')
		self.initUI()

	def initUI(self):
		self.l = QLabel("PrevFilesWidget")
		self.btn = QPushButton("< Back",self)

		self.qbly = QVBoxLayout()
		self.qbly.addWidget(self.btn,1)
		self.btn.clicked.connect(self.on_back_clicked)

		self.itemvlist = QVBoxLayout()
		self.createLoadButtons()
		self.setLayout(self.itemvlist)

	def createLoadButtons(self):
		self.tiflist = {}

		# Go through the saves folder and make a button for each one for loading
		# the tif along with its saved waypoints
		if os.path.exists(self.savespath):
			dirlist = os.listdir( self.savespath )
			for item in dirlist:
				if item[0] != '.':
					if item[-4:] == ".txt":
						itemhlist = QHBoxLayout()
						itembtn = QPushButton(item[:-4],self)
						fline = None
						with open( os.fspath(self.savespath + "/" + item) ) as f:
							fline = f.readline().rstrip()
						itembtn.clicked.connect( partial( self.item_button_clicked, fline ) )
						itemhlist.addWidget(itembtn)
						self.tiflist[item] = itembtn
						self.itemvlist.addLayout(itemhlist)

	def getLocations(self, save_name):
		coords = []
		save_path = self.savespath + '/' + save_name + ".txt"
		try:
			with open( os.fspath(save_path) ) as save:
				lines = [ line.rstrip('\n') for line in save ]
				fline = lines[0]
				for i in range(1, len(lines)):
					line = lines[i]
					comma = line.find(',')
					x = line[:comma]
					y = line[comma+1:]
					coords.append( (x, y) )
		except (OSError, IOError, FileNotFoundError) as e:
			return [ "error" ]
		return coords

	@pyqtSlot(str)
	def item_button_clicked(self,itemName):
		self.selectTifSignal.emit(itemName, 'prevfiles')

	# When the back button is clicked, go back to the MainWidget
	@pyqtSlot()
	def on_back_clicked(self):
		self.changeWidgetSignal.emit(0)

	# When user picks a savefile, its path/save filename will be set as a local and passed with this to the overlay.
	@pyqtSlot()
	def on_savefile_chosen(self):
		self.selectTifSignal.emit(self.saveChoice, "prevfiles")
