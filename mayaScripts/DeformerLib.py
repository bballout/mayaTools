'''
Created on Aug 9, 2012

@author: Bill
'''

import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya.cmds as cmds
import GenAPI
import MeasuringLib
import UILib

class WeightListTool():
    
    '''Class for creating and manipulating deformer weight lists'''
    #class attrs
    meshPath = ''
    defomerObject = ''
    
    def __init__(self,mesh = '',deformer = ''):
        
        self.mesh = mesh
        self.deformer = deformer
        self.meshPath = GenAPI.getDagPath(mesh)
        self.meshObject = GenAPI.getMObject(mesh)
        self.deformerObject = GenAPI.getMObject(deformer) 
        
        if self.meshObject.apiTypeStr() == 'kTransform':
            
            shape = cmds.listRelatives(mesh,type = 'shape')[0]
            self.meshPath  = GenAPI.getDagPath(shape)
            self.meshObject = GenAPI.getMObject(shape)
            
    def getWeightList(self):
        
        '''
        returns current weightList of mesh
        output python float list (weightList)
        '''
        
        deformerWeightFn = oma.MFnWeightGeometryFilter(self.deformerObject)
        vertItr = om.MItGeometry(self.meshPath)
        
        weightList = []
        while not vertItr.isDone():
            
            component = vertItr.currentItem()
            
            if not self.checkMembership(component):
                
                weightList.append(0)
                
            else:   
                
                floatArray = om.MFloatArray()
                deformerWeightFn.getWeights(self.meshPath,component,floatArray)
                weightList.append(floatArray[0])
                
            vertItr.next()
          
        return weightList
    
    def setWeightList(self,weightList):
        
        '''
        method for setting wieght list to mesh
        input python float list (weightList)  
        '''
        floatArray = om.MFloatArray()
        
        util = om.MScriptUtil()
        util.createFloatArrayFromList(weightList,floatArray)
        
        components = GenAPI.getMObjectAllVerts(self.meshPath)

        deformerWeightFn = oma.MFnWeightGeometryFilter(self.deformerObject)
        deformerWeightFn.setWeight(self.meshPath,components,floatArray)
        
    def setWeightListOld(self,weightList):
        
        '''
        method for setting wieght list to mesh
        input python float list (weightList)  
        '''
        
        verts = GenAPI.getMObjectAllVerts(self.mesh)
        
        deformerWeightFn = oma.MFnWeightGeometryFilter(self.deformerObject)
        util = om.MScriptUtil()
        
        mfloatArray = om.MFloatArray()
        util.createFloatArrayFromList(weightList,mfloatArray)
        
        deformerWeightFn.setWeight(self.meshPath,verts,mfloatArray)
        

    @staticmethod
    def saveWeights(clusters,filePath):
        
        '''
        method for saving clusters to file
        input clusterHandles (python list)
        input filePath (python string)
        '''

        if filePath != '':
            
            f = open(filePath,'w+')
            
            for clusterHandle in clusters:
 
                connection = cmds.connectionInfo('%s.worldMatrix[0]'%clusterHandle, dfs = True)[0]
                deformer = connection.split('.')[0]
                position = cmds.xform(clusterHandle,q = True, ws = True, rp = True)
                members = WeightListTool.getDagMembers(deformer)
                
                f.write('[CLUSTER]\n')
                f.write('%s\n'%clusterHandle)
                
                f.write('%s\n'%deformer)
                f.write('[%f,%f,%f]\n'%(position[0],position[1],position[2]))
                
                
                for member in members:
                    
                    f.write('[MEM]\n')
                    
                    f.write('%s\n'%member)
                    
                    print member
                    
                    deformerTool = WeightListTool(member,deformer)
                    weightList = deformerTool.getWeightList()
                    membershipList = deformerTool.getMembershipList()
                    pointList = MeasuringLib.MeasuringTool.getComponentPoints(member)
                    
                    f.write('[POINTS]\n')
                    for i in range(len(pointList)):
                        
                        f.write('[%f,%f,%f]\n'%(pointList[i][0],pointList[i][1],pointList[i][2]))

                    f.write('[POINTSEND]\n')
                    f.write('[MEMSHIP]\n')
                    for i in range(len(pointList)):
                        
                        f.write('%f\n'%membershipList[i])

                        
                    f.write('[MEMSHIPEND]\n')
                    f.write('[WEIGHTS]\n')
                    for i in range(len(pointList)):
                        
                        f.write('%f\n'%weightList[i])
                        
                    f.write('[WEIGHTSEND]\n')
                f.write('[MEMEND]\n')
                om.MGlobal.displayInfo('%s written successfully.'%deformer)
            
            f.write('[ENDCLUSTER]\n')
            f.close()
            
    @staticmethod
    def readWeights(filePath):
        
        '''
        method for loading clusters from file
        input filePath (python string)
        output clusterDataArray (python list of dicts [{},{}...])
        '''
        
        f = open(filePath,'r')
        f.seek(0)
        
        clusterDataArray = []
        
        while True:  
            
            while not f.readline() == '[ENDCLUSTER]\n':
                
                clusterDict = {'clusterHandle' : '',
                               'clusterName' : '',
                               'pos' : [],
                               'dagMembers': [],
                               'pointArray': [],
                               'membershipList':[],
                               'weightList':[]} 
    
                
                clusterDict['clusterHandle'] =  f.readline().rstrip()
                clusterDict['clusterName'] = f.readline().rstrip()
                
                pos = []
                exec('pos = %s'%f.readline())
                clusterDict['pos'] = pos
                dagMembers = []
                completePointArray = []
                copmpleteMembershipList = []
                completeWeightList = []
                                
                while not f.readline() == '[MEMEND]\n':
                    
                    pointArray = []
                    membershipList = []
                    weightList = []
                
                    dagMembers.append(f.readline().rstrip())
                    
                    rewind = None
                    while not f.readline() == '[POINTSEND]\n':
                        
                        if not rewind == None:
                            f.seek(rewind)
                        
                        point = []
                        exec('point = %s'%f.readline())
                        pointArray.append(point)
                        rewind = f.tell()
                    
                    rewind = None   
                    while not f.readline() == '[MEMSHIPEND]\n':
                        
                        if not rewind == None:
                            f.seek(rewind)
                            
                        member = bool(int(float(f.readline())))
                            
                        membershipList.append(member)
                        rewind = f.tell()
                    
                    rewind = None    
                    while not f.readline() == '[WEIGHTSEND]\n':
                        
                        if not rewind == None:
                            f.seek(rewind)
                        
                        weight = float(f.readline())   
                        weightList.append(weight)
                        rewind = f.tell()
                        
                    completePointArray.append(pointArray)
                    copmpleteMembershipList.append(membershipList)
                    completeWeightList.append(weightList)
                        
                clusterDict['dagMembers'] = dagMembers
                clusterDict['pointArray'] = completePointArray
                clusterDict['membershipList'] = copmpleteMembershipList
                clusterDict['weightList'] = completeWeightList
                                   
                clusterDataArray.append(clusterDict)
                   
            if f.readline() == '':
                break
           
        f.close()
        return clusterDataArray
        
           
    @staticmethod    
    def getDagMembers(deformer):
        
        '''
        method for gathering dag members from a deformer
        output members (pythonList[python string])
        '''
        
        dagList = []
        deformerObject = GenAPI.getMObject(deformer)
        
        geoFilter = oma.MFnGeometryFilter(deformerObject)
        deformerSet = geoFilter.deformerSet()
        deformerSetFn = om.MFnSet(deformerSet)
        
        selectionList = om.MSelectionList()
        deformerSetFn.getMembers(selectionList, False)
        
        selectionItr = om.MItSelectionList(selectionList)
        
        while not selectionItr.isDone():
            
            dagPath = om.MDagPath()
            selectionItr.getDagPath(dagPath)
            
            dagList.append(dagPath.partialPathName())
            
            selectionItr.next()
        
        return dagList
    
    @staticmethod
    def addDagMember(mesh,deformer):
        
        '''
        method for adding dagObject to deformer
        input meshPath (python string)
        input defrormer(python string)
        '''
        
        deformerObject = GenAPI.getMObject(deformer)
        meshPath = GenAPI.getDagPath(mesh)
        vertObjects = GenAPI.getMObjectAllVerts(mesh)
        
        geoFilter = oma.MFnGeometryFilter(deformerObject)
        deformerSet = geoFilter.deformerSet()
        deformerSetFn = om.MFnSet(deformerSet)
        
        for vert in vertObjects:
        
            deformerSetFn.addMember(meshPath,vert)
        
        
    
    @staticmethod
    def sortDagMembers(deformer,prefix = 'L',oppPrefix = 'R'):
        
        '''
        method for sorting dagMembers of a deformerSet
        input prefix (python string)
        output python list [singles,doubles]
        '''

        dagMembers = WeightListTool.getDagMembers(deformer)
    
        singles = []
        doubles = []
    
        print dagMembers
       
        for mesh in dagMembers:
            
            if len(mesh.split(prefix)) == 1 and len(mesh.split(oppPrefix)) == 1:
                print 'appending to singles'
                
                singles.append(mesh)
                
            elif not len(mesh.split(prefix)) == 1:
                
                oppMesh = '%s%s'%(oppPrefix,mesh.split(prefix)[1])
                doubles.append([mesh,oppMesh])
                
        return [singles,doubles]
            
        
    def checkMembership(self,component):
        
        '''
        method for checking if provided component is a member in the deformer set
        input MObject (component)
        output python bool (status)
        '''
        
        geoFilter = oma.MFnGeometryFilter(self.deformerObject)
        deformerSet = geoFilter.deformerSet()
        deformerSetFn = om.MFnSet(deformerSet)
        selectionList = om.MSelectionList()
        
        deformerSetFn.getMembers(selectionList, True) 
      
        if selectionList.hasItem(self.meshPath,component):
        
            return True
            
        else:
            
            return False
        

    def addComponentToMembershipList(self,component):
        
        '''
        method for adding component to membership
        input mesh (MDagPath)
        input component (MObject)
        '''
        
        geoFilter = oma.MFnGeometryFilter(self.deformerObject)
        deformerSet = geoFilter.deformerSet()
        deformerSetFn = om.MFnSet(deformerSet)
        deformerSetFn.addMember(self.meshPath,component)
        
     
    def getMembershipList(self):
        
        '''
        method for getting membership list for deformer sets
        output python bool list (membership list) 
        '''
        
        membershipList = []
        selectionList = om.MSelectionList()
        geoFilter = oma.MFnGeometryFilter(self.deformerObject)
        deformerSet = geoFilter.deformerSet()
        deformerSetFn = om.MFnSet(deformerSet)
        
        deformerSetFn.getMembers(selectionList,False)
        

        vertItr = om.MItGeometry(self.meshPath)
        
        while not vertItr.isDone():
            
            component = vertItr.currentItem()
            
            if selectionList.hasItem(self.meshPath,component):
        
                membershipList.append(True)
                
            elif selectionList.hasItem(self.meshObject):
                
                return self.createBlankList(0, True)[1]
                break
                
            else:
                
                membershipList.append(False)
            
            vertItr.next()
            
        return membershipList
    
    def reverseMembershipList(self):
        
        '''
        method for getting membership list for deformer sets
        output python bool list (membership list) 
        '''
        
        membershipList = []
        selectionList = om.MSelectionList()
        geoFilter = oma.MFnGeometryFilter(self.deformerObject)
        deformerSet = geoFilter.deformerSet()
        deformerSetFn = om.MFnSet(deformerSet)
        
        deformerSetFn.getMembers(selectionList,False)
        

        vertItr = om.MItMeshVertex(self.meshPath)
        
        while not vertItr.isDone():
            
            component = vertItr.currentItem()
            
            if selectionList.hasItem(self.meshPath,component):
        
                membershipList.append(False)
                
            elif selectionList.hasItem(self.meshObject):
                
                return self.createBlankList(0, False)[1]
                break
                
            else:
                
                membershipList.append(True)
            
            vertItr.next()
            
        return membershipList
        
     
    def setMembershipList(self,membershipList):
        
        '''
        method for setting membership list for deformer sets
        input python bool list (membership list) 
        '''
        
        geoFilter = oma.MFnGeometryFilter(self.deformerObject)
        deformerSet = geoFilter.deformerSet()
        deformerSetFn = om.MFnSet(deformerSet)
        
        addSelectionList = om.MSelectionList()
        removeSelectionList = om.MSelectionList()
        vertItr = om.MItGeometry(self.meshPath)
        
        while not vertItr.isDone():
            
            index = vertItr.index()
            component = vertItr.currentItem()
            
            if membershipList[index]:

                addSelectionList.add(self.meshPath,component)

            else:
                
                removeSelectionList.add(self.meshPath,component)
                    
            vertItr.next()
        
        if not addSelectionList.isEmpty(): 
            deformerSetFn.addMembers(addSelectionList)
        
        if not removeSelectionList.isEmpty():
            deformerSetFn.removeMembers(removeSelectionList)
            
    @staticmethod       
    def optimizeMembership(deformer,prune = 0.001):
        
        deformerObject = GenAPI.getMObject(deformer)
        geoFilter = oma.MFnGeometryFilter(deformerObject)
        deformerSet = geoFilter.deformerSet()
        deformerSetFn = om.MFnSet(deformerSet)
        
        addSelectionList = om.MSelectionList()
        removeSelectionList = om.MSelectionList()
        
        dagMembers = WeightListTool.getDagMembers(deformer)
        
        progressWindow = UILib.ProgressWin()
        progressWindow.setTitle('Optimizing Deformer')
        progressWindow.itr = len(dagMembers)
        
        for i in range(len(dagMembers)):
            
            dagPath = GenAPI.getDagPath(dagMembers[i])
            vertItr = om.MItGeometry(dagPath)
            weightListTool = WeightListTool(dagPath.fullPathName(),deformer)
            weightList = weightListTool.getWeightList()
            
            while not vertItr.isDone():
                index = vertItr.index()
                component = vertItr.currentItem()
                
                if weightList[index] < prune:
                    removeSelectionList.add(dagPath,component)
                 
                else:
                    addSelectionList.add(dagPath,component)
                    
                vertItr.next()
                
            if not addSelectionList.isEmpty(): 
                deformerSetFn.addMembers(addSelectionList)
            
            if not removeSelectionList.isEmpty():
                deformerSetFn.removeMembers(removeSelectionList)
                
            progressWindow.inc = i
            progressWindow.message = '%s...%s'%(deformer,dagMembers[i])
            progressWindow.progress()
        
        progressWindow.end()
        
    @staticmethod      
    def createBlankList(mesh,floatVal,boolVal):
        
        '''
        method for creating a blank weight and membershipList
        output blankList (python list)
        '''
        
        meshPath = GenAPI.getDagPath(mesh)
        vertItr = om.MItMeshVertex(meshPath)
        blankWeightList = []
        blankMemberList = []
        
        while not vertItr.isDone():
        
            blankWeightList.append(floatVal)
            blankMemberList.append(boolVal)
            vertItr.next()
            
        return [blankWeightList,blankMemberList]
        
    
        
    def mirrorWeightList(self,axis = 'x', direction = '<', table = [-1,1,1]):
        
        '''
        this method creates a mirrored weightlist and membership list for a single symetrical mesh
        '''
        
        vertItr = om.MItMeshVertex(self.meshPath)
        deformerWeightFn = oma.MFnWeightGeometryFilter(self.deformerObject)
                           
        util = om.MScriptUtil()
        weightList = []
        membershipList = []
        
        progressWindow = UILib.ProgressWin()
        progressWindow.setTitle('Mirror Wieghts')
        progressWindow.itr = vertItr.count()
        
        while not vertItr.isDone():
              
                
            currentIndex = vertItr.index()
            mirrorVert = MeasuringLib.MeasuringTool.getSymVert(self.meshPath, currentIndex, table = table)     
            weights = om.MFloatArray()
            
            tempItr = om.MItMeshVertex(self.meshPath)
            intPtr = util.asIntPtr()
            tempItr.setIndex(mirrorVert[0],intPtr)
            
            outComponent = tempItr.currentItem()
            
            deformerWeightFn.getWeights(self.meshPath,outComponent,weights)
                               
            membershipList.append(self.checkMembership(outComponent))
            
            weightList.append(weights[0])
                 
                
            progressWindow.inc = vertItr.index()
            progressWindow.message = '%s...%i of %i'%(self.mesh,vertItr.index(),vertItr.count())
            progressWindow.progress()

            vertItr.next()
            
        progressWindow.end()
        
        return weightList,membershipList
    
    @staticmethod
    def mirrorWeightListMultiMesh(fromMesh,toMesh,deformer,table = [-1,1,1]):
        
        '''
        this method will create a mirrored weightList from one mesh to another
        meshes must be symetrical
        input python string (fromMesh)
        input python string (toMesh)
        input python string (deformer)
        input python list (symetry table)
        '''

        weightList = []
        membershipList = []
        
        util = om.MScriptUtil()
        
        fromMeshPath = GenAPI.getDagPath(fromMesh)
        toMeshPath = GenAPI.getDagPath(toMesh)
        
        meshToVertItr = om.MItMeshVertex(toMeshPath)
        
        deformerObject = GenAPI.getMObject(deformer)
        
        deformerWeightFn = oma.MFnWeightGeometryFilter(deformerObject)
        weights = om.MFloatArray()
        
        progressWindow = UILib.ProgressWin()
        progressWindow.setTitle('Mirror Wieghts')
        progressWindow.itr = meshToVertItr.count()
        
        while not meshToVertItr.isDone():
            
            fromVertPoint = meshToVertItr.position(om.MSpace.kWorld)
            
            vertID =  MeasuringLib.MeasuringTool.getSymVertFromClosestPoint(fromMeshPath,fromVertPoint,table = table)

            meshFromVertItr = om.MItMeshVertex(fromMeshPath)
            intPtr = util.asIntPtr()
            
            meshFromVertItr.setIndex(vertID[0],intPtr)
            fromVert = meshToVertItr.currentItem()
            
            try:
                deformerWeightFn.getWeights(fromMeshPath,fromVert,weights)
                weightTool = WeightListTool(fromMesh,deformer)
                membershipList.append(weightTool.checkMembership(fromVert))
                weightList.append(weights[0])
            except:
                weightTool = WeightListTool(fromMesh,deformer)
                membershipList.append(weightTool.checkMembership(fromVert))
                weightList.append(0)
            
            
            
            progressWindow.inc = meshToVertItr.index()
            progressWindow.message = '%s...%i of %i'%(fromMesh,meshToVertItr.index(),meshToVertItr.count())
            progressWindow.progress()
             
            meshToVertItr.next()
            
        progressWindow.end()
            
        return weightList,membershipList
        
    
     
    def reverseWeightList(self):
        
        '''method for reversing weighList on current mesh'''  
        
        deformerWeightFn = oma.MFnWeightGeometryFilter(self.deformerObject)
        weightList = om.MFloatArray()
        verts = GenAPI.getMObjectAllVerts(self.mesh)
        deformerWeightFn.getWeights(self.meshPath,verts,weightList)
        
        reverseWeightList = []
    
        for i in range(weightList.length()):
                       
            reverseWeight = abs(weightList[i] - 1.00000)
            reverseWeightList.append(reverseWeight)
                
        return reverseWeightList
    
   
    @staticmethod    
    def transferWeightList(geo,fromDeformer,toDeformer):
        
        '''
         method for quickly transfering weightList
        input python string (mesh)
        input pythin string (fromDeformer)
        input python string (toDeformer)
        '''
        
        geoPath = GenAPI.getDagPath(geo)
        deformerObjectFrom = GenAPI.getMObject(fromDeformer)
        deformerObjectTo = GenAPI.getMObject(toDeformer)
        vertItr = om.MItMeshVertex(geoPath)
        deformerWeightFn = oma.MFnWeightGeometryFilter()
        
        
        while not vertItr.isDone():
            
            componentObject = vertItr.currentItem()
            weights = om.MFloatArray()
            deformerWeightFn.setObject(deformerObjectFrom)
            deformerWeightFn.getWeights(geoPath,componentObject,weights)
            deformerWeightFn.setObject(deformerObjectTo)
            deformerWeightFn.setWeight(geoPath,componentObject,weights)
            vertItr.next()
            
    
    @staticmethod               
    def transferReverseWeightList(geo,fromDeformer,toDeformer):
        
        '''
        method for quickly transfering reversed weightList
        input python string (mesh)
        input pythin string (fromDeformer)
        input python string (toDeformer)
        '''
        
        geoPath = GenAPI.getDagPath(geo)
        deformerObjectFrom = GenAPI.getMObject(fromDeformer)
        deformerObjectTo = GenAPI.getMObject(toDeformer)
        vertItr = om.MItMeshVertex(geoPath)
        deformerWeightFn = oma.MFnWeightGeometryFilter()
        
        while not vertItr.isDone():
            
            componentObject = vertItr.currentItem()
            weights = om.MFloatArray()
            deformerWeightFn.setObject(deformerObjectFrom)
            deformerWeightFn.getWeights(geoPath,componentObject,weights)
            
            if weights[0] > 0.000:
                weights[0] = abs(weights[0] - 1.0)
                
            deformerWeightFn.setObject(deformerObjectTo)
            deformerWeightFn.setWeight(geoPath,componentObject,weights)
            vertItr.next()   
      
    def mirrorDeformerWeightSingleMesh(self,axis = 'x',direction = '>',table = [-1,1,1]):
        
        '''
        method for mirroring deformer weights for one deformer...only works on single symetrical mesh
        input python string (axis)
        input python int list (table)
        '''

        vertItr = om.MItMeshVertex(self.meshPath)
        deformerWeightFn = oma.MFnWeightGeometryFilter(self.deformerObject)
        
        util = om.MScriptUtil()
        
        progressWin = UILib.ProgressWin()
        progressWin.itr = vertItr.count()
        progressWin.setTitle('Mirror Deformer')
        
        while not vertItr.isDone():
        
            inComponent = vertItr.currentItem()
            currentPosition = vertItr.position(om.MSpace.kWorld)
                        
            if eval('currentPosition.%s%s0.00000'%(axis,direction)):
                
                currentIndex = vertItr.index()
                inComponent = vertItr.currentItem()
                mirrorVert = MeasuringLib.MeasuringTool.getSymVert(self.meshPath, currentIndex, table)        
                weights = om.MFloatArray()
                
                tempItr = om.MItMeshVertex(self.meshPath)
                intPtr = util.asIntPtr()
                tempItr.setIndex(mirrorVert[0],intPtr)
                outComponent = tempItr.currentItem()
                
                if self.checkMembership(inComponent):
                    
                    self.addComponentToMembershipList(outComponent)
                
                deformerWeightFn.getWeights(self.meshPath,inComponent,weights)
                deformerWeightFn.setWeight(self.meshPath,outComponent,weights)
    
            progressWin.inc = vertItr.index()
            progressWin.message = '%s.vtx[%i]'%(self.mesh,progressWin.inc)
            progressWin.progress()       
            
            vertItr.next()
            
        progressWin.end()
                    
    def mirrorDeformerWeightMultiMesh(self,geoTo,axis = 'x',table = [-1,1,1]):
        
        '''
        method for mirroring deformer...only works on meshes mirrored across given axis
        input python string (geoFrom)
        imput python string (geoTo)
        input python string (deformer)
        input python string (axis)
        input python int list (table)
        '''
        
        nodePathTo = GenAPI.getDagPath(geoTo)
        vertItr = om.MItMeshVertex(self.meshPath)
        
        deformerWeightFn = oma.MFnWeightGeometryFilter(self.deformerObject)
        
        util = om.MScriptUtil()
        
        progressWin = UILib.ProgressWin()
        progressWin.itr = vertItr.count()
        progressWin.setTitle('Mirror Deformer')
        
        while not vertItr.isDone():
            
            inComponent = vertItr.currentItem()
            currentPosition = vertItr.position(om.MSpace.kWorld)
            
            inComponent = vertItr.currentItem()
            mirrorVert = MeasuringLib.MeasuringTool.getSymVertFromClosestPoint(nodePathTo, currentPosition, table)     
            weights = om.MFloatArray()
            
            tempItr = om.MItMeshVertex(nodePathTo)
            intPtr = util.asIntPtr()
            tempItr.setIndex(mirrorVert[0],intPtr)
            outComponent = tempItr.currentItem()
            
            if self.checkMembership(inComponent):
                
                self.addComponentToMembershipList(outComponent)
            
            deformerWeightFn.getWeights(self.meshPath,inComponent,weights)
            deformerWeightFn.setWeight(nodePathTo,outComponent,weights)
            
            progressWin.inc = vertItr.index()
            progressWin.message = '%s.vtx[%i]'%(self.mesh,progressWin.inc)
            progressWin.progress() 
    
            vertItr.next()
            
        progressWin.end()
            
            
