'''
@author Belal Ballout
 
Description:
Plug-in for creating surface rivets. A surface rivet follows a point 
on the surface. Command builds rivet and locator nodes with network connections.
Node has attributes for setting up and aim vectors, uv Value, and offset rotation.
 
MEL:
sphere;
kSurfaceRivetCmd -s nurbsSphereShape1 -u 2 -v 2.3 -nv 1 0 0 -tv 0 1 0;
 
 
Surface Rivet Node:
    kSurfaceRivetNode
     
Surface Rivet Command:
    kSurfaceRivetCmd -u float -v float -s string -nv int int int -tv int int int
 
'''
import sys,math
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
 
 
nodeName = 'kSurfaceRivetNode'
nodeID = om.MTypeId(0x8133f344)
 
cmdName = 'kSurfaceRivetCmd'
kSurfaceFlag = '-s'
kSurfaceFlagLong = '-surface'
kUValueFlag = '-u'
kUValueFlagLong = '-uValue'
kVValueFlag = '-v'
kVValueFlagLong = '-vValue'
kNormalVectorFlag = '-nv'
kNormalVectorFlagLong = '-normalVector'
kTangentVectorFlagLong = '-tangenVector'
kTangentVectorFlag = '-tv'
 
 
#node definition
class SurfaceRivetNode(ompx.MPxNode):
     
    #attrs
    inputSurface = om.MObject()
    uValue = om.MObject()
    vValue = om.MObject()
    offsetRotation = om.MObject()
    normalVector = om.MObject()
    tangentVector = om.MObject()
    outNormalVector = om.MObject()
    outTangentVector = om.MObject()
    outTranslation = om.MObject()
    outRotation = om.MObject()
    
    
     
    def __init__(self):
         
        ompx.MPxNode.__init__(self)
        self.__point = om.MPoint() 
        self.__outPlugs = [SurfaceRivetNode.outNormalVector,SurfaceRivetNode.outTangentVector,
                    SurfaceRivetNode.outTranslation,SurfaceRivetNode.outRotation]
 
         
    def compute(self,plug,data):
          
        if plug in self.__outPlugs:
             
            #outputs
            outputTranslationData = data.outputValue(SurfaceRivetNode.outTranslation)
            outputRotationData = data.outputValue(SurfaceRivetNode.outRotation)
            outputUVectorData = data.outputValue(SurfaceRivetNode.outNormalVector)
            outputVVectorData = data.outputValue(SurfaceRivetNode.outTangentVector)
              
            #surface data
            inputData = data.inputValue(SurfaceRivetNode.inputSurface) 
            inputFn = om.MFnNurbsSurface(inputData.data())
              
            #input data
            uValueData = data.inputValue(SurfaceRivetNode.uValue)
            vValueData = data.inputValue(SurfaceRivetNode.vValue)
              
            upVectorData = data.inputValue(SurfaceRivetNode.normalVector)
            aimVectorData = data.inputValue(SurfaceRivetNode.tangentVector)
              
            offsetRotationData = data.inputValue(SurfaceRivetNode.offsetRotation)
              
            try:
                #orient vectors
                upVector = upVectorData.asVector()
                aimVector = aimVectorData.asVector()
                                 
                uValue = uValueData.asFloat()
                vValue = vValueData.asFloat()
                  
                offsetRotationVector = offsetRotationData.asVector()
                offsetRotationEuler = offsetRotationEuler = om.MEulerRotation(offsetRotationVector,om.MEulerRotation.kXYZ)
                  
                #position
                point = om.MPoint()
                inputFn.getPointAtParam(uValue,vValue,point,om.MSpace.kWorld)
                self.__point = point
                  
                #normal
                #normalVector = inputFn.normal(uValue,vValue,om.MSpace.kWorld)
                  
                #uv tangents
                uVector = om.MVector()
                vVector = om.MVector()
                inputFn.getTangents(uValue,vValue,uVector,vVector,om.MSpace.kWorld)
  
                #quaternion
                aimQuaternion = om.MQuaternion(aimVector,vVector)
                  
                #angle
                toVector = upVector
                toVector = toVector.rotateBy(aimQuaternion)
                dot = toVector * uVector
                direction = uVector ^ vVector

                try:
                    theta = math.acos(dot / (toVector.length() * uVector.length()))
                      
                    if toVector * direction > 0:
                        angle = theta
                          
                    else:
                        angle = ((2 * math.pi) - theta)
                          
                except:
                    angle = 0
                  
                  
                upQuaternion = om.MQuaternion(angle,aimVector)
                  
                quatMatrix = upQuaternion.asMatrix() * aimQuaternion.asMatrix()
                #create tranformation data
                  
                #align to tangent
                transformMatrix = om.MTransformationMatrix(quatMatrix)
                  
                #add offset
                transformMatrix.rotateBy(offsetRotationEuler,om.MSpace.kObject)
                  
                #set translation
                transformMatrix.setTranslation(om.MVector(self.__point), om.MSpace.kWorld)
                  
                #outputs
                outTranslation = transformMatrix.getTranslation(om.MSpace.kWorld)
                outRotation = transformMatrix.eulerRotation()
                  
                outputTranslationData.set3Double(outTranslation.x,outTranslation.y,outTranslation.z)
                outputRotationData.set3Double(outRotation.x,outRotation.y,outRotation.z)
                
                outputUVectorData.set3Double(uVector.x,uVector.y,uVector.z)
                outputVVectorData.set3Double(vVector.x,vVector.y,vVector.z)
            except RuntimeError:
                  
                om.MGlobal.displayInfo('%s UV value out of range.'%self.name())
             
            #update data
            data.setClean(plug)
            
            pass
        
