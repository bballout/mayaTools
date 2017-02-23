'''
Created on May 19, 2013

attrs that need to be added upon setup:
    targetTranslate = om.MObject()
    targetParentMatrix = om.MObject()
    targetScale = om.MObject()
    targetRotateOrder = om.MObject()
    targetRotate = om.MObject()
    targetRotatePivotTranslate = om.MObject()
    targetRotatePivot = om.MObject()

@author: Bill
'''

import sys
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx

#node
nodeName = 'kParentConstraintNode'
nodeID = om.MTypeId(0x8114A)

#cmd
cmdName = 'kParentConstraintCmd'
kConstraintName = '-n'
kConstraintNameLong = '-name'
kMaintainOffset = '-mo'
kMaintainOffsetLong = '-maintainOffset'
kAddTarget = '-at'
kAddTargetLong = '-addTarget'
kRemoveTarget = '-rt'
kRemoveTargetLong = '-removeTarget'

class ParentConstraint(ompx.MPxNode):
    
    #in attrs
    #targets
    parentCount = om.MObject()
    parent = om.MObject()
    targetList = om.MObject()
    
    #constrainedObject
    constraintParentInverseMatrix = om.MObject()
    constraintParentMatrix = om.MObject()
    constraintWorldMatrix = om.MObject()
    constraintRotateOrder = om.MObject()
    constraintRotatePivot = om.MObject()
    constraintRotatePivotTranslate = om.MObject()
    constraintJointOrient = om.MObject()
    
    #target
    targetTranslate = om.MObject()
    targetParentMatrix = om.MObject()
    targetScale = om.MObject()
    targetRotateOrder = om.MObject()
    targetRotate = om.MObject()
    targetRotatePivotTranslate = om.MObject()
    targetRotatePivot = om.MObject()
    targetJointOrient = om.MObject()
    targetWorldMatrix = om.MObject()
    targetOffsetTranslate = om.MObject()
    targetOffsetRotate = om.MObject()

    #offsetTransformation
    offsetTranslation = om.MObject()
    offsetRotate = om.MObject()
    
    #out attrs
    outTranslation = om.MObject()
    outRotation = om.MObject()
    
    def __init__(self):
        
        ompx.MPxNode.__init__(self)
        
    def compute(self,plug,data):
        
        #print plug.name()
                        
        #outputs
        outTranslationData = data.outputValue(ParentConstraint.outTranslation)
        outRotationData = data.outputValue(ParentConstraint.outRotation)
        
        #parent count
        parentCountData = data.inputValue(ParentConstraint.parentCount)
        parentCount = parentCountData.asInt()
        
        #target array builder
        targetListData = data.inputArrayValue(ParentConstraint.targetList)
        targetArrayBuilder = targetListData.builder()
        
        targetArrayBuilder.addElementArray(parentCount)
        targetListData.set(targetArrayBuilder)
        
        #get parent
        parentData = data.inputValue(ParentConstraint.parent)
        parent = parentData.asInt()
        
        #inputs from contrained object
        constraintParentInverseData = data.inputValue(ParentConstraint.constraintParentInverseMatrix)
        constraintRotateOrderData = data.inputValue(ParentConstraint.constraintRotateOrder)
        constraintRotatePivotData = data.inputValue(ParentConstraint.constraintRotatePivot)
        constraintRotatePivotTranslateData = data.inputValue(ParentConstraint.constraintRotatePivotTranslate)
        constraintJointOrientData = data.inputValue(ParentConstraint.constraintJointOrient)
        
        #extract value from constrained object data
        constraintParentInverse = constraintParentInverseData.asMatrix()
        rotationOrder = constraintRotateOrderData.asShort()
        constraintRotatePivot = constraintRotatePivotData.asVector()
        constraintRotatePivotTranslate = constraintRotatePivotTranslateData.asVector()
        
        
        constraintJointOrient = constraintJointOrientData.asVector()
        constraintJointOrientEuler = om.MEulerRotation(constraintJointOrient,rotationOrder)
        constraintJointOrientMatrix = constraintJointOrientEuler.asMatrix().inverse()
        
        
        #create inverse transformation for constrained object pivot
        inversePivotTransformation = om.MTransformationMatrix()
        inversePivotTransformation.addTranslation(constraintRotatePivot,om.MSpace.kWorld)
        inversePivotTransformation.setRotatePivotTranslation(constraintRotatePivotTranslate,om.MSpace.kWorld)
        inversePivotMatrix = inversePivotTransformation.asMatrixInverse()
        
        #inputs for transform offset
        offsetTranslationData = data.inputValue(ParentConstraint.offsetTranslation)
        offsetRotateData = data.inputValue(ParentConstraint.offsetRotate)
        
        #extract offset from data
        offsetTranslation = offsetTranslationData.asVector()
        offsetRotate = offsetRotateData.asVector()
        offsetEuler = om.MEulerRotation(offsetRotate,rotationOrder)
        
        #get data from targetList
        targetCompData = data.inputArrayValue(ParentConstraint.targetList)
        targetParentMatrix = om.MMatrix()
        targetTranslationMatrix = om.MMatrix()
        targetScaleMatrix = om.MMatrix()
        targetRotationMatrix = om.MMatrix()
        targetJointOrientMatrix = om.MMatrix()
        targetOffsetTranslationMatrix = om.MMatrix()
        targetOffsetRotationMatrix = om.MMatrix()
        
        try:
            
            #get targetList data
            targetCompData.jumpToElement(parent)
            targetData = targetCompData.inputValue()
            
            targetParentMatrixData = targetData.child(ParentConstraint.targetParentMatrix)
            targetTranslateData = targetData.child(ParentConstraint.targetTranslate)
            targetRotateData = targetData.child(ParentConstraint.targetRotate)
            targetJointOrientData = targetData.child(ParentConstraint.targetJointOrient)
            targetScaleData = targetData.child(ParentConstraint.targetScale)
            targetRotateOrderData = targetData.child(ParentConstraint.targetRotateOrder)
            targetRotatePivotTranslateData = targetData.child(ParentConstraint.targetRotatePivotTranslate)
            targetRotatePivotData = targetData.child(ParentConstraint.targetRotatePivot)
            targetOffsetTranslationData = targetData.child(ParentConstraint.targetOffsetTranslate)
            targetOffsetRotationData = targetData.child(ParentConstraint.targetOffsetRotate)
            
            #extract targetList values from data
            targetParentMatrix = targetParentMatrixData.asMatrix()
            targetTranslate = targetTranslateData.asVector()
            targetRotate = targetRotateData.asVector()
            
            targetScaleTransformation = om.MTransformationMatrix()
            targetScale = targetScaleData.asDouble3()
            util = om.MScriptUtil()
            util.createFromList(targetScale,3)
            targetScaleDouble3 = util.asDoublePtr()
            targetScaleTransformation.setScale(targetScaleDouble3,om.MSpace.kWorld)
            
            targetRotateOrder = targetRotateOrderData.asShort()
            targetRotatePivotTranslate = targetRotatePivotTranslateData.asVector()
            targetRotatePivot = targetRotatePivotData.asVector()
            targetOffsetTranslate = targetOffsetTranslationData.asVector()
            targetJointOrient = targetJointOrientData.asVector()
            targetOffsetRotate = targetOffsetRotationData.asVector()
            
            targetRotateEuler = om.MEulerRotation(targetRotate,targetRotateOrder)
            targetJointOrientEuler = om.MEulerRotation(targetJointOrient,targetRotateOrder)
            targetJointOrientMatrix = targetJointOrientEuler.asMatrix()
            
            targetOffsetRotateEuler = om.MEulerRotation(targetOffsetRotate,targetRotateOrder)
            targetOffsetRotationMatrix = targetOffsetRotateEuler.asMatrix()
            
            targetTranslationTransformation = om.MTransformationMatrix()
            targetTranslationTransformation.addTranslation(targetTranslate,om.MSpace.kWorld)
            targetTranslationTransformation.addTranslation(targetRotatePivotTranslate,om.MSpace.kWorld)
            targetTranslationTransformation.addTranslation(targetRotatePivot,om.MSpace.kWorld)
            
            targetOffsetTranslationTransformation = om.MTransformationMatrix()
            targetOffsetTranslationTransformation.addTranslation(targetOffsetTranslate,om.MSpace.kWorld)
            targetOffsetTranslationMatrix = targetOffsetTranslationTransformation.asMatrix()
            
            targetRotationMatrix = targetRotateEuler.asMatrix()
            targetTranslationMatrix = targetTranslationTransformation.asMatrix()
            targetScaleMatrix = targetScaleTransformation.asMatrix()
            
        except RuntimeError:
            pass
        
        offsetTransformation = om.MTransformationMatrix()
        offsetTransformation.addTranslation(offsetTranslation,om.MSpace.kWorld)
        offsetTransformation.rotateBy(offsetEuler,om.MSpace.kWorld)
        offsetMatrix = offsetTransformation.asMatrix()
        
        finalMatrix =  offsetMatrix * targetOffsetRotationMatrix * targetOffsetTranslationMatrix * targetRotationMatrix * targetJointOrientMatrix * constraintJointOrientMatrix * targetScaleMatrix * targetTranslationMatrix * targetParentMatrix * constraintParentInverse * inversePivotMatrix
        finalTransformMatrix = om.MTransformationMatrix(finalMatrix)
        
        finalTranslation = finalTransformMatrix.getTranslation(om.MSpace.kWorld)
        finalRotation = finalTransformMatrix.eulerRotation()
        
        outTranslationData.setMVector(om.MVector(finalTranslation.x,finalTranslation.y,finalTranslation.z))
        outRotationData.setMVector(om.MVector(finalRotation.x,finalRotation.y,finalRotation.z))
        
        data.setClean(plug)
            

