'''
Created on May 22, 2012

@author: balloutb

Module for general api methods
'''

import maya.OpenMaya as om
import maya.OpenMayaAnim as oma


#create and return MObject datahandle
def getMObject(name):

    selectionList = om.MSelectionList()
    selectionList.add(name) 
    mobject = om.MObject()
    selectionList.getDependNode(0,mobject)
    return mobject


#create and return MObject datahandle
def getMObjectComponent(name):

    selectionList = om.MSelectionList()
    selectionList.add(name)
    mdagPath = om.MDagPath() 
    mobject = om.MObject()
    selectionList.getDagPath(0,mdagPath,mobject)
    return mobject
    

#return DagPath
def getDagPath(objectName):
        
    selectionList = om.MSelectionList()
    selectionList.add(objectName)
    dagPath = om.MDagPath()
    mobject = om.MObject()
    selectionList.getDagPath(0, dagPath, mobject )
    return dagPath

#get node name from mObject

def getStringFromMObject(mObject):
    
    depFn = om.MFnDependencyNode(mObject)
    nodeName = depFn.name()
    return nodeName



#method for returing the index values of an mObject
def getElementFromMObject(mObject):
    
    componentFn = om.MFnSingleIndexedComponent(mObject)
    elementArray = om.MIntArray()
    componentFn.getElements(elementArray)
    
    return elementArray



#creates a component list from active selection
#output componentList (MComponentListData)
def createComponentListFromSelection():
    
    selectionList = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(selectionList)
    selectionItr = om.MItSelectionList(selectionList)
    componentListData = om.MFnComponentListData()
    componentListData.create()
    
    while not selectionItr.isDone():
        
        dagPath = om.MDagPath()
        components = om.MObject()
        selectionItr.getDagPath(dagPath,components)
        componentListData.add(components)
        selectionItr.next()

    return componentListData


#get list from mobject
#input mObject (MObject)
#output intArray (MIntArray)
def getListFromMObject(mObject):

    singleComponentFn = om.MFnSingleIndexedComponent(mObject)
    intArray = om.MIntArray()
    singleComponentFn.getElements(intArray)
    return intArray


#getting components mobject from list,returns mobject holding verts
#input dagPath(MDagPath)
#input python int list (vertID list)
#output python list containing MObject.apiType.kComponent

def getComponentsFromList(dagPath,vertList):
    
    geoItr = om.MItGeometry(dagPath)
    selection = om.MSelectionList()
    components = om.MObject()
            
    while not geoItr.isDone():
        for i in vertList:
            if i == geoItr.index():
                selection.add(dagPath,geoItr.currentItem(),True)
        geoItr.next()
    
    selection.getDagPath(0,dagPath,components)
    return components  


#returns list of mobjects of components and dagPaths of geo from MSelectionList
#input selectionList (MSelectionList)
#output python list ([MDagPath],[MObject]])
def getComponentsFromMSelectionList(selectionList):
    
    selectionItr = om.MItSelectionList(selectionList)
    componentList = []
    
    while not selectionItr.isDone():
        
        dagPath = om.MDagPath()
        mObject = om.MObject()
        selectionItr.getDagPath(dagPath,mObject)
        componentList.append([dagPath,flattenMObject(mObject,dagPath)])
        selectionItr.next()
        
    return componentList 


#this method will convert mObject of vert components to individual mobject components
#input mObject vert components (MObject)
#input dagPath mesh path (MDagPath
def flattenMObject(mObject,dagPath):
    
    vertList = getListFromMObject(mObject)
    vertItr = om.MItMeshVertex(dagPath)
    util = om.MScriptUtil()
    ptr = util.asIntPtr()
    componentList = []
    for i in range(vertList.length()):
        
        vertItr.setIndex(vertList[i],ptr)
        vert = vertItr.currentItem()
        componentList.append(vert)
        
    return componentList
                                           
#return list of objectHandles for verts from selected geo
#input  mesh path(DagPath)
#output components (MObject)