def nodeCreator():
 
    return ompx.asMPxPtr(SurfaceRivetNode())
 
 
def nodeInitializer():
 
     
    gAttr = om.MFnGenericAttribute()
    nAttr = om.MFnNumericAttribute()
    uAttr = om.MFnUnitAttribute()
     
    #input object
    SurfaceRivetNode.inputSurface = gAttr.create('input','input')
    gAttr.addDataAccept(om.MFnData.kNurbsSurface)
    gAttr.addDataAccept(om.MFnData.kNurbsCurve)
    gAttr.setHidden(False)
    gAttr.setStorable(True)
    gAttr.setWritable(True)

     
    #uValue
    SurfaceRivetNode.uValue = nAttr.create('uValue', 'uValue', om.MFnNumericData.kFloat,0.0)
    nAttr.setStorable(True)
    nAttr.setWritable(True)
    nAttr.setChannelBox(True)
    nAttr.setKeyable(True)     

    #vValue
    SurfaceRivetNode.vValue = nAttr.create('vValue', 'vValue', om.MFnNumericData.kFloat,0.0)
    nAttr.setStorable(True)
    nAttr.setWritable(True)
    nAttr.setChannelBox(True)
    nAttr.setKeyable(True)
    
    #normal vector
    SurfaceRivetNode.normalVector = nAttr.create('normalVector','normalVector',
                                                 om.MFnNumericData.k3Double)
     
    #tangent vector
    SurfaceRivetNode.tangentVector = nAttr.create('tangentVector','tangentVector',
                                                  om.MFnNumericData.k3Double)
     
    #out translation
    SurfaceRivetNode.outTranslateX = uAttr.create('outTranslateX','outTranslateX',om.MFnUnitAttribute.kDistance,0)
    SurfaceRivetNode.outTranslateY = uAttr.create('outTranslateY','outTranslateY',om.MFnUnitAttribute.kDistance,0)
    SurfaceRivetNode.outTranslateZ = uAttr.create('outTranslateZ','outTranslateZ',om.MFnUnitAttribute.kDistance,0)
    SurfaceRivetNode.outTranslation = nAttr.create('outTranslation','outTranslation',SurfaceRivetNode.outTranslateX,
                                                SurfaceRivetNode.outTranslateY,SurfaceRivetNode.outTranslateZ)
    
    #out rotation
    SurfaceRivetNode.outRotationX = uAttr.create('outRotationX','outRotationX',om.MFnUnitAttribute.kAngle,0)
    SurfaceRivetNode.outRotationY = uAttr.create('outRotationY','outRotationY',om.MFnUnitAttribute.kAngle,0)
    SurfaceRivetNode.outRotationZ = uAttr.create('outRotationZ','outRotationZ',om.MFnUnitAttribute.kAngle,0) 
    SurfaceRivetNode.outRotation = nAttr.create('outRotation', 'outRotation',SurfaceRivetNode.outRotationX,
                                              SurfaceRivetNode.outRotationY,SurfaceRivetNode.outRotationZ)
    
    SurfaceRivetNode.outNormalVectorX = uAttr.create('outNormalVectorX','outNormalVectorX',om.MFnUnitAttribute.kDistance,0)
    SurfaceRivetNode.outNormalVectorY = uAttr.create('outNormalVectorY','outNormalVectorY',om.MFnUnitAttribute.kDistance,0)
    SurfaceRivetNode.outNormalVectorZ = uAttr.create('outNormalVectorZ','outNormalVectorZ',om.MFnUnitAttribute.kDistance,0) 
    SurfaceRivetNode.outNormalVector = nAttr.create('outNormalVector', 'outNormalVector',SurfaceRivetNode.outNormalVectorX,
                                              SurfaceRivetNode.outNormalVectorY,SurfaceRivetNode.outNormalVectorZ)
    
    SurfaceRivetNode.outTangentVectorX = uAttr.create('outTangentVectorX','outTangentVectorX',om.MFnUnitAttribute.kDistance,0)
    SurfaceRivetNode.outTangentVectorY = uAttr.create('outTangentVectorY','outTangentVectorY',om.MFnUnitAttribute.kDistance,0)
    SurfaceRivetNode.outTangentVectorZ = uAttr.create('outTangentVectorZ','outTangentVectorZ',om.MFnUnitAttribute.kDistance,0) 
    SurfaceRivetNode.outTangentVector = nAttr.create('outTangentVector', 'outTangentVector',SurfaceRivetNode.outTangentVectorX,
                                              SurfaceRivetNode.outTangentVectorY,SurfaceRivetNode.outTangentVectorZ)
    
    #offset rotation
    SurfaceRivetNode.offsetX = uAttr.create('offsetX', 'offsetX', om.MFnUnitAttribute.kAngle,0.0)
    SurfaceRivetNode.offsetY = uAttr.create('offsetY', 'offsetY', om.MFnUnitAttribute.kAngle,0.0)
    SurfaceRivetNode.offsetZ = uAttr.create('offsetZ', 'offsetZ', om.MFnUnitAttribute.kAngle,0.0)
    
    SurfaceRivetNode.offsetRotation = nAttr.create('offsetRotation', 'offsetRotation', SurfaceRivetNode.offsetX,
                                                SurfaceRivetNode.offsetY,SurfaceRivetNode.offsetZ)
    nAttr.setStorable(True)
    nAttr.setWritable(True)
    nAttr.setChannelBox(True)
    nAttr.setKeyable(True)
    
    #add attributes
    SurfaceRivetNode.addAttribute(SurfaceRivetNode.inputSurface)
    SurfaceRivetNode.addAttribute(SurfaceRivetNode.uValue)
    SurfaceRivetNode.addAttribute(SurfaceRivetNode.vValue)
    SurfaceRivetNode.addAttribute(SurfaceRivetNode.offsetRotation)
    SurfaceRivetNode.addAttribute(SurfaceRivetNode.normalVector)
    SurfaceRivetNode.addAttribute(SurfaceRivetNode.tangentVector)
    SurfaceRivetNode.addAttribute(SurfaceRivetNode.outNormalVector)
    SurfaceRivetNode.addAttribute(SurfaceRivetNode.outTangentVector)
    SurfaceRivetNode.addAttribute(SurfaceRivetNode.outTranslation)
    SurfaceRivetNode.addAttribute(SurfaceRivetNode.outRotation)
 
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.inputSurface, SurfaceRivetNode.outTranslation)
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.inputSurface, SurfaceRivetNode.outRotation)
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.inputSurface, SurfaceRivetNode.outNormalVector)
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.inputSurface, SurfaceRivetNode.outTangentVector)
     
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.uValue, SurfaceRivetNode.outTranslation)
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.uValue, SurfaceRivetNode.outRotation)
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.uValue, SurfaceRivetNode.outNormalVector)
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.uValue, SurfaceRivetNode.outTangentVector)
    
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.vValue, SurfaceRivetNode.outTranslation)
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.vValue, SurfaceRivetNode.outRotation)
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.vValue, SurfaceRivetNode.outNormalVector)
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.vValue, SurfaceRivetNode.outTangentVector)
    
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.offsetRotation, SurfaceRivetNode.outTranslation)
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.offsetRotation, SurfaceRivetNode.outRotation)
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.offsetRotation, SurfaceRivetNode.outNormalVector)
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.offsetRotation, SurfaceRivetNode.outTangentVector)    
    
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.normalVector, SurfaceRivetNode.outTranslation)
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.normalVector, SurfaceRivetNode.outRotation)
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.normalVector, SurfaceRivetNode.outNormalVector)
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.normalVector, SurfaceRivetNode.outTangentVector)   
    
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.tangentVector, SurfaceRivetNode.outTranslation)
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.tangentVector, SurfaceRivetNode.outRotation)
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.tangentVector, SurfaceRivetNode.outNormalVector)
    SurfaceRivetNode.attributeAffects(SurfaceRivetNode.tangentVector, SurfaceRivetNode.outTangentVector)   
             
