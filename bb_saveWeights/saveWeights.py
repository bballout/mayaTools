'''
Created on Aug 18, 2018

@author: Bill
'''
#include
import os,sys
import simplejson as json
import maya.OpenMaya as om
import maya.cmds as cmds

try:
    from PySide2 import QtWidgets,QtCore
except ImportError:
    from PySide2 import QtWidgets as QtWidgets
    from PySide2 import QtCore
from mayaTools.mayaScripts import SkinningLib,GenAPI

sys.path.append('C:/rig_menu/python/rig')
from dw_autoRig.AutoRigUI.UIModules import dwUILib

PATH = __file__.split('saveWeights.py')[0]
UIPATH = '%ssaveWeights.ui'%PATH

class SaveWeightsUI(QtWidgets.QMainWindow):
    def __init__(self,parent=dwUILib.getMayaWindow()):
        super(SaveWeightsUI, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)     
        uiFile = QtCore.QFile(UIPATH)
        uiFile.open(QtCore.QFile.ReadOnly)
        dwUILib.loadUI(uiFile,self)
        uiFile.close()
        self.setGeometry(500,400,400,240)
        self.setWindowTitle('Save Skin Weights')
        
        #adding icon to open folder button
        #self.iconPath = igRoot + r"\tech_art\maya\shared\icons"
        #self.folderIcon = QtWidgets.QIcon(os.path.join(self.iconPath, "folder.bmp"))
        #self.openFolderPushButton.setIcon(self.folderIcon)
        #self.openFolderPushButton.setToolTip('Set Directory')
        self.findFilePushButton.clicked.connect(self.setNewDir)
        self.loadWeightsPushButton.clicked.connect(self.loadWeights)
        self.saveWeightsPushButton.clicked.connect(self.saveWeights)
        self.selectSkinnedGeoPushButton.clicked.connect(self.selectSkinnedMeshes)
        self.selectFileSkinnedGeoPushButton.clicked.connect(self.selectFileSkinnedMeshes)   

    def setNewDir(self):
        startingPath = cmds.file(query = True,location = True).replace('/','\\')
        newPath = cmds.fileDialog2(dialogStyle=0,fm=0,okc='Save',startingDirectory=startingPath)[0]
        self.fileLineEdit.setText(newPath)
        
    def saveWeights(self):
        filePath = self.fileLineEdit.text()
        selection = cmds.ls(sl=True)
        saveFn = SaveWeightsFn(selection=selection,filePath=filePath)
        saveFn.progressA.connect(self.currentProgressBar.setValue)
        saveFn.progressB.connect(self.totalProgressBar.setValue)
        saveFn.progressC.connect(self.statusText.setText)
        saveFn.saveSkinData()        
        
    def loadWeights(self):
        filePath = self.fileLineEdit.text()
        selection = cmds.ls(sl=True)
        saveFn = SaveWeightsFn(selection=selection,filePath=filePath)
        saveFn.progressA.connect(self.currentProgressBar.setValue)
        saveFn.progressB.connect(self.totalProgressBar.setValue)
        saveFn.progressC.connect(self.statusText.setText)
        saveFn.loadWeights()
        

        #self.connect(saveFn.progress,QtCore.SIGNAL('progressA(int)'),self.statusText,QtCore.SLOT('setValue(int)'),QtCore.Qt.DirectConnection)
        #self.connect(saveFn.progress,QtCore.SIGNAL('progressC(str)'),self.statusText,QtCore.SLOT('setText(str)'),QtCore.Qt.DirectConnection)
        
    def selectSkinnedMeshes(self):
        skinnedGeo = SaveWeightsFn.findSkinnedGeo()
        cmds.select(skinnedGeo)
    
    def selectFileSkinnedMeshes(self):
        filePath = self.fileLineEdit.text()
        existingGeo = []
        nonexistingGeo = []
        if filePath:
            selection = cmds.ls(sl=True)
            saveFn = SaveWeightsFn(selection=selection,filePath=filePath)
            data = saveFn.skinDataFile
            meshes = data.keys()
            for mesh in meshes:
                if cmds.objExists(mesh):
                    existingGeo.append(mesh)
                else:
                    nonexistingGeo.append(mesh)
        
        if nonexistingGeo:
            cmds.confirmDialog(message='This geo does not exist:\n %s \n'%(" ; ".join(nonexistingGeo)))
        if existingGeo:     
            cmds.select(existingGeo)
          
