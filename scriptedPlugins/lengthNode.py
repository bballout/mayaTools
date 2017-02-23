'''
Created on Aug 4, 2013

@author: Bill
'''

import sys
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
 
nodeName = 'kLengthNode'
nodeID = om.MTypeId(0x8101f)
 
#node definition
class LengthNode(ompx.MPxNode):
    
    #attrs
    startWorldMatrix = om.MObject()
    endWorldMatrix = om.MObject()
    startParentInverseMatrix = om.MObject()
    endParentInverseMatrix = om.MObject()
    outLength = om.MObject()
    
    def __init__(self):
         
        ompx.MPxNode.__init__(self)
        
    def compute(self,plug,data):
        
        if plug == LengthNode.outLength:
            
            #output
            outLengthData = data.outputValue(LengthNode.outLength)
            
            #start world matrix
            startWorldMatrixData = data.inputValue(LengthNode.startWorldMatrix)
            startWorldMatrix = startWorldMatrixData.asMatrix()
            
            #end world matrix
            endWorldMatrixData = data.inputValue(LengthNode.endWorldMatrix)
            endWorldMatrix = endWorldMatrixData.asMatrix()
            
            #start parent inverse matrix
            startParentInverseMatrixData = data.inputValue(LengthNode.startParentInverseMatrix)
            startParentInverseMatrix = startParentInverseMatrixData.asMatrix()
            
            #end parent inverse matrix
            endParentInverseMatrixData = data.inputValue(LengthNode.endParentInverseMatrix)
            endParentInverseMatrix = endParentInverseMatrixData.asMatrix()
            
            startLocalMatrix = startWorldMatrix * startParentInverseMatrix
            endLocalMatrix =  endWorldMatrix * endParentInverseMatrix
            
            startVector = getVector(startLocalMatrix)
            endVector = getVector(endLocalMatrix)
            
            vectorBetween = startVector - endVector    
            vectorBetweenLength = vectorBetween.length()
            
            #set output
            outLengthData.setDouble(vectorBetweenLength)   
            
            #update data
            data.setClean(plug)
            
#function returns ws vector         
def getVector(matrix):

    newTransformMatrix = om.MTransformationMatrix(matrix)
    outVector = newTransformMatrix.getTranslation(om.MSpace.kWorld)
    
    return outVector
def nodeCreator():
 
    return ompx.asMPxPtr(LengthNode())
 
 
def nodeInitializer():
     
    mAttr = om.MFnMatrixAttribute()
    nAttr = om.MFnNumericAttribute()
    
    #start matrix
    LengthNode.startWorldMatrix = mAttr.create('startWorldMatrix','startWorldMatrix',
                                   om.MFnMatrixAttribute.kDouble)
    
    mAttr.setStorable(False)
    
    #end matrix
    LengthNode.endWorldMatrix = mAttr.create('endWorldMatrix','endWorldMatrix',
                                   om.MFnMatrixAttribute.kDouble)
    
    mAttr.setStorable(False)
    
    #start parent inverse matrix
    LengthNode.startParentInverseMatrix = mAttr.create('startParentInverseMatrix','startParentInverseMatrix',
                                   om.MFnMatrixAttribute.kDouble)
    
    #end parent inverse matrix
    LengthNode.endParentInverseMatrix = mAttr.create('endParentInverseMatrix','endParentInverseMatrix',
                                   om.MFnMatrixAttribute.kDouble)
    
    #out length
    LengthNode.outLength = nAttr.create('outLength', 'outLength', om.MFnNumericData.kDouble,0.0)

    #add attributes
    LengthNode.addAttribute(LengthNode.startWorldMatrix)
    LengthNode.addAttribute(LengthNode.endWorldMatrix)
    LengthNode.addAttribute(LengthNode.startParentInverseMatrix)
    LengthNode.addAttribute(LengthNode.endParentInverseMatrix)
    LengthNode.addAttribute(LengthNode.outLength)
    
    #affects
    LengthNode.attributeAffects(LengthNode.startWorldMatrix, LengthNode.outLength)
    LengthNode.attributeAffects(LengthNode.endWorldMatrix, LengthNode.outLength)
    LengthNode.attributeAffects(LengthNode.startParentInverseMatrix, LengthNode.outLength)
    LengthNode.attributeAffects(LengthNode.endParentInverseMatrix, LengthNode.outLength)

    
def initializePlugin(mobject):
     
    mplugin = ompx.MFnPlugin(mobject)
     
    try:
        mplugin.registerNode(nodeName, nodeID,nodeCreator,nodeInitializer)
    except:
        sys.stderr.write( "Failed to load node: %s\n" %nodeName )
        raise
  
def uninitializePlugin(mobject):
     
    mplugin = ompx.MFnPlugin(mobject)
     
    try:
        mplugin.deregisterNode(nodeID)
    except:
        sys.stderr.write( "Failed to unload node: %s" % nodeName)
        raise
