'''
Created on Jun 29, 2012

@author: balloutb
'''

import maya.OpenMaya as om
import maya.OpenMayaUI as mui
import maya.cmds as cmds

#QT4
try:
  try:
      from PySide import QtGui,QtCore
      from PySide.QtGui import QWidget as QWidget
      from PySide.QtGui import QMainWindow as QMainWindow
      from PySide.QtGui import QDialog as QDialog
      from PySide.QtGui import QMenuBar as QMenuBar
      from PySide.QtGui import QMenu as QMenu
      from PySide.QtGui import QAction as QAction
      from PySide.QtGui import QFrame as QFrame
      from PySide.QtGui import QGridLayout as QGridLayout
      from PySide.QtGui import QPushButton as QPushButton
      from PySide.QtGui import QHBoxLayout as QHBoxLayout
      from PySide.QtGui import QVBoxLayout as QVBoxLayout
      from PySide.QtGui import QLineEdit as QLineEdit
      from PySide.QtGui import QSlider as QSlider
      from PySide.QtGui import QDoubleSpinBox as QDoubleSpinBox
      from PySide.QtGui import QLabel as QLabel
      from PySide.QtGui import QGroupBox as QGroupBox
      from PySide.QtGui import QRadioButton as QRadioButton
      from PySide.QtGui import QCheckBox as QCheckBox
      from PySide.QtGui import QListWidget as QListWidget
      from PySide.QtGui import QColor as QColor
      
      from PySide import shiboken 
  except ImportError:
      import shiboken
#QT5      
except ImportError:
  from PySide2 import QtGui,QtWidgets,QtCore
  from PySide2.QtWidgets import QWidget as QWidget
  from PySide2.QtWidgets import QMainWindow as QMainWindow
  from PySide2.QtWidgets import QDialog as QDialog
  from PySide2.QtWidgets import QMenuBar as QMenuBar
  from PySide2.QtWidgets import QMenu as QMenu
  from PySide2.QtWidgets import QAction as QAction
  from PySide2.QtWidgets import QFrame as QFrame
  from PySide2.QtWidgets import QGridLayout as QGridLayout
  from PySide2.QtWidgets import QPushButton as QPushButton
  from PySide2.QtWidgets import QHBoxLayout as QHBoxLayout
  from PySide2.QtWidgets import QVBoxLayout as QVBoxLayout
  from PySide2.QtWidgets import QLineEdit as QLineEdit
  from PySide2.QtWidgets import QSlider as QSlider
  from PySide2.QtWidgets import QDoubleSpinBox as QDoubleSpinBox
  from PySide2.QtWidgets import QLabel as QLabel
  from PySide2.QtWidgets import QGroupBox as QGroupBox
  from PySide2.QtWidgets import QRadioButton as QRadioButton
  from PySide2.QtWidgets import QCheckBox as QCheckBox
  from PySide2.QtWidgets import QListWidget as QListWidget
  from PySide2.QtGui import QColor as QColor
  import shiboken2
   

import ToolBoxFn
import MayaScripts


#Get the maya main window as a QMainWindow instance
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    if not ptr == None:
      try:
        return shiboken.wrapInstance(long(ptr), QMainWindow)
      except:
        return shiboken2.wrapInstance(long(ptr), QMainWindow)
      
    return (long(ptr), QMainWindow)
    

#fuction for creating an image from the viewPort
#input path (python string)
#input imageName (python string)
#input imageFormat (python string)
#input imageSize (python list[int,int])
#input ration (python bool)
def captureViewport(**kwargs):
    
    path = kwargs.get('path','C:/temp') 
    imageName = kwargs.get('imageName','image')
    imageFormat = kwargs.get('imageFormat','bmp')
    imageSize = kwargs.get('imageSize',[600,800])
    ratio = kwargs.get('ratio',True)
    
    fullPath = '%s/%s.%s'%(path,imageName,imageFormat)
    
    view = mui.M3dView.active3dView()
    view.refresh()

    origStyle = view.displayStyle()
    
    view.setObjectDisplay(view.kDisplayMeshes)
    view.setDisplayStyle(view.kGouraudShaded,False)
    
    view.refresh(True,True)
    view.refresh(True,True)
     
    image = om.MImage()
    view.readColorBuffer(image,True)
    
    image.resize(imageSize[0],imageSize[1],ratio)
    image.writeToFile(fullPath, imageFormat)

    view.setObjectDisplay(4294967295L)
    view.setDisplayStyle(origStyle)
    
    

class ProgressWin(mui.MProgressWindow):
    
    '''blueprint for building progress windows'''
    
    inc = 0
    itr = 0
    startMessage = ''
    message = ''
    endMessage = ''
    
    def __init__(self):
        
        self.reserve()
        self.setProgressStatus(self.startMessage)       
        self.startProgress()
        
    def progress(self):
        
        self.setProgressStatus(self.message)
        self.setProgress(int(float(self.inc)/float(self.itr) * 100))
                  
    def end(self):
        
        print self.endMessage
        self.endProgress()
         
        
class ButtonPopUpMenu(QWidget):

    def __init__(self, objectName ='Button', parent=None):
        super(ButtonPopUpMenu, self).__init__(parent)

        layout = QHBoxLayout()
        self.setLayout(layout)
        
        self.button = QPushButton()
        self.button.setText('Button')
        self.button.setGeometry(0,10,10,20)
        self.menu = QMenu()

        self.button.setMenu(self.menu)

        layout.addWidget(self.button)
        
    def addMenuItem(self,label,func):
        
        action = self.menu.addAction(label)
        action.triggered.connect(func)
        
