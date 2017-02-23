'''
Created on Jan 30, 2013
@author: Belal Ballout

Description:

    node functions like maya's aim constraint in 'object up' mode
    node has the ability to be re-oriented via aim and up vectors
    node works with joints and has the ability to mainain offset
    attrs are found in the shape node of the aimLocator node
    offset rotation attrs are in the channel box.
    other attrs can be found in attr editor under 'Extra Attributes'
    
    command builds node and network connections
    
    openGL drawing represents relationship between target, up,
    and constrained object. 

MEL:
    
    Command only works with Maya 2012>.
    
    kAimLocatorNodeCmd -co str -tgt str -up str -uv int int int -av int int int -mo bool -n str;
    kAimLocatorNodeCmd -co "ConObj_02_Jnt" -tgt "Tgt_02_Jnt" -up "Up_02_Jnt" -uv 0 1 0 -av 1 0 0 -mo false -n "AimLocator";
    
    args:
        name,n..............string....sets name of constraint node
        conObj,co...........string....constrained object
        tgt,t...............string....aim target object
        up,u................string....up target object
        aimVector,av........int3......normal unit vector  
        upVector,uv.........int3......tangent unit vector 
        maintainOffset,mo...bool......sets maintain offset
                                    
'''

import sys,math
import maya.OpenMaya as om
import maya.OpenMayaRender as omr
import maya.OpenMayaMPx as ompx

nodeName = 'kAimLocatorNode'
nodeID = om.MTypeId(0x81338f)

cmdName = 'kAimLocatorNodeCmd'
kConstraintName = '-n'
kConstraintNameLong = '-name'
kConstrainedObject = '-co'
kConstrainedObjectLong = '-conObj'
kTargetName = '-tgt'
kTargetNameLong = '-target'
kUpName = '-up'
kUpNameLong = '-upObj'
kAimVector = '-av'
kAimVectorLong = '-aimVector'
kUpVector = '-uv'
kUpVectorLong = '-upVector'
kMaintainOffset = '-mo'
kMaintainOffsetLong = '-maintainOffset'

glRenderer = omr.MHardwareRenderer.theRenderer()
glFT = glRenderer.glFunctionTable()

