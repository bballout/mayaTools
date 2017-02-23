'''
Created on Jul 23, 2012

@author: balloutb
'''

import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya.cmds as cmds
import GenAPI
import MeasuringLib
import DeformerLib
import UILib


class SkinningTool():
    
    '''Class for querying data and manipulating skinClusters'''
    
    def __init__(self,skincluster = '',shape = ''):
        
        self.skincluster = skincluster
        self.shape = shape
        
        if not self.skincluster == '':
            
            self.skinclusterObject = GenAPI.getMObject(skincluster)
            self.skinclusterFn = oma.MFnSkinCluster(self.skinclusterObject)
            
        if not self.shape == '':
            
            self.shapePath = GenAPI.getDagPath(self.shape)
            self.shapeObject = GenAPI.getMObject(self.shape)
        
    
    @staticmethod
    def getSkinCluster(shape):
        
        '''
        get skinCluster from shape
        input python string (shape)
        out mObject (skincluster)
        '''
        
        shapeObject = GenAPI.getMObject(shape)
        
        depItr = om.MItDependencyGraph(shapeObject,om.MFn.kSkinClusterFilter,
                                       om.MItDependencyGraph.kUpstream,om.MItDependencyGraph.kDepthFirst,
                                       om.MItDependencyGraph.kNodeLevel)
    

        return depItr.currentItem(),GenAPI.getStringFromMObject(depItr.currentItem())
        
        
   
    @staticmethod
    def getAllSkinClusters():
        
        '''
        find all skincluster nodes in scene
        output MSelectionList
        '''
        
    
        itr = om.MItDependencyNodes(om.MFn.kSkinClusterFilter)
        outputSelectionList = om.MSelectionList()
        
        while not itr.isDone():
        
            outputSelectionList.add(itr.thisNode())
            itr.next()
            
        return outputSelectionList
    
     
    def getInfluencesFromSkincluster(self):
        
        '''
        get influences from skincluster
        output MDagPathArray (influences)   
        '''
        
        dagArray = om.MDagPathArray()
        self.skinclusterFn.influenceObjects(dagArray)
        return dagArray
    
    
    def getInfluencesAffectingPointsFromLists(self,selectionList):
       
        ''' 
        returns influences that affect components
        input MSelectionList
        output MSelectionList
        '''
            
        array = []
        selectionList.getSelectionStrings(array)
        flattenedArray = GenAPI.flattenList(array)
                
        influences = self.getInfluencesFromSkincluster()
        influencdSelectionList = om.MSelectionList()
        weights = om.MDoubleArray()
        
        outputSelectionList = om.MSelectionList()
        
        for component in flattenedArray:
            
            for i in range(influences.length()):
                
                self.skinclusterFn.getPointsAffectedByInfluence(influences[i],influencdSelectionList,weights)
                tempArray = []
                influencdSelectionList.getSelectionStrings(tempArray)
                tempFlattenedArray = GenAPI.flattenList(tempArray)
                
                for tempComponent in tempFlattenedArray:
                    
                    if tempComponent == component:
                        outputSelectionList.add(influences[i])
                       
        return outputSelectionList
    
    
    def getInfluencesAffectingPoints(self,vertList,geo):
        
        '''
        returns influences that affect components
        input MObject (components)
        input DagPath (mesh) 
        returns MSelectionList
        '''
            
        influenceArray = om.MDagPathArray()
        self.skinclusterFn.influenceObjects(influenceArray)
        
        outputSelectionList = om.MSelectionList()
        
        for influence in range(influenceArray.length()):
            
            weightList = om.MDoubleArray()
            index = self.skinclusterFn.indexForInfluenceObject(influenceArray[influence])
            
            self.skinclusterFn.getWeights(geo,vertList,index,weightList)
            
            for weightValue in range(weightList.length()):
                
                if weightList[weightValue] > 0:
                    
                    outputSelectionList.add(influenceArray[influence])
                
        return outputSelectionList
    
    
    def getPointsAffectedByInfluence(self,influence):
        
        '''
        returns points that are affected by an influence
        input DagPath (influence) 
        returns MSelectionList
        '''
        
        outputSelectionList = om.MSelectionList()
        weights = om.MDoubleArray()
        self.skinclusterFn.getPointsAffectedByInfluence(influence,outputSelectionList,weights)
        return outputSelectionList
    
    
    def getUnlockedInfluences(self):
        
        '''
        returns influences that are locked
        output MSelectionList
        '''
        
        influences = self.getInfluencesFromSkincluster()
        outputSelectionList = om.MSelectionList()
        
        for i in range(influences.length()):
        
            jointObject = influences[i].node() 
            nodeFn = om.MFnDependencyNode(jointObject)
            plug = om.MPlug(jointObject,nodeFn.attribute('lockInfluenceWeights'))
            value = plug.asInt(om.MDGContext())
            
            if value == 0:
                outputSelectionList.add(influences[i])
                
        return outputSelectionList
    
    
    def getWeights(self,verts,influence):
        
        '''
        get influence value
        input MObject (verts)
        input MDagPath (influence)
        returns MDoubleArray (weights)
        '''
        
        index = self.skinclusterFn.indexForInfluenceObject(influence)
        weights = om.MDoubleArray()
        self.skinclusterFn.getWeights(self.shape,verts,index,weights)
        return weights
    


    def setWeights(self,influence,weightList):
        
        '''
        set influence value ONLY WORKS FOR POLY MESH
        input MDagPath (influence)
        input python float list (weightList)
        '''
        
        index = self.skinclusterFn.indexForInfluenceObject(influence)
        util = om.MScriptUtil()
        weights = om.MFloatArray()        
        util.createFloatArrayFromList(weightList,weights)
        oldValues = om.MFloatArray()
        
        meshVertItr = om.MItMeshVertex(self.shapeObject)
        
        while not meshVertItr.isDone():
            
            vert = meshVertItr.currentItem()
            vertIndex = meshVertItr.index()
        
            self.skinclusterFn.setWeights(self.shapePath,vert,index,weightList[vertIndex],True,oldValues)
            
            meshVertItr.next()
    
    
    def getWeightsFromLattice(self,influence):
        
        '''
        method for returning weightlist of given influence from a lattice
        input MDagPath (influence) 
        output python list (weights)  
        '''
        
        weightList = []
        
        latticePntSelection = GenAPI.getLatticePoints(self.shapePath)
        selectionItr = om.MItSelectionList(latticePntSelection) 
        
        index = self.skinclusterFn.indexForInfluenceObject(influence)
        weights = om.MFloatArray()
        
        intArray = om.MIntArray()
        intArray.append(index)
        
        mdagPath = om.MDagPath()
        component = om.MObject()
            
        
        while not selectionItr.isDone():
            
            selectionItr.getDagPath(mdagPath,component)
            
            self.skinclusterFn.getWeights(self.shapePath,component,index,weights)
            
            weightList.append(weights[0])
            selectionItr.next()
        
        return weightList
       
        
    def setWeightsForLattice(self,influence,weightList):
        
        '''
        method for setting skinWeight value for lattice points
        input MDagPath (influence)
        input python float list (weightList) 
        '''

        latticePntSelection = GenAPI.getLatticePoints(self.shapePath)
        selectionItr = om.MItSelectionList(latticePntSelection) 
        
        index = self.skinclusterFn.indexForInfluenceObject(influence)
        
        oldValues = om.MFloatArray()
        
        mdagPath = om.MDagPath()
        component = om.MObject()
        
        itrIndex = 0
        
        while not selectionItr.isDone():
            
            selectionItr.getDagPath(mdagPath,component)

            self.skinclusterFn.setWeights(self.shapePath,component,index,weightList[itrIndex],True,oldValues)
            
            itrIndex += 1 
            selectionItr.next()
        
            
    #CLASS END
 