class ButtonFieldGroup(QWidget):
    
    def __init__(self, objectName  ='ButtonField', parent=None):
        super(ButtonFieldGroup, self).__init__(parent)
        
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        self.field = QLineEdit() 
        self.button = QPushButton()
        self.button.setGeometry(20,20,20,20)
        self.button.setText('<<<')
        
        
        layout.addWidget(self.field)
        layout.addWidget(self.button)
        
            
class FillSelectedField(ButtonFieldGroup):
    
    def __init__(self, objectName  ='ButtonField', parent=None):
        super(FillSelectedField, self).__init__(parent = parent,objectName = objectName)
        
        self.connect(self.button,QtCore.SIGNAL('clicked()'),self.buttonFn)
        
    def buttonFn(self):
    
        sel = cmds.ls(sl = True)
        
        if not sel == []:
            
            self.field.setText(sel[0])
            
class FloatSlider(QWidget):
    
    def __init__(self,parent = None):
        super(FloatSlider, self).__init__(parent = parent)
        
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        self.slider = QSlider()
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.spinBox = QDoubleSpinBox()
        self.spinBox.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        
        layout.addWidget(self.slider)
        layout.addWidget(self.spinBox)
        
        self.connect(self.slider,QtCore.SIGNAL('sliderReleased()'),self.sliderValueChanged)
        self.connect(self.spinBox,QtCore.SIGNAL('editingFinished()'),self.spinBoxValueChanged)
        
    def sliderValueChanged(self):
        value = self.slider.sliderPosition()
        self.spinBox.setValue(value)
        
    def spinBoxValueChanged(self):
        value = self.spinBox.value()
        self.slider.setSliderPosition(value)
        
    def getValue(self):
        value = self.spinBox.value()
        return value
        
            
class FillDeformerNameField(ButtonFieldGroup):
    
    def __init__(self, objectName  ='ButtonField', parent=None):
        super(FillDeformerNameField, self).__init__(parent = parent,objectName = objectName)
        
        self.connect(self.button,QtCore.SIGNAL('clicked()'),self.buttonFn)
        
    def buttonFn(self):
        
        transform = cmds.ls(sl = True)
        
        if not transform == []:
        
            shape = cmds.listRelatives(transform[0],type = 'shape')[0]
            nodeType = cmds.nodeType(shape)
            
            deformerName = ''
            
            if nodeType == 'clusterHandle':
                
                connection = cmds.connectionInfo('%s.worldMatrix[0]'%transform[0], dfs = True)[0]
                deformerName = connection.split('.')[0]
                
            elif nodeType == 'nurbsCurve':
    
                connection = cmds.connectionInfo('%s.worldSpace[0]'%shape, dfs = True)[0]
                deformerName = connection.split('.')[0]
                
            if not deformerName == '':
                
                self.field.setText(deformerName)

            
class TransferWeightsDialog(QDialog):
    
    def __init__(self, parent = getMayaWindow()):
        super(TransferWeightsDialog,self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.initUI()
        
    def initUI(self):
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setSpacing(0)
        self.setGeometry(450,200,450,200)
        self.setWindowTitle('Transfer Deformer Weights')
        
        self.fromDeformerLabel = QLabel()
        self.fromDeformerLabel.setText('From Deformer:')
        self.fromDeformerField = FillDeformerNameField()
        layout.addWidget(self.fromDeformerLabel)
        layout.addWidget(self.fromDeformerField)
        
        self.toDeformerLabel = QLabel()
        self.toDeformerLabel.setText('To Deformer:')
        self.toDeformerField = FillDeformerNameField()
        layout.addWidget(self.toDeformerLabel)
        layout.addWidget(self.toDeformerField)
        
        divider01 = QFrame()
        divider01.setFrameShape(QFrame.HLine)
        layout.addWidget(divider01)
        
        fromMeshLabel = QLabel()
        fromMeshLabel.setText('From Mesh:')
        self.fromMeshField = FillSelectedField()
        layout.addWidget(fromMeshLabel)
        layout.addWidget(self.fromMeshField)
        
        toMeshLabel = QLabel()
        toMeshLabel.setText('To Mesh:')
        self.toMeshfield = FillSelectedField()
        layout.addWidget(toMeshLabel)
        layout.addWidget(self.toMeshfield)      
        
        operationWidget = QWidget()
        operationWidgetLayout  = QHBoxLayout()
        operationWidget.setLayout(operationWidgetLayout)
        
        operationButtons = QGroupBox()
        operationButtonsLayout = QHBoxLayout()
        self.transferButton = QRadioButton()
        self.transferButton.setText('transfer')
        self.transferButton.setChecked(True)
        self.mirrorButton = QRadioButton()
        self.mirrorButton.setText('mirror')
        self.reverseButton = QRadioButton()
        self.reverseButton.setText('reverse')
        operationButtons.setTitle('operation:')
        operationButtonsLayout.addWidget(self.transferButton)
        operationButtonsLayout.addWidget(self.mirrorButton)
        operationButtonsLayout.addWidget(self.reverseButton)
        operationButtons.setLayout(operationButtonsLayout)
        
        operationWidgetLayout.addWidget(operationButtons)
        layout.addWidget(operationWidget)
        
        axisWidget = QWidget()
        axisWidgetLayout  = QHBoxLayout()
        axisWidget.setLayout(axisWidgetLayout)
        
        axisButtons = QGroupBox()
        axisButtonsLayout = QHBoxLayout()
        self.axisXButton = QRadioButton()
        self.axisXButton.setText('x')
        self.axisXButton.setChecked(True)
        self.axisYButton = QRadioButton()
        self.axisYButton.setText('y')
        self.axisZButton = QRadioButton()
        self.axisZButton.setText('z')
        axisButtons.setTitle('axis:')
        axisButtonsLayout.addWidget(self.axisXButton)
        axisButtonsLayout.addWidget(self.axisYButton)
        axisButtonsLayout.addWidget(self.axisZButton)
        axisButtons.setLayout(axisButtonsLayout)
                
        self.directionCheckBox = QCheckBox()
        self.directionCheckBox.setText('Pos to Neg') 
        self.directionCheckBox.setChecked(True) 
        axisButtonsLayout.addWidget(self.directionCheckBox)
        
        axisWidgetLayout.addWidget(axisButtons)
        layout.addWidget(axisWidget)
        
        buttonsWidget = QWidget()
        butttonsWidgetLayout = QHBoxLayout()
        buttonsWidget.setLayout(butttonsWidgetLayout)
        
        self.applyButton = QPushButton()
        self.applyButton.setText('Apply')
        self.connect(self.applyButton,QtCore.SIGNAL('clicked()'),self.applyFn)

        self.closeButton = QPushButton()
        self.closeButton.setText('Close')
        self.connect(self.closeButton,QtCore.SIGNAL('clicked()'),self.close)
        butttonsWidgetLayout.addWidget(self.applyButton)
        butttonsWidgetLayout.addWidget(self.closeButton)
        
        layout.addWidget(buttonsWidget)
        
    def applyFn(self):
        
        fromDeformer = str(self.fromDeformerField.field.text())
        toDeformer = str(self.toDeformerField.field.text())
        fromMesh = str(self.fromMeshField.field.text())
        toMesh = str(self.toMeshfield.field.text())
        axis = ''
        direction = ''
        table = []
        
        if self.axisXButton.isChecked():
            
            axis = 'x'
            table = [-1,1,1]
            
        if self.axisYButton.isChecked():
            
            axis = 'y'
            table = [1,-1,1]
            
        if self.axisZButton.isChecked():
            
            axis = 'z'
            table = [1,1,-1]
            
        if self.directionCheckBox.isChecked():
            
            direction = '<'
            
        else:
            
            direction = '>'
            
        if not fromDeformer == '' and not toDeformer == '' and not fromMesh == '' and not toMesh == '':
          
            if self.transferButton.isChecked():
                
                eval('ToolBoxFn.transferWeights(\'%s\',\'%s\',\'%s\',\'%s\')'%(fromMesh,toMesh,fromDeformer,toDeformer))
            
            if self.mirrorButton.isChecked():
                
                eval('ToolBoxFn.transferMirroredWeights(\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',[%i,%i,%i])'%
                (fromMesh,toMesh,fromDeformer,toDeformer,axis,direction,table[0],table[1],table[2]))
            
            if self.reverseButton.isChecked():
                
                eval('ToolBoxFn.transferReversedWeights(\'%s\',\'%s\',\'%s\',\'%s\')'%(fromMesh,toMesh,fromDeformer,toDeformer))
            
        else:
            
            om.MGlobal.displayError('Not enough info for request')
              
        