def getMObjectAllVerts(mesh):
    
    meshPath = getDagPath(mesh)
    selectionList = om.MSelectionList()
    geoItr = om.MItGeometry(meshPath)
    
    while not geoItr.isDone():
        
        component = geoItr.currentItem()
        selectionList.add(meshPath,component,True)  
        geoItr.next()
        
    componentList = om.MObject()
    selectionList.getDagPath(0, meshPath, componentList)
    return componentList

        
#return verts from selected geo

def getVerts():

    selection = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(selection)

    vertices = []
    iterator = om.MItSelectionList(selection, om.MFn.kGeometric)

    while not iterator.isDone():

        polyList = []
        vertexList = []
        
        dagPath = om.MDagPath()
        mobject = om.MObject()

        iterator.getDagPath( dagPath )
        iterator.getDependNode(mobject)

        iteratePoly = om.MItMeshPolygon(mobject)

        while not iteratePoly.isDone():
            
            polyList.append(iteratePoly.index())

            verts = om.MIntArray()
            iteratePoly.getVertices(verts)
                
            for i in range(verts.length()):
                vertexList.append(verts[i])
                
            iteratePoly.next()
        
        for i in vertexList:

            vertices.append('%s.vtx[%i]'%(dagPath.fullPathName(),i))
            
        iterator.next()
            
    return vertices



#returns selectionList of object handles for lattice points
#input MDagPath (lattice shape)
#output MSelectionList (lattice components)
def getLatticePoints(latticePath):
    
    selectionList = om.MSelectionList()
    
    latticeFn = oma.MFnLattice(latticePath)
    
    utilS = om.MScriptUtil()
    SintPtr = utilS.asUintPtr()
    
    utilT = om.MScriptUtil()
    TintPtr = utilT.asUintPtr()
    
    utilU = om.MScriptUtil()
    UintPtr = utilU.asUintPtr()
    
    latticeFn.getDivisions(SintPtr,TintPtr,UintPtr)
    
    SVal = utilS.getUint(SintPtr)
    TVal = utilT.getUint(TintPtr)
    UVal = utilU.getUint(UintPtr)
    
    for s in range(SVal):
        
        for u in range(UVal):
            
            for t in range(TVal):
                
                latticeShapeString = latticePath.fullPathName()
                component = getMObjectComponent('%s.pt[%i][%i][%i]'%(latticeShapeString,s,t,u))
                selectionList.add(latticePath,component,False)
                
    return selectionList
    
##convert components grouping into long lists
##input python list
##output python list
def flattenList(selection):
    
    masterArray = []
    for item in selection:
        
        array = []
        
        if len(item.split(':')) > 1:
        
            objectName = (item.split('.'))[0]
            componentType = ((item.split('.'))[1].split('['))[0]
            
            startNum = int(((item.split('['))[1].split(':'))[0])
            endNum = int(((item.split(':'))[1].split(']'))[0])
            
            
            itr = startNum
            
            while not itr > endNum:
                itemStr = '%s.%s[%i]'%(objectName,componentType,itr)
                array.append(itemStr)
                itr += 1
                
        else:
            
            array.append(item)
             
        masterArray += array
    
    return masterArray

##returns root dagNode
##input MObject (node)
##output MDagPath (node)

def getRootDagNode(nodeObject):
    
    nodeFn = om.MFnDagNode(nodeObject)
    
    while not nodeFn.parent(0).apiType() == om.MFn.kWorld:
        nodeFn.setObject(nodeFn.parent(0))
        
    dagPath = om.MDagPath()
    nodeFn.getPath(dagPath)
    return dagPath

##return hierarchy of the node
##input MObject/MDagPath (node)
##output MSelectionList (hierarchy)   

def getHierarchy(nodeObject):

    nodeItr = om.MItDag()
    nodeItr.reset(nodeObject,om.MItDag.kDepthFirst)
    
    outputSelectionList = om.MSelectionList()
    
    while not nodeItr.isDone():
        
        item = nodeItr.currentItem()
        outputSelectionList.add(item)
        nodeItr.next()
        
    return outputSelectionList