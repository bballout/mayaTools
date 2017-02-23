'''
@author Belal Ballout
 
Description:
Dependency node for computing a transformation following poly surface.
Poly index attr refers to face id. Uv set attr refers to map to work with.
UV attrs find point on polygon. Aim and Up vector attrs are basis vectors for 
defining vector space.Offset rotation attr adds rotation to transformation.

Network:
PolyShape.outMesh----------->PolyRivet.inputMesh
PolyShape.worldMatrix[i]---->PolyRivet.worldMatrix
PolyRivet.outTranslation---->Transform.translate
PolyRivet.outRotation------->Transform.rotate
'''
import sys,math
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
 
nodeName = 'kPolyRivetNode'
nodeID = om.MTypeId(0x8133f)
 
#node definition
class PolyRivetNode(ompx.MPxNode):
     
    #attrs
    inputMesh = om.MObject()
    worldMatrix = om.MObject()
    uValue = om.MObject()
    vValue = om.MObject()
    faceIndex = om.MObject()
    uvSet = om.MObject()
    offsetRotation = om.MObject()
    normalVector = om.MObject()
    tangentVector = om.MObject()
    outTranslation = om.MObject()
    outRotation = om.MObject()
     
    def __init__(self):
         
        ompx.MPxNode.__init__(self)
        self.__point = om.MPoint()
         
    def compute(self,plug,data):
         
        if plug == PolyRivetNode.outTranslation or plug == PolyRivetNode.outRotation:
             
            #outputs
            outputTranslationData = data.outputValue(PolyRivetNode.outTranslation)
            outputRotationData = data.outputValue(PolyRivetNode.outRotation)
             
            #mesh data
            meshData = data.inputValue(PolyRivetNode.inputMesh)
            meshFn = om.MFnMesh(meshData.asMesh())
            polyItr = om.MItMeshPolygon(meshData.asMesh())
            
            #mesh world matrix
            inWorldMatrixData = data.inputValue(PolyRivetNode.worldMatrix)
            inWorldMatrix = inWorldMatrixData.asMatrix()
            
            #faceIndex data
            faceIndexData = data.inputValue(PolyRivetNode.faceIndex)
            
            #uvSet data
            uvSetData = data.inputValue(PolyRivetNode.uvSet)
             
            #uv data
            uValueData = data.inputValue(PolyRivetNode.uValue)
            vValueData = data.inputValue(PolyRivetNode.vValue)
             
            upVectorData = data.inputValue(PolyRivetNode.tangentVector)
            aimVectorData = data.inputValue(PolyRivetNode.normalVector)
            
            #offset rotation data
            offsetRotationData = data.inputValue(PolyRivetNode.offsetRotation)

            try:
                #basis vectors
                upVector = upVectorData.asVector()
                aimVector = aimVectorData.asVector()
                
                #poly info
                #get uvSet name
                uvSetValue = uvSetData.asInt()
                uvSetNameList = []
                meshFn.getUVSetNames(uvSetNameList)
                uvSetName = uvSetNameList[uvSetValue]
                
                #face index 
                faceIndexValue = faceIndexData.asInt()
                polyCount = polyItr.count()
                faceIndexValue = max(0, min(faceIndexValue, polyCount))
                
                #uv values
                uValue = uValueData.asFloat()
                vValue = vValueData.asFloat()
                
                #ooffset rotation vector
                offsetRotationVector = offsetRotationData.asVector()
                offsetRotationEuler = om.MEulerRotation(offsetRotationVector,om.MEulerRotation.kXYZ)
                 
                #position
                uvList = [uValue,vValue]
                util = om.MScriptUtil()
                util.createFromList(uvList,2)
                uvPtr = util.asFloat2Ptr()
                
                try:
                    point = om.MPoint()
                    meshFn.getPointAtUV(faceIndexValue,point,uvPtr,om.MSpace.kWorld,uvSetName,0.0)
                    self.__point = point
                except RuntimeError:
                    pass
                    
                #get derivatives
                #tangent vectors mean
                tangentVectorArray = om.MFloatVectorArray()
                meshFn.getFaceVertexTangents(faceIndexValue,tangentVectorArray,om.MSpace.kWorld,uvSetName)
                
                i = 0
                tangentVector = om.MVector()
                tangnetScalar = 1/tangentVectorArray.length()
                
                while i < tangentVectorArray.length():
                    addVector = om.MVector(tangentVectorArray[i].x,tangentVectorArray[i].y,tangentVectorArray[i].z)
                    tangentVector = addVector + tangentVector
                    i += 1
                    
                tangentVector * tangnetScalar
                tangentVector.normalize()
                
                #binormal vector mean
                binormalVectorArray = om.MFloatVectorArray()
                meshFn.getFaceVertexBinormals(faceIndexValue,binormalVectorArray,om.MSpace.kWorld,uvSetName)
                
                i = 0
                binormalVector = om.MVector()
                binormalScalar = 1/tangentVectorArray.length()
                
                while i < binormalVectorArray.length():
                    addVector = om.MVector(binormalVectorArray[i].x,binormalVectorArray[i].y,binormalVectorArray[i].z)
                    binormalVector = addVector + binormalVector
                    i += 1
                    
                binormalVector * binormalScalar
                binormalVector.normalize()
                
                normalVector = om.MVector()
                meshFn.getPolygonNormal(faceIndexValue,normalVector,om.MSpace.kWorld)
                
                #create quaternion rotation to normal vector
                aimQuaternion = om.MQuaternion(aimVector,normalVector)
                 
                #get angle for up quaternion
                toVector = upVector
                toVector = toVector.rotateBy(aimQuaternion)
                dot = toVector * tangentVector

                try:
                    theta = math.acos(dot / (toVector.length() * tangentVector.length()))
                     
                    if toVector * binormalVector < 0:
                        angle = theta
                         
                    else:
                        angle = ((2 * math.pi) - theta)
                         
                except ZeroDivisionError:  
                    angle = 0
                 
                #create quaternion for pole
                upQuaternion = om.MQuaternion(angle,aimVector)
                
                #create tranformation 
                #rotation transformation
                aimMatrix = aimQuaternion.asMatrix()
                upMatrix = upQuaternion.asMatrix()
                quatMatrix = upMatrix * aimMatrix
                
                #translation transformation
                translateVector = om.MVector(self.__point.x,self.__point.y,self.__point.z)
                translateTransformMatrix = om.MTransformationMatrix()
                translateTransformMatrix.setTranslation(translateVector,om.MSpace.kWorld)
                translateMatrix = translateTransformMatrix.asMatrix()
                
                #final matrix
                outMatrix = quatMatrix * (translateMatrix * inWorldMatrix)
                transformMatrix = om.MTransformationMatrix(outMatrix)
                transformMatrix.rotateBy(offsetRotationEuler, om.MSpace.kObject)
                
                #get translate and rotate from final matrix
                outTranslation = transformMatrix.getTranslation(om.MSpace.kWorld)
                outRotation = transformMatrix.eulerRotation()
                
                #set outputs
                outputTranslationData.set3Double(outTranslation.x,outTranslation.y,outTranslation.z)
                outputRotationData.set3Double(outRotation.x,outRotation.y,outRotation.z)
                
            except ValueError:
                 
                om.MGlobal.displayInfo('%s:Basis vectors are parallel.'%self.name())

            #update data
            data.setClean(plug)
             
