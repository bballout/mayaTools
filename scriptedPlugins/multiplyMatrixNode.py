'''
Created on Aug 17, 2013

@author: Bill
'''

import sys
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
 
nodeName = 'kMultiplyMatrixNode'
nodeID = om.MTypeId(0x8112f)
 
#node definition
class MultiplyMatrixNode(ompx.MPxNode):
    
    #attrs
    matrixA = om.MObject()
    matrixB = om.MObject()
    outMatrix = om.MObject()
    operation = om.MObject()
    asInverse = om.MObject()
    
    def __init__(self):
         
        ompx.MPxNode.__init__(self)
        
    def compute(self,plug,data):
         
        if plug == MultiplyMatrixNode.outMatrix:
            
            #output
            outMatrixData = data.outputValue(MultiplyMatrixNode.outMatrix)
            
            #matrix A
            matrixAData = data.inputValue(MultiplyMatrixNode.matrixA)
            matrixA = matrixAData.asMatrix()
            
            #matrix B
            matrixBData = data.inputValue(MultiplyMatrixNode.matrixB)
            matrixB = matrixBData.asMatrix()
            
            #operation
            operationData = data.inputValue(MultiplyMatrixNode.operation)
            operation = operationData.asShort()
            
            asInverseData = data.inputValue(MultiplyMatrixNode.asInverse)
            asInverse = asInverseData.asBool()
            
            if operation == 0:
                outMatrix = matrixA * matrixB
            
            elif operation == 1:
                outMatrix = matrixA + matrixB
                
            elif operation == 2:
                outMatrix = matrixA - matrixB
                
            elif operation == 3:
                outMatrix = om.MMatrix()
                
            if asInverse:
                outMatrix = outMatrix.inverse()
            
            #set output
            outMatrixData.setMMatrix(outMatrix)   
            
            #update data
            data.setClean(plug)
            
def nodeCreator():
 
    return ompx.asMPxPtr(MultiplyMatrixNode())
 
 
def nodeInitializer():
    
    mAttr = om.MFnMatrixAttribute()
    eAttr = om.MFnEnumAttribute()
    nAttr = om.MFnNumericAttribute()
    
    #matrix A
    MultiplyMatrixNode.matrixA = mAttr.create('matrixA','matrixA',
                                   om.MFnMatrixAttribute.kDouble)
    
    mAttr.setStorable(True)
    
    #matrix B
    MultiplyMatrixNode.matrixB = mAttr.create('matrixB','matrixB',
                                   om.MFnMatrixAttribute.kDouble)
    
    mAttr.setStorable(True)
    
    #matrix B
    MultiplyMatrixNode.outMatrix = mAttr.create('outMatrix','outMatrix',
                                   om.MFnMatrixAttribute.kDouble)
    
    mAttr.setStorable(True)
    
    MultiplyMatrixNode.operation = eAttr.create('operation','operation')
    eAttr.addField('Mulitply',0)
    eAttr.addField('Add',1)
    eAttr.addField('Subtract',2)
    eAttr.addField('noOperation',3)
    eAttr.setStorable(True)
    eAttr.setChannelBox(True)
    
    MultiplyMatrixNode.asInverse = nAttr.create('asInverse','asInverse',om.MFnNumericData.kBoolean)
    nAttr.setStorable(True)
    nAttr.setChannelBox(True)
    
    #add attributes
    MultiplyMatrixNode.addAttribute(MultiplyMatrixNode.matrixA)
    MultiplyMatrixNode.addAttribute(MultiplyMatrixNode.matrixB)
    MultiplyMatrixNode.addAttribute(MultiplyMatrixNode.operation)
    MultiplyMatrixNode.addAttribute(MultiplyMatrixNode.asInverse)
    MultiplyMatrixNode.addAttribute(MultiplyMatrixNode.outMatrix)
    
    #affects
    MultiplyMatrixNode.attributeAffects(MultiplyMatrixNode.matrixA, MultiplyMatrixNode.outMatrix)
    MultiplyMatrixNode.attributeAffects(MultiplyMatrixNode.matrixB, MultiplyMatrixNode.outMatrix)
    MultiplyMatrixNode.attributeAffects(MultiplyMatrixNode.operation, MultiplyMatrixNode.outMatrix)
    MultiplyMatrixNode.attributeAffects(MultiplyMatrixNode.asInverse, MultiplyMatrixNode.outMatrix)

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