def extrapFromLattice(latticeTransform):
    
    '''function for extraping skincluster from ffd'''
    

    #gather lattice nodes
    latticeShape = cmds.listRelatives(latticeTransform, type = 'shape')[0]
    
    if cmds.nodeType(latticeShape) == 'lattice':
        
        
        progressWin = UILib.ProgressWin()
        progressWin.setTitle('Extrap Skincluster from Lattice')
        progressWin.itr = 7
        
        progressWin.inc = 1
        progressWin.progress()  
            
        
        latticeFFD = cmds.listConnections(latticeShape, type = 'ffd')[0]
        #get skincluster and gather influences in lattice skincluster
        
        try:
            latticeSkinCluster = SkinningTool.getSkinCluster(latticeShape)
            latticeSkinningTool = SkinningTool(skincluster = latticeSkinCluster[1],shape = latticeShape)
            influenceArray = latticeSkinningTool.getInfluencesFromSkincluster()
            floatingJointList = []
            
            progressWin.inc = 2
            progressWin.progress() 
            #create string list from influence array
            latticeInfluenceStringList = []
            for latInf in range(influenceArray.length()):
            
                latticeInfluenceStringList.append(influenceArray[latInf].fullPathName())
                print influenceArray[latInf].fullPathName()
            
            progressWin.inc = 3
            progressWin.progress() 
            #swapping influence for floating joints
            for influenceInc in range(influenceArray.length()):
                    
                    currentInfluenceString = influenceArray[influenceInc].fullPathName()
                    
                    #clear selection and gather verts
                    om.MGlobal.clearSelectionList()
                    
                    #creating floating joint
                    transformFn = om.MFnTransform(influenceArray[influenceInc])
                    position = transformFn.getTranslation(om.MSpace.kWorld)
                    
                    floatingJoint = [cmds.joint()][0]
                    floatingJointPath = GenAPI.getDagPath(floatingJoint)
                    transformFn.setObject(floatingJointPath)
                    transformFn.setTranslation(position,om.MSpace.kWorld)
                    floatingJointList.append(floatingJoint)
                    
                    #add floating joint to skin cluster and swap weights
                    cmds.skinCluster(latticeSkinCluster[1],e = True , weight = 0,addInfluence = floatingJoint)
                    
                    latticeWeightList = latticeSkinningTool.getWeightsFromLattice(influenceArray[influenceInc])
            
                    #re-gather influences after adding floating joint
                    latticeInfluenceStringList02 = []
                    
                    influenceArray02 = latticeSkinningTool.getInfluencesFromSkincluster()
            
                    for latInf in range(influenceArray02.length()):
                    
                        latticeInfluenceStringList02.append(influenceArray02[latInf].fullPathName())
                    
                    #lock influences        
                    for influence in latticeInfluenceStringList02:
                        
                        cmds.setAttr('%s.lockInfluenceWeights'%influence,1)
        
                    cmds.setAttr('%s.lockInfluenceWeights'%floatingJoint,0)
                    cmds.setAttr('%s.lockInfluenceWeights'%currentInfluenceString,0)                
                    
                    #swapWeights
        
                    latticeSkinningTool.setWeightsForLattice(floatingJointPath,latticeWeightList)   
            
            progressWin.inc = 4
            progressWin.progress() 
            #gather meshes affected by lattice
            latticeFn = oma.MFnLatticeDeformer(GenAPI.getMObject(latticeFFD))
            meshObjArray = om.MObjectArray()
            latticeFn.getAffectedGeometry(meshObjArray)
            
            progressWin.inc = 5
            progressWin.progress() 
            #iterate meshes and gather weightLists   
            for meshInc in range(meshObjArray.length()):
                
                weightLists = []
           
                #creating weightList from floating joint      
                for floatingJoint in floatingJointList:
        
                    #creating weightList
                    weightList = MeasuringLib.MeasuringTool.createWeigthListFromInfluence2(GenAPI.getStringFromMObject(meshObjArray[meshInc]),floatingJoint) 
                    weightLists.append(weightList)
                
        
                #remove mesh from lattice
                latticeFn.removeGeometry(meshObjArray[meshInc])
                        
                #create skincluster for current mesh in iteration 
                
                history  = cmds.listHistory(GenAPI.getStringFromMObject(meshObjArray[meshInc]),pdo = 1 ,il = 2)
                                            
                for node in history:
                    if cmds.nodeType(node) == 'skinCluster':
                        cmds.delete(node)
                    
                meshSkinCluster = cmds.skinCluster(GenAPI.getStringFromMObject(meshObjArray[meshInc]),latticeInfluenceStringList)[0]
                meshSkinningTool = SkinningTool(meshSkinCluster,GenAPI.getStringFromMObject(meshObjArray[meshInc]))
        
                #unlock all influences
                for influence in latticeInfluenceStringList:
                    
                    cmds.setAttr('%s.lockInfluenceWeights'%influence,0)
            
                #setWeightLists 
                for influenceInc in range(influenceArray.length()):
                    
                    meshSkinningTool.setWeights(influenceArray[influenceInc], weightLists[influenceInc])
                             
                    cmds.setAttr('%s.lockInfluenceWeights'%influenceArray[influenceInc].fullPathName(),1)
            
            progressWin.inc = 6
            progressWin.progress()                      
            #reset weighting
            
            for inc in range(influenceArray.length()):
                
                floatingJointPath = GenAPI.getDagPath(floatingJointList[inc])
                weightList = latticeSkinningTool.getWeightsFromLattice(floatingJointPath)
                
                allLatticeInfluences = latticeSkinningTool.getInfluencesFromSkincluster()
                
                #lock all inluences
                
                for influence in range(allLatticeInfluences.length()):
                    cmds.setAttr('%s.lockInfluenceWeights'%allLatticeInfluences[influence].fullPathName(),1)
                    
                    
                #unlock current influences
                cmds.setAttr('%s.lockInfluenceWeights'%floatingJointList[inc],0)
                cmds.setAttr('%s.lockInfluenceWeights'%influenceArray[inc].fullPathName(),0)
                
                
                latticeSkinningTool.setWeightsForLattice(influenceArray[inc],weightList)
                
            progressWin.inc = 7
            progressWin.progress() 
            #delete floating joints   
            for joint in floatingJointList: 
                cmds.delete(joint)
                
            progressWin.end()
        
        except:
            progressWin.end()
            om.MGlobal.displayError('There is no skincluster on %s'%latticeShape)
    
    else:
        om.MGlobal.displayError('%s is not a lattice'%latticeShape)    
        
