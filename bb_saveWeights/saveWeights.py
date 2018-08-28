'''
Created on Aug 18, 2018

@author: Bill
'''
#include
import os,sys
from collections import OrderedDict
import simplejson as json
import maya.cmds as cmds
from PySide import QtGui,QtCore
from scripts import SkinningLib,GenAPI

sys.path.append('G:/dwtv/hub/Tools/Rig/scripts/rig')
from dw_autoRig.AutoRigUI.UIModules import dwUILib

path = __file__.split('saveWeights.py')[0]
UIPATH = '%ssaveWeights2.ui'%path

class SaveWeightsUI(QtGui.QMainWindow):
    def __init__(self,parent=dwUILib.getMayaWindow()):
        super(SaveWeightsUI, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)        
        uiFile = QtCore.QFile(UIPATH)
        uiFile.open(QtCore.QFile.ReadOnly)
        dwUILib.loadUI(uiFile,self)
        uiFile.close()

class Progress(QtCore.QObject):
    progressA = QtCore.Signal(float)
    progressB = QtCore.Signal(float)
    progressC = QtCore.Signal(str)
    def __init__(self, parent = None):
            QtCore.QObject.__init__(self, parent)

class SaveWeightsFn(QtCore.QObject):
    def __init__(self,*args, **kwargs):
        self.progress = Progress()
        self._skinDataScene = OrderedDict()
        self._skinDataFile = OrderedDict()
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
        
    def getWeights(self,mesh):
        skinData = OrderedDict()
        skincluster = self.checkForSkincluster(mesh)
        skinTool = SkinningLib.SkinningTool(skincluster,mesh)
        influences = skinTool.getInfluencesFromSkincluster()
        
        for i in range(influences.length()):
            verts = GenAPI.getMObjectAllVerts(mesh)
            weights = skinTool.getWeights(verts,influences[i])
            weightList = GenAPI.createListFromDoubleArray(weights)
            skinData[influences[i].fullPathName()] = weightList
               
        return skinData
    
    @property
    def skinDataScene(self):
        data = OrderedDict()
        meshes = []
        for item in self.selection:
            if self.checkForSkincluster(item):
                meshes.append(item)              
        for mesh in meshes:
            skinData = self.getWeights(mesh)
            data[mesh] = skinData
                
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
            
    def bind(self):
        data = self.skinDataFile
        meshes = data.keys()

        for mesh in meshes:
            if mesh in self.selection:
                if not mesh in self.missingMeshes:
                    skinDataList = data[mesh]
                    bindJoints = []
                    for influence in skinDataList:
                        bindJoints.append(influence) 
                    if not mesh in self.skinnedMeshes:
                        cmds.skinCluster(mesh,bindJoints)
                    else:
                        cmds.confirmDialog(message='Adding missing influences for %s'%mesh)
                        skincluster = self.checkForSkincluster(mesh)
                        for influence in bindJoints:
                            try:
                                cmds.skinCluster(skincluster, e=True, weight=0, addInfluence=influence)
                            except RuntimeError:
                                pass
                    
    def loadWeights(self,holdLocked=False):
        data = self.skinDataFile
        meshes = data.keys()            
        
        bindCheck = False
        for mesh in self.selection:
            if mesh in meshes:
                bindCheck=True
        if bindCheck:
            self.progress.progressC.emit('Binding...')
            self.bind()
            
        noMeshData = []
        progressItrA = 100.0/len(self.selection)
        i = 0
        for mesh in self.selection:
            i+=progressItrA
            self.progress.progressA.emit(i)
            if mesh in meshes:
                skinDataList = data[mesh]
                self.progress.progressC.emit('Checking for skincluster...')
                skincluster = self.checkForSkincluster(mesh)
                skinningTool = SkinningLib.SkinningTool(skincluster,mesh)
                influences = skinningTool.getInfluencesFromSkincluster()   
                
                for i in range(influences.length()):
                    cmds.setAttr('%s.liw'%influences[i].fullPathName(), 0)
                
                self.progress.progressC.emit('Setting weights...')
                progressItrB = 100.0/len(skinDataList)
                t = 0
                for influence in skinDataList:
                    t+=progressItrB
                    self.progress.progressB.emit(t)
                    weightList = data[mesh][influence]
                    if cmds.objExists(influence):
                        skinningTool.setWeightList(GenAPI.getDagPath(influence),weightList)
                        cmds.setAttr('%s.liw'%influence, 1)
                    else:
                        cmds.confirmDialog(message='Cannot find %s in %s'%(influence,self.filePath))                        
            else:
                noMeshData.append(mesh)
            
        if noMeshData:
            cmds.confirmDialog(message='There is no data for:\n %s \n in: \n %s'%(" ; ".join(noMeshData),self.filePath))
            