'''
Created on Aug 12, 2014

@author: bballout
'''

import sys
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
 
nodeName = 'kPoseInverterNode'
nodeID = om.MTypeId(0x0008501f)


#node definition
class PoseInverterNode(ompx.MPxNode):
    
    #attrs
    origMesh = om.MObject()
    poseMesh = om.MObject()
    sculptMesh = om.MObject()
    outputMesh = om.MObject()
    
    deformerTransformRest = om.MObject()
    deformerTransformation = om.MObject()
    vertWeights = om.MObject()
    
    def __init__(self):
        ompx.MPxNode.__init__(self)
    
    def compute(self,plug,data):
        
        if plug == PoseInverterNode.outputMesh:
            
            origMeshData = data.inputValue(PoseInverterNode.origMesh)
            poseMeshData = data.inputValue(PoseInverterNode.poseMesh)
            sculptMeshData = data.inputValue(PoseInverterNode.sculptMesh)
            
            deformerTransformRestData = data.inputValue(PoseInverterNode.deformerTransformRest)
            deformerTransformationData = data.inputValue(PoseInverterNode.deformerTransformation)
            vertWeightsData = data.inputValue(PoseInverterNode.vertWeights)
            vertWeightsDataFn = om.MFnDoubleArrayData()
            vertWeightOutData = vertWeightsDataFn.create(vertWeightsData)
            vertWeights = vertWeightOutData.array()
            
            matrix = deformerTransformRestData.asMatrix() * deformerTransformationData.asMatrix()
            
            origMeshData = data.inputValue(PoseInverterNode.origMesh)
            poseMeshData = data.inputValue(PoseInverterNode.poseMesh)
            sculptMeshData = data.inputValue(PoseInverterNode.sculptMesh)
            outputMeshData = data.outputValue(PoseInverterNode.outputMesh)
            
            poseMeshFn = om.MFnMesh(poseMeshData.data())
            sculptMeshFn = om.MFnMesh(sculptMeshData.data())
            
            poseMeshPoints = om.MPointArray()
            poseMeshFn.getPoints(poseMeshPoints,om.MSpace.kWorld)
            
            sculptMeshPoints = om.MPointArray()
            sculptMeshFn.getPoints(sculptMeshPoints,om.MSpace.kWorld)
            
            pointArray = om.MPointArray()
            
            for i in range(poseMeshPoints.length()):
                
                startVector = om.MVector(poseMeshPoints[i].x,poseMeshPoints[i].y,poseMeshPoints[i].z)
                startTransformationMatrix = om.MTransformationMatrix()
                startTransformationMatrix.setTranslation(startVector,om.MSpace.kWorld)
                
                startMatrix = startTransformationMatrix.asMatrix()
                deformMatrix = matrix * vertWeights[i]
                finalMatrix = startMatrix * deformMatrix  
                
                transformationMatrix = om.MTransformationMatrix(finalMatrix)
                #transformationMatrix.addTranslation()
                

            origMeshFn = om.MFnMesh(origMeshData.data())
            
            #get mesh info
            numVerts = origMeshFn.numVertices()
            numPolys = origMeshFn.numPolygons()
            origMeshFn.getPoints(pointArray,om.MSpace.kWorld)
            polyVertCount = om.MIntArray()
            faceConnects = om.MIntArray()
            
            dataCreator = om.MFnMeshData()
            newOutputData = dataCreator.create()
            
            polyItr = om.MItMeshPolygon(origMeshData.data())
            
            while not polyItr.isDone():
                
                vertArray = om.MIntArray()
                polyItr.getVertices(vertArray)
                vertNum = vertArray.length()
                polyVertCount.append(vertNum)
                
                connectedVertArray = om.MIntArray()
                polyItr.getVertices(connectedVertArray)
                
                connectedVertArray.length()

                for i in range(connectedVertArray.length()):
                    faceConnects.append(connectedVertArray[i])
                    
                polyItr.next()
            
            outputMeshFn = om.MFnMesh()
            outputMeshFn.create(numVerts,numPolys,pointArray,polyVertCount,faceConnects,newOutputData)
            outputMeshFn.updateSurface()
            outputMeshData.setMObject(newOutputData)
            
            #update
            data.setClean(plug)

                       
def nodeCreator():
    return ompx.asMPxPtr(PoseInverterNode())
 
def nodeInitializer():
    
    mAttr = om.MFnMatrixAttribute()
    gAttr = om.MFnGenericAttribute()
    tAttr = om.MFnTypedAttribute()
    
    #orig mesh
    PoseInverterNode.origMesh = tAttr.create('origMesh','origMesh',om.MFnData.kMesh)
    
    #pose mesh
    PoseInverterNode.poseMesh = tAttr.create('poseMesh','poseMesh',om.MFnData.kMesh)

    #sculpt mesh
    PoseInverterNode.sculptMesh = tAttr.create('sculptMesh','sculptMesh',om.MFnData.kMesh)
    
    #out mesh
    PoseInverterNode.outputMesh = tAttr.create('outputMesh', 'outputMesh',om.MFnData.kMesh)
    
    
    PoseInverterNode.deformerTransformRest = mAttr.create('deformerTransformRest','deformerTransformRest',
                                                  om.MFnMatrixAttribute.kDouble)
    mAttr.setStorable(True)
    
    PoseInverterNode.deformerTransformation = mAttr.create('deformerTransformation','deformerTransformation',
                                                  om.MFnMatrixAttribute.kDouble)
    mAttr.setStorable(True)
    
    PoseInverterNode.vertWeights = gAttr.create('vertWeights','vertWeights')
    gAttr.addDataAccept(om.MFnData.kDoubleArray)
    gAttr.setStorable(True)
    gAttr.setWritable(True)
    
    PoseInverterNode.addAttribute(PoseInverterNode.origMesh)
    PoseInverterNode.addAttribute(PoseInverterNode.poseMesh)
    PoseInverterNode.addAttribute(PoseInverterNode.sculptMesh)
    PoseInverterNode.addAttribute(PoseInverterNode.outputMesh)
    PoseInverterNode.addAttribute(PoseInverterNode.deformerTransformRest)
    PoseInverterNode.addAttribute(PoseInverterNode.deformerTransformation)
    PoseInverterNode.addAttribute(PoseInverterNode.vertWeights)
 
    PoseInverterNode.attributeAffects(PoseInverterNode.origMesh, PoseInverterNode.outputMesh)
    PoseInverterNode.attributeAffects(PoseInverterNode.poseMesh, PoseInverterNode.outputMesh)
    PoseInverterNode.attributeAffects(PoseInverterNode.deformerTransformRest, PoseInverterNode.outputMesh)
    PoseInverterNode.attributeAffects(PoseInverterNode.deformerTransformation, PoseInverterNode.outputMesh)
    PoseInverterNode.attributeAffects(PoseInverterNode.vertWeights, PoseInverterNode.outputMesh)

    
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
    
