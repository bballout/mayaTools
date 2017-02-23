'''
Created on Jun 29, 2012

@author: balloutb
'''

from PySide import QtCore,QtGui
import UILib

##Main window
class CharToolsMainWin(QtGui.QMainWindow):
    
    def __init__(self, parent = UILib.getMayaWindow()):
        super(CharToolsMainWin,self).__init__(parent)
        
        self.initUI()
        
    def initUI(self):
          
        #setting window properties
        self.setWindowTitle('Pose Manager')
        self.layout = QtGui.QHBoxLayout()  
        self.setGeometry(400,250,710,660)
        
        #adding widgets
        self.setLayout(self.layout)
        self.menuBar = PoseManagerMenuBar(parent = self)
        self.toolBar = PoseManagerToolBar(objectName = 'ToolBar',parent = self)
        self.toolBar.setFloatable(False)
        self.addToolBar(self.toolBar)
        self.picture = PoseManagerCentralWidget()
        self.picture.setObjectName('Preview')
        self.setMenuBar(self.menuBar)
        self.setCentralWidget(self.picture)
        self.poseStatusBar = PoseManagerStatusBar(self)
        self.setStatusBar(self.poseStatusBar)
        #create side dock
        self.listDock = QtGui.QDockWidget('Pose List',self)
        self.listDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
        
        self.poseList = PoseManagerListWidget()
        self.listDock.setWidget(self.poseList)
        
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.listDock)
        
class PoseManagerStatusBar(QtGui.QStatusBar):
    
    def __init__(self,parent = None):
        
        super(PoseManagerStatusBar,self).__init__(parent)
        self.initStatusBar()
        
    def initStatusBar(self):
           
        statusFrame = QtGui.QFrame()
        statusFrame.setFrameStyle(QtGui.QFrame.Sunken)
        self.addPermanentWidget(statusFrame)
            

class PoseManagerMenuBar(QtGui.QMenuBar):
    
    def __init__(self, parent = None):
        super(PoseManagerMenuBar,self).__init__(parent)
        
        self.initMenu()
        
    def initMenu(self):
        
        fileAction = QtGui.QAction(self)
        fileAction.setText('File')
        
        editAction = QtGui.QAction(self)
        editAction.setText('Edit')
        
        self.addAction(fileAction)
        self.addAction(editAction)      
    
class PoseManagerToolBar(QtGui.QToolBar):
       
    def __init__(self,objectName = None,parent = None):
        
        super(PoseManagerToolBar,self).__init__(objectName,parent)
        self.initWidget()
        
    def initWidget(self):
        
        self.browseButton = QtGui.QPushButton()
        saveButtonIcon = QtGui.QIcon('C:/Icons/browse.png')
        self.browseButton.setIcon(saveButtonIcon)
        self.workSpaceField = QtGui.QLineEdit()
        self.workSpaceField.setMaximumWidth(200)
        self.saveButton = QtGui.QPushButton()
        saveButtonIcon = QtGui.QIcon('C:/Icons/save.png')
        self.saveButton.setIcon(saveButtonIcon)
        self.saveButton.move(5,0)
        self.addWidget(self.browseButton)
        self.addWidget(self.workSpaceField)
        self.addWidget(self.saveButton)
        
   
class PoseManagerCentralWidget(QtGui.QWidget):
    
    pic = QtGui.QImage('C:/Users/Bill/Desktop/image.png' , 'png')
       
    def __init__(self,parent = None):
        
        super(PoseManagerCentralWidget,self).__init__(parent)
        self.initWidget()
        
    def initWidget(self):
        
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        
        self.scrollArea = QtGui.QScrollArea(self)
        self.layout.addWidget(self.scrollArea)
        
        self.image = self.pic.scaled(400, 600,QtCore.Qt.KeepAspectRatioByExpanding)
        
        self.picLabel = QtGui.QLabel(self)
        self.picLabel.setMaximumSize(400, 600)
        self.picLabel.setAlignment(QtCore.Qt.AlignCenter)
        pixMap = QtGui.QPixmap.fromImage(self.image)
        self.picLabel.setPixmap(pixMap)
        
        
        pictureFrame = QtGui.QFrame()
        pictureFrame.setFrameStyle(QtGui.QFrame.Raised)
        pictureFrame.setMaximumSize(400, 600)
        
        pictureFrameLayout = QtGui.QVBoxLayout()
        pictureFrameLayout.addWidget(self.picLabel)
        pictureFrame.setLayout(pictureFrameLayout)
        
        self.scrollArea.setWidget(pictureFrame)
        self.scrollArea.setWidgetResizable(True)

    def switchImage(self,imagePath,imageFormat):
        
        self.pic.__init__(imagePath,imageFormat)
        self.image = self.pic.scaled(400, 600,QtCore.Qt.KeepAspectRatioByExpanding)
        
        self.picLabel.setPixmap(QtGui.QPixmap.fromImage(self.image))
        
        
class PoseListWidget(QtGui.QWidget):
    
    def __init__(self, parent = None):
        
        super(PoseListWidget,self).__init__(parent)
        self.initWidget()
        
    def initWidget(self):

        self.layout = QtGui.QHBoxLayout()
        self.setLayout(self.layout)
        
        frame = QtGui.QFrame()
        self.listWidget = QtGui.QListWidget()
        
        frameLayout = QtGui.QVBoxLayout()
        frameLayout.addWidget(self.listWidget)
        frame.setLayout(frameLayout)
        
        self.layout.addWidget(frame)
    

class ControlSetListWidget(QtGui.QWidget):
    
    def __init__(self, parent = None):
        
        super(ControlSetListWidget,self).__init__(parent)
        self.initWidget()
        
    def initWidget(self):

        self.layout = QtGui.QHBoxLayout()
        self.setLayout(self.layout)
        
        frame = QtGui.QFrame()
        self.listWidget = QtGui.QListWidget()
        
        frameLayout = QtGui.QVBoxLayout()
        frameLayout.addWidget(self.listWidget)
        frame.setLayout(frameLayout)
        
        self.layout.addWidget(frame)

class PoseManagerListWidget(QtGui.QWidget):
    
    def __init__(self, parent = None):
        
        super(PoseManagerListWidget,self).__init__(parent)
        self.initWidget()
        
    def initWidget(self):
        
        self.layout = QtGui.QHBoxLayout()
        self.setLayout(self.layout)
        
        self.splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.poseList = PoseListWidget()
        self.controlList = ControlSetListWidget()
        
        self.splitter.addWidget(self.poseList)
        self.splitter.addWidget(self.controlList)
        
        self.layout.addWidget(self.splitter)
        
        
           