def mirrorDeformerWeights(deformer,prefix = 'LT',oppPrefix = 'RT', axis = 'x', direction = '>',table = [-1,1,1]):
    
    dagList = WeightListTool.sortDagMembers(deformer,prefix,oppPrefix)
        
    singles = dagList[0]
    doubles = dagList[1]  
           
    for mesh in singles:
        
        try:
            
            deformerTool = WeightListTool(mesh,deformer)
            deformerTool.mirrorDeformerWeightSingleMesh(axis = axis,direction = direction,table = table)
            om.MGlobal.displayInfo('Mirrored %s weights for %s'%(deformer,mesh))
        
        except RuntimeError:
            om.MGlobal.displayError('Cannot mirror %s for %s.Check naming....'%(deformer,mesh))
            raise
 

    for mesh in doubles:
        
        try:

            deformerTool = WeightListTool(mesh[0],deformer)
            deformerTool.mirrorDeformerWeightMultiMesh(mesh[1], axis = axis, table = table)
            om.MGlobal.displayInfo('Mirrored %s weights for %s'%(deformer,mesh))
            
        except RuntimeError:
            om.MGlobal.displayError('Cannot mirror %s for %s.Check naming....'%(deformer,mesh))
            raise
        
    
            
            
def flipDeformerWeights(deformer,prefix = 'LT',oppPrefix = 'RT', axis = 'x', direction = '<',table = [-1,1,1]):
   
    dagList = WeightListTool.sortDagMembers(deformer,prefix = prefix,oppPrefix = oppPrefix)
    singles = dagList[0]
    doubles = dagList[1]
            
            
    for mesh in singles:
        
        deformerTool = WeightListTool(mesh,deformer)
        weightList = deformerTool.mirrorWeightList(axis,direction,table)
        
        
        #deformerTool.setMembershipList(weightList[1])
        deformerTool.setWeightList(weightList[0])
        
    
    for mesh in doubles:
        
        weightListA = WeightListTool.mirrorWeightListMultiMesh(mesh[0], mesh[1], deformer, table)
        weightListB = WeightListTool.mirrorWeightListMultiMesh(mesh[1], mesh[0], deformer, table)
        
        deformerTool = WeightListTool(mesh[1],deformer)
        deformerTool.setMembershipList(weightListA[1])
        deformerTool.setWeightList(weightListA[0])
        
        deformerTool.__init__(mesh[0],deformer)
        deformerTool.setMembershipList(weightListB[1])
        deformerTool.setWeightList(weightListB[0])
        
    om.MGlobal.displayInfo('Flipped %s weights'%deformer)
      
            