#node definition
class AimLocatorNode(ompx.MPxLocatorNode):
    
    #attrs
    contraintParentInverseMatrix = om.MObject()
    constraintTranslate = om.MObject()
    constraintRotatePivot = om.MObject()
    constraintRotateOrder = om.MObject()
    constraintJointOrient = om.MObject()
    constraintRotateOrder = om.MObject()
    
    aimObjectParentMatrix = om.MObject()
    aimObjectTranslate = om.MObject()
    aimObjectRotatePivot = om.MObject()
    
    upObjectParentMatrix = om.MObject()
    upObjectTranslate = om.MObject()
    upObjectRotatePivot = om.MObject()
    
    aimVector = om.MObject()
    upVector = om.MObject()
    offsetRotation = om.MObject()
    upScalar = om.MObject()
    outRotation = om.MObject()

    def __init__(self):
        
        ompx.MPxLocatorNode.__init__(self)
        self.constraintVector = om.MVector()
        self.aimObjVector = om.MVector()
        self.upObjVector = om.MVector()
        self.projectedVector = om.MVector()
        self.aimEueler = om.MEulerRotation()
        self.theta = 0

    def compute(self,plug,data):
        
        if plug == AimLocatorNode.outRotation:
            
            #output
            outputRotationData = data.outputValue(AimLocatorNode.outRotation)
            
            #inputs
            #constrained object
            contraintParentInverseMatrixData = data.inputValue(AimLocatorNode.contraintParentInverseMatrix)
            constraintTranslateData = data.inputValue(AimLocatorNode.constraintTranslate)
            constraintRotatePivotData = data.inputValue(AimLocatorNode.constraintRotatePivot)
            
            #aim object
            aimObjParentMatrixData = data.inputValue(AimLocatorNode.aimObjectParentMatrix)
            aimObjTranslateData = data.inputValue(AimLocatorNode.aimObjectTranslate)
            aimObjRotatePivotData = data.inputValue(AimLocatorNode.aimObjectRotatePivot)
            
            #up object
            upObjParentMatrixData = data.inputValue(AimLocatorNode.upObjectParentMatrix)
            upObjTranslateData = data.inputValue(AimLocatorNode.upObjectTranslate)
            upObjRotatePivotData = data.inputValue(AimLocatorNode.upObjectRotatePivot)
            
            #orient vectors
            upVectorData = data.inputValue(AimLocatorNode.upVector)
            aimVectorData = data.inputValue(AimLocatorNode.aimVector)
            jointOrientData = data.inputValue(AimLocatorNode.constraintJointOrient)
            rotateOrderData = data.inputValue(AimLocatorNode.constraintRotateOrder)
            offsetRotationData = data.inputValue(AimLocatorNode.offsetRotation)
            upScalarData = data.inputValue(AimLocatorNode.upScalar)
            
            #get vectors from inputs
            #get constrained object vector
            parentInverseMatrix = contraintParentInverseMatrixData.asMatrix().inverse() 
            constraintTransformation = om.MTransformationMatrix(parentInverseMatrix)
            constraintTranslateVector = constraintTranslateData.asVector()
            constraintRotatePivotVector = constraintRotatePivotData.asVector()
            constraintTransformation.addTranslation(constraintTranslateVector,om.MSpace.kObject)
            constraintTransformation.addTranslation(constraintRotatePivotVector,om.MSpace.kObject)
            self.constraintVector = constraintTransformation.getTranslation(om.MSpace.kWorld)
            
            upScalar = upScalarData.asFloat()
            
            #get aim object vector
            aimObjParentMatrix = aimObjParentMatrixData.asMatrix()
            aimObjTranslate = aimObjTranslateData.asVector()
            aimObjRotatePivot = aimObjRotatePivotData.asVector()
            self.aimObjVector = getVector(aimObjParentMatrix,aimObjTranslate,aimObjRotatePivot)
            
            #get up object vector
            upObjParentMatrix = upObjParentMatrixData.asMatrix()
            upObjTranslate = upObjTranslateData.asVector()
            upObjRotatePivot = upObjRotatePivotData.asVector()
            self.upObjVector = getVector(upObjParentMatrix,upObjTranslate,upObjRotatePivot)
            
            #unit vectors
            upVector = upVectorData.asVector()
            aimVector = aimVectorData.asVector()                
            offsetVector = offsetRotationData.asVector()
            jointOrientAxis = jointOrientData.asVector()
            rotationOrder = rotateOrderData.asShort()
            
            #create vectors for aim and up
            normalVector = self.aimObjVector - self.constraintVector
            tangentVector = self.upObjVector - self.constraintVector
            direction =  tangentVector ^ normalVector

            offsetRotation = om.MVector(offsetVector.x,offsetVector.y,offsetVector.z)

            jointOrient = om.MVector(jointOrientAxis.x,jointOrientAxis.y,jointOrientAxis.z)
            
            #create eueler rotations for offsets
            eulerRotateOffset = om.MEulerRotation(offsetRotation,rotationOrder)
            eulerJointOrient = om.MEulerRotation(jointOrient,rotationOrder)
            
            #quaternion for aim
            aimQuat = om.MQuaternion(aimVector,normalVector)

            #get quat tangent
            fromVector = upVector
            fromVector = fromVector.transformAsNormal(aimQuat.asMatrix())
            
            #project upObj vector against quat normal vector
            unitVector = normalVector.normal()
            self.projectedVector = tangentVector - (unitVector * (unitVector * tangentVector))
            
            #calculate angle       
            dot = fromVector * self.projectedVector

            try:

                self.theta = math.acos(dot / (fromVector.length() * self.projectedVector.length()))
                print self.theta,fromVector.length(),self.projectedVector.length()
                
                #check which side dest vector lies on
                if fromVector * direction > 0:
                    angle = self.theta
                     
                else:
                    angle = (((2 * math.pi) - self.theta))
    
            except ValueError:
                 
                angle = 0
                
            #create quat for up    
            upQuat = om.MQuaternion(angle,aimVector)
            
            #create tranformation data
            aimMatrix = aimQuat.asMatrix()
            upMatrix = upQuat.asMatrix()
            eulerJointOrientMatrix = eulerJointOrient.asMatrix()
            
            quatMatrix = upMatrix * aimMatrix
            worldMatrix = (quatMatrix * parentInverseMatrix.inverse()) * eulerJointOrientMatrix.inverse()

            #set transformation
            transformMatrix = om.MTransformationMatrix(worldMatrix)
            transformMatrix.rotateBy(eulerRotateOffset,om.MSpace.kObject)

            
            #set output
            outRotation = transformMatrix.eulerRotation()
            reorderedOutRotation = outRotation.reorderIt(rotationOrder)
            outputRotationData.set3Double(reorderedOutRotation.x,reorderedOutRotation.y,reorderedOutRotation.z)   
            
            #update data
            data.setClean(plug)
            
            #send rotation to aimEueler attr
            rotateQuat = om.MQuaternion(om.MVector(0,0,1),normalVector)
            self.aimEueler = rotateQuat.asEulerRotation()
            
    def draw(self, view, path, style, status):
        
        pocVector = self.projectedVector + self.constraintVector
        
        def drawTriangle():
            
            pointArray = [[0.258,0,0], [0,0.386,0], [-0.258,0,0],[-0.258,0,0]]
            
            glFT.glBegin(omr.MGL_LINE_LOOP)
            
            for point in pointArray:
            
                glFT.glVertex3f(point[0], point[1], point[2])
                 
            glFT.glEnd()
        
        def drawCircle(radius):
            
            pointArray = []
            for i in range(360):
                
                angle = math.radians(i)
                pointX = math.cos(angle)*radius
                pointY = math.sin(angle)*radius
                circlePoint = om.MVector(pointX,pointY,0)
                pointArray.append([circlePoint.x,circlePoint.y,circlePoint.z])

            for point in pointArray:
                
                glFT.glBegin(omr.MGL_LINE_LOOP)
                glFT.glVertex3f(point[0], point[1], point[2])
                
            glFT.glEnd()    
        
        radius = self.projectedVector.length()
        
        #draw rotate plane circle
        view.beginGL()
        glFT.glPushMatrix()
        glFT.glTranslatef(self.constraintVector.x,self.constraintVector.y,self.constraintVector.z)
        glFT.glRotatef(math.degrees(self.aimEueler.x),1,0,0)
        glFT.glRotatef(math.degrees(self.aimEueler.y),0,1,0)
        glFT.glRotatef(math.degrees(self.aimEueler.z),0,0,1)
        drawCircle(radius)
        glFT.glPopMatrix()
        view.endGL()
        
        #draw arrow 1
        view.beginGL()
        glFT.glPushMatrix()
        glFT.glTranslatef(self.aimObjVector.x,self.aimObjVector.y,self.aimObjVector.z)
        glFT.glRotatef(math.degrees(self.aimEueler.x),1,0,0)
        glFT.glRotatef(math.degrees(self.aimEueler.y),0,1,0)
        glFT.glRotatef(math.degrees(self.aimEueler.z),0,0,1)
        glFT.glRotatef(90,1,0,0)
        drawTriangle()
        glFT.glPopMatrix()
        view.endGL()
        
        #draw arrow 2
        view.beginGL()
        glFT.glPushMatrix()
        glFT.glTranslatef(self.aimObjVector.x,self.aimObjVector.y,self.aimObjVector.z)
        glFT.glRotatef(math.degrees(self.aimEueler.x),1,0,0)
        glFT.glRotatef(math.degrees(self.aimEueler.y),0,1,0)
        glFT.glRotatef(math.degrees(self.aimEueler.z),0,0,1)
        glFT.glRotatef(90,0,1,0)
        glFT.glRotatef(90,0,0,1)
        drawTriangle()
        glFT.glPopMatrix()
        view.endGL()
        
        #draw arrow circle
        view.beginGL()
        glFT.glPushMatrix()
        glFT.glTranslatef(self.aimObjVector.x,self.aimObjVector.y,self.aimObjVector.z)
        glFT.glRotatef(math.degrees(self.aimEueler.x),1,0,0)
        glFT.glRotatef(math.degrees(self.aimEueler.y),0,1,0)
        glFT.glRotatef(math.degrees(self.aimEueler.z),0,0,1)
        drawCircle(0.258)
        glFT.glPopMatrix()
        view.endGL()
        
        #draw line to target
        view.beginGL()
        glFT.glBegin(omr.MGL_LINES)
        glFT.glVertex3f(self.aimObjVector.x, self.aimObjVector.y, self.aimObjVector.z)
        glFT.glVertex3f(self.constraintVector.x, self.constraintVector.y, self.constraintVector.z)
        glFT.glEnd()
        view.endGL()
        
        #draw line to up
        view.beginGL()
        glFT.glBegin(omr.MGL_LINES)
        glFT.glVertex3f(self.upObjVector.x, self.upObjVector.y, self.upObjVector.z)
        glFT.glVertex3f(self.constraintVector.x, self.constraintVector.y, self.constraintVector.z)
        view.endGL()
        
        #draw line from up to projected up vector
        view.beginGL()
        glFT.glBegin(omr.MGL_LINES)
        glFT.glVertex3f(self.upObjVector.x, self.upObjVector.y, self.upObjVector.z)
        glFT.glVertex3f(pocVector.x, pocVector.y, pocVector.z)
        glFT.glEnd()
        view.endGL()
        
        #draw line from constrained object to projected up vector
        view.beginGL()
        glFT.glBegin(omr.MGL_LINES)
        glFT.glVertex3f(pocVector.x, pocVector.y, pocVector.z)
        glFT.glVertex3f(self.constraintVector.x, self.constraintVector.y, self.constraintVector.z)
        glFT.glEnd()
        view.endGL()
        
        #display Target text
        view.beginGL()
        tgtTextPoint = om.MPoint(self.aimObjVector.x,self.aimObjVector.y,self.aimObjVector.z)
        view.drawText('Target', tgtTextPoint)
        view.endGL()
        
        #display Up text
        view.beginGL()
        upTextPoint = om.MPoint(self.upObjVector.x,self.upObjVector.y,self.upObjVector.z)
        view.drawText('Up', upTextPoint)
        view.endGL()
        
        #display theta text
        view.beginGL()
        thetaTextPoint = om.MPoint(pocVector.x,pocVector.y,pocVector.z)
        view.drawText('%f'%math.degrees(self.theta), thetaTextPoint)
        view.endGL()
        
