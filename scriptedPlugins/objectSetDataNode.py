'''
Created on Oct 4, 2013

@author: Belal Ballout

Scripted plugin creates a custom set. Also comes with 'data'
attr that stores python objects.

Command creates set and includes objects given in the
kwarg.

Store and get data through kObjectSetDataCmd args 'setData' and 'getData'

'''

import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
import sys

kNodeName = 'kObjectSetDataNode'
kCmdName = 'kObjectSetDataCmd'
kNodeId = om.MTypeId(0x8016F)

class ObjectSetDataNode(ompx.MPxObjectSet):
    
    data = om.MObject()
    
    def __init__(self):
        ompx.MPxObjectSet.__init__(self)

class ObjectSetDataCmd(ompx.MPxCommand):
    
    def __init__(self):
        ompx.MPxCommand.__init__(self)
        self.__fDGMod = om.MDGModifier()

    def doIt(self, args):

        setNode = self.__fDGMod.createNode(kNodeId)
        self.__fDGMod.doIt()
        
        
        # Populate the set with the selected items
        argData = om.MArgDatabase(self.syntax(), args)
        selectionList = om.MSelectionList()
        argData.getObjects(selectionList)
        
        
        if selectionList.length():
                setFn = om.MFnSet(setNode)
                setFn.addMembers(selectionList)
        
        depNodeFn = om.MFnDependencyNode(setNode)
        ompx.MPxCommand.setResult(depNodeFn.name())
            
    def undoIt(self):
        self.__fDGMod.undoIt()

                    
# initializer
def nodeInitializer():
    tAttr = om.MFnTypedAttribute()

    ObjectSetDataNode.data = tAttr.create('data','data',om.MFnData.kString)
    ObjectSetDataNode.addAttribute(ObjectSetDataNode.data)
    
    
# creator
def nodeCreator():
    return ompx.asMPxPtr(ObjectSetDataNode())


def cmdCreator():
    return ompx.asMPxPtr(ObjectSetDataCmd())


def sntaxCreator():
    
    syntax = om.MSyntax()
    syntax.setObjectType(syntax.kSelectionList)
    
    return syntax

# initialize the script plug-in
def initializePlugin(mobject):
    mplugin = ompx.MFnPlugin(mobject, "Autodesk", "1.0", "Any")
    
    try:
            mplugin.registerNode(kNodeName, kNodeId, nodeCreator, nodeInitializer, ompx.MPxNode.kObjectSet)
            mplugin.registerCommand(kCmdName, cmdCreator, sntaxCreator)
            
    except:
            sys.stderr.write("Failed to register node: %s" % kNodeName)
            raise


# uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = ompx.MFnPlugin(mobject)
    try:
            mplugin.deregisterCommand(kCmdName)
            mplugin.deregisterNode(kNodeId)
    except:
            sys.stderr.write("Failed to deregister node: %s" % kNodeName)
            raise