#command definition           
class SurfaceRivetCmd(ompx.MPxCommand):
     
    def __init__(self):
        ompx.MPxCommand.__init__(self)
        self.__fDGMod = om.MDGModifier()
        self.__dagMod = om.MDagModifier()
 
    def isUndoable(self):
         
        return True
         
    def doIt(self,args):
         
        dgFn = om.MFnDependencyNode()       
        selection = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(selection)
        argData = om.MArgDatabase(self.syntax(), args)
         
        if argData.isFlagSet(kSurfaceFlag):
            surfaceString = argData.flagArgumentString(kSurfaceFlag, 0)
             
        else:
            om.MGlobal.displayError('Please provide surface name.')
             
        selectionList = om.MSelectionList()
        selectionList.add(surfaceString)
        surfaceNode = om.MObject()
        selectionList.getDependNode(0,surfaceNode)
             
        if argData.isFlagSet(kUValueFlag):
            uValue = argData.flagArgumentDouble(kUValueFlag, 0)
             
        else:
            uValue = 0
             
        if argData.isFlagSet(kVValueFlag):
            vValue = argData.flagArgumentDouble(kVValueFlag, 0) 
             
        else:
            vValue = 0
            
        if argData.isFlagSet(kNormalVectorFlag):
            normalX = argData.flagArgumentDouble(kNormalVectorFlag, 0)
            normalY = argData.flagArgumentDouble(kNormalVectorFlag, 1)
            normalZ = argData.flagArgumentDouble(kNormalVectorFlag, 2)
 
             
        else:
            normalX = 1
            normalY = 0
            normalZ = 0
 
             
        if argData.isFlagSet(kTangentVectorFlag):
            tangentX = argData.flagArgumentDouble(kTangentVectorFlag, 0)
            tangentY = argData.flagArgumentDouble(kTangentVectorFlag, 1)
            tangentZ = argData.flagArgumentDouble(kTangentVectorFlag, 2)
 
             
        else:
            tangentX = 0
            tangentY = 1
            tangentZ = 0
             
         
        if surfaceNode.apiType() == om.MFn.kNurbsSurface:
             
            rivetNode = self.__fDGMod.createNode(nodeID)
            locatorNode = self.__dagMod.createNode('locator',om.MObject())
            self.__dagMod.doIt()
            self.__fDGMod.doIt()
             
            dgFn.setObject(rivetNode)
            rivetTranslatePlug = dgFn.findPlug('outTranslation')
            rivetRotatePlug = dgFn.findPlug('outRotation')
            rivetSurfacePlug = dgFn.findPlug('input')
            uPlug = dgFn.findPlug('uValue')
            vPlug = dgFn.findPlug('vValue')
            rivetNodeName = dgFn.name()
             
            normalPlugX = dgFn.findPlug('normalVector0')
            normalPlugY = dgFn.findPlug('normalVector1')
            normalPlugZ = dgFn.findPlug('normalVector2')
 
            tangentPlugX = dgFn.findPlug('tangentVector0')
            tangentPlugY = dgFn.findPlug('tangentVector1')
            tangentPlugZ = dgFn.findPlug('tangentVector2')
  
            dgFn.setObject(surfaceNode)
            worldSpacePlug = dgFn.findPlug('worldSpace')
            worldSpacePlug.setNumElements(1)
            worldSpacePlug.evaluateNumElements()
            worldSpaceIndexPlug = worldSpacePlug.elementByPhysicalIndex(0)
             
            dgFn.setObject(locatorNode)
            locatorTranslatePlug = dgFn.findPlug('translate')
            locatorRotatePlug = dgFn.findPlug('rotate')
            locatorName = dgFn.name()
 
            om.MGlobal.displayInfo(rivetTranslatePlug.info())
            om.MGlobal.displayInfo(locatorTranslatePlug.info())
             
            self.__fDGMod.connect(worldSpaceIndexPlug,rivetSurfacePlug)
            self.__fDGMod.connect(rivetTranslatePlug,locatorTranslatePlug)
            self.__fDGMod.connect(rivetRotatePlug,locatorRotatePlug)
             
            self.__fDGMod.newPlugValueFloat(uPlug, uValue)
            self.__fDGMod.newPlugValueFloat(vPlug, vValue)
 
            self.__fDGMod.newPlugValueDouble(normalPlugX, normalX)
            self.__fDGMod.newPlugValueDouble(normalPlugY, normalY)
            self.__fDGMod.newPlugValueDouble(normalPlugZ, normalZ)
            self.__fDGMod.newPlugValueDouble(tangentPlugX, tangentX)
            self.__fDGMod.newPlugValueDouble(tangentPlugY, tangentY)
            self.__fDGMod.newPlugValueDouble(tangentPlugZ, tangentZ)
 
            self.__fDGMod.doIt()
            self.setResult([rivetNodeName,locatorName])
   
        else:
            om.MGlobal.displayError('Object is not a surface.')
 
    def redoIt(self):
         
        self.__dagMod.doIt()
        self.__fDGMod.doIt()
 
    def undoIt(self):
         
        self.__fDGMod.undoIt()
        self.__dagMod.undoIt()
     
