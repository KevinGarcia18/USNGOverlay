import os.path
import collections
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from GeoInfo import *

class QtImageViewer(QGraphicsView):
    
    # 'add_delete_waypoint_signal' is used to communicate with the class 'OverlayWidget'
    add_delete_waypoint_signal = pyqtSignal(int, str, int, int)

    # this signal is caught by the overlaywidget where the png is created and saved
    save_png_signal = pyqtSignal()

#### Initialization Functions ###########################################################

    def __init__(self):
        # 'cur_path' is used to generate the paths for the .pngs
        self.cur_path = os.path.dirname(__file__)

        # important for upholding zoom max and min
        self.zoom_level = 0
        self.zoom_max = 15
        self.zoom_min = 0

        # the following variables are used to scale waypoints with relation to the image
        self.wpt_cur_scale = 15.0
        self.wpt_max_scale = 15.0
        self.wpt_min_scale = 0

        # 'key_array' holds the alphabetical keys associated with each waypoint
        # 'key_array' is in the order Z through A
        self.key_array = []
        for x in range(0, 10):
            self.key_array.append(chr(ord('9') - x))
        for y in range(0, 26):
            self.key_array.append(chr(ord('Z') - y))

        # 'waypoints' holds all waypoints in the order that they are added to the screen
        self.waypoints = collections.OrderedDict()

        ###################################
        # Create the image viewer
        ###################################

        QGraphicsView.__init__(self)
        self.setRenderHints(QPainter.Antialiasing|QPainter.SmoothPixmapTransform)

        # 'vlayout' controls the vertical placement of the onscreen buttons
        self.vlayout = QBoxLayout(QBoxLayout.TopToBottom)
        self.vlayout.setAlignment(Qt.AlignTop|Qt.AlignRight)
        #self.vlayout.addSpacing(10)

        self.init_navbtns()
        self.setLayout(self.vlayout)

        # 'hlayout' controls the horizontal placement of the onscreen buttons
        self.hlayout = QHBoxLayout()
        self.hlayout.setAlignment(Qt.AlignRight)
        self.hlayout.addSpacing(50)
        self.vlayout.addLayout(self.hlayout)

    # set up all of the nav buttons that appear over the map
    def init_navbtns(self):
        zoom_in_btn = QPushButton()
        zoom_in_btn.setFixedSize(QSize(35, 35))
        zoom_in_btn.setIcon( QIcon( os.fspath(os.path.join(self.cur_path, '../../assets/zoom_in.png') ) ) )
        zoom_in_btn.setIconSize(QSize(25, 25))
        zoom_in_btn.setToolTip("zoom in to image")
        zoom_in_btn.clicked.connect(self.zoom_in_btn_press)
        self.vlayout.addWidget(zoom_in_btn)

        zoom_out_btn = QPushButton()
        zoom_out_btn.setFixedSize(QSize(35, 35))
        zoom_out_btn.setIcon( QIcon( os.fspath(os.path.join(self.cur_path, '../../assets/zoom_out.png') ) ) )
        zoom_out_btn.setIconSize(QSize(25, 25))
        zoom_out_btn.setToolTip("zoom out of image")
        zoom_out_btn.clicked.connect(self.zoom_out_btn_press)
        self.vlayout.addWidget(zoom_out_btn)

        expand_btn = QPushButton()
        expand_btn.setFixedSize(QSize(35, 35))
        expand_btn.setIcon( QIcon( os.fspath( os.path.join(self.cur_path, '../../assets/expand.png') ) ) )
        expand_btn.setIconSize(QSize(25, 25))
        expand_btn.setToolTip("reset zoom level")
        expand_btn.clicked.connect(self.expand_btn_press)
        self.vlayout.addWidget(expand_btn)

        visibility_wpts_btn = QPushButton()
        visibility_wpts_btn.setFixedSize(QSize(35, 35))
        visibility_wpts_btn.setIcon( QIcon( os.fspath(os.path.join(self.cur_path, '../../assets/visibility.png') ) ) )
        visibility_wpts_btn.setIconSize(QSize(25, 25))
        visibility_wpts_btn.setToolTip("hide/show all waypoints")
        visibility_wpts_btn.clicked.connect(self.visibility_wpts_btn_press)
        self.vlayout.addWidget(visibility_wpts_btn)

        undo_wpt_btn = QPushButton()
        undo_wpt_btn.setFixedSize(QSize(35, 35))
        undo_wpt_btn.setIcon( QIcon( os.fspath(os.path.join(self.cur_path, '../../assets/undo.png') ) ) )
        undo_wpt_btn.setIconSize(QSize(25, 25))
        undo_wpt_btn.setToolTip("undo last added waypoint")
        undo_wpt_btn.clicked.connect(self.undo_wpt_btn_press)
        self.vlayout.addWidget(undo_wpt_btn)

        download_png = QPushButton()
        download_png.setFixedSize(QSize(35, 35))
        download_png.setIcon( QIcon( os.fspath( os.path.join(self.cur_path, '../../assets/download.png') ) ) )
        download_png.setIconSize(QSize(25, 25))
        download_png.setToolTip("download view as png")
        download_png.clicked.connect(self.download_png_press)
        self.vlayout.addWidget(download_png)

    ###################################
    # Helper functions
    ###################################

    # 'set_image' is called by 'OverlayWidget' to add the .tif image to the image viewer
    def set_image(self, str_):
        self.image_path = str_

        try:
            self.pixmap = QPixmap( os.fspath(self.image_path) )
        except (OSError, IOError, FileNotFoundError) as e:
            raise IOError("Unable to load tif image. File not found or insufficient permissions to read.")
        self.scene = QGraphicsScene()
        self.scene.addPixmap(self.pixmap)
        self.setScene(self.scene)
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.gps_points = get_points( os.fspath(self.image_path) )
        if not ("error" in self.gps_points):
            self.create_grid()

        # this reader has error member functions unlike QPixMap so we can at least
        # get a vague error out...
        if self.pixmap.isNull():
            print( "self.pixmap is null after attempted load, trying QImageReader" )
            self.testing = QImageReader( os.fspath(self.image_path) )
            print( "can QImageReader read the tif?", self.testing.canRead() )
            self.testing.read()
            print( "QImageReader .error():", self.testing.error() )
            print( ".errorString():", self.testing.errorString() )


    def download_png_press(self):
        self.save_png_signal.emit()

    def create_grid(self):
        lines, labels = compute_gridlines( self.gps_points )
        # 1000m gridline pen
        major = QPen()
        major.setWidth(2)
        major.setCosmetic(True)
        major.setBrush(Qt.red)
        # 100m gridline pen
        minor = QPen()
        minor.setWidth(1)
        minor.setCosmetic(True)
        minor.setBrush(Qt.red)
        minor.setStyle(Qt.DashLine)
        self.minorgrid = []
        self.gridlabels = []
        # for each direction i in [ north, east ]
        for i in range( 0, len(lines) ):
            # for each line j in direction i
            for j in range( 0, len(lines[i]) ):
                line = lines[i][j]
                label = labels[i][j]

                # Create QGraphicsSimpleTextItem for each side of the line and place it
                grid_label = QGraphicsTextItem( str(label) )
                if line[1]:
                    grid_label.setScale(75)
                else:
                    grid_label.setScale(50)

                bounding = grid_label.mapRectToScene(grid_label.boundingRect())
                width = bounding.width()/2
                height = bounding.height()/2
                
                # if i is 0 this is a vertical line
                if i == 0:
                    grid_label.setPos( line[0].p1().x() - width, line[0].p1().y() - 1.75*height )
                # else this is a horizontal line
                else:
                    grid_label.setPos( line[0].p1().x() - 1.75*width, line[0].p1().y() - height)

                self.scene.addItem(grid_label)
                if line[1]:
                    self.scene.addLine( line[0], major )
                else:
                    cur = self.scene.addLine( line[0], minor )
                    self.minorgrid.append(cur)
                    self.gridlabels.append(grid_label)

    # 'zoom_in' handles the zooming of the image and the related scaling of the waypoints
    def zoom_in(self):
        if self.zoom_level < self.zoom_max:
            self.scale(1.25, 1.25)
            self.zoom_level += 1
            self.wpt_cur_scale *= 0.8
            if self.waypoints:
                for key, val in self.waypoints.items():
                    val.setScale(self.wpt_cur_scale)

    # 'zoom_out' handles the zooming of the image and the related scaling of the waypoints
    def zoom_out(self):
        if self.zoom_level > self.zoom_min:
            self.scale(0.8, 0.8)
            self.zoom_level -= 1
            self.wpt_cur_scale *= 1.25
            if self.waypoints:
                for key, val in self.waypoints.items():
                    val.setScale(self.wpt_cur_scale)

    # 'delete_waypoint' deletes the specified waypoint if it exists
    def delete_waypoint(self, _key):
        if self.waypoints and _key not in self.key_array:
            self.scene.removeItem(self.waypoints[_key])
            self.key_array.append(_key)
            num_keys = []
            for x in self.key_array[:]:
                if x.isnumeric():
                    num_keys.append(x)
                    self.key_array.remove(x)
            self.key_array.sort(reverse = True)
            num_keys.sort(reverse = True)
            self.key_array = num_keys + self.key_array
            del self.waypoints[_key]

    # 'add_waypoint' adds a waypoint to the image if there are less than 26 on screen
    def add_waypoint(self, x, y, shift=True):
        if self.key_array:
            _key = self.key_array.pop()
            _alpha_pin_path = '../../assets/pins/pin_' + _key + '.png'
            self.waypoint_icon = QPixmap(os.path.join(self.cur_path, _alpha_pin_path))
            self.waypoint = QGraphicsPixmapItem(self.waypoint_icon)
            self.waypoint.setTransformOriginPoint(self.waypoint_icon.width() / 2, self.waypoint_icon.height())
            if shift:
                self.waypoint.setPos(x - (self.waypoint_icon.width() / 2), y - self.waypoint_icon.height())
            else:
                self.waypoint.setPos(x,y)
            self.waypoint.setScale(self.wpt_cur_scale)
            self.scene.addItem(self.waypoint)
            self.waypoints[_key] = self.waypoint
            if shift:
                self.add_delete_waypoint_signal.emit( 1, _key, x - (self.waypoint_icon.width() / 2), y - self.waypoint_icon.height())
            else:
                self.add_delete_waypoint_signal.emit( 1, _key, x, y )


    ###################################
    # Button press functions
    ###################################

    def zoom_in_btn_press(self):
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        self.zoom_in()

    def zoom_out_btn_press(self):
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        self.zoom_out()

    def expand_btn_press(self):
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.zoom_level = self.zoom_min
        self.wpt_cur_scale = self.wpt_max_scale
        if self.waypoints:
            for key, val in self.waypoints.items():
                val.setScale(self.wpt_cur_scale)

    def visibility_wpts_btn_press(self):
        if self.waypoints and self.waypoints[list(self.waypoints.keys())[0]].isVisible():
            for x in self.waypoints:
                self.waypoints[x].hide()
        else:
            for x in self.waypoints:
                self.waypoints[x].show()

    def undo_wpt_btn_press(self):
        if self.waypoints:
            self.add_delete_waypoint_signal.emit(0, list(self.waypoints.keys())[-1], 0, 0)

    ###################################
    # Mouse interaction functions
    ###################################

    # 'wheelEvent' is used to register zooming of the image with the mouse scroll wheel
    def wheelEvent(self, event):
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    # 'mousePressEvent' is used to register panning of the image with the left mouse button
    # 'mousePressEvent' is used to register the adding of waypoints with the right mouse button
    def mousePressEvent(self, event):
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.RightButton:
            self.add_waypoint(scenePos.x(), scenePos.y())
        else:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        QGraphicsView.mousePressEvent(self, event)

    # 'mouseReleaseEvent' is used to stop the panning of the image upon the release of the left mouse button
    def mouseReleaseEvent(self, event):
        QGraphicsView.mouseReleaseEvent(self, event)
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)

#########################################################################################
