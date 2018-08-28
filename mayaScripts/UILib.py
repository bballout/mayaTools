'''
Created on Jun 29, 2012

@author: balloutb
'''

import maya.OpenMaya as om
import maya.OpenMayaUI as mui
import maya.cmds as cmds

try:
    from PySide import QtGui,QtCore  # @UnresolvedImport
    
    try:
        from PySide import shiboken
    except ImportError:
        import shiboken
except ImportError:
    from PySide2 import QtWidgets as QtGui
    from PySide2 import QtCore
    import shiboken2 as shiboken
    


import ToolBoxFn
import MayaScripts


#Get the maya main window as a QMainWindow instance
def getMayaWindow():
    
    try:
        ptr = mui.MQtUtil.mainWindow()
        
        if not ptr == None:
            return shiboken.wrapInstance(long(ptr), QtGui.QMainWindow)
        
    except AttributeError:
        
        return None
    

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
         
        
class ButtonPopUpMenu(QtGui.QWidget):

    def __init__(self, objectName ='Button', parent=None):
        super(ButtonPopUpMenu, self).__init__(parent)

        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
        
        self.button = QtGui.QPushButton()
        self.button.setText('Button')
        self.button.setGeometry(0,10,10,20)
        self.menu = QtGui.QMenu()

        self.button.setMenu(self.menu)

        layout.addWidget(self.button)
        
    def addMenuItem(self,label,func):
        
        action = self.menu.addAction(label)
        action.triggered.connect(func)
        