def nodeCreator():
 
    return ompx.asMPxPtr(PolyRivetNode())
 
 
def nodeInitializer():
     
    gAttr = om.MFnGenericAttribute()
    mAttr = om.MFnMatrixAttribute()
    nAttr = om.MFnNumericAttribute()
    uAttr = om.MFnUnitAttribute()

    #input mesh
    PolyRivetNode.inputMesh = gAttr.create('input','input')
    gAttr.addDataAccept(om.MFnData.kMesh)

    gAttr.setHidden(False)
    gAttr.setStorable(True)
    gAttr.setWritable(True)
    
    #input matrix
    PolyRivetNode.worldMatrix = mAttr.create('worldMatrix','worldMatrix',
                                   om.MFnMatrixAttribute.kDouble)
    
    mAttr.setStorable(False)

    #face index
    PolyRivetNode.faceIndex = nAttr.create('faceIndex', 'faceIndex',om.MFnNumericData.kInt,0)
    nAttr.setStorable(True)
    nAttr.setWritable(True)
    nAttr.setChannelBox(True)
    nAttr.setMin(0)
    
    #uv set
    PolyRivetNode.uvSet = nAttr.create('uvSet', 'uvSet',om.MFnNumericData.kInt,0)
    nAttr.setStorable(True)
    nAttr.setWritable(True)
    nAttr.setChannelBox(True)
    nAttr.setMin(0)
 
    #uValue
    PolyRivetNode.uValue = nAttr.create('uValue', 'uValue', om.MFnNumericData.kFloat,0.0)
    nAttr.setStorable(True)
    nAttr.setWritable(True)
    nAttr.setChannelBox(True)
     
    #vValue
    PolyRivetNode.vValue = nAttr.create('vValue', 'vValue', om.MFnNumericData.kFloat,0.0)
    nAttr.setStorable(True)
    nAttr.setWritable(True)
    nAttr.setChannelBox(True)
    
    #normal vector
    PolyRivetNode.normalVector = nAttr.create('normalVector','normalVector',
                                              om.MFnNumericData.k3Double)

    
    #tangent vector
    PolyRivetNode.tangentVector = nAttr.create('tangentVector','tangentVector',
                                                  om.MFnNumericData.k3Double)
    
    #out translation
    PolyRivetNode.outTranslateX = uAttr.create('outTranslateX','outTranslateX',om.MFnUnitAttribute.kDistance,0)
    PolyRivetNode.outTranslateY = uAttr.create('outTranslateY','outTranslateY',om.MFnUnitAttribute.kDistance,0)
    PolyRivetNode.outTranslateZ = uAttr.create('outTranslateZ','outTranslateZ',om.MFnUnitAttribute.kDistance,0)
    PolyRivetNode.outTranslation = nAttr.create('outTranslation','outTranslation',PolyRivetNode.outTranslateX,
                                                PolyRivetNode.outTranslateY,PolyRivetNode.outTranslateZ)
    
    #out rotation
    PolyRivetNode.outRotationX = uAttr.create('outRotationX','outRotationX',om.MFnUnitAttribute.kAngle,0)
    PolyRivetNode.outRotationY = uAttr.create('outRotationY','outRotationY',om.MFnUnitAttribute.kAngle,0)
    PolyRivetNode.outRotationZ = uAttr.create('outRotationZ','outRotationZ',om.MFnUnitAttribute.kAngle,0) 
    PolyRivetNode.outRotation = nAttr.create('outRotation', 'outRotation',PolyRivetNode.outRotationX,
                                              PolyRivetNode.outRotationY,PolyRivetNode.outRotationZ)
    #offset rotation
    PolyRivetNode.offsetX = uAttr.create('offsetX', 'offsetX', om.MFnUnitAttribute.kAngle,0.0)
    PolyRivetNode.offsetY = uAttr.create('offsetY', 'offsetY', om.MFnUnitAttribute.kAngle,0.0)
    PolyRivetNode.offsetZ = uAttr.create('offsetZ', 'offsetZ', om.MFnUnitAttribute.kAngle,0.0)
    
    PolyRivetNode.offsetRotation = nAttr.create('offsetRotation', 'offsetRotation', PolyRivetNode.offsetX,
                                                PolyRivetNode.offsetY,PolyRivetNode.offsetZ)
    nAttr.setStorable(True)
    nAttr.setWritable(True)
    nAttr.setChannelBox(True)
                                              
    #add attributes
    PolyRivetNode.addAttribute(PolyRivetNode.inputMesh)
    PolyRivetNode.addAttribute(PolyRivetNode.worldMatrix)
    PolyRivetNode.addAttribute(PolyRivetNode.faceIndex)
    PolyRivetNode.addAttribute(PolyRivetNode.uvSet)
    PolyRivetNode.addAttribute(PolyRivetNode.uValue)
    PolyRivetNode.addAttribute(PolyRivetNode.vValue)
    PolyRivetNode.addAttribute(PolyRivetNode.offsetRotation)
    PolyRivetNode.addAttribute(PolyRivetNode.normalVector)
    PolyRivetNode.addAttribute(PolyRivetNode.tangentVector)
    PolyRivetNode.addAttribute(PolyRivetNode.outTranslation)
    PolyRivetNode.addAttribute(PolyRivetNode.outRotation)
 
    PolyRivetNode.attributeAffects(PolyRivetNode.inputMesh, PolyRivetNode.outTranslation)
    PolyRivetNode.attributeAffects(PolyRivetNode.inputMesh, PolyRivetNode.outRotation)
    PolyRivetNode.attributeAffects(PolyRivetNode.worldMatrix, PolyRivetNode.outTranslation)
    PolyRivetNode.attributeAffects(PolyRivetNode.worldMatrix, PolyRivetNode.outRotation)
    PolyRivetNode.attributeAffects(PolyRivetNode.faceIndex, PolyRivetNode.outTranslation)
    PolyRivetNode.attributeAffects(PolyRivetNode.faceIndex, PolyRivetNode.outRotation)
    PolyRivetNode.attributeAffects(PolyRivetNode.uvSet, PolyRivetNode.outTranslation)
    PolyRivetNode.attributeAffects(PolyRivetNode.uvSet, PolyRivetNode.outRotation)  
    PolyRivetNode.attributeAffects(PolyRivetNode.uValue, PolyRivetNode.outTranslation)
    PolyRivetNode.attributeAffects(PolyRivetNode.uValue, PolyRivetNode.outRotation)
    PolyRivetNode.attributeAffects(PolyRivetNode.vValue, PolyRivetNode.outTranslation)
    PolyRivetNode.attributeAffects(PolyRivetNode.vValue, PolyRivetNode.outRotation)
    PolyRivetNode.attributeAffects(PolyRivetNode.offsetRotation, PolyRivetNode.outTranslation)
    PolyRivetNode.attributeAffects(PolyRivetNode.offsetRotation, PolyRivetNode.outRotation)
    PolyRivetNode.attributeAffects(PolyRivetNode.normalVector, PolyRivetNode.outTranslation)
    PolyRivetNode.attributeAffects(PolyRivetNode.normalVector, PolyRivetNode.outRotation)
    PolyRivetNode.attributeAffects(PolyRivetNode.tangentVector, PolyRivetNode.outTranslation)
    PolyRivetNode.attributeAffects(PolyRivetNode.tangentVector, PolyRivetNode.outRotation)
             
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
##############################################################################################