#function returns ws vector         
def getVector(parentMatrix,translate,rotatePivot):

    newTransformMatrix = om.MTransformationMatrix(parentMatrix)
    newTransformMatrix.addTranslation(translate,om.MSpace.kObject)
    newTransformMatrix.addTranslation(rotatePivot,om.MSpace.kObject)
    
    outVector = newTransformMatrix.getTranslation(om.MSpace.kWorld)
    
    return outVector

def nodeCreator():

    return ompx.asMPxPtr(AimLocatorNode())

def nodeInitializer():
    
    nAttr = om.MFnNumericAttribute()
    mAttr = om.MFnMatrixAttribute()
    eAttr = om.MFnEnumAttribute()
    uAttr = om.MFnUnitAttribute()
    
    #constrained object
    AimLocatorNode.contraintParentInverseMatrix = mAttr.create('constraintInverseParentMatrix','constraintInverseParentMatrix',
                                       om.MFnMatrixAttribute.kDouble)
    
    mAttr.setStorable(False)

    AimLocatorNode.constraintTranslate = nAttr.create('constraintTranslate','constraintTranslate',
                                                      om.MFnNumericData.k3Double)
    mAttr.setStorable(False)
    
    AimLocatorNode.constraintRotatePivot = nAttr.create('constraintRotatePivot','constraintRotatePivot', 
                                                  om.MFnNumericData.k3Double)
    nAttr.setStorable(False)
    
    AimLocatorNode.jointOrientX = uAttr.create('jointOrientX', 'jointOrientX',
                                                om.MFnUnitAttribute.kAngle,0)
    AimLocatorNode.jointOrientY = uAttr.create('jointOrientY', 'jointOrientY',
                                                om.MFnUnitAttribute.kAngle,0)
    AimLocatorNode.jointOrientZ = uAttr.create('jointOrientZ', 'jointOrientZ',
                                                om.MFnUnitAttribute.kAngle,0)
    
    AimLocatorNode.constraintJointOrient = nAttr.create('jointOrient','jointOrient', 
                                                  AimLocatorNode.jointOrientX,
                                                  AimLocatorNode.jointOrientY,
                                                  AimLocatorNode.jointOrientZ)
    nAttr.setStorable(False)
    
    AimLocatorNode.constraintRotateOrder = eAttr.create('constraintRotateOrder','constraintRotateOrder') 
    eAttr.addField('xyz',0)
    eAttr.addField('yzx',1)
    eAttr.addField('zxy',2)
    eAttr.addField('xzy',3)
    eAttr.addField('yxz',4)
    eAttr.addField('zyx',5)
    eAttr.setStorable(False)

    #aim object
    AimLocatorNode.aimObjectParentMatrix = mAttr.create('aimParentMatrix','aimParentMatrix',
                                           om.MFnMatrixAttribute.kDouble)    
    mAttr.setStorable(False)

    AimLocatorNode.aimObjectTranslate = nAttr.create('aimTranslate','aimTranslate', 
                                                  om.MFnNumericData.k3Double)
    nAttr.setStorable(False)

    AimLocatorNode.aimObjectRotatePivot = nAttr.create('aimRotatePivot','aimRotatePivot', 
                                                  om.MFnNumericData.k3Double)
    nAttr.setStorable(False)

    #up object
    
    AimLocatorNode.upObjectParentMatrix = mAttr.create('upParentMatrix','upParentMatrix',
                                           om.MFnMatrixAttribute.kDouble)
    mAttr.setStorable(False)
    
    AimLocatorNode.upObjectTranslate= nAttr.create('upTranslate','upTranslate', 
                                              om.MFnNumericData.k3Double)
    nAttr.setStorable(False)
    
    AimLocatorNode.upObjectRotatePivot = nAttr.create('upRotatePivot','upRotatePivot', 
                                                  om.MFnNumericData.k3Double)
    nAttr.setStorable(False)
    
    #orient vectors

    AimLocatorNode.aimVector = nAttr.create('aimVector','aimVector', 
                                                 om.MFnNumericData.k3Double)

    AimLocatorNode.upVector = nAttr.create('upVector','upVector', 
                                                  om.MFnNumericData.k3Double)
    
    #up scalar
    AimLocatorNode.upScalar = nAttr.create('upScalar','upScalar',om.MFnNumericData.kFloat,1)
    nAttr.setChannelBox(True)
    nAttr.setStorable(True)
    nAttr.setWritable(True)
    nAttr.setMax(1.0)
    nAttr.setMin(0.0)
    
    #rotation
    
    AimLocatorNode.outRotationX = uAttr.create('outRotationX', 'outRotationX',
                                                om.MFnUnitAttribute.kAngle,0)
    AimLocatorNode.outRotationY = uAttr.create('outRotationY', 'outRotationY',
                                                om.MFnUnitAttribute.kAngle,0)
    AimLocatorNode.outRotationZ = uAttr.create('outRotationZ', 'outRotationZ',
                                                om.MFnUnitAttribute.kAngle,0)

    AimLocatorNode.outRotation = nAttr.create('outRotation', 'outRotation',
                                                AimLocatorNode.outRotationX,
                                                AimLocatorNode.outRotationY, 
                                                AimLocatorNode.outRotationZ)

    AimLocatorNode.offsetRotationX = uAttr.create('offsetRotationX', 'offsetRotationX',
                                                om.MFnUnitAttribute.kAngle,0)
    AimLocatorNode.offsetRotationY = uAttr.create('offsetRotationY', 'offsetRotationY',
                                                om.MFnUnitAttribute.kAngle,0)
    AimLocatorNode.offsetRotationZ = uAttr.create('offsetRotationZ', 'offsetRotationZ',
                                                om.MFnUnitAttribute.kAngle,0)
    
    AimLocatorNode.offsetRotation = nAttr.create('offsetRotation', 'offsetRotation',
                                            AimLocatorNode.offsetRotationX,
                                            AimLocatorNode.offsetRotationY,
                                            AimLocatorNode.offsetRotationZ)
    nAttr.setStorable(True)
    nAttr.setWritable(True)
    nAttr.setChannelBox(True)
    
    #add attributes
    AimLocatorNode.addAttribute(AimLocatorNode.contraintParentInverseMatrix)
    AimLocatorNode.addAttribute(AimLocatorNode.constraintTranslate)
    AimLocatorNode.addAttribute(AimLocatorNode.constraintRotatePivot)
    AimLocatorNode.addAttribute(AimLocatorNode.constraintJointOrient)
    AimLocatorNode.addAttribute(AimLocatorNode.constraintRotateOrder)
    
    AimLocatorNode.addAttribute(AimLocatorNode.aimObjectParentMatrix)
    AimLocatorNode.addAttribute(AimLocatorNode.aimObjectTranslate)
    AimLocatorNode.addAttribute(AimLocatorNode.aimObjectRotatePivot)
    
    AimLocatorNode.addAttribute(AimLocatorNode.upObjectParentMatrix)
    AimLocatorNode.addAttribute(AimLocatorNode.upObjectTranslate)
    AimLocatorNode.addAttribute(AimLocatorNode.upObjectRotatePivot)
    
    AimLocatorNode.addAttribute(AimLocatorNode.aimVector)
    AimLocatorNode.addAttribute(AimLocatorNode.upVector)
    AimLocatorNode.addAttribute(AimLocatorNode.offsetRotation)
    AimLocatorNode.addAttribute(AimLocatorNode.upScalar)
    AimLocatorNode.addAttribute(AimLocatorNode.outRotation)
    
    #attribute effects
    AimLocatorNode.attributeAffects(AimLocatorNode.contraintParentInverseMatrix,AimLocatorNode.outRotation)
    AimLocatorNode.attributeAffects(AimLocatorNode.constraintTranslate, AimLocatorNode.outRotation)
    AimLocatorNode.attributeAffects(AimLocatorNode.constraintRotatePivot, AimLocatorNode.outRotation)
    AimLocatorNode.attributeAffects(AimLocatorNode.constraintJointOrient, AimLocatorNode.outRotation)
    AimLocatorNode.attributeAffects(AimLocatorNode.constraintRotateOrder, AimLocatorNode.outRotation)

    AimLocatorNode.attributeAffects(AimLocatorNode.aimObjectParentMatrix, AimLocatorNode.outRotation)
    AimLocatorNode.attributeAffects(AimLocatorNode.aimObjectTranslate, AimLocatorNode.outRotation)
    AimLocatorNode.attributeAffects(AimLocatorNode.aimObjectRotatePivot, AimLocatorNode.outRotation)
    
    AimLocatorNode.attributeAffects(AimLocatorNode.upObjectParentMatrix, AimLocatorNode.outRotation)
    AimLocatorNode.attributeAffects(AimLocatorNode.upObjectTranslate, AimLocatorNode.outRotation)
    AimLocatorNode.attributeAffects(AimLocatorNode.upObjectRotatePivot, AimLocatorNode.outRotation)
    
    AimLocatorNode.attributeAffects(AimLocatorNode.aimVector, AimLocatorNode.outRotation)
    AimLocatorNode.attributeAffects(AimLocatorNode.upVector, AimLocatorNode.outRotation)
    AimLocatorNode.attributeAffects(AimLocatorNode.offsetRotation, AimLocatorNode.outRotation)
    AimLocatorNode.attributeAffects(AimLocatorNode.upScalar, AimLocatorNode.outRotation)
    