def cmdCreator():
     
    return ompx.asMPxPtr(SurfaceRivetCmd())
 
# Syntax creator
def syntaxCreator():
     
        syntax = om.MSyntax()
        syntax.addFlag(kSurfaceFlag, kSurfaceFlagLong, om.MSyntax.kString)
        syntax.addFlag(kUValueFlag, kUValueFlagLong, om.MSyntax.kDouble)
        syntax.addFlag(kVValueFlag, kVValueFlagLong, om.MSyntax.kDouble)
         
        syntax.addFlag(kNormalVectorFlag, kNormalVectorFlagLong, om.MSyntax.kDouble,
                       om.MSyntax.kDouble,om.MSyntax.kDouble)
         
        syntax.addFlag(kTangentVectorFlag, kTangentVectorFlagLong, om.MSyntax.kDouble,
                       om.MSyntax.kDouble,om.MSyntax.kDouble)
         
        return syntax
         
     
def initializePlugin(mobject):
     
    mplugin = ompx.MFnPlugin(mobject)
     
    try:
        mplugin.registerCommand(cmdName, cmdCreator, syntaxCreator)    
    except:
        sys.stderr.write("Failed to register command: %s" % cmdName)
        raise
     
    try:
        mplugin.registerNode(nodeName, nodeID,nodeCreator,nodeInitializer)
    except:
        sys.stderr.write( "Failed to load node: %s\n" %nodeName )
        raise
 
 
def uninitializePlugin(mobject):
     
    mplugin = ompx.MFnPlugin(mobject)
     
    try:
        mplugin.deregisterCommand(cmdName)
    except:
        sys.stderr.write("Failed to deregister command: %s" % cmdName)
        raise
     
    try:
        mplugin.deregisterNode(nodeID)
    except:
        sys.stderr.write( "Failed to unload node: %s" % nodeName)
        raise
##############################################################################################
