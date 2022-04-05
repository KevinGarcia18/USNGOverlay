import sys
import os
from functools import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from QtImageViewer import *
from GeoInfo import *
from PrevFilesWidget import *

class OverlayWidget(QWidget):

	changeWidgetSignal = pyqtSignal(int)
	load_error_signal = pyqtSignal(str)

	def __init__(self):
		super().__init__()
		self.initUI()

#### Initialization Functions ###########################################################

	def initUI(self):

		self.initWayptList()
		self.initLoadingWindow()

		self.viewer = QtImageViewer()
		self.make_connection(self.viewer)

		self.navlayout = QHBoxLayout()

		self.subgridlayout = QGridLayout()
		self.subgridlayout.addWidget(self.viewer,0,0,10,10)

		self.mainlayout = QHBoxLayout()
		self.mainlayout.addWidget(self.scrollarea, 1)
		self.mainlayout.addLayout(self.subgridlayout, 5)

		self.layout = QVBoxLayout()
		self.layout.addLayout(self.navlayout)
		self.layout.addLayout(self.mainlayout)

		self.viewer.save_png_signal.connect(self.save_png)

		self.setLayout(self.layout)

	def initLoadingWindow(self):
		# the following code is for the loading_screen
		# the loading_screen is displayed while the .tif is being loaded
		self.loading_screen = QWidget()
		self.loading_screen.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
		self.loading_screen.frameGeometry().moveCenter(QDesktopWidget().availableGeometry().center())
		self.loading_screen.setWindowTitle("Loading...")
		self.loading_screen.resize(200, 50)
		self.loading_layout = QVBoxLayout()
		self.loading_screen.setLayout(self.loading_layout)

	def initWayptList(self):
		# 'waypts' is the panel itself, it is a QWidget
		self.waypts = QWidget()
		self.waypts.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		self.scrollarea = QScrollArea()
		self.scrollarea.setWidget(self.waypts)
		self.scrollarea.setWidgetResizable(True)

		# 'waypts_layout' allows us to add waypoints to 'waypts'
		# 'waypts_layout' is a QVBoxLayout so the waypoints are shown vertically
		self.waypts_sublayout = QVBoxLayout()
		self.waypts_sublayout.setAlignment(Qt.AlignTop|Qt.AlignCenter)

		self.waypts_layout = QHBoxLayout()
		self.waypts_layout.setAlignment(Qt.AlignTop)
		self.waypts_layout.setSpacing(0)

		self.waypts_layout.addLayout(self.waypts_sublayout)
		self.waypts.setLayout(self.waypts_layout)

		# each waypoint will be a QWidget
		self.waypoint_widgets = []

		for x in range(0, 36):
			# each waypoint's QWidget 'waypts_widget' is created
			self.waypts_widget = QWidget()
			self.waypts_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

			# 'waypts_widget_label' will display the waypoint's key, a letter between 'A' and 'Z'
			self.waypts_widget_label = QLabel()
			if x > 25:
				self.waypts_icon = QIcon( os.fspath('../../assets/pins/pin_' + chr(ord('0') + x - 26) + '.png') )
				self.waypts_widget_label.setPixmap( self.waypts_icon.pixmap(QSize(35,35)))
			else:
				self.waypts_icon = QIcon( os.fspath('../../assets/pins/pin_' + chr(ord('A') + x) + '.png') )
				self.waypts_widget_label.setPixmap( self.waypts_icon.pixmap(QSize(35,35)))

			# this label is left empty until set with a waypoint's coordinates when it is placed
			self.waypts_widget_usng = QLabel()
			self.waypts_widget_usng.setFont( QFont( "Arial", 15, QFont.Bold) )

			# 'waypoint_delete_btn' will display the waypoint's delete button
			self.waypoint_delete_btn = QPushButton('X')
			self.waypoint_delete_btn.setFixedSize(QSize(35, 35))
			if x > 25:
				self.waypoint_delete_btn.clicked.connect(partial(self.del_hide_waypoint, chr(ord('0') + x - 26)))
			else:
				self.waypoint_delete_btn.clicked.connect(partial(self.del_hide_waypoint, chr(ord('A') + x)))

			# 'waypts_widget_layout' allows us to add a label and button to 'waypts_widget'
			# 'waypts_widget_layout' is a QHBoxLayout so the label and buttons are shown horizontally
			self.waypts_widget_layout = QHBoxLayout()
			self.waypts_widget_layout.addWidget(self.waypts_widget_label)
			self.waypts_widget_layout.addWidget(self.waypts_widget_usng)
			self.waypts_widget_layout.addWidget(self.waypoint_delete_btn)
			self.waypts_widget.setLayout(self.waypts_widget_layout)

			# each waypoint's QWidget 'waypts_widget' is added to 'waypoint_widgets'
			self.waypoint_widgets.append(self.waypts_widget)

	def initToolbar(self):
		exitAct = QAction(QIcon('gimp_pepper.png'), 'Exit', self)
		exitAct.triggered.connect(self.close)
		toolbar = self.addToolBar('Exit')
		toolbar.addAction(exitAct)

