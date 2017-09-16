'''
Created on Jan 22, 2013

@author: Bill
'''

import maya.OpenMaya as om
import maya.cmds as cmds
import GenAPI

class ShapeTool():
    
    '''
    class for editing meshes 
    '''
    
    def __init__(self,shape):
        
        if cmds.nodeType(shape) == 'shape':
            self.shape = shape
        
        else:
            shapes = cmds.listRelatives(shape,type = 'shape')
            self.shape = shapes[0]
            
        self.transform = cmds.listRelatives(self.shape,parent = True)[0]
        self.shapePath = GenAPI.getDagPath(shape)
        
        self.origShape = ''
        shapes = cmds.listRelatives(self.transform,shapes = True)
        '''
        for obj in shapes:

            if cmds.getAttr('%s.intermediateObject'%obj) and cmds.listConnections('%s.worldMesh'%obj,source=False):
                self.origShape = obj
                break
        else:
            raise RuntimeError('No deformers found for %s.' % self.shape)
        '''
    
    @staticmethod    
    def getPointArray(shape):
        
        '''
        method gathers point array from verts
        output pointArray(mPointArray)
        '''
        if cmds.nodeType(shape) == 'transform':
            shape = cmds.listRelatives(shape, type = 'shape')[0]
        
        geoPath = GenAPI.getDagPath(shape)
        geoItr = om.MItGeometry(geoPath)
        pointArray = om.MPointArray()
        
        geoItr.allPositions(pointArray, om.MSpace.kObject)
        
        return pointArray
    
    @staticmethod
    def setPointArray(shape,pointArray):
        
        '''
        method sets positions of verts
        input pointArray(mPointArray)
        '''
        
        if cmds.nodeType(shape) == 'transform':
            shape = cmds.listRelatives(shape, type = 'shape')[0]
        
        shapePath = GenAPI.getDagPath(shape)
        geoItr = om.MItGeometry(shapePath)
        geoItr.setAllPositions(pointArray, om.MSpace.kObject)
        
      
    def getTranslationVectors(self,fromMesh):
        
        '''
        method build an array of vectors for translation
        input fromMesh (python string)
        '''
        
        fromMeshPath = GenAPI.getDagPath(fromMesh)
        geoItr = om.MItGeometry(fromMeshPath)
        pointArrayA = om.MPointArray()
        geoItr.allPositions(pointArrayA, om.MSpace.kObject)
        
        pointArrayB = ShapeTool.getPointArray(self.shape)

        if pointArrayA.length() == pointArrayB.length():
 
            outVectorArray = om.MVectorArray()
            
            itr = 0
             
            while itr <= pointArrayA.length():
                 
                vectorA = pointArrayA[itr]
                vectorB = pointArrayB[itr]
                vectorC = vectorA - vectorB               
                outVectorArray.append(vectorC)
                
                itr += 1
                
        return  outVectorArray
    
    def getOrigPoints(self):
        origPoints = self.getPointArray(self.origShape)
        return origPoints
    
    def getDeltas(self):
        deformedPoints = self.getPointArray(self.shape)
        origPoints = self.getPointArray(self.origShape)
        
        vectorArray = om.MVectorArray()
        
        for i in range(deformedPoints.length()):
            
            vectorA = om.MVector(origPoints[i])
            vectorB = om.MVector(deformedPoints[i])
            vectorC = vectorB - vectorA
            
            vectorArray.append(vectorC)
            
        return vectorArray
    
    def getInverseMatricies(self,correctivePoints):
        
        deformedPoints = self.getPointArray(self.shape)
        origPoints = self.getPointArray(self.origShape)
        matrixArray = om.MMatrixArray()
        
        deltas = self.getDeltas()

        for i in range(deformedPoints.length()):
            matrix = om.MMatrix()
            setMatrixRow(matrix, deltas[i], 0)
            setMatrixRow(matrix, deltas[i], 1)
            setMatrixRow(matrix, deltas[i], 2)
            setMatrixRow(matrix, correctivePoints[i], 3)
            matrixArray.append(matrix.inverse())
                 
        return matrixArray

    
    @staticmethod
    def createPointArrayFromMatrixArray(matrixArray):
        
        pointArray = om.MPointArray()
        
        for i in range(matrixArray.length()):
              
            matrix = matrixArray[i]
            transformMatrix = om.MTransformationMatrix(matrix)
            translation  = transformMatrix.getTranslation(om.MSpace.kObject)
            mpoint = om.MPoint(translation)
            pointArray.append(mpoint)
        
        return pointArray
    
    @staticmethod
    def multiplyPointsByMatrices(shape,matrices):
        
        shapePath = GenAPI.getDagPath(shape)
        geoItr = om.MItGeometry(shapePath)
        pointArray = om.MPointArray()
        
        while not geoItr.isDone():
            index = geoItr.index()
            pointPos = geoItr.position()
            newPos = pointPos * matrices[index]
            pointArray.append(newPos)
            geoItr.next()
            
        geoItr.setAllPositions(pointArray)
        
    @staticmethod
    def setTranslation(mesh,vectorArray):
        
        meshPath = GenAPI.getDagPath(mesh)
        
        vertItr = om.MItMeshVertex(meshPath)
        
        while not vertItr.isDone():
            
            index = vertItr.index()
            vertItr.translateBy(vectorArray[index],om.MSpace.kObject)
            vertItr.next()
            
    #class end
    
def transferPointPos(fromShape,toShape):
    
    points = ShapeTool.getPointArray(fromShape)
    ShapeTool.setPointArray(toShape, points)
    