def extrapToCluster(transform,meshes):
    
    '''function for extraping weights from a transform to a cluster'''
       
    vertSelection = om.MSelectionList()
    
    for mesh in meshes:
        
        #gathering verticies
        meshPath = GenAPI.getDagPath(mesh)
        meshObject = GenAPI.getMObject(mesh)
        shape = mesh
        
        if meshObject.apiTypeStr() == 'kTransform':
            shape = cmds.listRelatives(meshPath.fullPathName(),type = 'shape')[0]
            
        meshObject = GenAPI.getMObject(shape)
        verts = GenAPI.getMObjectAllVerts(mesh)
        vertSelection.add(meshPath,verts)
        
    om.MGlobal.setActiveSelectionList(vertSelection)

    #creating cluster    
    cluster = cmds.cluster()
    transformPosition = cmds.xform(transform,q = True,ws = True, rp = True)
    clusterShape = cmds.listRelatives(cluster[1],type = 'shape')
    
    cmds.setAttr('%s.originX'%clusterShape[0],transformPosition[0])
    cmds.setAttr('%s.originY'%clusterShape[0],transformPosition[1])
    cmds.setAttr('%s.originZ'%clusterShape[0],transformPosition[2])
    
    cmds.setAttr('%s.rotatePivotX'%cluster[1],transformPosition[0])
    cmds.setAttr('%s.rotatePivotY'%cluster[1],transformPosition[1])
    cmds.setAttr('%s.rotatePivotZ'%cluster[1],transformPosition[2])
    
    cmds.setAttr('%s.scalePivotX'%cluster[1],transformPosition[0])
    cmds.setAttr('%s.scalePivotY'%cluster[1],transformPosition[1])
    cmds.setAttr('%s.scalePivotZ'%cluster[1],transformPosition[2])
    
    #retrieving weight lists

    progressWin = UILib.ProgressWin()
    progressWin.setTitle('Extrap Cluster')
    progressWin.itr = len(meshes)
    inc = 0
    for mesh in meshes:
        
        meshObject = GenAPI.getMObject(mesh)
        meshPath = GenAPI.getDagPath(mesh)
        shape = mesh
        weightList = []
        
        if meshObject.apiTypeStr() == 'kTransform':
            shape = cmds.listRelatives(meshPath.fullPathName(),type = 'shape')[0]
        
        weightList = MeasuringLib.MeasuringTool.createWeigthListFromTransform(shape,transform)
        weightTool = WeightListTool(shape,cluster[0])
        weightTool.setWeightList(weightList)
                 
        progressWin.inc = inc
        progressWin.progress()
        inc += 1
        
    progressWin.end()
 
    om.MGlobal.displayInfo('Extraped cluster from %s'%transform)
    