def nodeCreator():
    return ompx.asMPxPtr(ParentConstraint())

def nodeInitializer():
    
    mAttr = om.MFnMatrixAttribute()
    nAttr = om.MFnNumericAttribute()
    uAttr = om.MFnUnitAttribute()
    eAttr = om.MFnEnumAttribute()
    cAttr = om.MFnCompoundAttribute()

    #parentCount attr
    ParentConstraint.parentCount = nAttr.create('parentCount','parentCount',om.MFnNumericData.kInt,0)
    
    #parent attr
    ParentConstraint.parent = nAttr.create('parent','parent',om.MFnNumericData.kInt,0)
    nAttr.setStorable(True)
    nAttr.setChannelBox(True)
    nAttr.setKeyable(True)
    nAttr.setReadable(True)
    nAttr.setMin(0)

    #target translate
    ParentConstraint.targetTranslateX = uAttr.create('targetTranslateX','targetTranslateX',om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.targetTranslateY = uAttr.create('targetTranslateY','targetTranslateY',om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.targetTranslateZ = uAttr.create('targetTranslateZ','targetTranslateZ',om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.targetTranslate = nAttr.create('targetTranslate','targetTranslate',ParentConstraint.targetTranslateX,
                                        ParentConstraint.targetTranslateY,ParentConstraint.targetTranslateZ)
    
    #target parent matrix
    ParentConstraint.targetParentMatrix = mAttr.create('targetParentMatrix','targetParentMatrix',om.MFnMatrixAttribute.kDouble)
    mAttr.setInternal(True)
    
    #target scale
    ParentConstraint.targetScaleX = uAttr.create('targetScaleX','targetScaleX',om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.targetScaleY = uAttr.create('targetScaleY','targetScaleY',om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.targetScaleZ = uAttr.create('targetScaleZ','targetScaleZ',om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.targetScale = nAttr.create('targetScale','targetScale',ParentConstraint.targetScaleX,
                                            ParentConstraint.targetScaleY,ParentConstraint.targetScaleZ)
    
    #target rotation order
    ParentConstraint.targetRotateOrder = eAttr.create('targetRotateOrder','targetRotateOrder') 
    eAttr.addField('xyz',0)
    eAttr.addField('yzx',1)
    eAttr.addField('zxy',2)
    eAttr.addField('xzy',3)
    eAttr.addField('yxz',4)
    eAttr.addField('zyx',5)
    eAttr.setStorable(False)
    
    #target rotate
    ParentConstraint.targetRotateX = uAttr.create('targetRotateX','targetRotateX',om.MFnUnitAttribute.kAngle,0)
    ParentConstraint.targetRotateY = uAttr.create('targetRotateY','targetRotateY',om.MFnUnitAttribute.kAngle,0)
    ParentConstraint.targetRotateZ = uAttr.create('targetRotateZ','targetRotateZ',om.MFnUnitAttribute.kAngle,0)
    ParentConstraint.targetRotate = nAttr.create('targetRotate','targetRotate',ParentConstraint.targetRotateX,
                                                                                    ParentConstraint.targetRotateY,
                                                                                    ParentConstraint.targetRotateZ)
    
    
    #target rotate translate
    ParentConstraint.targetRotatePivotTranslateX = uAttr.create('targetRotatePivotTranslateX','targetRotatePivotTranslateX',
                                                                                            om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.targetRotatePivotTranslateY = uAttr.create('targetRotatePivotTranslateY','targetRotatePivotTranslateY',
                                                                                            om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.targetRotatePivotTranslateZ = uAttr.create('targetRotatePivotTranslateZ','targetRotatePivotTranslateZ',
                                                                                            om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.targetRotatePivotTranslate = nAttr.create('targetRotatePivotTranslate','targetRotatePivotTranslate',
                                                                   ParentConstraint.targetRotatePivotTranslateX,
                                                                   ParentConstraint.targetRotatePivotTranslateY,
                                                                   ParentConstraint.targetRotatePivotTranslateZ)
    
    #target rotate pivot
    ParentConstraint.targetRotatePivotX = uAttr.create('targetRotatePivotX','targetRotatePivotX',
                                                                                        om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.targetRotatePivotY = uAttr.create('targetRotatePivotY','targetRotatePivotY',
                                                                                        om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.targetRotatePivotZ = uAttr.create('targetRotatePivotZ','targetRotatePivotZ',
                                                                                        om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.targetRotatePivot = nAttr.create('targetRotatePivot','targetRotatePivot',
                                                                   ParentConstraint.targetRotatePivotX,
                                                                   ParentConstraint.targetRotatePivotY,
                                                                   ParentConstraint.targetRotatePivotZ)
    
    #target joint orient
    ParentConstraint.targetJointOrientX = uAttr.create('targetJointOrientX','targetJointOrientX',
                                                                                        om.MFnUnitAttribute.kAngle,0)
    ParentConstraint.targetJointOrientY = uAttr.create('targetJointOrientY','targetJointOrientY',
                                                                                        om.MFnUnitAttribute.kAngle,0)
    ParentConstraint.targetJointOrientZ = uAttr.create('targetJointOrientZ','targetJointOrientZ',
                                                                                        om.MFnUnitAttribute.kAngle,0)
    ParentConstraint.targetJointOrient = nAttr.create('targetJointOrient','targetJointOrient',
                                                                   ParentConstraint.targetJointOrientX,
                                                                   ParentConstraint.targetJointOrientY,
                                                                   ParentConstraint.targetJointOrientZ)
    
    #target parent matrix
    ParentConstraint.targetWorldMatrix = mAttr.create('targetWorldMatrix','targetWorldMatrix',om.MFnMatrixAttribute.kDouble)
    
    #target offset translation
    ParentConstraint.targetOffsetTranslateX = uAttr.create('targetOffsetTranslateX','targetOffsetTranslateX',om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.targetOffsetTranslateY = uAttr.create('targetOffsetTranslateY','targetOffsetTranslateY',om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.targetOffsetTranslateZ = uAttr.create('targetOffsetTranslateZ','targetOffsetTranslateZ',om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.targetOffsetTranslate = nAttr.create('targetOffsetTranslate','targetOffsetTranslate',ParentConstraint.targetOffsetTranslateX,
                                        ParentConstraint.targetOffsetTranslateY,ParentConstraint.targetOffsetTranslateZ)
    
    nAttr.setChannelBox(True)
    
    #target offset rotation
    ParentConstraint.targetOffsetRotateX = uAttr.create('targetOffsetRotateX','targetOffsetRotateX',om.MFnUnitAttribute.kAngle,0)
    ParentConstraint.targetOffsetRotateY = uAttr.create('targetOffsetRotateY','targetOffsetRotateY',om.MFnUnitAttribute.kAngle,0)
    ParentConstraint.targetOffsetRotateZ = uAttr.create('targetOffsetRotateZ','targetOffsetRotateZ',om.MFnUnitAttribute.kAngle,0)
    ParentConstraint.targetOffsetRotate = nAttr.create('targeOffsetRotate','targeOffsetRotate',ParentConstraint.targetOffsetRotateX,
                                        ParentConstraint.targetOffsetRotateY,ParentConstraint.targetOffsetRotateZ)
    nAttr.setChannelBox(True)
    
    #targetList compound attribute
    ParentConstraint.targetList = cAttr.create('targetList','targetList')
    cAttr.addChild(ParentConstraint.targetTranslate)
    cAttr.addChild(ParentConstraint.targetParentMatrix)
    cAttr.addChild(ParentConstraint.targetScale)
    cAttr.addChild(ParentConstraint.targetRotateOrder)
    cAttr.addChild(ParentConstraint.targetRotate)
    cAttr.addChild(ParentConstraint.targetRotatePivotTranslate)
    cAttr.addChild(ParentConstraint.targetRotatePivot)
    cAttr.addChild(ParentConstraint.targetJointOrient)
    cAttr.addChild(ParentConstraint.targetWorldMatrix)
    cAttr.addChild(ParentConstraint.targetOffsetTranslate)
    cAttr.addChild(ParentConstraint.targetOffsetRotate)
    cAttr.setArray(True)
    cAttr.setUsesArrayDataBuilder(True)

    #constrained object inverse parent matrix
    ParentConstraint.constraintParentInverseMatrix = mAttr.create('constraintInverseParentMatrix','constraintInverseParentMatrix',
                                                                       om.MFnMatrixAttribute.kDouble)
    
    #constrained object world matrix
    ParentConstraint.constraintWorldMatrix = mAttr.create('constraintWorldMatrix','constraintWorldMatrix',
                                                                       om.MFnMatrixAttribute.kDouble)
    mAttr.setInternal(True)
    
    ParentConstraint.constraintParentMatrix = mAttr.create('constraintParentMatrix','constraintParentMatrix',
                                                                       om.MFnMatrixAttribute.kDouble)
    mAttr.setInternal(True)
    

    #rotate Order
    ParentConstraint.constraintRotateOrder = eAttr.create('constraintRotateOrder','constraintRotateOrder') 
    eAttr.addField('xyz',0)
    eAttr.addField('yzx',1)
    eAttr.addField('zxy',2)
    eAttr.addField('xzy',3)
    eAttr.addField('yxz',4)
    eAttr.addField('zyx',5)
    eAttr.setStorable(False)
    
    #constraint rotate translate
    ParentConstraint.constraintRotatePivotTranslateX = uAttr.create('constraintRotatePivotTranslateX','constraintRotatePivotTranslateX',
                                                                                            om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.constraintRotatePivotTranslateY = uAttr.create('constraintRotatePivotTranslateY','constraintRotatePivotTranslateY',
                                                                                            om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.constraintRotatePivotTranslateZ = uAttr.create('constraintRotatePivotTranslateZ','constraintRotatePivotTranslateZ',
                                                                                            om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.constraintRotatePivotTranslate = nAttr.create('constraintRotatePivotTranslate','constraintRotatePivotTranslate',
                                                                   ParentConstraint.constraintRotatePivotTranslateX,
                                                                   ParentConstraint.constraintRotatePivotTranslateY,
                                                                   ParentConstraint.constraintRotatePivotTranslateZ)
    
    #constraint rotate pivot
    ParentConstraint.constraintRotatePivotX = uAttr.create('constraintRotatePivotX','constraintRotatePivotX',
                                                                                        om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.constraintRotatePivotY = uAttr.create('constraintRotatePivotY','constraintRotatePivotY',
                                                                                        om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.constraintRotatePivotZ = uAttr.create('constraintRotatePivotZ','constraintRotatePivotZ',
                                                                                        om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.constraintRotatePivot = nAttr.create('constraintRotatePivot','constraintRotatePivot',
                                                                   ParentConstraint.constraintRotatePivotX,
                                                                   ParentConstraint.constraintRotatePivotY,
                                                                   ParentConstraint.constraintRotatePivotZ)
    
    #constraint joint orient
    ParentConstraint.constraintJointOrientX = uAttr.create('constraintJointOrientX','constraintJointOrientX',
                                                                                    om.MFnUnitAttribute.kAngle,0)
    ParentConstraint.constraintJointOrientY = uAttr.create('constraintJointOrientY','constraintJointOrientY',
                                                                                    om.MFnUnitAttribute.kAngle,0)
    ParentConstraint.constraintJointOrientZ = uAttr.create('constraintJointOrientZ','constraintJointOrientZ',
                                                                                    om.MFnUnitAttribute.kAngle,0)
    ParentConstraint.constraintJointOrient = nAttr.create('constraintJointOrient','constraintJointOrient',
                                                               ParentConstraint.constraintJointOrientX,
                                                               ParentConstraint.constraintJointOrientY,
                                                               ParentConstraint.constraintJointOrientZ)

    #offset translation
    ParentConstraint.offsetTranslateX = uAttr.create('offsetTranslateX','offsetTranslateX',om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.offsetTranslateY = uAttr.create('offsetTranslateY','offsetTranslateY',om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.offsetTranslateZ = uAttr.create('offsetTranslateZ','offsetTranslateZ',om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.offsetTranslation = nAttr.create('offsetTranslate','offsetTranslate',ParentConstraint.offsetTranslateX,
                                        ParentConstraint.offsetTranslateY,ParentConstraint.offsetTranslateZ)
    nAttr.setChannelBox(True)
    nAttr.setKeyable(True)
    nAttr.setReadable(True)
    
    #offset rotation
    ParentConstraint.offsetRotateX = uAttr.create('offsetRotateX','offsetRotateX',om.MFnUnitAttribute.kAngle,0)
    ParentConstraint.offsetRotateY = uAttr.create('offsetRotateY','offsetRotateY',om.MFnUnitAttribute.kAngle,0)
    ParentConstraint.offsetRotateZ = uAttr.create('offsetRotateZ','offsetRotateZ',om.MFnUnitAttribute.kAngle,0)
    ParentConstraint.offsetRotate = nAttr.create('offsetRotate','offsetRotate',ParentConstraint.offsetRotateX,
                                        ParentConstraint.offsetRotateY,ParentConstraint.offsetRotateZ)
    nAttr.setChannelBox(True)
    nAttr.setKeyable(True)
    nAttr.setReadable(True)
    
    #out translation 
    ParentConstraint.outTranslateX = uAttr.create('outTranslateX','outTranslateX',om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.outTranslateY = uAttr.create('outTranslateY','outTranslateY',om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.outTranslateZ = uAttr.create('outTranslateZ','outTranslateZ',om.MFnUnitAttribute.kDistance,0)
    ParentConstraint.outTranslation = nAttr.create('outTranslation','outTranslation',ParentConstraint.outTranslateX,
                                        ParentConstraint.outTranslateY,ParentConstraint.outTranslateZ)
    #out rotation
    ParentConstraint.outRotationX = uAttr.create('outRotationX','outRotationX',om.MFnUnitAttribute.kAngle,0)
    ParentConstraint.outRotationY = uAttr.create('outRotationY','outRotationY',om.MFnUnitAttribute.kAngle,0)
    ParentConstraint.outRotationZ = uAttr.create('outRotationZ','outRotationZ',om.MFnUnitAttribute.kAngle,0) 
    ParentConstraint.outRotation = nAttr.create('outRotation', 'outRotation',ParentConstraint.outRotationX,
                                        ParentConstraint.outRotationY,ParentConstraint.outRotationZ)
    
    #add attributes
    ParentConstraint.addAttribute(ParentConstraint.parentCount)
    ParentConstraint.addAttribute(ParentConstraint.parent)
    ParentConstraint.addAttribute(ParentConstraint.targetList)
    
    ParentConstraint.addAttribute(ParentConstraint.constraintParentInverseMatrix)
    ParentConstraint.addAttribute(ParentConstraint.constraintWorldMatrix)
    ParentConstraint.addAttribute(ParentConstraint.constraintParentMatrix)
    ParentConstraint.addAttribute(ParentConstraint.constraintRotateOrder)
    ParentConstraint.addAttribute(ParentConstraint.constraintRotatePivotTranslate)
    ParentConstraint.addAttribute(ParentConstraint.constraintJointOrient)
    ParentConstraint.addAttribute(ParentConstraint.constraintRotatePivot)
    ParentConstraint.addAttribute(ParentConstraint.offsetTranslation)
    ParentConstraint.addAttribute(ParentConstraint.offsetRotate)
    
    ParentConstraint.addAttribute(ParentConstraint.outTranslation)
    ParentConstraint.addAttribute(ParentConstraint.outRotation)

    #attr affects

    ParentConstraint.attributeAffects(ParentConstraint.targetTranslate, ParentConstraint.outTranslation)
    ParentConstraint.attributeAffects(ParentConstraint.targetTranslate, ParentConstraint.outRotation)
    
    ParentConstraint.attributeAffects(ParentConstraint.targetParentMatrix, ParentConstraint.outTranslation)
    ParentConstraint.attributeAffects(ParentConstraint.targetParentMatrix, ParentConstraint.outRotation)
    
    ParentConstraint.attributeAffects(ParentConstraint.targetScale, ParentConstraint.outTranslation)
    ParentConstraint.attributeAffects(ParentConstraint.targetScale, ParentConstraint.outRotation)
    
    ParentConstraint.attributeAffects(ParentConstraint.targetRotateOrder, ParentConstraint.outTranslation)
    ParentConstraint.attributeAffects(ParentConstraint.targetRotateOrder, ParentConstraint.outRotation)
    
    ParentConstraint.attributeAffects(ParentConstraint.targetRotate, ParentConstraint.outTranslation)
    ParentConstraint.attributeAffects(ParentConstraint.targetRotate, ParentConstraint.outRotation)
    
    ParentConstraint.attributeAffects(ParentConstraint.targetRotatePivotTranslate, ParentConstraint.outTranslation)
    ParentConstraint.attributeAffects(ParentConstraint.targetRotatePivotTranslate, ParentConstraint.outRotation)
    
    ParentConstraint.attributeAffects(ParentConstraint.targetRotatePivot, ParentConstraint.outTranslation)
    ParentConstraint.attributeAffects(ParentConstraint.targetRotatePivot, ParentConstraint.outRotation)
    
    ParentConstraint.attributeAffects(ParentConstraint.targetOffsetTranslate, ParentConstraint.outTranslation)
    ParentConstraint.attributeAffects(ParentConstraint.targetOffsetTranslate, ParentConstraint.outRotation)
    
    ParentConstraint.attributeAffects(ParentConstraint.targetOffsetRotate, ParentConstraint.outTranslation)
    ParentConstraint.attributeAffects(ParentConstraint.targetOffsetRotate, ParentConstraint.outRotation)
    
    ParentConstraint.attributeAffects(ParentConstraint.targetJointOrient, ParentConstraint.outTranslation)
    ParentConstraint.attributeAffects(ParentConstraint.targetJointOrient, ParentConstraint.outRotation)

    ParentConstraint.attributeAffects(ParentConstraint.constraintParentInverseMatrix, ParentConstraint.outTranslation)
    ParentConstraint.attributeAffects(ParentConstraint.constraintParentInverseMatrix, ParentConstraint.outRotation)
    
    ParentConstraint.attributeAffects(ParentConstraint.constraintRotateOrder, ParentConstraint.outTranslation)
    ParentConstraint.attributeAffects(ParentConstraint.constraintRotateOrder, ParentConstraint.outRotation)
    
    ParentConstraint.attributeAffects(ParentConstraint.constraintRotatePivotTranslate, ParentConstraint.outTranslation)
    ParentConstraint.attributeAffects(ParentConstraint.constraintRotatePivotTranslate, ParentConstraint.outRotation)
    
    ParentConstraint.attributeAffects(ParentConstraint.constraintRotatePivot, ParentConstraint.outTranslation)
    ParentConstraint.attributeAffects(ParentConstraint.constraintRotatePivot, ParentConstraint.outRotation)
    
    ParentConstraint.attributeAffects(ParentConstraint.constraintJointOrient, ParentConstraint.outTranslation)
    ParentConstraint.attributeAffects(ParentConstraint.constraintJointOrient, ParentConstraint.outRotation)
    
    ParentConstraint.attributeAffects(ParentConstraint.offsetTranslation, ParentConstraint.outTranslation)
    ParentConstraint.attributeAffects(ParentConstraint.offsetTranslation, ParentConstraint.outRotation)
    
    ParentConstraint.attributeAffects(ParentConstraint.offsetRotate, ParentConstraint.outTranslation)
    ParentConstraint.attributeAffects(ParentConstraint.offsetRotate, ParentConstraint.outRotation)
    
    ParentConstraint.attributeAffects(ParentConstraint.parent, ParentConstraint.outTranslation)
    ParentConstraint.attributeAffects(ParentConstraint.parent, ParentConstraint.outRotation)
    
    
class ParentConstraintCmd(ompx.MPxCommand):
     
    def __init__(self):
        ompx.MPxCommand.__init__(self)
        self.__fDGMod = om.MDGModifier()
        self.__dagMod = om.MDagModifier()
        self.__dagFn = om.MFnDagNode()
        self.__dpFn = om.MFnDependencyNode()
        
    def isUndoable(self):
         
        return True
         
    def doIt(self,args):
    
        nameString = ''
        maintainOffset = False
        #addTargetString = ''
        #removeTargetString = ''
        
        argData = om.MArgDatabase(self.syntax(), args)
        selectionList = om.MSelectionList()
        argData.getObjects(selectionList)
        
        selectionLength = selectionList.length()
        constrainedObject = om.MObject()
        selectionList.getDependNode(selectionLength - 1,constrainedObject)
        
        targetObjectList = []
        
        for i in range(selectionLength-1):
            targetObject = om.MObject()
            selectionList.getDependNode(i,targetObject)
            targetObjectList.append(targetObject)

        
        if argData.isFlagSet(kConstraintName):
            nameString = argData.flagArgumentString(kConstraintName, 0)
             
        else:
            nameString = 'switchParentConstraint'
            
        if argData.isFlagSet(kMaintainOffset):
            maintainOffset = True
    
        #create and connect spNode if add and remove flags arent set
        if not argData.isFlagSet(kAddTarget) or argData.isFlagSet(kRemoveTarget):
            
            #create switchParent node  
            switchParentNode = self.__fDGMod.createNode(nodeID)
            
            #get plugs from constrained object
            self.__dpFn.setObject(constrainedObject)
            
            conObjParentInversePlug = self.__dpFn.findPlug('parentInverseMatrix')
            conObjParentInversePlug.setNumElements(1)
            conObjParentInversePlug.evaluateNumElements()
            conObjParentInversePlugIndex = conObjParentInversePlug.elementByPhysicalIndex(0)
            
            conObjWorldPlug = self.__dpFn.findPlug('worldMatrix')
            conObjWorldPlug.setNumElements(1)
            conObjWorldPlug.evaluateNumElements()
            conObjWorldPlugIndex = conObjWorldPlug.elementByPhysicalIndex(0)
            
            conObjRotateOrderPlug = self.__dpFn.findPlug('rotateOrder')
            conObjRotatePivotPlug = self.__dpFn.findPlug('rotatePivot')
            conObjRotatePivotTranslatePlug = self.__dpFn.findPlug('rotatePivotTranslate')
            conObjTranslatePlug = self.__dpFn.findPlug('translate')
            conObjectRotatePlug = self.__dpFn.findPlug('rotate')
            
            try:
                conObjJointOrientPlug = self.__dpFn.findPlug('jointOrient')
            
            except RuntimeError:
                conObjJointOrientPlug = False
            
                
            #get plugs from sp node for constrained object
            self.__dpFn.setObject(switchParentNode)
            self.__dpFn.setName(nameString)
            
            constraintInverseParentPlug = self.__dpFn.findPlug('constraintInverseParentMatrix')
            constraintWorldMatrixPlug = self.__dpFn.findPlug('constraintWorldMatrix')
            constraintRotatePivotTranslatePlug = self.__dpFn.findPlug('constraintRotatePivotTranslate')
            constraintRotateOrderPlug = self.__dpFn.findPlug('constraintRotateOrder')
            constraintRotatePivotPlug = self.__dpFn.findPlug('constraintRotatePivot')
            constraintJointOrientPlug = self.__dpFn.findPlug('constraintJointOrient')
            constraintOutTranslatePlug = self.__dpFn.findPlug('outTranslation')
            constraintOutRotatePlug = self.__dpFn.findPlug('outRotation')
            
            
            #connect constrained object to sp node
            
            self.__fDGMod.connect(conObjParentInversePlugIndex,constraintInverseParentPlug)
            self.__fDGMod.connect(conObjWorldPlugIndex,constraintWorldMatrixPlug)
            self.__fDGMod.connect(conObjRotateOrderPlug,constraintRotateOrderPlug)
            self.__fDGMod.connect(conObjRotatePivotTranslatePlug,constraintRotatePivotTranslatePlug)
            self.__fDGMod.connect(conObjRotatePivotPlug,constraintRotatePivotPlug)
            self.__fDGMod.connect(constraintOutTranslatePlug,conObjTranslatePlug)
            self.__fDGMod.connect(constraintOutRotatePlug,conObjectRotatePlug)
                                    
            if conObjJointOrientPlug:
                self.__fDGMod.connect(conObjJointOrientPlug,constraintJointOrientPlug)
            
            worldSpaceObject = conObjWorldPlugIndex.asMObject()
            worldSpaceMatrixData = om.MFnMatrixData(worldSpaceObject)
            worldSpaceMatrix = worldSpaceMatrixData.matrix()
            
            #decompose constrained obj world matrix
            worldSpaceTransformationMatrix = om.MTransformationMatrix(worldSpaceMatrix)
            worldSpaceTranslation = worldSpaceTransformationMatrix.getTranslation(om.MSpace.kWorld)
            worldSpaceEulerRotation = worldSpaceTransformationMatrix.eulerRotation()
            
            transformation = om.MTransformationMatrix(worldSpaceMatrix)
            translation = transformation.getTranslation(om.MSpace.kWorld)

            #set parent count value
            parentCountValue = len(targetObjectList)
            parentCountPlug = self.__dpFn.findPlug('parentCount')
            self.__fDGMod.newPlugValueDouble(parentCountPlug, parentCountValue)
            
            #connect target list
            targetCompPlug = self.__dpFn.findPlug('targetList')
            
            i = 0
            for targetObject in targetObjectList:
                
                self.__dpFn.setObject(switchParentNode)
                currentTargetPlug = targetCompPlug.elementByLogicalIndex(i)
                
                #plugs from constraint
                targetTranslatePlug = currentTargetPlug.child(0)
                targetParentMatrixPlug = currentTargetPlug.child(1)
                targetScalePlug = currentTargetPlug.child(2)
                targetRotateOrderPlug = currentTargetPlug.child(3)
                targetRotatePlug = currentTargetPlug.child(4)
                targetRotatePivotTranslatePlug = currentTargetPlug.child(5)
                targetRotatePivotPlug = currentTargetPlug.child(6)
                targetJointOrientPlug = currentTargetPlug.child(7)
                targetWorldMatrixPlug = currentTargetPlug.child(8)
                targetOffsetTranslatePlug = currentTargetPlug.child(9)
                targetOffsetRotatePlug = currentTargetPlug.child(10)
                
                #plugs from target
                self.__dpFn.setObject(targetObject)
                targetObjTranslatePlug = self.__dpFn.findPlug('translate')
                
                targetObjParentMatrixPlug = self.__dpFn.findPlug('parentMatrix')
                targetObjParentMatrixPlug.setNumElements(1)
                targetObjParentMatrixPlug.evaluateNumElements()
                targetObjParentMatrixPlugIndex = targetObjParentMatrixPlug.elementByPhysicalIndex(0)
                
                targetObjWorldMatrixPlug = self.__dpFn.findPlug('worldMatrix')
                targetObjWorldMatrixPlug.setNumElements(1)
                targetObjWorldMatrixPlug.evaluateNumElements()
                targetObjWorldMatrixPlugIndex = targetObjWorldMatrixPlug.elementByPhysicalIndex(0)
                
                targetObjWorldObject = targetObjWorldMatrixPlugIndex.asMObject()
                targetObjWorldMatrixData = om.MFnMatrixData(targetObjWorldObject)
                targetObjWorldMatrix = targetObjWorldMatrixData.matrix()
                
                #decompose target world space matrix
                targetObjWorldSpaceTransformationMatrix = om.MTransformationMatrix(targetObjWorldMatrix)
                targetObjTranslation = targetObjWorldSpaceTransformationMatrix.getTranslation(om.MSpace.kWorld)
                targetObjEulerRotation = targetObjWorldSpaceTransformationMatrix.eulerRotation()
                
                offsetTranslation = worldSpaceTranslation - targetObjTranslation
                offsetRotation = worldSpaceEulerRotation - targetObjEulerRotation
                
                targetOffsetTranslateXPlug = targetOffsetTranslatePlug.child(0)
                targetOffsetTranslateYPlug = targetOffsetTranslatePlug.child(1)
                targetOffsetTranslateZPlug = targetOffsetTranslatePlug.child(2)
                
                targetOffsetRotateXPlug = targetOffsetRotatePlug.child(0)
                targetOffsetRotateYPlug = targetOffsetRotatePlug.child(1)
                targetOffsetRotateZPlug = targetOffsetRotatePlug.child(2)
                
                if maintainOffset:
                
                    self.__fDGMod.newPlugValueDouble(targetOffsetTranslateXPlug,offsetTranslation.x)
                    self.__fDGMod.newPlugValueDouble(targetOffsetTranslateYPlug,offsetTranslation.y)
                    self.__fDGMod.newPlugValueDouble(targetOffsetTranslateZPlug,offsetTranslation.z)
                    
                    self.__fDGMod.newPlugValueDouble(targetOffsetRotateXPlug,offsetRotation.x)
                    self.__fDGMod.newPlugValueDouble(targetOffsetRotateYPlug,offsetRotation.y)
                    self.__fDGMod.newPlugValueDouble(targetOffsetRotateZPlug,offsetRotation.z)
                
                targetObjScalePlug = self.__dpFn.findPlug('scale')
                targetObjRotateOrderPlug = self.__dpFn.findPlug('rotateOrder')
                targetObjRotatePlug = self.__dpFn.findPlug('rotate')
                targetObjRotatePivotTranslatePlug = self.__dpFn.findPlug('rotatePivotTranslate')
                targetObjRotatePivotPlug = self.__dpFn.findPlug('rotatePivot')
                
                try:
                    targetObjJointOrientPlug = self.__dpFn.findPlug('jointOrient')
                except RuntimeError:
                    targetObjJointOrientPlug = False
                
                #connect plugs
                self.__fDGMod.connect(targetObjTranslatePlug,targetTranslatePlug)
                self.__fDGMod.connect(targetObjParentMatrixPlugIndex,targetParentMatrixPlug)
                self.__fDGMod.connect(targetObjScalePlug,targetScalePlug)
                self.__fDGMod.connect(targetObjRotateOrderPlug,targetRotateOrderPlug)
                self.__fDGMod.connect(targetObjRotatePlug,targetRotatePlug)
                self.__fDGMod.connect(targetObjRotatePivotTranslatePlug,targetRotatePivotTranslatePlug)
                self.__fDGMod.connect(targetObjRotatePivotPlug,targetRotatePivotPlug)
                self.__fDGMod.connect(targetObjWorldMatrixPlugIndex,targetWorldMatrixPlug)
                
                if targetObjJointOrientPlug:
                    self.__fDGMod.connect(targetObjJointOrientPlug,targetJointOrientPlug)
                
                i += 1
                
            #set max value for parent int attr
            self.__dpFn.setObject(switchParentNode)
            parentPlug = self.__dpFn.findPlug('parent')
            parentAttrObject = parentPlug.attribute()
            nAttr = om.MFnNumericAttribute(parentAttrObject)
            nAttr.setMax(parentCountValue)
            
            self.__fDGMod.doIt()

    def redoIt(self):
         
        self.__dagMod.doIt()
        self.__fDGMod.doIt()
 
    def undoIt(self):
         
        self.__fDGMod.undoIt()
        self.__dagMod.undoIt()
    
    
# Syntax creator
def syntaxCreator():
        
    syntax = om.MSyntax()
    
    syntax.addFlag(kConstraintName,kConstraintNameLong,om.MSyntax.kString)
    syntax.addFlag(kMaintainOffset,kMaintainOffsetLong,om.MSyntax.kBoolean)
    syntax.addFlag(kAddTarget,kAddTargetLong,om.MSyntax.kString)
    syntax.addFlag(kRemoveTarget,kRemoveTargetLong,om.MSyntax.kString)
    
    syntax.setObjectType(syntax.kSelectionList)
    
    return syntax

def cmdCreator():
     
    return ompx.asMPxPtr(ParentConstraintCmd())

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
    