def invertDeformer(poseMesh,corrective):
    
    newMesh = cmds.duplicate(poseMesh)[0]
    
    shapes = cmds.listRelatives(newMesh,type = 'shape')
    for shape in shapes:
        if cmds.getAttr('%s.intermediateObject'%shape):
            cmds.delete(shape)
            
    correctivePoints = ShapeTool.getPointArray(corrective)
    
    shapeTool = ShapeTool(poseMesh)
    invMatricies = shapeTool.getInverseMatricies(correctivePoints)
    deltas = shapeTool.getTranslationVectors(corrective)
    
    geoItr = om.MItGeometry(GenAPI.getDagPath(poseMesh))
    
    pointArray = om.MPointArray()
    
    while not geoItr.isDone():
        i = geoItr.index()
        pt = geoItr.position()
        invPt = pt * invMatricies[i]
        newPt = om.MVector(invPt)
        pointArray.append(om.MPoint(invPt))
        geoItr.next()
        
    shapeTool.setPointArray(newMesh, pointArray)
             
def setBlendTargetWeights(blendShape = '',target = 0,geo = '',weightList = []):
    
    geoPath = GenAPI.getDagPath(geo)
    geoItr = om.MItGeometry(geoPath)
    
    while not geoItr.isDone():
        
        index = geoItr.index()
   
        cmds.setAttr('%s.inputTarget[0].inputTargetGroup[%i].targetWeights[%i]'%(blendShape,target,index),weightList[index])
        
        geoItr.next()
    
            
def createParamTracker(name = ''):
    
    sphere = cmds.sphere(n = '%s_Target_Surface'%name)[0]
    sphereShape = cmds.listRelatives(sphere,type = 'shape')[0]
    loc = cmds.spaceLocator(name = '%s_Target_Loc'%name)[0]
    cmds.move(1,0,0,loc)
    cpsNode = cmds.createNode('closestPointOnSurface',n = '%s_Target_CPS'%name)
    cmds.connectAttr('%s.worldSpace[0]'%sphereShape,'%s.inputSurface'%cpsNode)
    dmNode = cmds.createNode('decomposeMatrix',name = '%s_Target_DM'%name)
    cmds.connectAttr('%s.worldMatrix[0]'%loc,'%s.inputMatrix'%dmNode)
    cmds.connectAttr('%s.outputTranslate'%dmNode,'%s.inPosition'%cpsNode)
    
    cmds.addAttr(loc,ln = 'paramU',at = 'double')
    cmds.setAttr('%s.paramU'%loc,e = True, keyable = True)
    cmds.connectAttr('%s.result.parameterU'%cpsNode,'%s.paramU'%loc)
    
    cmds.addAttr(loc,ln = 'paramV',at = 'double')
    cmds.setAttr('%s.paramV'%loc,e = True, keyable = True)
    cmds.connectAttr('%s.result.parameterV'%cpsNode,'%s.paramV'%loc)
    
    grp = cmds.group(name = '%s_Target_Grp'%name,empty = True)
    cmds.parent(sphere,grp)
    cmds.parent(loc,grp)
    
def setMatrixRow(matrix, newVector, row):
    setMatrixCell(matrix, newVector.x, row, 0)
    setMatrixCell(matrix, newVector.y, row, 1)
    setMatrixCell(matrix, newVector.z, row, 2)

def setMatrixCell(matrix, value, row, column):
    om.MScriptUtil.setDoubleArray(matrix[row], column, value)
    
def getMatrix(matrix):
    out = []
    
    for i in range(4):
        for x in range(4):
            out.append(matrix(x,i))
            
    return out
            
            


def addInbetweenShape():
    import pymel.core as pm

    #Adds InBetweens for properly named and connected shapes
    objects = pm.ls(sl = 1)
    base = str(objects.pop(-1))
    
    baseInputs = pm.listHistory(base)
    
    for b in baseInputs:
        if b.nodeType() == 'blendShape':
            blShape = b
    
    targets = blShape.getTarget()
    
    for o in objects:
        nameList = o.split('_')
        ibSuffix = nameList.pop()
        ibTarget = '_'.join(nameList)
        ibName = str(o)
        ibWeight = int(ibSuffix.strip('IB')) * .01
        
        print ibWeight
        print ibTarget
        ibIndex = targets.index(ibTarget)
        
        print ibIndex
    pm.blendShape(str(blShape), e = 1, ib = 1,tc = False, t = (base, ibIndex, ibName, ibWeight))
    
def poseReader(name,parent,pose):
    #create pose reader
    loc = cmds.spaceLocator(name = '%s_Loc'%name)[0]
    poseReader = cmds.createNode('poseReader', name = '%s_PRShape'%name)
    prParent = cmds.listRelatives(poseReader,parent = True)[0]
    cmds.connectAttr('%s.worldMatrix[0]'%loc,'%s.worldMatrixPoseIn'%poseReader)
    cmds.connectAttr('%s.worldMatrix[0]'%prParent,'%s.worldMatrixLiveIn'%poseReader)
    prParent = cmds.listRelatives(poseReader,parent = True)[0]
    cmds.parent(prParent,loc)
    constraint = cmds.parentConstraint(pose,loc)
    cmds.delete(constraint)
    cmds.parentConstraint(pose,prParent)
    cmds.parentConstraint(parent,loc, mo = True)
    
    cmds.setAttr( '%s.drawCone'%poseReader,1)
    cmds.setAttr('%s.drawText'%poseReader,1)