#function for transfering weights to given deformer   
def extrapWeightsToExistingDeformer(transform,meshes,deformer):
    
    weightLists = []

    for mesh in meshes:
        
        weightList = MeasuringLib.MeasuringTool.createWeigthListFromTransform(mesh, transform)
        weightLists.append(weightList)
        
    meshInc = 0
        
    for mesh in meshes:
        
        deformerTool = WeightListTool(mesh,deformer)
        deformerTool.setWeightList(weightLists[meshInc])
        meshInc += 1
    
    om.MGlobal.displayInfo('Extraped weights from %s'%transform)
    

#function for mirroring clusters
def mirrorCluster(transform,deformerName,prefix = 'L',oppPrefix = 'R', axis = 'x',direction = '<', table = [-1,1,1]):
    
    vertSelection = om.MSelectionList()
    name = transform.split(prefix)[1]
    
    dagList = WeightListTool.sortDagMembers(deformerName,prefix,oppPrefix)
    
    if not len(dagList) == 0:
    
        singles = dagList[0]
        doubles = dagList[1]
        members = WeightListTool.getDagMembers(deformerName)
        
                
        for mesh in singles:
            
            meshPath = GenAPI.getDagPath(mesh)
            verts = GenAPI.getMObjectAllVerts(mesh)
            vertSelection.add(meshPath,verts)
            
        for meshGroup in doubles:
            
            for mesh in meshGroup: 
                
                if not mesh in members:
                    blankWeightList = WeightListTool.createBlankList(mesh, 0, True)
                    weightTool = WeightListTool(mesh,deformerName)
                    weightTool.setMembershipList(blankWeightList[1])
                    weightTool.setWeightList(blankWeightList[0])
                
                meshPath = GenAPI.getDagPath(mesh)
                verts = GenAPI.getMObjectAllVerts(mesh)
                vertSelection.add(meshPath,verts)
                
        om.MGlobal.setActiveSelectionList(vertSelection)
        
        #creating cluster    
        cluster = cmds.cluster()
        transformPosition = cmds.xform(transform,q = True,ws = True, rp = True)
        mirrorPosition = [transformPosition[0] * table[0],transformPosition[1] * table[1],transformPosition[2] * table[2]]
        
        clusterShape = cmds.listRelatives(cluster[1],type = 'shape')
        
        cmds.setAttr('%s.originX'%clusterShape[0],mirrorPosition[0])
        cmds.setAttr('%s.originY'%clusterShape[0],mirrorPosition[1])
        cmds.setAttr('%s.originZ'%clusterShape[0],mirrorPosition[2])
        
        cmds.setAttr('%s.rotatePivotX'%cluster[1],mirrorPosition[0])
        cmds.setAttr('%s.rotatePivotY'%cluster[1],mirrorPosition[1])
        cmds.setAttr('%s.rotatePivotZ'%cluster[1],mirrorPosition[2])
        
        cmds.setAttr('%s.scalePivotX'%cluster[1],mirrorPosition[0])
        cmds.setAttr('%s.scalePivotY'%cluster[1],mirrorPosition[1])
        cmds.setAttr('%s.scalePivotZ'%cluster[1],mirrorPosition[2])
        
        for mesh in singles:
            
            weightTool = WeightListTool(mesh,deformerName)
            weightList = weightTool.mirrorWeightList(table = table,axis = axis, direction = direction)
            weightTool.__init__(mesh,cluster[0])
            
            print weightList
     
            weightTool.setWeightList(weightList[0])
            weightTool.setMembershipList(weightList[1])
            
        
        for meshGroup in doubles:
            
            
            weightListA = WeightListTool.mirrorWeightListMultiMesh(meshGroup[0], meshGroup[1], deformerName, table)
            weightListB = WeightListTool.mirrorWeightListMultiMesh(meshGroup[1], meshGroup[0], deformerName, table)
            
            deformerTool = WeightListTool(meshGroup[1],cluster[0])
            deformerTool.setMembershipList(weightListA[1])
            deformerTool.setWeightList(weightListA[0])
            
            deformerTool.__init__(meshGroup[0],cluster[0])
            deformerTool.setMembershipList(weightListB[1])
            deformerTool.setWeightList(weightListB[0])
        
        try:    
            cmds.rename(cluster[1],'%s%s'%(oppPrefix,name))
            
        except:
            pass
            
        om.MGlobal.displayInfo('Created mirrored cluster from %s'%deformerName)
        
    else:
        om.MGlobal.displayError('Cannot mirror %s. Please make sure both sides are members.'%deformerName)
        

