'''
Created on Aug 17, 2013

@author: Bill
'''

import sys
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
 
nodeName = 'kDecomposeMatrixNode'
nodeID = om.MTypeId(0x81666)
 
#node definition
class DecomposeMatrixNode(ompx.MPxNode):
    
    #attrs
    inMatrix = om.MObject()
    outTransformation = om.MObject()
    outTranslation = om.MObject()
    outRotation = om.MObject()
    outScale = om.MObject()

    def __init__(self):
         
        ompx.MPxNode.__init__(self)
        
    def compute(self,plug,data):
         
        if plug.isCompound():
            
            #output
            outTransformationData = data.outputValue(DecomposeMatrixNode.outTransformation)
            outTranslationData = outTransformationData.child(DecomposeMatrixNode.outTranslation)
            outRotationData = outTransformationData.child(DecomposeMatrixNode.outRotation)
            outScaleData = outTransformationData.child(DecomposeMatrixNode.outScale)
            
            #matrix A
            inMatrixData = data.inputValue(DecomposeMatrixNode.inMatrix)
            inMatrix = inMatrixData.asMatrix()
            
            #decompose
            transformMatrix = om.MTransformationMatrix(inMatrix)
            translationVector = transformMatrix.getTranslation(om.MSpace.kWorld)
            
            eulerRotation = transformMatrix.eulerRotation()
            
            scaleDouble3 = om.MScriptUtil()
            scaleDouble3.createFromList([0.0, 0.0, 0.0],3)
            scaleDouble3Ptr = scaleDouble3.asDoublePtr()
            
            transformMatrix.getScale(scaleDouble3Ptr,om.MSpace.kWorld)
            
            scaleX = om.MScriptUtil.getDoubleArrayItem(scaleDouble3Ptr,0)
            scaleY = om.MScriptUtil.getDoubleArrayItem(scaleDouble3Ptr,1)
            scaleZ = om.MScriptUtil.getDoubleArrayItem(scaleDouble3Ptr,2)
            
            '''
            print translationVector.x,translationVector.y,translationVector.z
            print eulerRotation.x,eulerRotation.y,eulerRotation.z
            print scaleX,scaleY,scaleZ
            '''

            #update outs
            outTranslationData.set3Double(translationVector.x,translationVector.y,translationVector.z)
            outRotationData.set3Double(eulerRotation.x,eulerRotation.y,eulerRotation.z)
            outScaleData.set3Double(scaleX,scaleY,scaleZ)
            
            #update data
            data.setClean(plug)
            
def nodeCreator():
 
    return ompx.asMPxPtr(DecomposeMatrixNode())
 
 
def nodeInitializer():
    
    mAttr = om.MFnMatrixAttribute()
    nAttr = om.MFnNumericAttribute()
    uAttr = om.MFnUnitAttribute()
    cAttr = om.MFnCompoundAttribute()
    
    #in matrix
    DecomposeMatrixNode.inMatrix = mAttr.create('inMatrix','inMatrix',
                                   om.MFnMatrixAttribute.kDouble)
    
    mAttr.setStorable(False)
    
    #translation
    DecomposeMatrixNode.outTranslationX = uAttr.create('outTranslateX', 'outTranslateX',
                                                om.MFnUnitAttribute.kDistance,0)
    DecomposeMatrixNode.outTranslationY = uAttr.create('outTranslateY', 'outTranslateY',
                                                om.MFnUnitAttribute.kDistance,0)
    DecomposeMatrixNode.outTranslationZ = uAttr.create('outTranslateZ', 'outTranslateZ',
                                                om.MFnUnitAttribute.kDistance,0)

    DecomposeMatrixNode.outTranslation = nAttr.create('outTranslation', 'outTranslation',
                                                DecomposeMatrixNode.outTranslationX,
                                                DecomposeMatrixNode.outTranslationY, 
                                                DecomposeMatrixNode.outTranslationZ)
    #rotation
    DecomposeMatrixNode.outRotationX = uAttr.create('outRotationX', 'outRotationX',
                                                om.MFnUnitAttribute.kAngle,0)
    DecomposeMatrixNode.outRotationY = uAttr.create('outRotationY', 'outRotationY',
                                                om.MFnUnitAttribute.kAngle,0)
    DecomposeMatrixNode.outRotationZ = uAttr.create('outRotationZ', 'outRotationZ',
                                                om.MFnUnitAttribute.kAngle,0)

    DecomposeMatrixNode.outRotation = nAttr.create('outRotation', 'outRotation',
                                                DecomposeMatrixNode.outRotationX,
                                                DecomposeMatrixNode.outRotationY, 
                                                DecomposeMatrixNode.outRotationZ)
    
    #scale
    DecomposeMatrixNode.outScaleX = uAttr.create('outScaleX', 'outScaleX',
                                                om.MFnUnitAttribute.kDistance,0)
    DecomposeMatrixNode.outScaleY = uAttr.create('outScaleY', 'outScaleY',
                                                om.MFnUnitAttribute.kDistance,0)
    DecomposeMatrixNode.outScaleZ = uAttr.create('outScaleZ', 'outScaleZ',
                                                om.MFnUnitAttribute.kDistance,0)

    DecomposeMatrixNode.outScale = nAttr.create('outScale', 'outScale',
                                                DecomposeMatrixNode.outScaleX,
                                                DecomposeMatrixNode.outScaleY, 
                                                DecomposeMatrixNode.outScaleZ)
    
    #transformation attr
    DecomposeMatrixNode.outTransformation = cAttr.create('outTransformation','outTransformation')
    cAttr.addChild(DecomposeMatrixNode.outTranslation)
    cAttr.addChild(DecomposeMatrixNode.outRotation)
    cAttr.addChild(DecomposeMatrixNode.outScale)


    #add attributes
    DecomposeMatrixNode.addAttribute(DecomposeMatrixNode.inMatrix)
    DecomposeMatrixNode.addAttribute(DecomposeMatrixNode.outTransformation)  
    
    #affects
    DecomposeMatrixNode.attributeAffects(DecomposeMatrixNode.inMatrix, DecomposeMatrixNode.outTransformation)

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