class SaveWeightsFn(QtCore.QObject):
    progressA = QtCore.Signal(int)
    progressB = QtCore.Signal(int)
    progressC = QtCore.Signal(str)
    
    def __init__(self,*args, **kwargs):                                                
        super(SaveWeightsFn, self).__init__()
        self._skinDataScene = dict()
        self._skinDataFile = dict()
        self._skinnedMeshes = []
        self._missingMeshes = []
            
        self.filePath = kwargs.get('filePath',None)
        self.selection = kwargs.get('selection',None)
        self.mode = kwargs.get('mode','multi')
        
    def checkForSkincluster(self,mesh):
        shape = mesh
        if cmds.nodeType(mesh) == 'transform':
            shape = cmds.listRelatives(mesh,type='shape')[0]
        if cmds.nodeType(shape) == 'mesh':
            history = cmds.listHistory(shape,il=2,pdo=1)
            if history:
                for node in history:
                    if cmds.nodeType(node) == 'skinCluster':
                        return node
        else:
            return False
        
    @staticmethod       
    def findSkinnedGeo():
        meshes = cmds.ls(type='mesh')
        skinnedMeshes = []
        for mesh in meshes:
            history = cmds.listHistory(mesh,il=2,pdo=1)
            if history:
                for node in history:
                    if cmds.nodeType(node) == 'skinCluster':
                        transform = cmds.listRelatives(mesh,parent=True)[0]
                        skinnedMeshes.append(transform)
        return skinnedMeshes
        
    def getWeights(self,mesh):
        skinData = dict()
        skincluster = self.checkForSkincluster(mesh)
        skinTool = SkinningLib.SkinningTool(skincluster,mesh)
        influences = skinTool.getInfluencesFromSkincluster()
        verts = GenAPI.getMObjectAllVerts(mesh)
        self.progressC.emit(mesh)
        
        progressBItr = 100.0/influences.length()
        influenceCounter = 0
        for i in range(influences.length()):
            influenceCounter+=progressBItr
            self.progressB.emit(influenceCounter)
            weights = skinTool.getWeights(verts,influences[i])
            weightList = GenAPI.createListFromDoubleArray(weights)
            skinData[influences[i].fullPathName().split('|')[-1]] = weightList
           
        self.progressB.emit(0)
        self.progressC.emit('Status')   
        return skinData
    
    @property
    def skinDataScene(self):
        data = dict()
        progressItrA = 100.0/len(self.selection)
        meshCounter = 0
        meshes = []
        for item in self.selection:
            if self.checkForSkincluster(item):
                meshes.append(item)              
        for mesh in meshes:
            meshCounter+=progressItrA
            self.progressA.emit(meshCounter)
            skinData = self.getWeights(mesh)
            data[mesh] = skinData
        
        self.progressA.emit(0)       
        self._skinDataScene = data
        return self._skinDataScene
    
    @skinDataScene.setter
    def skinDataScene(self, value):
        self._skinDataScene = value
    
    @property    
    def skinDataFile(self):
        with open(self.filePath) as f:
            data = json.load(f)
        self._skinDataFile = data
        return self._skinDataFile
    
    @skinDataFile.setter
    def skinDataFile(self, value):
        self._skinDataFile = value
        
    @property
    def skinnedMeshes(self):
        data = self.skinDataFile
        meshes = data.keys()
        skinnedMeshes = []
        for mesh in meshes:
            if mesh in self.selection:
                check = self.checkForSkincluster(mesh)
                if check:
                    skinnedMeshes.append(mesh)
        self._skinnedMeshes = skinnedMeshes
        return self._skinnedMeshes
    
    @skinnedMeshes.setter
    def skinnedMeshes(self,value):
        self._skinnedMeshes = value
        
    @property
    def missingMeshes(self):
        data = self.skinDataFile
        meshes = data.keys()
        for mesh in meshes:
            if not cmds.objExists(mesh):
                self._missingMeshes.append(mesh)
        return self._missingMeshes
    
    @missingMeshes.setter
    def missingMeshes(self,value):
        self._missingMeshes = value
        
    def saveSkinData(self):
        with open(self.filePath,'w') as f:
            json.dump(self.skinDataScene,f, indent=4 * ' ')
        om.MGlobal.displayInfo('saved weights')
            
    def bind(self,data):
        meshes = data.keys()
        for mesh in meshes:
            if mesh in self.selection:
                if not mesh in self.missingMeshes:
                    skinDataList = data[mesh]
                    bindJoints = []
                    for influence in skinDataList:
                        bindJoints.append(influence) 
                    if not mesh in self.skinnedMeshes:
                        cmds.skinCluster(mesh,bindJoints,rui=False,omi=False,mi=1)
                    else:
                        skincluster = self.checkForSkincluster(mesh)
                        skinTool = SkinningLib.SkinningTool(shape=mesh,skincluster=skincluster)
                        influenceDagArray = skinTool.getInfluencesFromSkincluster()
                        influenceList = GenAPI.getShortNamesFromDagArray(influenceDagArray)
                        #cmds.confirmDialog(message='Adding missing influences for %s'%mesh)
                        for influence in bindJoints:
                            if not influence in influenceList:
                                try:
                                    cmds.skinCluster(skincluster, e=True, weight=0, addInfluence=influence)
                                except RuntimeError:
                                    pass
                    
    def loadWeights(self,holdLocked=False):
        self.progressC.emit('Reading File...')
        data = self.skinDataFile
        meshes = data.keys()            
        
        bindCheck = False
        self.progressC.emit('Checking for skinclusters...')
        for mesh in self.selection:
            if mesh in meshes:
                bindCheck=True
        if bindCheck:
            self.progressC.emit('Binding...')
            self.bind(data)
            
        noMeshData = []
        progressItrA = 100.0/len(self.selection)
        numMeshes = 0
        for mesh in self.selection:
            if mesh in meshes:
                numMeshes+=progressItrA
                self.progressA.emit(numMeshes)
                skinDataList = data[mesh]
                self.progressC.emit(mesh)
                skincluster = self.checkForSkincluster(mesh)
                skinningTool = SkinningLib.SkinningTool(skincluster,mesh)
                influences = skinningTool.getInfluencesFromSkincluster()   
                
                for i in range(influences.length()):
                    cmds.setAttr('%s.liw'%influences[i].fullPathName(), 0)
                

                progressItrB = 100.0/len(skinDataList)
                t = 0
                for influence in skinDataList:
                    t+=progressItrB
                    weightList = data[mesh][influence]
                    if cmds.objExists(influence):
                        skinningTool.setWeightList(GenAPI.getDagPath(influence),weightList)
                        cmds.setAttr('%s.liw'%influence, 1)
                    else:
                        cmds.confirmDialog(message='Cannot find %s in %s'%(influence,self.filePath)) 
                        
                    self.progressB.emit(t)                       
            else:
                noMeshData.append(mesh)
                
        self.progressA.emit(0)
        self.progressB.emit(0)
        self.progressC.emit('Status')
            
        if noMeshData:
            cmds.confirmDialog(message='There is no data for:\n %s \n in: \n %s'%(" ; ".join(noMeshData),self.filePath))
    

                         
saveWeightWinVar = ''
def open_win():
    global saveWeightWinVar
    try:
        saveWeightWinVar.close()
    except:
        pass
    
    try:
        cmds.deleteUI('saveWeightsWin')
    except:
        pass
            
    saveWeightWinVar = SaveWeightsUI()
    saveWeightWinVar.show()

            