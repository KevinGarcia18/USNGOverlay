import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from StackWidget import StackWidget
from OverlayWidget import OverlayWidget

class Overlay(QMainWindow):
	def __init__(self):
		super().__init__()

		self.initUI()

#### Initialization Functions ###########################################################

	def initUI(self):
		self.setWindowTitle('USNG Overlay - Start')

		self.setWindowIcon( QIcon( os.fspath('../../assets/usng-overlay.ico') ) )

		self.wid = StackWidget()
		self.setCentralWidget(self.wid)

		# Set class variable in overlaywidget to prevfileswidget instance
		self.wid.page2.prevfileswidget = self.wid.page3

		# Button signals
		self.wid.page1.changeWidgetSignal.connect(self.switchWidget)
		self.wid.page2.changeWidgetSignal.connect(self.switchWidget)
		self.wid.page3.changeWidgetSignal.connect(self.switchWidget)
		self.wid.page1.selectTifSignal.connect(self.wid.page2.on_load_signal)
		self.wid.page3.selectTifSignal.connect(self.wid.page2.on_load_signal)
		# Slot to receive tif loading error and handle it
		self.wid.page2.load_error_signal.connect(self.handleFileError)

		self.createMenuBar()
		self.menubar.hide()
		self.showMaximized()

	def createMenuBar(self):
		# Create a file menu for opening new file, exporting to image, & other file ops
		self.menubar = self.menuBar()
		fileMenu = self.menubar.addMenu('File')
		viewMenu = self.menubar.addMenu('View')

		# Create the file actions and add them
		openAct = QAction('Open TIFF Image', self)
		openAct.triggered.connect(self.wid.page1.on_opentif_clicked)
		loadAct = QAction('Load Saved TIFF File', self)
		loadAct.triggered.connect(self.wid.page1.on_prevfiles_clicked)
		exportPngAct = QAction('Export Overlay to PNG', self)
		exportPngAct.triggered.connect(self.wid.page2.viewer.download_png_press)
		saveWayptsAct = QAction('Save Waypoints to File', self)
		saveWayptsAct.triggered.connect(self.wid.page2.buildEntry)
		exitAct = QAction('Exit Program', self)
		exitAct.triggered.connect(QApplication.instance().quit)
		fileMenu.addAction(openAct)
		fileMenu.addAction(loadAct)
		fileMenu.addAction(exportPngAct)
		fileMenu.addAction(saveWayptsAct)
		fileMenu.addAction(exitAct)

		# Create a view menu for show/hide waypoint list popup, & other view ops
		toggleWayptsAct = QAction('Toggle Waypoint List', self)
		toggleWayptsAct.triggered.connect(self.wid.page2.hide_sidebar)
		viewMenu.addAction(toggleWayptsAct)

		toggle100mGrid = QAction('Toggle 100 meter Grid Lines', self)
		toggle100mGrid.triggered.connect(self.wid.page2.hide_100m_grid)
		viewMenu.addAction(toggle100mGrid)

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

#### Slots ##############################################################################

	@pyqtSlot(int)
	def switchWidget(self,widgetID):
		if widgetID == 0:
			self.setWindowTitle("USNG Overlay - Start")
			self.menubar.hide()
		elif widgetID == 1:
			self.setWindowTitle("USNG Overlay - Main")
			self.menubar.show()
		else:
			self.setWindowTitle("USNG Overlay - Load Saved Waypoints")
			self.menubar.hide()
		# if widgetID == 2:
			#self.wid.page3.createLoadButtons()
		self.wid.setCurrentIndex(widgetID)

		if widgetID == 1:
			self.wid.page2.viewer.expand_btn_press()

	@pyqtSlot(str)
	def handleFileError(self,errmsg):
		# Set the error message in the error window and show it
		QMessageBox.warning(self, "Error", errmsg, QMessageBox.Ok)

		# On clicking ok, switch back to main widget
		self.setWindowTitle("USNG Overlay - Start")
		self.wid.setCurrentIndex(0)

#########################################################################################

if __name__ == '__main__':

	app = QApplication(sys.argv)
	ex = Overlay()
	sys.exit(app.exec_())