class ButtonFieldGroup(QtGui.QWidget):
    
    def __init__(self, objectName  ='ButtonField', parent=None):
        super(ButtonFieldGroup, self).__init__(parent)
        
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
        
        self.field = QtGui.QLineEdit() 
        self.button = QtGui.QPushButton()
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

            
class TransferWeightsDialog(QtGui.QDialog):
    
    def __init__(self, parent = getMayaWindow()):
        super(TransferWeightsDialog,self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.initUI()
        
    def initUI(self):
        
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        layout.setSpacing(0)
        self.setGeometry(450,200,450,200)
        self.setWindowTitle('Transfer Deformer Weights')
        
        self.fromDeformerLabel = QtGui.QLabel()
        self.fromDeformerLabel.setText('From Deformer:')
        self.fromDeformerField = FillDeformerNameField()
        layout.addWidget(self.fromDeformerLabel)
        layout.addWidget(self.fromDeformerField)
        
        self.toDeformerLabel = QtGui.QLabel()
        self.toDeformerLabel.setText('To Deformer:')
        self.toDeformerField = FillDeformerNameField()
        layout.addWidget(self.toDeformerLabel)
        layout.addWidget(self.toDeformerField)
        
        divider01 = QtGui.QFrame()
        divider01.setFrameShape(QtGui.QFrame.HLine)
        layout.addWidget(divider01)
        
        fromMeshLabel = QtGui.QLabel()
        fromMeshLabel.setText('From Mesh:')
        self.fromMeshField = FillSelectedField()
        layout.addWidget(fromMeshLabel)
        layout.addWidget(self.fromMeshField)
        
        toMeshLabel = QtGui.QLabel()
        toMeshLabel.setText('To Mesh:')
        self.toMeshfield = FillSelectedField()
        layout.addWidget(toMeshLabel)
        layout.addWidget(self.toMeshfield)      
        
        operationWidget = QtGui.QWidget()
        operationWidgetLayout  = QtGui.QHBoxLayout()
        operationWidget.setLayout(operationWidgetLayout)
        
        operationButtons = QtGui.QGroupBox()
        operationButtonsLayout = QtGui.QHBoxLayout()
        self.transferButton = QtGui.QRadioButton()
        self.transferButton.setText('transfer')
        self.transferButton.setChecked(True)
        self.mirrorButton = QtGui.QRadioButton()
        self.mirrorButton.setText('mirror')
        self.reverseButton = QtGui.QRadioButton()
        self.reverseButton.setText('reverse')
        operationButtons.setTitle('operation:')
        operationButtonsLayout.addWidget(self.transferButton)
        operationButtonsLayout.addWidget(self.mirrorButton)
        operationButtonsLayout.addWidget(self.reverseButton)
        operationButtons.setLayout(operationButtonsLayout)
        
        operationWidgetLayout.addWidget(operationButtons)
        layout.addWidget(operationWidget)
        
        axisWidget = QtGui.QWidget()
        axisWidgetLayout  = QtGui.QHBoxLayout()
        axisWidget.setLayout(axisWidgetLayout)
        
        axisButtons = QtGui.QGroupBox()
        axisButtonsLayout = QtGui.QHBoxLayout()
        self.axisXButton = QtGui.QRadioButton()
        self.axisXButton.setText('x')
        self.axisXButton.setChecked(True)
        self.axisYButton = QtGui.QRadioButton()
        self.axisYButton.setText('y')
        self.axisZButton = QtGui.QRadioButton()
        self.axisZButton.setText('z')
        axisButtons.setTitle('axis:')
        axisButtonsLayout.addWidget(self.axisXButton)
        axisButtonsLayout.addWidget(self.axisYButton)
        axisButtonsLayout.addWidget(self.axisZButton)
        axisButtons.setLayout(axisButtonsLayout)
                
        self.directionCheckBox = QtGui.QCheckBox()
        self.directionCheckBox.setText('Pos to Neg') 
        self.directionCheckBox.setChecked(True) 
        axisButtonsLayout.addWidget(self.directionCheckBox)
        
        axisWidgetLayout.addWidget(axisButtons)
        layout.addWidget(axisWidget)
        
        buttonsWidget = QtGui.QWidget()
        butttonsWidgetLayout = QtGui.QHBoxLayout()
        buttonsWidget.setLayout(butttonsWidgetLayout)
        
        self.applyButton = QtGui.QPushButton()
        self.applyButton.setText('Apply')
        self.connect(self.applyButton,QtCore.SIGNAL('clicked()'),self.applyFn)

        self.closeButton = QtGui.QPushButton()
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
              
        
class MirrorWeightsDialog(QtGui.QDialog):
    
    def __init__(self, parent = getMayaWindow()):
        super(MirrorWeightsDialog,self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.initDialog()
        
    def initDialog(self):
        
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle('Mirror Cluster')
        self.setGeometry(425,300,425,300)
        
        tranformNameWidget = QtGui.QWidget()
        transformNameLayout = QtGui.QVBoxLayout()
        tranformNameWidget.setLayout(transformNameLayout)
        transformNameLabel = QtGui.QLabel()
        transformNameLabel.setText('Transform Name:')
        self.transformButton = FillSelectedField()
        transformNameLayout.addWidget(transformNameLabel)
        transformNameLayout.addWidget(self.transformButton)
        
        deformerNameWidget = QtGui.QWidget()
        deformerNameWidgetLayout = QtGui.QVBoxLayout()
        deformerNameWidget.setLayout(deformerNameWidgetLayout)
        deformerNameLabel = QtGui.QLabel()
        deformerNameLabel.setText('Deformer Name:')
        self.deformerNameField = QtGui.QLineEdit()        
        deformerNameWidgetLayout.addWidget(deformerNameLabel)
        deformerNameWidgetLayout.addWidget(self.deformerNameField)
        
        divider01 = QtGui.QFrame()
        divider01.setFrameShape(QtGui.QFrame.HLine)
        
        prefixWidget = QtGui.QWidget()
        prefixWidgetLayout = QtGui.QVBoxLayout()
        prefixWidget.setLayout(prefixWidgetLayout)
        searchPrefixLabel = QtGui.QLabel()
        searchPrefixLabel.setText('Search for:')
        self.searchPrefixField = QtGui.QLineEdit()
        self.searchPrefixField.setText('L_')
        replacePrefixLabel = QtGui.QLabel()
        replacePrefixLabel.setText('Replace with')
        self.replacePrefixField = QtGui.QLineEdit()
        self.replacePrefixField.setText('R_')
        prefixWidgetLayout.addWidget(searchPrefixLabel)
        prefixWidgetLayout.addWidget(self.searchPrefixField)
        prefixWidgetLayout.addWidget(replacePrefixLabel)
        prefixWidgetLayout.addWidget(self.replacePrefixField) 
        
        divider02 = QtGui.QFrame()
        divider02.setFrameShape(QtGui.QFrame.HLine)
        
        operationWidget = QtGui.QWidget()
        operationLayout = QtGui.QHBoxLayout()
        operationWidget.setLayout(operationLayout)
        operationButtonGrp = QtGui.QGroupBox()
        operationButtonGrpLayout = QtGui.QHBoxLayout()
        operationButtonGrp.setLayout(operationButtonGrpLayout)
        operationButtonGrp.setTitle('operation:')
        self.mirrorButton = QtGui.QRadioButton()
        self.mirrorButton.setText('mirror cluster')
        self.mirrorButton.setChecked(True)
        self.mirrorWeightButton = QtGui.QRadioButton()
        self.mirrorWeightButton.setText('mirror weights')   
        self.flipButton = QtGui.QRadioButton()
        self.flipButton.setText('flip weights')
        operationButtonGrpLayout.addWidget(self.mirrorButton)
        operationButtonGrpLayout.addWidget(self.mirrorWeightButton)
        operationButtonGrpLayout.addWidget(self.flipButton)
        operationLayout.addWidget(operationButtonGrp)
        
        mirrorSetttingWidget = QtGui.QWidget()
        mirrorSetttingWidgetLayout  = QtGui.QHBoxLayout()
        mirrorSetttingWidget.setLayout(mirrorSetttingWidgetLayout)
        axisButtonGroup = QtGui.QGroupBox()
        axisButtonLayout = QtGui.QHBoxLayout()
        self.axisXButton = QtGui.QRadioButton()
        self.axisXButton.setText('x')
        self.axisXButton.setChecked(True)
        self.axisYButton = QtGui.QRadioButton()
        self.axisYButton.setText('y')
        self.axisZButton = QtGui.QRadioButton()
        self.axisZButton.setText('z')
        axisButtonGroup.setTitle('Axis:')
        axisButtonLayout.addWidget(self.axisXButton)
        axisButtonLayout.addWidget(self.axisYButton)
        axisButtonLayout.addWidget(self.axisZButton)
        axisButtonGroup.setLayout(axisButtonLayout)
        mirrorSetttingWidgetLayout.addWidget(axisButtonGroup)
        
        self.directionCheckBox = QtGui.QCheckBox()
        self.directionCheckBox.setText('Pos to Neg') 
        self.directionCheckBox.setChecked(True) 
        axisButtonLayout.addWidget(self.directionCheckBox)
        
        buttonsWidget = QtGui.QWidget()
        butttonsWidgetLayout = QtGui.QHBoxLayout()
        buttonsWidget.setLayout(butttonsWidgetLayout)
        
        self.connect(self.transformButton.button, QtCore.SIGNAL('clicked()'),self.fillDeformerName)
        
        self.applyButton = QtGui.QPushButton()
        self.applyButton.setText('Apply')
        self.connect(self.applyButton, QtCore.SIGNAL('clicked()'), self.applyFn)
        
        self.closeButton = QtGui.QPushButton()
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
            
class ClustertoJointWin(QtGui.QDialog):
    
    def __init__(self,parent = None):
        super(ClustertoJointWin,self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle('Cluster To Joint')
        self.setGeometry(425,300,425,300)
        self.initDialog()
        
    def initDialog(self):
        
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle('Cluster To Joint')
        self.setGeometry(425,300,425,300)
        
        geoFieldWidget = QtGui.QWidget()
        deformerFieldLayout = QtGui.QVBoxLayout()
        geoFieldWidget.setLayout(deformerFieldLayout)
        geoNameLabel = QtGui.QLabel()
        geoNameLabel.setText('Geo Name:')
        self.geoNameField = FillSelectedField()
        
        deformerFieldLayout.addWidget(geoNameLabel)
        deformerFieldLayout.addWidget(self.geoNameField)
        
        deformerFieldWidget = QtGui.QWidget()
        deformerFieldLayout = QtGui.QVBoxLayout()
        deformerFieldWidget.setLayout(deformerFieldLayout)
        deformerNameLabel = QtGui.QLabel()
        deformerNameLabel.setText('From Deformer Weights')
        self.deformerFillField = FillDeformerNameField()
        
        deformerFieldLayout.addWidget(deformerNameLabel)
        deformerFieldLayout.addWidget(self.deformerFillField)
        
        jointFieldWidget = QtGui.QWidget()
        jointFieldLayout = QtGui.QVBoxLayout()
        jointFieldWidget.setLayout(jointFieldLayout)
        jointFromLabel = QtGui.QLabel()
        jointFromLabel.setText('Take Influence Weight From:')
        self.jointFromButton = FillSelectedField()
        
        jointFieldLayout.addWidget(jointFromLabel)
        jointFieldLayout.addWidget(self.jointFromButton)
        
        jointToLabel = QtGui.QLabel()
        jointToLabel.setText('Set Influence Weight for:')
        self.jointToButton = FillSelectedField()
        
        divider01 = QtGui.QFrame()
        divider01.setFrameShape(QtGui.QFrame.HLine)
        
        divider02 = QtGui.QFrame()
        divider02.setFrameShape(QtGui.QFrame.HLine)
        
        divider03 = QtGui.QFrame()
        divider03.setFrameShape(QtGui.QFrame.HLine)

        jointFieldLayout.addWidget(jointToLabel)
        jointFieldLayout.addWidget(self.jointToButton)
        
        buttonsWidget = QtGui.QWidget()
        butttonsWidgetLayout = QtGui.QHBoxLayout()
        buttonsWidget.setLayout(butttonsWidgetLayout)
        
        self.applyButton = QtGui.QPushButton()
        self.applyButton.setText('Apply')
        self.connect(self.applyButton,QtCore.SIGNAL('clicked()'),self.applyFn)
        
        self.closeButton = QtGui.QPushButton()
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
            
class OptimizeDeformerDialog(QtGui.QDialog):
    
    def __init__(self,parent = None):
        super(OptimizeDeformerDialog,self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle('Optimize Deformer')
        self.setGeometry(600,325,300,325)
        
        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)
        
        listLayout = QtGui.QVBoxLayout()
        
        self.deformerList = QtGui.QListWidget()
        self.deformerLoadButton = QtGui.QPushButton()
        self.deformerLoadButton.setText('Load Deformers')

        frame = QtGui.QFrame()
        frame.setFrameStyle(QtGui.QFrame.Panel)
        mainLayout.addWidget(frame)

        frame.setLayout(listLayout)
        
        self.spinBoxButtonGrp = QtGui.QWidget()
        spinBoxButtonLayout = QtGui.QGridLayout()
        self.spinBoxButtonGrp.setLayout(spinBoxButtonLayout)
        pruneLabel = QtGui.QLabel()
        pruneLabel.setText('Prune Weight:')
        self.pruneSpinBox = QtGui.QDoubleSpinBox()
        self.pruneSpinBox.setMinimum(0.0005)
        self.pruneSpinBox.setMaximum(1.000)
        self.pruneSpinBox.setValue(0.001)
        self.pruneSpinBox.setDecimals(4)
        self.pruneSpinBox.setSingleStep(0.001)
        self.optimizeButton = QtGui.QPushButton()
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
        
           
class RenameWindow(QtGui.QDialog):
    
    def __init__(self,parent = getMayaWindow()):
        super(RenameWindow,self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        layout = QtGui.QVBoxLayout()
        
        self.setLayout(layout)
        self.setWindowTitle('Renamer')
        self.setGeometry(900,600,250,75)
        
        textHelp = QtGui.QLabel()
        textHelp.setText('Name_**_Name')
        self.textField = QtGui.QLineEdit()
        self.renameButton = QtGui.QPushButton()
        self.renameButton.setText('Apply')
        
        layout.addWidget(textHelp)
        layout.addWidget(self.textField)
        layout.addWidget(self.renameButton)

        self.applyButton = QtGui.QPushButton()
        self.applyButton.setText('Apply')
        self.connect(self.renameButton, QtCore.SIGNAL('clicked()'),self.applyFn)
        #self.connect(self.applyButton, QtCore.SIGNAL('clicked()'), self.applyFn)
        
    def applyFn(self):
        name = self.textField.text()
        MayaScripts.renamer(name)

class MoveAttrWin(QtGui.QDialog):
    
    def __init__(self,parent = None):
        super(MoveAttrWin,self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle('Move Attributes')
        
        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)
        
        self.setWindowTitle('Move Attributes')
        self.setGeometry(900,600,200,75)
      
        self.moveUpButton = QtGui.QPushButton()
        self.moveUpButton.setText('Move Up')
        self.moveDownButton = QtGui.QPushButton('Move Down')
        
        mainLayout.addWidget(self.moveUpButton)
        mainLayout.addWidget(self.moveDownButton)
        
        self.connect(self.moveUpButton,QtCore.SIGNAL('clicked()'),self.moveUp)
        self.connect(self.moveDownButton,QtCore.SIGNAL('clicked()'),self.moveDown)
        
    def moveUp(self):
        MayaScripts.moveAttrUp('up')
    
    def moveDown(self):
        MayaScripts.moveAttrUp('down')
    
class ExtrapClusterWin(QtGui.QDialog):
    
    def __init__(self,parent = None):
        super(ExtrapClusterWin,self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle('Extrapolate Clusters')
        self.setGeometry(600,450,300,450)
        
        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)
        
        listLayout = QtGui.QVBoxLayout()
        
        self.transformList = QtGui.QListWidget()
        self.transformButton = QtGui.QPushButton()
        self.transformButton.setText('Load Transforms')
        
        self.meshList = QtGui.QListWidget()
        self.meshButton = QtGui.QPushButton()
        self.meshButton.setText('Load Meshes')
        
        frame = QtGui.QFrame()
        frame.setFrameStyle(QtGui.QFrame.Panel)
        mainLayout.addWidget(frame)
        
        frame.setLayout(listLayout)
        
        self.extrapButton = QtGui.QPushButton()
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
            
class MeshToSkinclusterWin(QtGui.QDialog):
    
    def __init__(self,parent = None):
        super(MeshToSkinclusterWin,self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle('Mesh To Skincluster')
        self.setGeometry(600,450,350,450)
        
        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)
        
        listLayout = QtGui.QVBoxLayout()
        
        meshFromLabel = QtGui.QLabel()
        meshFromLabel.setText('Mesh From:')
        
        meshToLabel = QtGui.QLabel()
        meshToLabel.setText('Mesh To:')
        
        self.jointList = QtGui.QListWidget()
        self.meshFromButton = FillSelectedField()
        self.meshToButton = FillSelectedField()
        
        frame = QtGui.QFrame()
        frame.setFrameStyle(QtGui.QFrame.Panel)
        
        
        frame.setLayout(listLayout)
        
        self.loadJointsButton = QtGui.QPushButton()
        self.loadJointsButton.setText('Load Joints')
        
        self.meshToSkinclusterButton = QtGui.QPushButton()
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
            
class ColorPalette(QtGui.QDialog):
    
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
        
        self.layout = QtGui.QGridLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        
        column = 0
        row = 0        
        
        for i in range(len(self.indexColors)):
            
            button = QtGui.QPushButton()
            palette = button.palette()
            color = QtGui.QColor()
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
                    shapeNodes = cmds.listRelatives(obj, type = 'shape')
                    
                    for node in shapeNodes:
                        shapes.append(node)
                        
                for shape in shapes:
                    
                    cmds.setAttr('%s.overrideEnabled'%shape,True)
                    cmds.setAttr('%s.overrideColor'%shape,index)
                    
            except:
                pass
 
        
class ToolBoxMenuBar(QtGui.QMenuBar):
    
    def __init__(self, parent = None):
        super(ToolBoxMenuBar,self).__init__(parent)

        fileMenu = self.addMenu('&File')
        
        editMenu = self.addMenu('&Edit')

        winMenu = self.addMenu('&Window')
        
        renamerAction = QtGui.QAction('&Renamer',self,triggered = self.openRenamer)
        winMenu.addAction(renamerAction)
        
        moveAttrAction = QtGui.QAction('&Move Attributes',self,triggered = self.openMoveAttrDialog)
        winMenu.addAction(moveAttrAction)
        
        reorderHistoryAction = QtGui.QAction('&Reorder History',self,triggered = self.reorderHistory)
        editMenu.addAction(reorderHistoryAction)
        
        colorPaletteAction = QtGui.QAction('&Color Palette',self,triggered = self.openColorPalette)
        winMenu.addAction(colorPaletteAction)
        
        saveClusterAction = QtGui.QAction('&Save Clusters',self, triggered = ToolBoxFn.saveClusters)
        fileMenu.addAction(saveClusterAction)
        
        loadClusterAction = QtGui.QAction('&Load Clusters',self, triggered = ToolBoxFn.loadClusters)
        fileMenu.addAction(loadClusterAction)
        
        fileMenu.addSeparator()
        
        saveEyePlacementAction = QtGui.QAction('&Save Eye Placement',self, triggered = ToolBoxFn.saveEyePlacement)
        fileMenu.addAction(saveEyePlacementAction)
        
        loadEyePlacementAction = QtGui.QAction('&Load Eye Placement',self, triggered = ToolBoxFn.loadEyePlacment)
        fileMenu.addAction(loadEyePlacementAction)
        
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
        
        
class ToolBoxWidget(QtGui.QWidget):
    
    def __init__(self,parent = None):
        super(ToolBoxWidget,self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        frame = QtGui.QFrame()
        frame.setFrameStyle(QtGui.QFrame.Panel)
        
        mainLayout = QtGui.QHBoxLayout()
        self.setLayout(mainLayout)
        
        gridLayout = QtGui.QGridLayout()
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
        mirrorButton = QtGui.QPushButton()
        mirrorButton.setText('Mirror Cluster')
        mirrorButton.setGeometry(60,33,60,33)
        
        self.connect(mirrorButton, QtCore.SIGNAL('clicked()'),self.openMirrorClusterDialog)
        
        #transfer
        transferButton = QtGui.QPushButton()
        transferButton.setText('Transfer Weights')
        transferButton.setGeometry(60,33,60,33)
        
        self.connect(transferButton, QtCore.SIGNAL('clicked()'),self.openTransferDialog)
        
        #optimize deformer
        optimizeDeformerButton  = QtGui.QPushButton()
        optimizeDeformerButton.setText('Optimize Deformer')
        optimizeDeformerButton.setGeometry(60,33,60,33)
        self.connect(optimizeDeformerButton, QtCore.SIGNAL('clicked()'),self.openOptimizeDeformerDialog)
        
        #skinningTool
        skinningButton = QtGui.QPushButton()
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
                 
                       
class ToolBoxWin(QtGui.QMainWindow):
    
    def __init__(self, parent = getMayaWindow()):
        super(ToolBoxWin,self).__init__(parent)
        self.setWindowTitle('Tool Box')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
        
        centralWidget = ToolBoxWidget(self)
        centralLayout = QtGui.QGridLayout()
        centralWidget.setLayout(centralLayout)
 
        menuBar = ToolBoxMenuBar(self)
        self.setMenuBar(menuBar)
        self.setCentralWidget(centralWidget)
        
        