def extrapFromWire(wire):
    
    curveShapeConnection = cmds.connectionInfo('%s.deformedWire[0]'%wire, sfd = True)
    curveShape = curveShapeConnection.split('.')[0]
    
    dagMembers = DeformerLib.WeightListTool.getDagMembers(wire)
    
    curvePath = GenAPI.getDagPath(curveShape)
    
    progressWin = UILib.ProgressWin()
    progressWin.setTitle('Extrap Skincluster from Wire')
    progressWin.itr = 5
    
    progressWin.inc = 1
    progressWin.progress()
    #creating clusters
    
    cvSelection = om.MSelectionList()
    
    cvItr = om.MItCurveCV(curvePath)
    
    clusters = []
    
    while not cvItr.isDone():
        
        cvSelection.clear()
        
        currentCV = cvItr.currentItem()
        
        cvSelection.add(curvePath,currentCV)
        om.MGlobal.setActiveSelectionList(cvSelection)
        
        cluster = cmds.cluster()
        clusters.append(cluster)
        
        cvItr.next()
    
    progressWin.inc = 2
    progressWin.message = 'extraping...'
    progressWin.progress()  
    #getting weights from clusters
    
    allWeightLists = []
    
    for mesh in dagMembers:
        
        influenceWeightLists = []
        
        for cluster in clusters:
            
            currentWeightList = MeasuringLib.MeasuringTool.createWeigthListFromTransform(mesh, cluster[1])
            influenceWeightLists.append(currentWeightList)
            
        allWeightLists.append(influenceWeightLists)
    
    #delete clusters
    for cluster in clusters:
        cmds.delete(cluster[0])
    
    progressWin.inc = 3
    progressWin.progress()
    #create joints    
    
    cmds.select(cl = True)
    
    joints = []
    
    cvItr.reset(curvePath)
    
    while not cvItr.isDone():
        
        cmds.select(cl = True)
        
        position = cvItr.position(om.MSpace.kWorld)
        
        currentJoint = cmds.joint()
        cmds.move(position.x,position.y,position.z,currentJoint)
        joints.append(currentJoint)
        
        cvItr.next()
    
    cmds.select(cl = True)
        
    baseJoint = cmds.joint()
    
    progressWin.inc = 4
    progressWin.progress()
    #create group for bind joints
    
    jointGroup = cmds.group(empty = True)
    cmds.parent(baseJoint,jointGroup)
    
    for joint in joints:
        
        cmds.parent(joint,jointGroup)
    
    progressWin.inc = 5
    progressWin.message = 'setting weights'
    progressWin.progress()   
    #smooth bind
    
    
    inc = 0
    for mesh in dagMembers:
        
        progressWin = UILib.ProgressWin()
        progressWin.setTitle('Setting Weights for %s'%mesh)
        progressWin.itr = len(joints)

    
        skincluster = cmds.skinCluster(mesh,baseJoint)[0]
        skinningTool = SkinningTool(skincluster,mesh)
        
        cmds.setAttr('%s.liw'%baseJoint, 0)
        
        for i in range(len(joints)):
            
            cmds.skinCluster(skincluster,e = True , weight = 0,addInfluence = joints[i])
            cmds.setAttr('%s.liw'%joints[i], 0)
            
            skinningTool.setWeights(GenAPI.getDagPath(joints[i]), allWeightLists[inc][i])
            
            cmds.setAttr('%s.liw'%joints[i], 1)
            
            progressWin.inc = i
            progressWin.progress()
            
        inc += 1
        progressWin.end()
        