def createClusterFromSoftSelection(name):
    
    '''function for creating a cluster from a soft selection'''
    
    sel = cmds.ls(sl = True)
    cmds.select(cl = True)
    
    cmds.select(sel)
    
    clusterData = MeasuringLib.MeasuringTool.createWeightListFromSoftSelection()
    cluster = cmds.cluster(name = name)
      
    deformerObject = GenAPI.getMObject(cluster[0])
    deformerTool = oma.MFnWeightGeometryFilter(deformerObject)
    
    inc = 0
    
    progressWindow = UILib.ProgressWin()
    progressWindow.setTitle('Cluster From Soft Selection')
    progressWindow.itr = len(clusterData[1])
    
    for components in clusterData[1]:
        
        geoFilter = oma.MFnGeometryFilter(deformerObject)
        deformerSet = geoFilter.deformerSet()
        setFn = om.MFnSet(deformerSet)
        setFn.addMember(components[0],components[1])
        
        floatArray = om.MFloatArray()
        
        for i in range(len(clusterData[2][inc])):
        
            floatArray.append(clusterData[2][inc][i])
            
        deformerTool.setWeight(components[0],components[1],floatArray)
        inc += 1
        
        progressWindow.inc = inc
        progressWindow.message = '%s.vtx[%i]'%(components[0].fullPathName(),inc)
        progressWindow.progress()
    
    progressWindow.end()
    om.MGlobal.displayInfo('Created cluster from soft selection')
    
    
