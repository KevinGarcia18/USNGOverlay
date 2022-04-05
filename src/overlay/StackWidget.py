from PyQt5.QtWidgets import QWidget, QStackedWidget, QVBoxLayout
from MainWidget import MainWidget
from OverlayWidget import OverlayWidget
from PrevFilesWidget import PrevFilesWidget

class StackWidget(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		# Create one widget for each "page" of our application, 
		# instancing that page's custom widget
		self.page1 = MainWidget()
		self.page2 = OverlayWidget()
		self.page3 = PrevFilesWidget()

		self.stackWidget = QStackedWidget()
		self.stackWidget.addWidget(self.page1)
		self.stackWidget.addWidget(self.page2)
		self.stackWidget.addWidget(self.page3)

		vbox = QVBoxLayout(self)
		vbox.addWidget(self.stackWidget)
		self.setLayout(vbox)

	def setCurrentIndex( self, pagenum ):
		self.stackWidget.setCurrentIndex(pagenum)