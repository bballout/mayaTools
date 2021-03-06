'''
Created on Feb 23, 2015

@author: bballout
'''
import sys
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
import math

nodeName = 'kDeformerNode'
nodeID = om.MTypeId(0x810f0)
 
#node definition
class DeformerNode(ompx.MPxDeformerNode):

    deformSpace = om.MObject()
    amplitude = om.MObject()
    frequency = om.MObject()
    inMesh = om.MObject()
    
    def __init__(self):
        ompx.MPxDeformerNode.__init__(self)
    
    def deform(self, data, geoIter, matrix, multiIndex ):
      
        inMesh = data.inputValue(DeformerNode.inMesh).asMesh()
        meshFn = om.MFnMesh(inMesh)
        colors = om.MColorArray()
        colorSet = 'polyColorPerVertex1'
        meshFn.getColors(colors)
        
        envelope = ompx.cvar.MPxGeometryFilter_envelope
        envelopeHandle = data.inputValue( envelope )
        envelopeValue = envelopeHandle.asFloat()

        matrixData = data.inputValue(DeformerNode.deformSpace)
        matrixVal = matrixData.asMatrix()
        invMatrixVal = matrixVal.inverse()
        
        amplitudeData = data.inputValue(DeformerNode.amplitude)
        amplitudeValue = amplitudeData.asFloat()
        
        frequencyData = data.inputValue(DeformerNode.frequency)
        frequencyValue = frequencyData.asFloat()
        
        while not geoIter.isDone():
            
            if envelopeValue > 0:
                i = geoIter.index()
                color = colors[i]
                point = geoIter.position()
                point *= invMatrixVal
                
                length = math.sqrt((point.x * point.x) + (point.z * point.z))
                sinVal = math.sin(length)
                point.y = sinVal / length
                point.y *=  envelopeValue
                 
                point *= matrixVal
                   
                
                #===============================================================
                # point.x = color.r + pos.x
                # point.y = color.g + pos.y
                # point.z = color.b + pos.z
                #===============================================================

                geoIter.setPosition(point)
            
            geoIter.next()
            
    def accessoryNodeSetup(self, cmds):
        thisNode = self.thisMObject()
        objLoc = cmds.createNode('locator')
        fnLoc = om.MFnDependencyNode(objLoc)
        attrMat  = fnLoc.attribute('matrix')
        cmds.connect(objLoc,attrMat,thisNode,DeformerNode.deformSpace)
        
    def accessoryAttribute(self):
        return DeformerNode.deformSpace
        
def nodeCreator():
 
    return ompx.asMPxPtr(DeformerNode())
 
def nodeInitializer():
    
    mAttr = om.MFnMatrixAttribute()
    nAttr = om.MFnNumericAttribute()
    tAttr = om.MFnTypedAttribute()

    DeformerNode.deformSpace = mAttr.create('deformSpace','dm')
    mAttr.setStorable(False)
    mAttr.setConnectable(True)
    
    DeformerNode.amplitude = nAttr.create('amplitude','amp',om.MFnNumericData.kFloat,0)
    nAttr.setChannelBox(True)
    nAttr.setHidden(False);
    nAttr.setStorable(True); 
    nAttr.setKeyable(True)
    
    DeformerNode.frequency = nAttr.create('frequency','fqy',om.MFnNumericData.kFloat,0)
    nAttr.setChannelBox(True)
    nAttr.setHidden(False);
    nAttr.setStorable(True); 
    nAttr.setKeyable(True)

    outputGeom = ompx.cvar.MPxGeometryFilter_outputGeom
    
    DeformerNode.inMesh = tAttr.create('inMesh', 'im', om.MFnData.kMesh)
    
    DeformerNode.addAttribute(DeformerNode.inMesh)
    DeformerNode.addAttribute(DeformerNode.deformSpace)
    DeformerNode.addAttribute(DeformerNode.amplitude)
    DeformerNode.addAttribute(DeformerNode.frequency)
    
    DeformerNode.attributeAffects( DeformerNode.deformSpace, outputGeom)
    DeformerNode.attributeAffects( DeformerNode.amplitude, outputGeom)
    DeformerNode.attributeAffects( DeformerNode.frequency, outputGeom)
    DeformerNode.attributeAffects(DeformerNode.inMesh, outputGeom)
    
def initializePlugin(mobject):
     
    mplugin = ompx.MFnPlugin(mobject)
     
    try:
        mplugin.registerNode(nodeName, nodeID,nodeCreator,nodeInitializer,ompx.MPxNode.kDeformerNode)
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