def createClusterFromMesh(fromMesh,toMesh):
    
    '''
    Function for creating cluster from another duplicate modified mesh
    input fromMesh (python string)
    input toMesh (python string)
    '''
    
    
    toMeshPath = GenAPI.getDagPath(toMesh)
    
    fromVerts = GenAPI.getMObjectAllVerts(toMesh)
    selectionList = om.MSelectionList()
    
    selectionList.add(toMeshPath,fromVerts)
    om.MGlobal.setActiveSelectionList(selectionList)
    
    #creating cluster   
    cluster = cmds.cluster()
    transformPosition = cmds.xform(fromMesh,q = True,ws = True, rp = True)
    
    clusterShape = cmds.listRelatives(cluster[1],type = 'shape')
    
    cmds.setAttr('%s.originX'%clusterShape[0],transformPosition[0])
    cmds.setAttr('%s.originY'%clusterShape[0],transformPosition[1])
    cmds.setAttr('%s.originZ'%clusterShape[0],transformPosition[2])
    
    cmds.setAttr('%s.rotatePivotX'%cluster[1],transformPosition[0])
    cmds.setAttr('%s.rotatePivotY'%cluster[1],transformPosition[1])
    cmds.setAttr('%s.rotatePivotZ'%cluster[1],transformPosition[2])
    
    cmds.setAttr('%s.scalePivotX'%cluster[1],transformPosition[0])
    cmds.setAttr('%s.scalePivotY'%cluster[1],transformPosition[1])
    cmds.setAttr('%s.scalePivotZ'%cluster[1],transformPosition[2])
    
    weightList = MeasuringLib.MeasuringTool.createWeightListFromMesh(fromMesh, toMesh)
    deformerTool = WeightListTool(toMesh,cluster[0])
    deformerTool.setWeightList(weightList)
    
    om.MGlobal.displayInfo('Created cluster from %s'%fromMesh)
    