#command definition           
class AimLocatorCmd(ompx.MPxCommand):
     
    def __init__(self):
        ompx.MPxCommand.__init__(self)
        self.__fDGMod = om.MDGModifier()
        self.__dagMod = om.MDagModifier()
        self.__dagFn = om.MFnDagNode()
        self.__dpFn = om.MFnDependencyNode()
        
    def isUndoable(self):
         
        return True
         
    def doIt(self,args):
        
        argData = om.MArgDatabase(self.syntax(), args)
        
        #get args
        
        if argData.isFlagSet(kConstraintName):
            nameString = argData.flagArgumentString(kConstraintName, 0)
             
        else:
            nameString = 'aimLocator1'
        
        if argData.isFlagSet(kConstrainedObject):
            conObjectString = argData.flagArgumentString(kConstrainedObject, 0)
             
        else:
            om.MGlobal.displayError('Please provide constrained Object.')
            
        if argData.isFlagSet(kTargetName):
            targetString = argData.flagArgumentString(kTargetName, 0)
             
        else:
            om.MGlobal.displayError('Please provide target.')
            
        if argData.isFlagSet(kUpName):
            upString = argData.flagArgumentString(kUpName, 0)
             
        else:
            om.MGlobal.displayError('Please provide aim.')
            
        if argData.isFlagSet(kAimVector):
            aimVectorX = argData.flagArgumentDouble(kAimVector, 0)
            aimVectorY = argData.flagArgumentDouble(kAimVector, 1)
            aimVectorZ = argData.flagArgumentDouble(kAimVector, 2)
  
        else:
            aimVectorX = 1
            aimVectorY = 0
            aimVectorZ = 0
            
        if argData.isFlagSet(kUpVector):
            upVectorX = argData.flagArgumentDouble(kUpVector, 0)
            upVectorY = argData.flagArgumentDouble(kUpVector, 1)
            upVectorZ = argData.flagArgumentDouble(kUpVector, 2)
 
             
        else:
            upVectorX = 0
            upVectorY = 1
            upVectorZ = 0   
            
        if argData.isFlagSet(kMaintainOffset):
            maintainOffset = argData.flagArgumentBool(kMaintainOffset, 0)
             
        else:
            maintainOffset = False
             
        
        #data handles for nodes
        constrainedObject = om.MObject()
        targetObject = om.MObject()
        upObject = om.MObject()
        
        selectionList = om.MSelectionList()
        selectionList.add(conObjectString) 
        selectionList.add(targetString)
        selectionList.add(upString) 
        selectionList.getDependNode(0,constrainedObject)
        selectionList.getDependNode(1,targetObject)
        selectionList.getDependNode(2,upObject)
        
        #create aim node    
        aimNode = self.__dagMod.createNode(nodeName)
        self.__dagMod.doIt()
        
        #parent aim node under constrained object
        self.__dagFn.setObject(constrainedObject)
        #self.__dagFn.addChild(aimNode,0,False)
        
        #rename nodes
        self.__dagFn.setObject(aimNode)
        self.__dagFn.setName(nameString)
        shapeObject = self.__dagFn.child(0)
        self.__dpFn.setObject(shapeObject)
        self.__dpFn.setName('%sShape'%nameString)
        
        #get plugs
        conObjInvMtxAimNodePlug = self.__dpFn.findPlug('constraintInverseParentMatrix')

        conObjTranslateNodePlug = self.__dpFn.findPlug('constraintTranslate')
        conObjRotatePivotNodePlug = self.__dpFn.findPlug('constraintRotatePivot')
        conObjJointOrientNodePlug = self.__dpFn.findPlug('jointOrient')
        conObjRotateOrderNodePlug = self.__dpFn.findPlug('constraintRotateOrder')
        
        aimParentMtxNodePlug = self.__dpFn.findPlug('aimParentMatrix')
        aimTraslateNodePlug = self.__dpFn.findPlug('aimTranslate')
        aimRotatePivotNodePlug= self.__dpFn.findPlug('aimRotatePivot')
        
        upParentMtxNodePlug = self.__dpFn.findPlug('upParentMatrix')
        upTranslateNodePlug = self.__dpFn.findPlug('upTranslate')
        upRotatePivotNodePlug = self.__dpFn.findPlug('upRotatePivot')
        
        aimVectorXPlug = self.__dpFn.findPlug('aimVector0')
        aimVectorYPlug = self.__dpFn.findPlug('aimVector1')
        aimVectorZPlug = self.__dpFn.findPlug('aimVector2')
        
        upVectorXPlug = self.__dpFn.findPlug('upVector0')
        upVectorYPlug = self.__dpFn.findPlug('upVector1')
        upVectorZPlug = self.__dpFn.findPlug('upVector2')
        
        outRotationNodePlug = self.__dpFn.findPlug('outRotation')
        
        offsetRotationXPlug = self.__dpFn.findPlug('offsetRotationX')
        offsetRotationYPlug = self.__dpFn.findPlug('offsetRotationY')
        offsetRotationZPlug = self.__dpFn.findPlug('offsetRotationZ')
        
        self.__dpFn.setObject(constrainedObject)
        constrainedParentMtxPlug = self.__dpFn.findPlug('parentInverseMatrix')
        constrainedParentMtxPlug.setNumElements(1)
        constrainedParentMtxPlug.evaluateNumElements()
        constrainedParentMtxIndexPlug = constrainedParentMtxPlug.elementByPhysicalIndex(0)
        
        constrainedTranslatePlug = self.__dpFn.findPlug('translate')
        constrainedRotatePlug = self.__dpFn.findPlug('rotate')
        constrainedRotatePivotPlug = self.__dpFn.findPlug('rotatePivot')
        constrainedRotateOrderPlug = self.__dpFn.findPlug('rotateOrder')
        
        self.__dpFn.setObject(targetObject)
        targetParentMtxPlug = self.__dpFn.findPlug('parentMatrix')
        targetParentMtxPlug.setNumElements(1)
        targetParentMtxPlug.evaluateNumElements()
        targetParentMtxIndexPlug = targetParentMtxPlug.elementByPhysicalIndex(0)        
        
        targetTranslatePlug = self.__dpFn.findPlug('translate')
        targetRotatePivotPlug = self.__dpFn.findPlug('rotatePivot')
        
        self.__dpFn.setObject(upObject)
        upParentMtxPlug = self.__dpFn.findPlug('parentMatrix')
        upParentMtxPlug.setNumElements(1)
        upParentMtxPlug.evaluateNumElements()
        upParentMtxIndexPlug = upParentMtxPlug.elementByPhysicalIndex(0)    
        
        upTranslatePlug = self.__dpFn.findPlug('translate')
        upRotatePivotPlug = self.__dpFn.findPlug('rotatePivot')
        
        #make connections
        self.__fDGMod.connect(constrainedParentMtxIndexPlug,conObjInvMtxAimNodePlug)
        
        self.__fDGMod.connect(constrainedTranslatePlug,conObjTranslateNodePlug)
        self.__fDGMod.connect(constrainedRotatePivotPlug,conObjRotatePivotNodePlug)
        self.__fDGMod.connect(constrainedRotateOrderPlug,conObjRotateOrderNodePlug)
        self.__fDGMod.connect(targetParentMtxIndexPlug,aimParentMtxNodePlug)
        self.__fDGMod.connect(targetTranslatePlug,aimTraslateNodePlug)
        self.__fDGMod.connect(targetRotatePivotPlug,aimRotatePivotNodePlug)
        self.__fDGMod.connect(upParentMtxIndexPlug,upParentMtxNodePlug)
        self.__fDGMod.connect(upTranslatePlug,upTranslateNodePlug)
        self.__fDGMod.connect(upRotatePivotPlug,upRotatePivotNodePlug)
        self.__fDGMod.connect(outRotationNodePlug,constrainedRotatePlug)
        
        #make connection if object is a joint
        if constrainedObject.apiType() == om.MFn.kJoint:
            self.__dpFn.setObject(constrainedObject)
            constrainedJointOrientPlug = self.__dpFn.findPlug('jointOrient')
            self.__fDGMod.connect(constrainedJointOrientPlug,conObjJointOrientNodePlug)
        
        #set unit vectors
        self.__fDGMod.newPlugValueDouble(aimVectorXPlug, aimVectorX)
        self.__fDGMod.newPlugValueDouble(aimVectorYPlug, aimVectorY)
        self.__fDGMod.newPlugValueDouble(aimVectorZPlug, aimVectorZ)
        
        self.__fDGMod.newPlugValueDouble(upVectorXPlug, upVectorX)
        self.__fDGMod.newPlugValueDouble(upVectorYPlug, upVectorY)
        self.__fDGMod.newPlugValueDouble(upVectorZPlug, upVectorZ)
        
        transformFn = om.MFnTransform(constrainedObject)
        origTransformation = transformFn.transformation()
        
        self.__fDGMod.doIt()
        
        if maintainOffset:
            
            newTransformation = transformFn.transformation()
            transformMatrix =  origTransformation.asMatrix() * newTransformation.asMatrix().inverse()
            mtransformationMatrix = om.MTransformationMatrix(transformMatrix)
            euelerRotation = mtransformationMatrix.eulerRotation()
            
            self.__fDGMod.newPlugValueDouble(offsetRotationXPlug, euelerRotation.x)
            self.__fDGMod.newPlugValueDouble(offsetRotationYPlug, euelerRotation.y)
            self.__fDGMod.newPlugValueDouble(offsetRotationZPlug, euelerRotation.z)
            
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
    syntax.addFlag(kConstrainedObject,kConstrainedObjectLong,om.MSyntax.kString)
    syntax.addFlag(kTargetName, kTargetNameLong, om.MSyntax.kString)
    syntax.addFlag(kUpName, kUpNameLong, om.MSyntax.kString)
                       
    syntax.addFlag(kAimVector, kAimVectorLong, om.MSyntax.kDouble,
               om.MSyntax.kDouble,om.MSyntax.kDouble)
    
    
    syntax.addFlag(kUpVector, kUpVectorLong, om.MSyntax.kDouble,
               om.MSyntax.kDouble,om.MSyntax.kDouble)
    
    syntax.addFlag(kMaintainOffset,kMaintainOffsetLong,om.MSyntax.kBoolean)

    return syntax

def cmdCreator():
     
    return ompx.asMPxPtr(AimLocatorCmd())

    
def initializePlugin(mobject):
    
    mplugin = ompx.MFnPlugin(mobject)
    
    try:
        mplugin.registerCommand(cmdName, cmdCreator, syntaxCreator)    
    except:
        sys.stderr.write("Failed to register command: %s" % cmdName)
        raise
     
    try:
        mplugin.registerNode(nodeName, nodeID,nodeCreator,nodeInitializer,
                             ompx.MPxNode.kLocatorNode)
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
    
    
##Thank you for your time and have a wonderful day! :D  