#### Helper Functions ###################################################################

	# For use in labeling waypoints, returns a USNG string given x,y in scene coordinates
	# If no image is loaded, does nothing
	def getUSNG ( self, x, y ):
		# This should do nothing if there isn't an image loaded (no image path)
		if self.viewer.image_path and self.viewer.gps_points:
			return pixels_to_usng( x, y, self.viewer.gps_points["tl"], self.viewer.gps_points["pxscale"])

	# 'make_connection' connects this class to the 'viewer'
	def make_connection(self, viewer_object):
		viewer_object.add_delete_waypoint_signal.connect(self.add_delete_waypoint_widget)

	# 'del_hide_waypoint' deletes the waypoint from 'waypts'
	def del_hide_waypoint(self, _key):
		index = 0
		if _key.isnumeric():
			index = ord(_key) - ord('0') + 26
		else:
			index = ord(_key) - ord('A')

		self.waypoint_widgets[index].hide()
		self.waypts_layout.removeWidget(self.waypoint_widgets[index])
		self.viewer.delete_waypoint(_key)

	# 'add_show_waypoint' adds the waypoint from 'waypts'
	def add_show_waypoint(self, _key, label):
		for x in self.waypoint_widgets:
			self.waypts_layout.removeWidget(x)

		index = 0
		if _key.isnumeric():
			index = ord(_key) - ord('0') + 26
		else:
			index = ord(_key) - ord('A')

		self.waypoint_widgets[index].show()

		# Set the waypoint's USNG coordinates label if given
		self.waypoint_widgets[index].layout().itemAt(1).widget().setText(label)
		self.waypoint_widgets[index].show()

		count = 0
		for x in self.waypoint_widgets:
			if x.isVisible():
				self.waypts_sublayout.addWidget(x)

	def hide_sidebar(self):
		if self.scrollarea.isVisible():
			self.scrollarea.hide()
		else:
			self.scrollarea.show()

	def hide_100m_grid(self):
		for line in self.viewer.minorgrid:
			if line.isVisible():
				line.hide()
			else:
				line.show()
		for label in self.viewer.gridlabels:
			if label.isVisible():
				label.hide()
			else:
				label.show()

#### Slots ##############################################################################

	@pyqtSlot()
	def save_png(self):
		fileName, ignore = QFileDialog.getSaveFileName(self, 'Save image', QCoreApplication.applicationDirPath(), 'PNG (*.png)')
		if fileName:
			pixmap = self.grab()
			pixmap.save(fileName)

	@pyqtSlot()
	def on_start_clicked(self):
		self.changeWidgetSignal.emit(0)

	@pyqtSlot()
	def on_load_clicked(self):
		self.changeWidgetSignal.emit(2)

	# this slot is called after user selects a fileName to load from an open tif button
	@pyqtSlot(str,str)
	def on_load_signal(self,fileName,origin):
		self.initLoadingWindow()
		self.loading_screen.show()

		try:
			# If image_path exists, cleanup before loading
			if hasattr(self.viewer, 'image_path'):
				# Reset the waypoints list to initial state
				for index in range( 0, len(self.waypoint_widgets) ):
					if self.waypoint_widgets[index].isVisible():
						key = ''
						if index < 26:
							key = chr( ord('A') + index )
						else:
							key = chr( ord('0') + (index - 26) )
						print('key: ', key)
						self.del_hide_waypoint(key)
				# Close the open tif file (in case they want to open same file again for some reason)
				QPixmapCache.clear()
			
			self.viewer.set_image(fileName)
			self.viewer.gps_points = get_points(self.viewer.image_path)
			self.loading_screen.hide()
			if origin == "prevfiles":
				save_name = fileName[ fileName.rfind('/')+1:-4] + "_waypoints"

				coords = self.prevfileswidget.getLocations( save_name )
				if coords[0] == "error":
					raise IOError( "File IO Error on save file. Save file likely missing." )
				for i in range(0, len(coords)):
					self.viewer.add_waypoint( int(coords[i][0]), int(coords[i][1]), False )
			if "error" in self.viewer.gps_points:
				raise ValueError( self.viewer.gps_points["error"] )
			else:
				self.changeWidgetSignal.emit(1)
		except (OSError, IOError, FileNotFoundError, ValueError) as e:
			self.loading_screen.hide()
			msg = ''
			if len(e.args) > 0:
				msg = e.args[0]
			else:
				msg = repr(e)
			self.load_error_signal.emit( msg )

	# this slot is called when a signal is passed from the QtImageViewer class
	@pyqtSlot(int, str, int, int)
	def add_delete_waypoint_widget(self, flag, _key, x, y):
		if flag is 1:
			label = self.getUSNG(x, y)
			self.add_show_waypoint(_key, label)
		else:
			self.del_hide_waypoint(_key)

	@pyqtSlot()
	def buildEntry(self):

		# full path of the loaded tif image
		tifPath = self.viewer.image_path

		# path of save files relative to src/overlay (cwd when this is running)
		savepath = os.fspath("../../saves")

		# create saves folder if it doesn't exist
		if not os.path.exists(savepath):
			os.makedirs(savepath)

	    # take the filename off of the full path to the loaded tif file
		index = tifPath.rfind( '/' )
		name = tifPath[index:]
		name = name[:-4]

		newFileName = name + "_waypoints.txt"
		newFilePath = os.fspath( "../../saves" + newFileName )
		print("Saving waypoints to %s" % newFileName)

		# open the savefile for writing and insert the tif's path followed by
		# the x,y scene coordinates of each active waypoint.
		f = open( newFilePath, "w+")
		f.write("%s\n" % tifPath)
		for key,val in self.viewer.waypoints.items():
			xdata = int( round(val.x()) )
			ydata = int( round(val.y()) )
			newEntry = str(xdata) + "," + str(ydata)
			f.write("%s\n" % newEntry)
		f.close()