class MirrorWeightsDialog(QDialog):
    
    def __init__(self, parent = getMayaWindow()):
        super(MirrorWeightsDialog,self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.initDialog()
        
    def initDialog(self):
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle('Mirror Cluster')
        self.setGeometry(425,300,425,300)
        
        tranformNameWidget = QWidget()
        transformNameLayout = QVBoxLayout()
        tranformNameWidget.setLayout(transformNameLayout)
        transformNameLabel = QLabel()
        transformNameLabel.setText('Transform Name:')
        self.transformButton = FillSelectedField()
        transformNameLayout.addWidget(transformNameLabel)
        transformNameLayout.addWidget(self.transformButton)
        
        deformerNameWidget = QWidget()
        deformerNameWidgetLayout = QVBoxLayout()
        deformerNameWidget.setLayout(deformerNameWidgetLayout)
        deformerNameLabel = QLabel()
        deformerNameLabel.setText('Deformer Name:')
        self.deformerNameField = QLineEdit()        
        deformerNameWidgetLayout.addWidget(deformerNameLabel)
        deformerNameWidgetLayout.addWidget(self.deformerNameField)
        
        divider01 = QFrame()
        divider01.setFrameShape(QFrame.HLine)
        
        prefixWidget = QWidget()
        prefixWidgetLayout = QVBoxLayout()
        prefixWidget.setLayout(prefixWidgetLayout)
        searchPrefixLabel = QLabel()
        searchPrefixLabel.setText('Search for:')
        self.searchPrefixField = QLineEdit()
        self.searchPrefixField.setText('L_')
        replacePrefixLabel = QLabel()
        replacePrefixLabel.setText('Replace with')
        self.replacePrefixField = QLineEdit()
        self.replacePrefixField.setText('R_')
        prefixWidgetLayout.addWidget(searchPrefixLabel)
        prefixWidgetLayout.addWidget(self.searchPrefixField)
        prefixWidgetLayout.addWidget(replacePrefixLabel)
        prefixWidgetLayout.addWidget(self.replacePrefixField) 
        
        divider02 = QFrame()
        divider02.setFrameShape(QFrame.HLine)
        
        operationWidget = QWidget()
        operationLayout = QHBoxLayout()
        operationWidget.setLayout(operationLayout)
        operationButtonGrp = QGroupBox()
        operationButtonGrpLayout = QHBoxLayout()
        operationButtonGrp.setLayout(operationButtonGrpLayout)
        operationButtonGrp.setTitle('operation:')
        self.mirrorButton = QRadioButton()
        self.mirrorButton.setText('mirror cluster')
        self.mirrorButton.setChecked(True)
        self.mirrorWeightButton = QRadioButton()
        self.mirrorWeightButton.setText('mirror weights')   
        self.flipButton = QRadioButton()
        self.flipButton.setText('flip weights')
        operationButtonGrpLayout.addWidget(self.mirrorButton)
        operationButtonGrpLayout.addWidget(self.mirrorWeightButton)
        operationButtonGrpLayout.addWidget(self.flipButton)
        operationLayout.addWidget(operationButtonGrp)
        
        mirrorSetttingWidget = QWidget()
        mirrorSetttingWidgetLayout  = QHBoxLayout()
        mirrorSetttingWidget.setLayout(mirrorSetttingWidgetLayout)
        axisButtonGroup = QGroupBox()
        axisButtonLayout = QHBoxLayout()
        self.axisXButton = QRadioButton()
        self.axisXButton.setText('x')
        self.axisXButton.setChecked(True)
        self.axisYButton = QRadioButton()
        self.axisYButton.setText('y')
        self.axisZButton = QRadioButton()
        self.axisZButton.setText('z')
        axisButtonGroup.setTitle('Axis:')
        axisButtonLayout.addWidget(self.axisXButton)
        axisButtonLayout.addWidget(self.axisYButton)
        axisButtonLayout.addWidget(self.axisZButton)
        axisButtonGroup.setLayout(axisButtonLayout)
        mirrorSetttingWidgetLayout.addWidget(axisButtonGroup)
        
        self.directionCheckBox = QCheckBox()
        self.directionCheckBox.setText('Pos to Neg') 
        self.directionCheckBox.setChecked(True) 
        axisButtonLayout.addWidget(self.directionCheckBox)
        
        buttonsWidget = QWidget()
        butttonsWidgetLayout = QHBoxLayout()
        buttonsWidget.setLayout(butttonsWidgetLayout)
        
        self.connect(self.transformButton.button, QtCore.SIGNAL('clicked()'),self.fillDeformerName)
        
        self.applyButton = QPushButton()
        self.applyButton.setText('Apply')
        self.connect(self.applyButton, QtCore.SIGNAL('clicked()'), self.applyFn)
        
        self.closeButton = QPushButton()
        self.closeButton.setText('Close')
        self.connect(self.closeButton,QtCore.SIGNAL('clicked()'),self.close)
        
        butttonsWidgetLayout.addWidget(self.applyButton)
        butttonsWidgetLayout.addWidget(self.closeButton)
        
        layout.addWidget(tranformNameWidget)      
        layout.addWidget(deformerNameWidget)
        layout.addWidget(divider01)
        layout.addWidget(prefixWidget)
        layout.addWidget(divider02)
        layout.addWidget(operationWidget)
        layout.addWidget(mirrorSetttingWidget)
        layout.addWidget(buttonsWidget)
        
    def fillDeformerName(self):
        
        transform = str(self.transformButton.field.text())
        shape = cmds.listRelatives(transform,type = 'shape')[0]
        nodeType = cmds.nodeType(shape)
        
        deformerName = ''
        
        if nodeType == 'clusterHandle':
            
            connection = cmds.connectionInfo('%s.worldMatrix[0]'%transform, dfs = True)[0]
            deformerName = connection.split('.')[0]
            
        elif nodeType == 'nurbsCurve':

            connection = cmds.connectionInfo('%s.worldSpace[0]'%shape, dfs = True)[0]
            deformerName = connection.split('.')[0]
            
        if not deformerName == '':
            
            self.deformerNameField.setText(deformerName)

    def applyFn(self):
        
        transformName = str(self.transformButton.field.text())
        deformerName = str(self.deformerNameField.text())
        prefix = str(self.searchPrefixField.text())
        oppPrefix = str(self.replacePrefixField.text())
        
        axis = ''
        table = []
        
        if self.axisXButton.isChecked():
            axis = 'x'
            table = [-1,1,1]
            
        elif self.axisYButton.isChecked():
            axis = 'y'
            table = [1,-1,1]
            
        elif self.axisZButton.isChecked():
            axis = 'z'
            table = [1,1,-1]
               
               
        direction = ''
        
        if self.directionCheckBox.isChecked():
            direction = '>'
            
        else:
            direction = '<'
        
        if not deformerName == '' and not prefix == '' and not oppPrefix == '':
            
            if self.mirrorButton.isChecked():
                eval('ToolBoxFn.mirrorDeformer(transform = \'%s\',deformerName = \'%s\',prefix = \'%s\',oppPrefix = \'%s\',axis = \'%s\',direction = \'%s\',table = %s)'%
                     (transformName,deformerName,prefix,oppPrefix,axis,direction,table))
                
            if self.mirrorWeightButton.isChecked():
                eval('ToolBoxFn.mirrorDeformerWeights(deformerName = \'%s\',prefix = \'%s\',oppPrefix = \'%s\',direction = \'%s\',axis = \'%s\', table = %s)'%
                     (deformerName,prefix,oppPrefix,direction,axis,table))
                
            if self.flipButton.isChecked():
                eval('ToolBoxFn.flipClusterWeights(deformer = \'%s\',prefix = \'%s\',oppPrefix = \'%s\',axis = \'%s\',direction = \'%s\',table = %s)'%
                     (deformerName,prefix,oppPrefix,axis,direction,table))

        else:
            
            om.MGlobal.displayError('Not enough info provided for request.')
            
class ClustertoJointWin(QDialog):
    
    def __init__(self,parent = None):
        super(ClustertoJointWin,self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle('Cluster To Joint')
        self.setGeometry(425,300,425,300)
        self.initDialog()
        
    def initDialog(self):
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle('Cluster To Joint')
        self.setGeometry(425,300,425,300)
        
        geoFieldWidget = QWidget()
        deformerFieldLayout = QVBoxLayout()
        geoFieldWidget.setLayout(deformerFieldLayout)
        geoNameLabel = QLabel()
        geoNameLabel.setText('Geo Name:')
        self.geoNameField = FillSelectedField()
        
        deformerFieldLayout.addWidget(geoNameLabel)
        deformerFieldLayout.addWidget(self.geoNameField)
        
        deformerFieldWidget = QWidget()
        deformerFieldLayout = QVBoxLayout()
        deformerFieldWidget.setLayout(deformerFieldLayout)
        deformerNameLabel = QLabel()
        deformerNameLabel.setText('From Deformer Weights')
        self.deformerFillField = FillDeformerNameField()
        
        deformerFieldLayout.addWidget(deformerNameLabel)
        deformerFieldLayout.addWidget(self.deformerFillField)
        
        jointFieldWidget = QWidget()
        jointFieldLayout = QVBoxLayout()
        jointFieldWidget.setLayout(jointFieldLayout)
        jointFromLabel = QLabel()
        jointFromLabel.setText('Take Influence Weight From:')
        self.jointFromButton = FillSelectedField()
        
        jointFieldLayout.addWidget(jointFromLabel)
        jointFieldLayout.addWidget(self.jointFromButton)
        
        jointToLabel = QLabel()
        jointToLabel.setText('Set Influence Weight for:')
        self.jointToButton = FillSelectedField()
        
        divider01 = QFrame()
        divider01.setFrameShape(QFrame.HLine)
        
        divider02 = QFrame()
        divider02.setFrameShape(QFrame.HLine)
        
        divider03 = QFrame()
        divider03.setFrameShape(QFrame.HLine)

        jointFieldLayout.addWidget(jointToLabel)
        jointFieldLayout.addWidget(self.jointToButton)
        
        buttonsWidget = QWidget()
        butttonsWidgetLayout = QHBoxLayout()
        buttonsWidget.setLayout(butttonsWidgetLayout)
        
        self.applyButton = QPushButton()
        self.applyButton.setText('Apply')
        self.connect(self.applyButton,QtCore.SIGNAL('clicked()'),self.applyFn)
        
        self.closeButton = QPushButton()
        self.closeButton.setText('Close')
        self.connect(self.closeButton,QtCore.SIGNAL('clicked()'),self.close)
        butttonsWidgetLayout.addWidget(self.applyButton)
        butttonsWidgetLayout.addWidget(self.closeButton)
        
        layout.addWidget(geoFieldWidget)
        layout.addWidget(divider01)
        layout.addWidget(deformerFieldWidget)
        layout.addWidget(divider02)
        layout.addWidget(jointFieldWidget)
        layout.addWidget(divider03)
        layout.addWidget(buttonsWidget)

    def applyFn(self):
        
        geoName = str(self.geoNameField.field.text())
        fromDeformer = str(self.deformerFillField.field.text())
        fromJoint = str(self.jointFromButton.field.text())
        toJoint = str(self.jointToButton.field.text())
        
        try:
            ToolBoxFn.clusterToJoint(geoName, fromDeformer, fromJoint, toJoint)
            om.MGlobal.displayInfo('Weights for %s set on %s.'%(fromJoint,geoName))
            
        except:
            om.MGlobal.displayError('Can not send weights on %s.'%geoName)
            
class OptimizeDeformerDialog(QDialog):
    
    def __init__(self,parent = None):
        super(OptimizeDeformerDialog,self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle('Optimize Deformer')
        self.setGeometry(600,325,300,325)
        
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        listLayout = QVBoxLayout()
        
        self.deformerList = QListWidget()
        self.deformerLoadButton = QPushButton()
        self.deformerLoadButton.setText('Load Deformers')

        frame = QFrame()
        frame.setFrameStyle(QFrame.Panel)
        mainLayout.addWidget(frame)

        frame.setLayout(listLayout)
        
        self.spinBoxButtonGrp = QWidget()
        spinBoxButtonLayout = QGridLayout()
        self.spinBoxButtonGrp.setLayout(spinBoxButtonLayout)
        pruneLabel = QLabel()
        pruneLabel.setText('Prune Weight:')
        self.pruneSpinBox = QDoubleSpinBox()
        self.pruneSpinBox.setMinimum(0.0005)
        self.pruneSpinBox.setMaximum(1.000)
        self.pruneSpinBox.setValue(0.001)
        self.pruneSpinBox.setDecimals(4)
        self.pruneSpinBox.setSingleStep(0.001)
        self.optimizeButton = QPushButton()
        self.optimizeButton.setText('Optimize')
        spinBoxButtonLayout.addWidget(pruneLabel,0,0)
        spinBoxButtonLayout.addWidget(self.pruneSpinBox,1,0)
        spinBoxButtonLayout.addWidget(self.optimizeButton,1,1)
        
        spinBoxButtonLayout.setColumnStretch(1,20)
        
        listLayout.addWidget(self.deformerList)
        listLayout.addWidget(self.deformerLoadButton)
        mainLayout.addWidget(self.spinBoxButtonGrp)

        self.connect(self.deformerLoadButton, QtCore.SIGNAL('clicked()'),self.loadDeformers)
        self.connect(self.optimizeButton, QtCore.SIGNAL('clicked()'),self.optimizeFunc)
        
        
    def loadDeformers(self):
        
        self.deformerList.clear()
        sel = cmds.ls(sl = True)
        
        for obj in sel:
            
            transform = obj
            shape = cmds.listRelatives(transform,type = 'shape')[0]
            nodeType = cmds.nodeType(shape)
            
            deformerName = ''
            
            if nodeType == 'clusterHandle':
                
                connection = cmds.connectionInfo('%s.worldMatrix[0]'%transform, dfs = True)[0]
                deformerName = connection.split('.')[0]
                
            elif nodeType == 'nurbsCurve':
    
                connection = cmds.connectionInfo('%s.worldSpace[0]'%shape, dfs = True)[0]
                deformerName = connection.split('.')[0]
            
            if not deformerName  == '':
                self.deformerList.addItem(deformerName)
        
    def optimizeFunc(self):
        
        deformers = []
        deformerCount = self.deformerList.count()
        
        for i in range(deformerCount):
            deformerName = self.deformerList.item(i).text()
            deformers.append(deformerName)
        
        prune = self.pruneSpinBox.value()
        
        for deformer in deformers:
            try:
                ToolBoxFn.optimizedDeformer(deformer, prune)
                
            except:
                pass
        
           
class RenameWindow(QDialog):
    
    def __init__(self,parent = getMayaWindow()):
        super(RenameWindow,self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        layout = QVBoxLayout()
        
        self.setLayout(layout)
        self.setWindowTitle('Renamer')
        self.setGeometry(900,600,250,75)
        
        textHelp = QLabel()
        textHelp.setText('Name_**_Name')
        self.textField = QLineEdit()
        self.renameButton = QPushButton()
        self.renameButton.setText('Apply')
        
        layout.addWidget(textHelp)
        layout.addWidget(self.textField)
        layout.addWidget(self.renameButton)

        self.applyButton = QPushButton()
        self.applyButton.setText('Apply')
        self.connect(self.renameButton, QtCore.SIGNAL('clicked()'),self.applyFn)
        #self.connect(self.applyButton, QtCore.SIGNAL('clicked()'), self.applyFn)
        
    def applyFn(self):
        name = self.textField.text()
        MayaScripts.renamer(name)

class MoveAttrWin(QDialog):
    
    def __init__(self,parent = None):
        super(MoveAttrWin,self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle('Move Attributes')
        
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        self.setWindowTitle('Move Attributes')
        self.setGeometry(900,600,200,75)
      
        self.moveUpButton = QPushButton()
        self.moveUpButton.setText('Move Up')
        self.moveDownButton = QPushButton('Move Down')
        
        mainLayout.addWidget(self.moveUpButton)
        mainLayout.addWidget(self.moveDownButton)
        
        self.connect(self.moveUpButton,QtCore.SIGNAL('clicked()'),self.moveUp)
        self.connect(self.moveDownButton,QtCore.SIGNAL('clicked()'),self.moveDown)
        
    def moveUp(self):
        MayaScripts.moveAttrUp('up')
    
    def moveDown(self):
        MayaScripts.moveAttrUp('down')
    
class ExtrapClusterWin(QDialog):
    
    def __init__(self,parent = None):
        super(ExtrapClusterWin,self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle('Extrapolate Clusters')
        self.setGeometry(600,450,300,450)
        
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        listLayout = QVBoxLayout()
        
        self.transformList = QListWidget()
        self.transformButton = QPushButton()
        self.transformButton.setText('Load Transforms')
        
        self.meshList = QListWidget()
        self.meshButton = QPushButton()
        self.meshButton.setText('Load Meshes')
        
        frame = QFrame()
        frame.setFrameStyle(QFrame.Panel)
        mainLayout.addWidget(frame)
        
        frame.setLayout(listLayout)
        
        self.extrapButton = QPushButton()
        self.extrapButton.setText('Extrapolate')
        
        listLayout.addWidget(self.transformList)
        listLayout.addWidget(self.transformButton)
        listLayout.addWidget(self.meshList)
        listLayout.addWidget(self.meshButton)
        
        mainLayout.addWidget(self.extrapButton)
        
        self.connect(self.meshButton, QtCore.SIGNAL('clicked()'),self.loadMeshes)
        self.connect(self.transformButton, QtCore.SIGNAL('clicked()'),self.loadTransforms)
        self.connect(self.extrapButton,QtCore.SIGNAL('clicked()'),self.extrapToCluster)
        
    def loadTransforms(self):
        
        self.transformList.clear()
        sel = cmds.ls(sl = True)
        
        for obj in sel:
            
            self.transformList.addItem(obj)
            
    def loadMeshes(self):
        
        self.meshList.clear()
        sel = cmds.ls(sl = True)
        for obj in sel:
            
            shape = obj
            
            if cmds.nodeType(obj) == 'transform':
                shape = cmds.listRelatives(obj,type = 'shape')[0]
            
            self.meshList.addItem(shape)
            
    def extrapToCluster(self):
        
        transforms = []
        transformCount = self.transformList.count()
        
        for i in range(transformCount):
            transform = self.transformList.item(i).text()
            transforms.append(transform)
        
        meshes = []    
        meshCount = self.meshList.count()
        
        for i in range(meshCount):
            mesh = self.meshList.item(i).text()
            meshes.append(mesh)
        
        for transform in transforms:
            
            sel = []
            sel.append(transform)
            for mesh in meshes:
                sel.append(mesh)
                
            ToolBoxFn.extrapToCluster(sel)
            
class MeshToSkinclusterWin(QDialog):
    
    def __init__(self,parent = None):
        super(MeshToSkinclusterWin,self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle('Mesh To Skincluster')
        self.setGeometry(600,450,350,450)
        
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        listLayout = QVBoxLayout()
        
        meshFromLabel = QLabel()
        meshFromLabel.setText('Mesh From:')
        
        meshToLabel = QLabel()
        meshToLabel.setText('Mesh To:')
        
        self.jointList = QListWidget()
        self.meshFromButton = FillSelectedField()
        self.meshToButton = FillSelectedField()
        
        frame = QFrame()
        frame.setFrameStyle(QFrame.Panel)
        
        
        frame.setLayout(listLayout)
        
        self.loadJointsButton = QPushButton()
        self.loadJointsButton.setText('Load Joints')
        
        self.meshToSkinclusterButton = QPushButton()
        self.meshToSkinclusterButton.setText('Mesh To Skincluster')
        
        mainLayout.addWidget(meshFromLabel)
        mainLayout.addWidget(self.meshFromButton)
        mainLayout.addWidget(meshToLabel)
        mainLayout.addWidget(self.meshToButton)
        mainLayout.addWidget(frame)
        listLayout.addWidget(self.jointList)
        listLayout.addWidget(self.loadJointsButton)
        mainLayout.addWidget(self.meshToSkinclusterButton)
        
        self.connect(self.loadJointsButton, QtCore.SIGNAL('clicked()'),self.loadJoints)
        self.connect(self.meshToSkinclusterButton, QtCore.SIGNAL('clicked()'),self.meshToSkincluster)
        
        
    def loadJoints(self):
        
        self.jointList.clear()
        sel = cmds.ls(sl = True)
        
        for obj in sel:
            
            self.jointList.addItem(obj)
            
    def meshToSkincluster(self):
        
        meshFrom = self.meshFromButton.field.text()
        meshTo = self.meshToButton.field.text()
        
        joints = []
        jointCount = self.jointList.count()
        
        for i in range(jointCount):
            joint = self.jointList.item(i).text()
            joints.append(joint)
            
        ToolBoxFn.meshToSkincluster(meshFrom, meshTo, joints)
            
class ColorPalette(QDialog):
    
    def __init__(self,parent = None):
        super(ColorPalette,self).__init__(parent)
        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle('Color Palette')
        self.setGeometry(600,450,300,100)
        self.setFixedSize(300,100)
        
        self.index = 0
        
        self.indexColors = ([0,0,0],
                            [0.25,0.25,0.25],
                            [0.5,0.5,0.5],
                            [0.608,0,0.157],
                            [0,0.016,0.376],
                            [0,0,1],
                            [0,0.275,0.098],
                            [0.149,0,0.263],
                            [0.784,0,0.784],
                            [0.541,0.282,0.2],
                            [0.247,0.137,0.122],
                            [0.6,0.149,0],
                            [1,0,0],
                            [0,1,0],
                            [0,0.255,0.6],
                            [1,1,1],
                            [1,1,0],
                            [0.392,0.863,1],
                            [0.263,1,0.639],
                            [1,0.69,0.69],
                            [0.894,0.675,0.475],
                            [1,1,0.388],
                            [0,0.6,0.329],
                            [0.63,0.41391,0.189],
                            [0.62118,0.63,0.189],
                            [0.4095,0.63,0.189],
                            [0.189,0.63,0.3654],
                            [0.189,0.63,0.63],
                            [0.189,0.4051,0.63],
                            [0.43596,0.189,0.63],
                            [0.63,0.189,0.41391])
        
        self.layout = QGridLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        
        column = 0
        row = 0        
        
        for i in range(len(self.indexColors)):
            
            button = QPushButton()
            palette = button.palette()
            color = QColor()
            color.setRgbF(self.indexColors[i][0],self.indexColors[i][1],self.indexColors[i][2])
            palette.setColor(button.backgroundRole(),color)
            button.setPalette(palette)
            self.layout.addWidget(button,row,column,0)
            
            self.connect(button, QtCore.SIGNAL('clicked()'),lambda arg=i+1: self.setOverride(arg))
            
            if column < 7:
                column += 1
            else:
                row += 1
                column = 0
                        
    def setOverride(self,index):
        
        sel = cmds.ls(sl = True)
        shapes = []
        
        if len(sel):
            
            try:
        
                for obj in sel:
                    shapeNodes = cmds.listRelatives(obj, type = 'shape',f = True)
                    
                    for node in shapeNodes:
                        shapes.append(node)
                        
                for shape in shapes:
                    
                    cmds.setAttr('%s.overrideEnabled'%shape,True)
                    cmds.setAttr('%s.overrideColor'%shape,index)
                    
            except:
                pass
 
        
class ToolBoxMenuBar(QMenuBar):
    
    def __init__(self, parent = None):
        super(ToolBoxMenuBar,self).__init__(parent)

        fileMenu = self.addMenu('&File')
        
        editMenu = self.addMenu('&Edit')

        winMenu = self.addMenu('&Window')
        
        renamerAction = QAction('&Renamer',self,triggered = self.openRenamer)
        winMenu.addAction(renamerAction)
        
        moveAttrAction = QAction('&Move Attributes',self,triggered = self.openMoveAttrDialog)
        winMenu.addAction(moveAttrAction)
        
        reorderHistoryAction = QAction('&Reorder History',self,triggered = self.reorderHistory)
        editMenu.addAction(reorderHistoryAction)
        
        colorPaletteAction = QAction('&Color Palette',self,triggered = self.openColorPalette)
        winMenu.addAction(colorPaletteAction)
        
        saveClusterAction = QAction('&Save Clusters',self, triggered = ToolBoxFn.saveClusters)
        fileMenu.addAction(saveClusterAction)
        
        loadClusterAction = QAction('&Load Clusters',self, triggered = ToolBoxFn.loadClusters)
        fileMenu.addAction(loadClusterAction)
        
    def openRenamer(self): 
        
        try:
            self.renamerWin.close()
        except:
            pass
        
        self.renamerWin = RenameWindow(self)
        self.renamerWin.show()
        
    def openMoveAttrDialog(self):
        try:
            self.MoveAttrWin.close()  # @UndefinedVariable
        except:
            pass
        
        self.MoveAttrWin = MoveAttrWin(self)
        self.MoveAttrWin.show()
    
    def reorderHistory(self):
        ToolBoxFn.reorderHistory()
        
    def openColorPalette(self):
        try:
            self.colorPalette.close()  # @UndefinedVariable
        except:
            pass
        
        self.colorPalette = ColorPalette(self)
        self.colorPalette.show() 
        
        
class ToolBoxWidget(QWidget):
    
    def __init__(self,parent = None):
        super(ToolBoxWidget,self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        frame = QFrame()
        frame.setFrameStyle(QFrame.Panel)
        
        mainLayout = QHBoxLayout()
        self.setLayout(mainLayout)
        
        gridLayout = QGridLayout()
        gridLayout.setSpacing(0)
        frame.setLayout(gridLayout)
        
        #create clusters
        createClusterButton  = ButtonPopUpMenu()
        createClusterButton.button.setText('Create Cluster')
        createClusterButton.button.setGeometry(60,33,60,33)
        createClusterButton.addMenuItem('Extrap Cluster', self.openExtrapClusterDialog)
        createClusterButton.addMenuItem('Soft Selection to Cluster', ToolBoxFn.softSelToCluster)
        createClusterButton.addMenuItem('Mesh to Cluster', ToolBoxFn.meshToCluster)
        createClusterButton.addMenuItem('Combined to Cluster', ToolBoxFn.combinClusters)
        
        #skinclusters
        skinclusterButton  = ButtonPopUpMenu()
        skinclusterButton.button.setText('Skincluster')
        skinclusterButton.button.setGeometry(60,33,60,33)
        skinclusterButton.addMenuItem('From Lattice', ToolBoxFn.latticeToSkincluster)
        skinclusterButton.addMenuItem('From Wire', ToolBoxFn.wireToSkincluster)
        skinclusterButton.addMenuItem('Cluster to Joint', self.openClusterToJointDialog)
        skinclusterButton.addMenuItem('Mesh To Skincluster',self.openMeshToSkinclusterDialog)
        
        #mirror
        mirrorButton = QPushButton()
        mirrorButton.setText('Mirror Cluster')
        mirrorButton.setGeometry(60,33,60,33)
        
        self.connect(mirrorButton, QtCore.SIGNAL('clicked()'),self.openMirrorClusterDialog)
        
        #transfer
        transferButton = QPushButton()
        transferButton.setText('Transfer Weights')
        transferButton.setGeometry(60,33,60,33)
        
        self.connect(transferButton, QtCore.SIGNAL('clicked()'),self.openTransferDialog)
        
        #optimize deformer
        optimizeDeformerButton  = QPushButton()
        optimizeDeformerButton.setText('Optimize Deformer')
        optimizeDeformerButton.setGeometry(60,33,60,33)
        self.connect(optimizeDeformerButton, QtCore.SIGNAL('clicked()'),self.openOptimizeDeformerDialog)
        
        #skinningTool
        skinningButton = QPushButton()
        skinningButton.setText('Skin Tool')
        skinningButton.setGeometry(60,33,60,33)
        self.connect(skinningButton, QtCore.SIGNAL('clicked()'),ToolBoxFn.skinningTool)
        
        #gridLayout.setVerticalSpacing(0)
        #gridLayout.setHorizontalSpacing(0)
        
        gridLayout.addWidget(createClusterButton,0,0)       
        gridLayout.addWidget(mirrorButton,0,1)
        gridLayout.addWidget(skinclusterButton,0,2)
        gridLayout.addWidget(transferButton,1,0)
        gridLayout.addWidget(optimizeDeformerButton,1,1)
        gridLayout.addWidget(skinningButton,1,2)
        
        mainLayout.addWidget(frame)
        
    def openExtrapClusterDialog(self):
        
        try:
            self.extrapClusterWin.close()
        except:
            pass
        
        self.extrapClusterWin = ExtrapClusterWin(self)
        self.extrapClusterWin.show()
    
    def openMirrorClusterDialog(self):
        
        try:
            self.mirrorDialog.close()  # @UndefinedVariable
        except:
            pass
        
        self.mirrorDialog = MirrorWeightsDialog(self)

        self.mirrorDialog.show()
        
    def openTransferDialog(self):
        try:
            self.transferDialog.close()  # @UndefinedVariable
        except:
            pass
        
        self.transferDialog = TransferWeightsDialog(self)
        self.transferDialog.show()
    
    def openClusterToJointDialog(self):
        try:
            self.clusterToJointDialog.close()  # @UndefinedVariable
        except:
            pass
        
        self.clusterToJointDialog = ClustertoJointWin(self)
        self.clusterToJointDialog.show()

    def openOptimizeDeformerDialog(self):
        try:
            self.optimizeDeformerDialog.close()  # @UndefinedVariable
        except:
            pass
        
        self.optimizeDeformerDialog = OptimizeDeformerDialog(self)
        self.optimizeDeformerDialog.show() 
        
    def openMeshToSkinclusterDialog(self):
        try:
            self.meshToSkinclusterDialog.close()
            
        except:
            pass
        
        self.meshToSkinclusterDialog = MeshToSkinclusterWin(self)
        self.meshToSkinclusterDialog.show()
                 
                       
class ToolBoxWin(QMainWindow):
    
    def __init__(self, parent = getMayaWindow()):
        super(ToolBoxWin,self).__init__(parent)
        self.setWindowTitle('Tool Box')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        layout = QHBoxLayout()
        self.setLayout(layout)
        
        centralWidget = ToolBoxWidget(self)
        centralLayout = QGridLayout()
          
        centralWidget.setLayout(centralLayout)
 
        menuBar = ToolBoxMenuBar(self)
        self.setMenuBar(menuBar)
        self.setCentralWidget(centralWidget)
        
        