def clusterWeightToJoints(geo,cluster,jointFrom,jointTo):
    
    weightTool = DeformerLib.WeightListTool(geo,cluster)
    weightList = weightTool.getWeightList()
    
    skincluster = SkinningTool.getSkinCluster(geo)[1]
    print skincluster
    
    skinningTool = SkinningTool(skincluster,geo)
    influences = skinningTool.getInfluencesFromSkincluster()

    
    for i in range(influences.length()):
        cmds.setAttr('%s.liw'%influences[i].fullPathName(), 1)
        
    cmds.setAttr('%s.liw'%jointFrom, 0)
    cmds.setAttr('%s.liw'%jointTo, 0)

    skinningTool.setWeights(GenAPI.getDagPath(jointTo), weightList)
    
def skinclusterFromMesh(meshFrom,meshTo,joints):
    
    floatingJointList = []
    constraintList = []
    weightLists = []
    
    progressWin = UILib.ProgressWin()
    progressWin.setTitle('Mesh To Skincluster')
    
    
    cmds.select(cl = True)
    for joint in joints:
        
        transformFn = om.MFnTransform(GenAPI.getDagPath(joint))
        position = transformFn.getTranslation(om.MSpace.kWorld)
        
        floatingJoint = cmds.joint()
        floatingJointPath = GenAPI.getDagPath(floatingJoint)
        transformFn.setObject(floatingJointPath)
        transformFn.setTranslation(position,om.MSpace.kWorld)
        floatingJointList.append(floatingJoint)
        
        parentConstraint = cmds.parentConstraint(floatingJoint,joint,mo = True)
        constraintList.append(parentConstraint)
        cmds.select(cl = True)
        
    baseJoint = cmds.joint() 
    skincluster = cmds.skinCluster(meshTo,baseJoint)[0]
    skinningTool = SkinningTool(skincluster,meshTo)
    
    cmds.setAttr('%s.liw'%baseJoint, 0)
    
    progressWin.itr = len(joints)
    
    inc = 0
    
    for i in range(len(floatingJointList)):
        
        weightList = MeasuringLib.MeasuringTool.createWeigthListFromInfluence2(meshFrom, floatingJointList[i])
        cmds.skinCluster(skincluster,e = True , weight = 0,addInfluence = joints[i])
        weightLists.append(weightList)
        
        cmds.setAttr('%s.liw'%joints[i], 0)   
        skinningTool.setWeights(GenAPI.getDagPath(joints[i]), weightList)
        cmds.setAttr('%s.liw'%joints[i], 1)
        
        inc += 1
        progressWin.inc = inc
        progressWin.progress()
        
    for i in range(len(floatingJointList)):  
        cmds.delete(constraintList[i])
        cmds.delete(floatingJointList[i])
        
    progressWin.end()
            
        
        
        
    
    