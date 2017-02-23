'''
Created on Feb 17, 2013

@author: Bill
'''
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
import sys


kAdjustablePivotTransformationMatrix = "kAdjustablePivotTranformation" 
kAdjustablePivotTransformNodeName = "kAdjustablePivotTransformNode"
kAdjustablePivotTranformationID = om.MTypeId(0x81333)
kAdjustablePivotTransformNodeID = om.MTypeId(0x81338)

kTrackingDictionary = {}

class AdjustablePivotTranformMatrix(ompx.MPxTransformationMatrix):
    
    def __init__(self):
        ompx.MPxTransformationMatrix.__init__(self)
        kTrackingDictionary[ompx.asHashable(self)] = self
        self.pivotX = 0.0
        self.pivotY = 0.0
        self.pivotZ = 0.0

    def __del__(self):
        del kTrackingDictionary[ompx.asHashable(self)]
        
    def getPivot(self):
        print 'returning %f %f %f'%(self.pivotX,self.pivotY,self.pivotZ)
        return om.MPoint(self.pivotX,self.pivotY,self.pivotZ)
        
    def setPivot(self,point):
        
        print 'setting %f %f %f'%(point.x,point.y,point.z) 
        
        self.pivotX = point.x
        self.pivotY = point.y
        self.pivotZ = point.z
        
    def asMatrix(self,percent = None):
        
        if percent == None:
            matrix = ompx.MPxTransformationMatrix.asMatrix(self)
            transformMatrix = om.MTransformationMatrix(matrix)
            
            translation = transformMatrix.getTranslation(om.MSpace.kWorld)
            pivotPoint = self.getPivot()
            
            transformMatrix.setRotatePivot(pivotPoint,om.MSpace.kTransform,True)
            transformMatrix.setScalePivot(pivotPoint,om.MSpace.kTransform,True)
            transformMatrix.addTranslation(om.MVector(pivotPoint),om.MSpace.kWorld)
            
            return transformMatrix.asMatrix()

        else:
            matrix = ompx.MPxTransformationMatrix.asMatrix(self)
            transformMatrix = om.MTransformationMatrix(matrix)
            
            translation = self.getTranslation(om.MSpace.kWorld)
            rotatePivotTranslate = self.rotatePivotTranslation(om.MSpace.kTransform)
            scalePivotTranslate = self.scalePivotTranslation(om.MSpace.kTransform)
            
            #scale transformation
            translation = translation * percent
            rotatePivotTranslate = rotatePivotTranslate * percent
            scalePivotTranslate = scalePivotTranslate * percent
            
            transformMatrix.setTranslation(translation,om.MSpace.kTransform)
            transformMatrix.setRotatePivotTranslation(rotatePivotTranslate,om.MSpace.kTransform,True)
            transformMatrix.setScalePivotTranslation(scalePivotTranslate,om.MSpace.kTransform,True)
            
            pivotPoint = self.getPivot()
            
            pivotPoint.x = pivotPoint.x * percent
            pivotPoint.y = pivotPoint.y * percent
            pivotPoint.z = pivotPoint.z * percent
            
            transformMatrix.setRotatePivot(pivotPoint)
            transformMatrix.setScalePivot(pivotPoint)
            transformMatrix.translateTo(translation)
            
            rotate = transformMatrix.eulerRotation()
            transformMatrix.rotateTo( rotate * percent, om.MSpace.kTransform)
            
            scale = transformMatrix.scale()
            scale.x = 1.0 + ( scale.x - 1.0 ) * percent
            scale.y = 1.0 + ( scale.y - 1.0 ) * percent
            scale.z = 1.0 + ( scale.z - 1.0 ) * percent
            transformMatrix.scaleTo(scale,om.MSpace.kTransform)
            return transformMatrix.asMatrix()

    
class AdjustablePivotTransformNode(ompx.MPxTransform):
    
        pivot = om.MObject()
   
        def __init__(self, transform=None):
            if transform is None:
                ompx.MPxTransform.__init__(self)
            else:
                ompx.MPxTransform.__init__(self, transform)
                    
        def className(self):
            return kAdjustablePivotTransformNodeName
        
        def createTransformationMatrix(self): 
            return ompx.asMPxPtr(AdjustablePivotTranformMatrix())
        
        def validateAndSetValue(self, plug, handle, context):
            
            if not plug.isNull():
                block = self._forceCache(context)
                dataHandle = block.outputValue(plug)
                
                if plug == self.pivot:
                    pivotVector = handle.asVector()
                    print pivotVector.x,pivotVector.y,pivotVector.z
                    dataHandle.setMVector(pivotVector)
                    
                    ltm = self.getPivotTransformationMatrix()
                    
                    ltm.setPivot(pivotVector)
    
                    dataHandle.setClean()
                    self._dirtyMatrix()
            
            ompx.MPxTransform.validateAndSetValue(self, plug, handle, context)
            
        def getPivotTransformationMatrix(self):
            baseXform = self.transformationMatrixPtr()
            return kTrackingDictionary[ompx.asHashable(baseXform)]
         
def nodeInitializer():

    uAttr = om.MFnUnitAttribute()
    nAttr = om.MFnNumericAttribute()
    
    AdjustablePivotTransformNode.pivotX = uAttr.create('pivotX', 'pivotX',
                                                om.MFnUnitAttribute.kDistance,0)
    AdjustablePivotTransformNode.pivotY = uAttr.create('pivotY', 'pivotY',
                                                om.MFnUnitAttribute.kDistance,0)
    AdjustablePivotTransformNode.pivotZ = uAttr.create('pivotZ', 'pivotZ',
                                                om.MFnUnitAttribute.kDistance,0)

    
    AdjustablePivotTransformNode.pivot = nAttr.create('pivot', 'pivot',
                                            AdjustablePivotTransformNode.pivotX,
                                            AdjustablePivotTransformNode.pivotY,
                                            AdjustablePivotTransformNode.pivotZ)
    nAttr.setKeyable(True)
    nAttr.setAffectsWorldSpace(True)
    
    AdjustablePivotTransformNode.addAttribute(AdjustablePivotTransformNode.pivot)
    AdjustablePivotTransformNode.mustCallValidateAndSet(AdjustablePivotTransformNode.pivot)

    
def matrixCreator():
    return ompx.asMPxPtr(AdjustablePivotTranformMatrix())

def nodeCreator():
    return ompx.asMPxPtr(AdjustablePivotTransformNode())

# initialize the script plug-in
def initializePlugin(mobject):
        mplugin = ompx.MFnPlugin(mobject)

        try:
                mplugin.registerTransform(kAdjustablePivotTransformNodeName, kAdjustablePivotTransformNodeID,
                                          nodeCreator, nodeInitializer, matrixCreator, kAdjustablePivotTranformationID)
        except:
                sys.stderr.write("Failed to register transform: %s\n" % kAdjustablePivotTransformNodeName)
                raise

# uninitialize the script plug-in
def uninitializePlugin(mobject):
        mplugin = ompx.MFnPlugin(mobject)

        try:
                mplugin.deregisterNode(kAdjustablePivotTransformNodeID)
        except:
                sys.stderr.write("Failed to unregister node: %s\n" % kAdjustablePivotTransformNodeName)
                raise   