def combineCluster(clusterHandles,clamp):
    
    '''
    function for setting a cluster from combined weightlist of given deformers
    input clusterHandles (ptyhon list)
    input clamp (python bool)
    '''
    
    #gathering deformers
    deformers = []
    
    for handle in clusterHandles:
        
        connection = cmds.connectionInfo('%s.worldMatrix[0]'%handle, dfs = True)[0]
        deformer = connection.split('.')[0]
        deformers.append(deformer)
        
    
    #creating null cluster
    cmds.select(cl = True)
    cluster = cmds.cluster()
    pos = cmds.xform(clusterHandles[-1],q = True, ws = True, rp = True)
    clusterShape = cmds.listRelatives(cluster[1],type = 'shape')
    
    #move clusterShape
    
    cmds.setAttr('%s.originX'%clusterShape[0],pos[0])
    cmds.setAttr('%s.originY'%clusterShape[0],pos[1])
    cmds.setAttr('%s.originZ'%clusterShape[0],pos[2])
    
    cmds.setAttr('%s.rotatePivotX'%cluster[1],pos[0])
    cmds.setAttr('%s.rotatePivotY'%cluster[1],pos[1])
    cmds.setAttr('%s.rotatePivotZ'%cluster[1],pos[2])
    
    cmds.setAttr('%s.scalePivotX'%cluster[1],pos[0])
    cmds.setAttr('%s.scalePivotY'%cluster[1],pos[1])
    cmds.setAttr('%s.scalePivotZ'%cluster[1],pos[2])
    
    #gathering members
    allmembers = []
    
    for deformer in deformers:
        
        members = WeightListTool.getDagMembers(deformer)  
                
        for member in members:
        
            allmembers.append(member)
            
    completeDagSet = set(allmembers)
    
    progressWin = UILib.ProgressWin()
    progressWin.setTitle('Combining Clusters')
    progressWin.itr = len(completeDagSet)
    inc = 0

    #creating weight and membership lists
    for member in completeDagSet:
           
        completeWeightList = WeightListTool.createBlankList(member, 0, False)[0]
        completeMembership = WeightListTool.createBlankList(member, 0, False)[1]
        
        for deformer in deformers:
            
            deformerTool = WeightListTool(member,deformer)
            
            weightList = deformerTool.getWeightList()
            membershipList = deformerTool.getMembershipList()
            
            for i in range(len(weightList)):
                
                completeWeightList[i] += weightList[i]
                completeMembership[i] += membershipList[i]
                
            deformerTool.__init__(member,cluster[0])
            
            if clamp:
                
                for i in range(len(completeWeightList)):
                   
                    currentValue = completeWeightList[i] 
                    completeWeightList[i]  = max(min(currentValue, 1), 0)
            
            progressWin.inc = inc
            progressWin.message = '%s...'%member
            progressWin.progress()
            inc += 1
        
        deformerTool.setMembershipList(completeMembership)
        deformerTool.setWeightList(completeWeightList)
        
    progressWin.end()
    om.MGlobal.displayInfo('Combine Complete')
    
