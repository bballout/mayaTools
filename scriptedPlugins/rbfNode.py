'''
Created on Oct 14, 2013

@author: Bill Ballout

Node that computes radial basis functions

kernels:
    linear
    multi-quadratic
    inverse multi-quadratic
    gaussian
    
inputs:
    center -> transform.worldMatrix[*]
    points/targets -> point.worldMatrix[*]
    shape parameter
    kernel
    
outputs:
    array of results
    
'''

import sys
import math
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
import maya.OpenMayaRender as omr
 
nodeName = 'kRBFNode'
nodeID = om.MTypeId(0x80088f)

glRenderer = omr.MHardwareRenderer.theRenderer()
glFT = glRenderer.glFunctionTable()

#node definition
class RBFNode(ompx.MPxLocatorNode):
    #attrs
    rbfCenter = om.MObject()
    rbfParam = om.MObject()
    point = om.MObject()
    kernel = om.MObject()
    shapeParam = om.MObject()
    
    result = om.MObject()
    

    def __init__(self):
        ompx.MPxLocatorNode.__init__(self)
        self.centerVector = om.MVector()
        self.pointVectorArray = om.MVectorArray()
        self.results = []
         
         
    def compute(self,plug,data):
        if plug == RBFNode.result:
            #inputs
            rbfCenterData = data.inputValue(RBFNode.rbfCenter)
            rbfCenterMatrix = rbfCenterData.asMatrix()
            
            rbfParamCompData = data.inputArrayValue(RBFNode.rbfParam)
            rbfParamCount = rbfParamCompData.elementCount()
            
            print rbfParamCount
            
            resultArrayData = data.outputArrayValue(RBFNode.result)
            arrayBuilder = resultArrayData.builder()
            
            transformMatrix = om.MTransformationMatrix(rbfCenterMatrix)
            self.centerVector = transformMatrix.getTranslation(om.MSpace.kWorld)
            
            #clear out attributes
            self.results = []
            self.pointVectorArray = om.MVectorArray()
            
            for i in range(rbfParamCount):
                print i
                rbfParamCompData.jumpToElement(i)
                rbfParamData = rbfParamCompData.inputValue()
                
                pointData = rbfParamData.child(RBFNode.point)
                kernelData = rbfParamData.child(RBFNode.kernel)
                shapeParamData = rbfParamData.child(RBFNode.shapeParam)
                
                pointMatrix = pointData.asMatrix()
                kernel = kernelData.asShort()
                shapeParam = shapeParamData.asFloat()
                
                pointTransformation = om.MTransformationMatrix(pointMatrix)
                pointVector = pointTransformation.getTranslation(om.MSpace.kWorld)
                self.pointVectorArray.append(pointVector)
                
                resultVal = interpolate(kernel,self.centerVector,pointVector,shapeParam)
                self.results.append(resultVal)
                
                rHandle = arrayBuilder.addElement(i) 
                rHandle.setFloat(resultVal)
                
                resultArrayData.set(arrayBuilder)
                resultArrayData.setAllClean()
                
            #update
            data.setClean(plug)
            
    def draw(self,view,path,style,status):
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
            
        def drawSphere():
            view.beginGL()
            glFT.glPushMatrix()
            glFT.glRotatef(90,1,0,0)
            glFT.glRotatef(0,0,1,0)
            glFT.glRotatef(0,0,0,1)
            drawCircle(0.5)
            glFT.glPopMatrix()
            view.endGL()
                
            view.beginGL()
            glFT.glPushMatrix()
            glFT.glRotatef(0,1,0,0)
            glFT.glRotatef(90,0,1,0)
            glFT.glRotatef(0,0,0,1)
            drawCircle(0.5)
            glFT.glPopMatrix()
            view.endGL()
            
            view.beginGL()
            glFT.glPushMatrix()
            glFT.glRotatef(0,1,0,0)
            glFT.glRotatef(0,0,1,0)
            glFT.glRotatef(90,0,0,1)
            drawCircle(0.5)
            glFT.glPopMatrix()
            view.endGL()
            
        view.beginGL()
        glFT.glPushMatrix()
        glFT.glTranslatef(self.centerVector.x,self.centerVector.y,self.centerVector.z)
        drawSphere()
        glFT.glPopMatrix()
        view.endGL()
        
        for i in range(self.pointVectorArray.length()):
            currentPoint = self.pointVectorArray[i]
            
            #draw line from center to point
            view.beginGL()
            glFT.glBegin(omr.MGL_LINES)
            glFT.glVertex3f(self.centerVector.x, self.centerVector.y, self.centerVector.z)
            glFT.glVertex3f(currentPoint.x, currentPoint.y, currentPoint.z)
            glFT.glEnd()
            view.endGL()
            
            #display result text
            view.beginGL()
            resultTextPoint = om.MPoint(currentPoint.x,currentPoint.y,currentPoint.z)
            view.drawText('%f'%self.results[i], resultTextPoint)
            view.endGL()