def loadClusters(clusterDicts):
    
    
    for clusterDict in clusterDicts:
        
        clusterHandleName = clusterDict.get('clusterHandle')
        clusterName = clusterDict.get('clusterName')
        pos = clusterDict.get('pos')
        dagMembers = clusterDict.get('dagMembers')
       
        selectionList = om.MSelectionList()
        
        for member in dagMembers:
            
            meshPath = GenAPI.getDagPath(member)
            verts = GenAPI.getMObjectAllVerts(member)
            selectionList.add(meshPath,verts)
        
        om.MGlobal.setActiveSelectionList(selectionList)
        
        #creating cluster    
        cluster = cmds.cluster()
        clusterShape = cmds.listRelatives(cluster[1],type = 'shape')
        
        cmds.setAttr('%s.originX'%clusterShape[0],pos[0])
        cmds.setAttr('%s.originY'%clusterShape[0],pos[1])
        cmds.setAttr('%s.originZ'%clusterShape[0],pos[2])
        
        cmds.setAttr('%s.rotatePivotX'%cluster[1],pos[0])
        cmds.setAttr('%s.rotatePivotY'%cluster[1],pos[1])
        cmds.setAttr('%s.rotatePivotZ'%cluster[1],pos[2])
        
        cmds.setAttr('%s.scalePivotX'%cluster[1],pos[0])
        cmds.setAttr('%s.scalePivotY'%cluster[1],pos[1])
        cmds.setAttr('%s.scalePivotZ'%cluster[1],pos[2])
        
        inc = 0
        
        progressWin = UILib.ProgressWin()
        progressWin.itr = len(dagMembers)
        progressWin.setTitle('Loading Clusters')
        
        for member in dagMembers:
            

            deformerTool = WeightListTool(member,cluster[0])
            weightList = clusterDict.get('weightList')[inc]
            membershipList = clusterDict.get('membershipList')[inc]
            deformerTool.setMembershipList(membershipList)
            deformerTool.setWeightList(weightList)
            inc += 1
            
            progressWin.message = member
            progressWin.inc = inc
            progressWin.progress()
            
        
        cmds.rename(cluster[0],clusterName)
        cmds.rename(cluster[1],clusterHandleName)
            
        progressWin.end()
        om.MGlobal.displayInfo('Successfully loaded clusters.')
            
        
    
        
            
            
        
        