def interpolate(kernel,vectorA,vectorB,shapeParam):
    vectorC = vectorA - vectorB
    length = vectorC.length()
    
    output = 0
    
    if kernel == 0:
        '''linear'''
        output = abs(length) * (-1 * shapeParam) + 1

    if kernel == 1:
        '''multiquadratic'''
        output = (math.sqrt(1 + ((length * length) * (shapeParam * shapeParam))) - 1)
    
    if kernel == 2:
        '''inverse multiquadratic'''
        output = 1 / (1 + ((length * length) * (shapeParam * shapeParam)))
    
    if kernel == 3:
        '''gaussian'''
        output = math.exp(-1 * ((length * length) * (shapeParam * shapeParam)))
    
    return output

def nodeCreator():
    return ompx.asMPxPtr(RBFNode())
 
def nodeInitializer():
    cAttr = om.MFnCompoundAttribute()
    eAttr = om.MFnEnumAttribute()
    mAttr = om.MFnMatrixAttribute()
    nAttr = om.MFnNumericAttribute()

    #rbfCenter
    RBFNode.rbfCenter = mAttr.create('rbfCenter','rbfCenter',om.MFnMatrixAttribute.kDouble)
    mAttr.setStorable(True)
    
    #points
    RBFNode.point = mAttr.create('point','point',om.MFnMatrixAttribute.kDouble)
    mAttr.setStorable(True)
    
    #kernel
    RBFNode.kernel = eAttr.create('kernel','kernel')
    eAttr.addField('linear',0)
    eAttr.addField('multiquadratic',1)
    eAttr.addField('inverseMultiquadratic',2)
    eAttr.addField('gaussian',3)
    eAttr.setStorable(True)

    
    #result
    RBFNode.result = nAttr.create('result','result',om.MFnNumericData.kFloat,0)
    nAttr.setArray(True)
    nAttr.setUsesArrayDataBuilder(True)
    
    #shapeParam
    RBFNode.shapeParam = nAttr.create('shapeParam','shapeParam',om.MFnNumericData.kFloat,0)
    nAttr.setMin(-10)
    nAttr.setMax(10)
    nAttr.setStorable(False)
    
    #rbf param (combo attr)
    RBFNode.rbfParam = cAttr.create('RBFParam','RBFParam')
    
    cAttr.addChild(RBFNode.point)
    cAttr.addChild(RBFNode.kernel)
    cAttr.addChild(RBFNode.shapeParam)
    cAttr.setArray(True)
    cAttr.setUsesArrayDataBuilder(True)
                                    
    #add attributes
    RBFNode.addAttribute(RBFNode.rbfCenter)
    RBFNode.addAttribute(RBFNode.rbfParam)
    RBFNode.addAttribute(RBFNode.result)
    
    #attribute affects
    RBFNode.attributeAffects(RBFNode.rbfCenter, RBFNode.result)
    RBFNode.attributeAffects(RBFNode.point, RBFNode.result)
    RBFNode.attributeAffects(RBFNode.kernel, RBFNode.result)
    RBFNode.attributeAffects(RBFNode.shapeParam, RBFNode.result)


def initializePlugin(mobject):
    mplugin = ompx.MFnPlugin(mobject)
    try:
        mplugin.registerNode(nodeName, nodeID,nodeCreator,nodeInitializer,
                             ompx.MPxNode.kLocatorNode)
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
    