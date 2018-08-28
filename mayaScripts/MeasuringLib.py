'''
Created on May 22, 2012

@author: balloutb

Module for gathering and manipulating measurements
'''
import math
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya.cmds as cmds
import GenAPI

try:
    import UILib
    
except ImportError:
    pass

class MeasuringTool():

    ''' Auto Rig Measurements Class '''

    #class attrs:
    
    objectStartPath = ''
    objectEndPath = ''
           
    def __init__(self,objectStart,objectEnd):
    
        self.objectStart = objectStart
        self.objectEnd = objectEnd
        self.objectStartPath = GenAPI.getDagPath(self.objectStart)
        self.objectEndPath = GenAPI.getDagPath(self.objectEnd)
    
    #Vector Methods Through API.....
    
    @staticmethod
    #returns mpoint of transform path
    def getMPoint(dagObject):
    
        mDagPath = GenAPI.getDagPath(dagObject)
        
        transformFn = om.MFnTransform(mDagPath)
        space = om.MSpace()
        
        mpoint = transformFn.rotatePivot(space.kWorld)
        return mpoint       
    
    
    def getPointDistanceBetween(self):
    
        pointAPos = self.getPointLocation(self.objectStart)
        pointBPos = self.getPointLocation(self.objectEnd)
        pointA = om.MPoint(pointAPos[0],pointAPos[1],pointAPos[2])
        pointB = om.MPoint(pointBPos[0],pointBPos[1],pointBPos[2])
        
        pointDiffence = om.MPoint(pointA - pointB)
        
        return [math.fabs(pointDiffence.x),math.fabs(pointDiffence.y),math.fabs(pointDiffence.z)]
    
    @staticmethod    
    def getVectorLength(vector):
        
        length = math.sqrt( (vector[0] * vector[0]) + (vector[1] * vector[1]) + (vector[2] * vector[2]) ) 
        return length
    
    #method returns length of vector between two points
    #input MPoint (firstPoint)
    #input MPoint (secondPoint)
    #output python float (vectorLength) 
    @staticmethod
    def getVectorLengthBetween(pointA,pointB):
    
        
        vectorA = om.MVector(pointA)
        vectorB = om.MVector(pointB)
        
        vectorC = om.MVector(vectorA - vectorB)
        
        length = vectorC.length()
        return length
    
        
    def getAngleBetween(self):
    
        posA = self.getPointLocation(self.objectStart)
        posB = self.getPointLocation(self.objectEnd)
        
        vectorA = om.MVector(posA[0],posA[1],posA[2])
        vectorB = om.MVector(posB[0],posB[1],posB[2])
        
        #cos^-1(a.b/|a||b|)*(180/pi)
        
        angleRadians = vectorA.angle(vectorB)
        angleDegrees = math.degrees(angleRadians)
        
        return angleDegrees
        
    
    def getPerpendicularVector(self):
        
        posA = self.getPointLocation(self.objectStart)
        posB = self.getPointLocation(self.objectEnd)
        
        vectorA = om.MVector(posA[0],posA[1],posA[2])
        vectorB = om.MVector(posB[0],posB[1],posB[2])
        
        #(aybz- azby, azbx- axbz, axby - aybx)
        #(a[1]b[2]- a[2]b[1], a[2]b[0]- a[0]b[2], a[0]b[1] - a[1]b[0])
        
        '''
        vectorCx = ((vectorA[1] * vectorB[2]) - (vectorA[2] * vectorB[1]))
        vectorCy = ((vectorA[2] * vectorB[0]) - (vectorA[0] * vectorB[2]))
        vectorCz = ((vectorA[0] * vectorB[1]) - (vectorA[1] * vectorB[0]))
        '''
        
        vectorC = vectorA ^ vectorB
        
        return [vectorC[0],vectorC[1],vectorC[2]]
    
   
    #Rotation Methods Through API...
    @staticmethod
    def getQuaternionRotation(dagObject,space = 'world'):
        
        mDagPath = GenAPI.getDagPath(dagObject)

        transformFn = om.MFnTransform(mDagPath)
        mSpace = om.MSpace()
        quatSpace = ''
        
        if(space == 'world'):
            quatSpace = mSpace.kWorld
            
        else:
            quatSpace = mSpace.kObject


        utilX = om.MScriptUtil()
        ptrX = utilX.asDoublePtr()

        utilY = om.MScriptUtil()
        ptrY = utilY.asDoublePtr()

        utilZ = om.MScriptUtil()
        ptrZ = utilZ.asDoublePtr()

        utilW = om.MScriptUtil()
        ptrW = utilW.asDoublePtr()

        transformFn.getRotationQuaternion(ptrX,ptrY,ptrZ,ptrW,quatSpace)

        quatX = utilX.getDouble(ptrX)
        quatY = utilY.getDouble(ptrY)
        quatZ = utilZ.getDouble(ptrZ)
        quatW = utilW.getDouble(ptrW)

        return [quatX,quatY,quatZ,quatW]
    
    
    @staticmethod    
    def getVectorFromQuaternion(dagObject,vector,space = 'world'):
    
        initVector = om.MVector(vector[0],vector[1],vector[2])
        
        if(space == 'world'):
            quaternion = MeasuringTool.getQuaternionRotation(dagObject,'world')
            
        else:
            quaternion = MeasuringTool.getQuaternionRotation(dagObject,'local')
        
        mquat = om.MQuaternion(quaternion[0],quaternion[1],quaternion[2],quaternion[3])
        rotatedVector = initVector.rotateBy(mquat)
        return [rotatedVector.x,rotatedVector.y,rotatedVector.z]
        
    @staticmethod
    def getWorldTranslation(dagObject):
    
        transformFn = om.MFnTransform(dagObject)    
        translation = transformFn.getTranslation(om.MSpace.kWorld)
        
        return translation
        
    @staticmethod
    def getLocalEulerRotation(dagObject):
        
        transformFn = om.MFnTransform(dagObject)
        euler = om.MEulerRotation()
        
        transformFn.getRotation(euler)
        
        return [math.degrees(euler.x),math.degrees(euler.y),math.degrees(euler.z),euler.order]
    
    @staticmethod
    def getWorldEulerRotation(dagObject):
        
        quaternionRotation = MeasuringTool.getQuaternionRotation(dagObject,'world')
        
        quaternion = om.MQuaternion(quaternionRotation[0],quaternionRotation[1],quaternionRotation[2],quaternionRotation[3])
        eulerRotation = quaternion.asEulerRotation()
        
        return [math.degrees(eulerRotation[0]),math.degrees(eulerRotation[1]),math.degrees(eulerRotation[2])]
        
    @staticmethod
    def getRotationOrder(dagObject):
        
        transformFn = om.MFnTransform(dagObject)
        rotationOrder = transformFn.rotationOrder()
        
        return rotationOrder
        
    #matching...
    @staticmethod
    def matchSpace(dagObject,name):
    
        translation = MeasuringTool.getWorldTranslation(dagObject)
        rotation = MeasuringTool.getWorldEulerRotation(dagObject)
        rotationOrder = MeasuringTool.getRotationOrder(dagObject)

        newTransform = cmds.group(empty = True, n = '%s_Group'%(name))
        dagPath = GenAPI.getDagPath(newTransform)
        transformFn = om.MFnTransform(dagPath)

        transformFn.setTranslation(translation,om.MSpace.kWorld)
        transformFn.setRotation(rotation,rotationOrder)
        transformFn.setRotationOrder(rotationOrder,1)
    
    #returns the combined vector length of transforms in hierarchy
    #input MObject (root)
    #output float value (length) 
    @staticmethod
    def getLengthOfHierarchy(nodeObject):
        
        #root =  GenAPI.getRootDagNode(nodeObject)
        children = GenAPI.getHierarchy(nodeObject)
        
        nodeFn = om.MFnDagNode()
        transformFn = om.MFnTransform()
        
        selectionItr = om.MItSelectionList(children)
        length = 0.0

        while not selectionItr.isDone():
            
            currentObject = om.MObject()
            currentPath = om.MDagPath()
            selectionItr.getDependNode(currentObject)
            nodeFn.setObject(currentObject)
            nodeFn.getPath(currentPath)
            
            if not nodeFn.childCount() == 0:
                
                childNode = nodeFn.child(0)
                nodeFn.setObject(childNode)
                childPath = om.MDagPath()
                nodeFn.getPath(childPath)
                
                transformFn.setObject(currentPath)
                vectorA = transformFn.getTranslation(om.MSpace.kWorld)

                transformFn.setObject(childPath)
                vectorB = transformFn.getTranslation(om.MSpace.kWorld)
                
                vectorC = vectorA - vectorB
                
                currentLength = vectorC.length()
                
                length += currentLength
                
            selectionItr.next()
            
        return length
    
    ##Methods for components...
    
    #returns list of vert positions from mesh
    #input mesh (python string)
    #output pointArray(python list [[x,y,z],[']...])
    @staticmethod
    def getComponentPoints(mesh):
        
        meshPath = GenAPI.getDagPath(mesh)
        vertItr = om.MItMeshVertex(meshPath)
        
        pointArray = []
        
        while not vertItr.isDone():
            
            point = vertItr.position(om.MSpace.kWorld)
            pointArray.append([point.x,point.y,point.z])
            vertItr.next()
            
        return pointArray
    
    #returns symetrical vertex,works for symetrical mesh only
    #input MDagPath (mesh)
    #input python int (vertID)
    #input python list (mirror table)
    #output python int (vertID)
    @staticmethod
    def getSymVert(mesh,vertID,table = [-1,1,1]):
        
        meshFn = om.MFnMesh(mesh)
        polyItr = om.MItMeshPolygon(mesh)
        position = om.MPoint()
        
        meshFn.getPoint(vertID,position,om.MSpace.kWorld)
        
        mirroredPosition = om.MPoint(position.x * table[0],
                                     position.y * table[1],
                                     position.z * table[2])
        
        closestPoint = om.MPoint()
        
        util = om.MScriptUtil()
        indexPtr = util.asIntPtr()
        prevIndexPtr = util.asIntPtr()
        
        meshFn.getClosestPoint(mirroredPosition,closestPoint,om.MSpace.kWorld,indexPtr)
        indexInt = util.getInt(indexPtr)
        polyItr.setIndex(indexInt,prevIndexPtr)
        
        polyVerts = om.MIntArray()
        polyItr.getVertices(polyVerts)
        
        vectorLengths = []
        points = []
        
        for vert in polyVerts:
            
            fromPoint = om.MPoint()
            meshFn.getPoint(vert,fromPoint,om.MSpace.kWorld)
            
            vectorLengths.append(MeasuringTool.getVectorLengthBetween(fromPoint,mirroredPosition))
            points.append([fromPoint.x,fromPoint.y,fromPoint.z])
        
        closestVert = min(vectorLengths)
        vertIndex = vectorLengths.index(closestVert)
        
        return polyVerts[vertIndex],points[vertIndex]
            
    
    #input MDagPath (mesh)
    #input MPoint (position)
    #input python list (mirror table)
    #output python int (vertID)
    @staticmethod
    def getSymVertFromClosestPoint(mesh,point,table = [-1,1,1]):
        
        meshFn = om.MFnMesh(mesh)
        
        
        mirrorPosition = [(point.x * table[0]),
                          (point.y * table[1]),
                          (point.z * table[2])]
        
        
        mirroredPoint = om.MPoint(mirrorPosition[0],mirrorPosition[1],mirrorPosition[2])
        
        closestPoint = om.MPoint()
        
        indexUtil = om.MScriptUtil()
        indexPtr = indexUtil.asIntPtr()
        
        prevIndexPtrUtil = om.MScriptUtil()
        prevIndexPtr = prevIndexPtrUtil.asIntPtr()
        
        meshFn.getClosestPoint(mirroredPoint,closestPoint,om.MSpace.kWorld,indexPtr)

        polyItr = om.MItMeshPolygon(mesh)
        polyVerts = om.MIntArray()
        polyItr.setIndex(indexUtil.getInt(indexPtr),prevIndexPtr)
        polyItr.getVertices(polyVerts)
        
        vectorLengths = []
        points = []
        
        for vert in polyVerts:
            
            pointA = om.MPoint()
            meshFn.getPoint(vert,pointA,om.MSpace.kWorld)
            
            pointB = om.MPoint(mirrorPosition[0], mirrorPosition[1], mirrorPosition[2])
            
            vectorLengths.append(MeasuringTool.getVectorLengthBetween(pointA,pointB))
            points.append([pointA.x,pointA.y,pointA.z])
        
        closestVert = min(vectorLengths)
        vertIndex = vectorLengths.index(closestVert)
        
        return polyVerts[vertIndex],points[vertIndex]
 
    
    #creates a weight list based on vector length of deformation per vert
    #single loop...tranformations every iteration
    #input python string (geometry)
    #input python string (deformer transform node)
    #output python list (weights)
    @staticmethod
    def createWeigthListFromInfluence(mesh,transform):
        
        meshPath = GenAPI.getDagPath(mesh)
        transformPath = GenAPI.getDagPath(transform)
        
        transformFn = om.MFnTransform(transformPath)
        
        geoItr = om.MItGeometry(meshPath)
        
        weightList = []
        
        translateVector = om.MVector(1,0,0)
        
        while not geoItr.isDone():
            
            transformFn.set(om.MTransformationMatrix.identity)
            vertStartPos = geoItr.position(om.MSpace.kWorld)
            
            transformFn.translateBy(translateVector,om.MSpace.kWorld)
            vertEndPos = geoItr.position(om.MSpace.kWorld)
            
            length = MeasuringTool.getVectorLengthBetween(vertStartPos, vertEndPos)
            
            weightList.append(length)
            transformFn.set(om.MTransformationMatrix.identity)
            
            geoItr.next()
        
        return weightList
    
    
    #creates a weight list based on vector length of deformation per vert
    #input python string (geometry)
    #two loops...one transformation
    #input python string (deformer transform node)
    #output python list (weights)
    @staticmethod
    def createWeigthListFromInfluence2(mesh,transform):
        
        meshPath = GenAPI.getDagPath(mesh)
        transformPath = GenAPI.getDagPath(transform)
        
        transformFn = om.MFnTransform(transformPath)
        origTransform = transformFn.transformation()
        transformFn.set(om.MTransformationMatrix.identity)
        
        vertItr = om.MItMeshVertex(meshPath)
        
        startPoints = []
        
        translateVector = om.MVector(1,0,0)
        
        while not vertItr.isDone():
            
            vertStartPos = vertItr.position(om.MSpace.kWorld)
            startPoints.append(vertStartPos)
            vertItr.next()
        
        vertItr.reset()     
        transformFn.translateBy(translateVector,om.MSpace.kObject)
        
        weightList = []
        index = 0
        

        while not vertItr.isDone():
            
            vertEndPos = vertItr.position(om.MSpace.kWorld)
            length = MeasuringTool.getVectorLengthBetween(startPoints[index], vertEndPos)
            
            weightList.append(length)
        
            index += 1
            vertItr.next()
        
        transformFn.set(origTransform)

        return weightList
    
    #creates a weight list based on vector length of deformation per lattice point
    #input python string (latticeShape)
    #two loops...one transformation
    #input python string (deformer transform node)
    #output python list (weights)
    @staticmethod
    def createWeigthListFromTransformForLattice(latticeShape,transform):
        
        latPath = GenAPI.getDagPath(latticeShape)
        transformPath = GenAPI.getDagPath(transform)
        latticeFn = oma.MFnLattice(latPath)
        
        transformFn = om.MFnTransform(transformPath)
        origTransform = transformFn.transformation()
        transformFn.set(om.MTransformationMatrix.identity)
        
        translateVector = om.MVector(1,0,0)
        
        utilS = om.MScriptUtil()
        ptrS = utilS.asUintPtr()
        
        utilT = om.MScriptUtil()
        ptrT = utilT.asUintPtr()
        
        utilU = om.MScriptUtil()
        ptrU = utilS.asUintPtr()
        
        latticeFn.getDivisions(ptrS,ptrT,ptrU)
        
        SInt = utilS.getUint(ptrS)
        TInt = utilT.getUint(ptrT)
        UInt = utilU.getUint(ptrU)
        
        print SInt,TInt,UInt
        
        startPoints = []
        transformedPoints = []
        
        for s in range(SInt):
            for t in range(TInt):
                for u in range(UInt):
                    
                    point  = latticeFn.point(s,t,u)
                    startPoints.append(point)
            
        transformFn.translateBy(translateVector,om.MSpace.kObject)
        
        for s in range(SInt):
            for t in range(TInt):
                for u in range(UInt):
                    
                    point  = latticeFn.point(s,t,u)
                    transformedPoints.append(point)
        
        transformFn.set(origTransform)
        weightList = []
        
        for i in range(len(startPoints)):
            
            print startPoints[i].x,startPoints[i].y,startPoints[i].z
            print transformedPoints[i].x,transformedPoints[i].y,transformedPoints[i].z
            
            vector = startPoints[i] - transformedPoints[i]
            length = vector.length()
            weightList.append(length)

        return weightList
    
            
    #creates a weight list based on vector length of deformation per vert
    #input python string (geometry)
    #two loops...one transformation
    #input python string (deformer transform node)
    #output python list (weights)
    @staticmethod
    def createWeigthListFromTransform(mesh,transform):
        
        meshPath = GenAPI.getDagPath(mesh)
        transformPath = GenAPI.getDagPath(transform)
        
        transformFn = om.MFnTransform(transformPath)
        origTransform = transformFn.transformation()
        transformFn.set(om.MTransformationMatrix.identity)
        
        geoItr = om.MItGeometry(meshPath)
        origPositions = om.MPointArray()
        geoItr.allPositions(origPositions,om.MSpace.kWorld)
           
        translateVector = om.MVector(1,0,0)
        transformFn.translateBy(translateVector,om.MSpace.kWorld)
        
        geoItr = om.MItGeometry(meshPath)
        deltaPositions = om.MPointArray()
        geoItr.allPositions(deltaPositions,om.MSpace.kWorld)
        
        weightList = []
        for i in range(origPositions.length()):
            
            weight = MeasuringTool.getVectorLengthBetween(origPositions[i],deltaPositions[i])
            weightList.append(weight)
       
        transformFn.set(origTransform)
        return weightList
    
    #creates a weightList from mesh
    #input fromMesh (python string)
    #input toMesh (python string)
    #output weightList (python floating point list)
    @staticmethod
    def createWeightListFromMesh(fromMesh,toMesh):
        
        fromMeshPath = GenAPI.getDagPath(fromMesh)
        toMeshPath = GenAPI.getDagPath(toMesh)
        
        fromVertItr = om.MItMeshVertex(fromMeshPath)
        toVertItr = om.MItMeshVertex(toMeshPath)
        util = om.MScriptUtil()
        intPtr = util.asIntPtr()
        
        weightList = []

        progressWin = UILib.ProgressWin()
        progressWin.itr = fromVertItr.count()
        
        while not fromVertItr.isDone():
            
            
            toVertItr.setIndex(fromVertItr.index(),intPtr)
            
            currentFromVertPoint = fromVertItr.position()
            currentToVertPoint = toVertItr.position()
            
            length = MeasuringTool.getVectorLengthBetween(currentFromVertPoint, currentToVertPoint)
            weight = max(min(length, 1), 0)
            weightList.append(weight)
            
            progressWin.message = '%s.vtx[%i]'%(fromMesh, fromVertItr.index())
            progressWin.inc = fromVertItr.index()
            progressWin.progress()
            
            fromVertItr.next()
        
        progressWin.end()
        return weightList
    
    @staticmethod
    #creates a blank weightlist with specified value
    #input MDagPath (mesh)
    #input python float (weightValue)
    def createBlankWeightList(meshPath, value = 0):
        
        vertItr = om.MItMeshVertex(meshPath)
        
        weightList = []
        
        while not vertItr.isDone():
            
            weightList.append(value)
            vertItr.next()
        return weightList
    
    @staticmethod
    #method for retrieving weightlist from softSelection
    #output selectionList from richSelection (MSelectionList)
    #output components in pythonList ([MDagPath,MObject])
    #output weights in pythonList (pythonList)
    def createWeightListFromSoftSelection():
    
        richSelection = om.MRichSelection()
        om.MGlobal.getRichSelection(richSelection)
        
        selectionList = om.MSelectionList()
        
        richSelection.getSelection(selectionList)
        
        selectionItr = om.MItSelectionList(selectionList)
        
        componentObjects = []
        completeWeights = []
        
        while not selectionItr.isDone():
            
            component = om.MObject()
            dagPath = om.MDagPath()
            
            selectionItr.getDagPath(dagPath,component)
            
            componentObjects.append([dagPath,component])
            
            selectionItr.next()
            
        for components in componentObjects:
            
            print components[1].apiTypeStr()
            
            if components[1].apiTypeStr() == 'kMeshVertComponent' or components[1].apiTypeStr() == 'kCurveCVComponent':

                componentIndexFn = om.MFnSingleIndexedComponent(components[1])
                componentFn = om.MFnComponent(components[1])
                weights = []
                
                for i in range(componentIndexFn.elementCount()):
                    
                    mWeights = componentFn.weight(i)
                    weights.append(mWeights.influence())
                    
                completeWeights.append(weights)
                
            elif components[1].apiTypeStr() == 'kSurfaceCVComponent' or components[1].apiTypeStr() == 'kSubdivCVComponent':
                
                componentIndexFn = om.MFnDoubleIndexedComponent(components[1])
                componentFn = om.MFnComponent(components[1])
                weights = []
                
                for i in range(componentIndexFn.elementCount()):
                    
                    mWeights = componentFn.weight(i)
                    weights.append(mWeights.influence())
                    
                completeWeights.append(weights)
                
            elif components[1].apiTypeStr() == 'kLatticeComponent':
            
                componentIndexFn = om.MFnTripleIndexedComponent(components[1])
                componentFn = om.MFnComponent(components[1])
                
                weights = []
                
                for i in range(componentFn.elementCount()):
                    
                    mWeights = componentFn.weight(i)
                    weights.append(mWeights.influence())
                
                completeWeights.append(weights)
                
        return selectionList,componentObjects,completeWeights
              
    #Measuring Rigs...
    def nullMeasurementRig(self,name):
    
        #finds starting position and orientation
        startPos = MeasuringTool.getPointLocation(self.objectStart)
        startOrient = cmds.xform(self.objectStart,q = True, ws = True, rotation = True)
        
        #create parent group
        parentGroup = cmds.group(empty = True, name = '%s_Stretch_Group'%name)
         
        #create main null
        mainNull = cmds.group(empty = True, parent  = parentGroup,name = '%s_Main_Null'%name)
        
        #creates starting null
        startNull = cmds.group(empty = True,parent = parentGroup, name = '%s_Start_Null'%(name))
        
        #creates end null
        endNull = cmds.group(empty = True, parent = startNull, name = '%s_End_Null'%(name))
        
        cmds.move(startPos[0], startPos[1], startPos[2],parentGroup)
        cmds.rotate(startOrient[0],startOrient[1],startOrient[2],parentGroup)
        
        #finds end location
        pointDistance = self.getPointDistanceBetween()
        length = MeasuringTool.getVectorLength(pointDistance)   
        cmds.move(length,0,0,endNull, a = True, os = True)
        cmds.move(length,0,0,mainNull, a = True, os = True)
        
        #create constraints
        cmds.aimConstraint(mainNull,startNull,aim = (1,0,0))
        cmds.pointConstraint(mainNull,endNull)
        
        return [startNull,endNull,mainNull,parentGroup]
        
    #Aiming Mechanism....
    def aimRig(self,name):
    
        #query start location and orient
        startPosition = MeasuringTool.getPointLocation(self.objectStart)
        startOrient = MeasuringTool.getWorldEulerRotation(self.objectStart)
        
        
        #create locators
        aimLoc = cmds.spaceLocator(n = '%s_Aim_AimVector_Loc'%(name))
        upLoc = cmds.spaceLocator(n = '%s_Aim_UpVector_Loc'%(name))
        tgt = cmds.spaceLocator(n = '%s_Aim_Target_Loc'%(name))

        #create hierarchy
        posNull = cmds.group(aimLoc[0],upLoc[0],tgt[0],n = '%s_Aim_Pos_Null'%(name))

        cmds.move(startPosition[0],startPosition[1],startPosition[2],posNull)
        cmds.rotate(startOrient[0],startOrient[1],startOrient[2],posNull)
        
        #find vector length
        distance = self.getPointDistanceBetween()
        length = MeasuringTool.getVectorLength([distance[0],distance[1],distance[2]])
    
        #move and apply constraints to target
        cmds.move(length,0,0,tgt, a = True, os = True)
        cmds.move(0,0,10,upLoc[0],os = True)
        cmds.parentConstraint(self.objectStart,posNull)
        cmds.pointConstraint(self.objectEnd,tgt[0])
        cmds.aimConstraint(tgt,aimLoc, aimVector = (1,0,0), upVector = (0,0,1), worldUpType = "object", worldUpObject = upLoc[0])
    
    #Find U value at CV position...
    @staticmethod    
    def curveCVtoU (curveShape,curveCVIndex):
    
        curveFn = om.MFnNurbsCurve(GenAPI.getMObject(curveShape))
        mpoint = om.MPoint()
        curveFn.getCV(curveCVIndex,mpoint)
        uValue =  om.MScriptUtil()
        uValueNull = uValue.asDoublePtr()
        curveFn.closestPoint(mpoint,uValueNull)
        return uValue.getDouble(uValueNull)
    
    @staticmethod
    def pointOnCurveLoc(name,curve,count):
        
        normalValue = 1.0 / count
        uValue = 0
        
        for i in range(count):
            
            zero = ''
            if i > 10:
                zero = ''
                
            else:
                zero = '0'
                
            indexName = i + 1
            
                
            locator = cmds.spaceLocator(n = ('%s_%s%i_Loc'%(name,zero,indexName)))
            cmds.addAttr(locator[0],ln = "Offset" ,at = 'double')
            cmds.setAttr('%s.Offset'%locator[0], e = True, keyable = True)
            upLocator = cmds.spaceLocator(n = '%s_%s%i_MP_Up_Loc'%(name,zero,indexName))
            motionPath = cmds.createNode('motionPath', n =('%s_%s%i_MotionPath'%(name,zero,indexName)))
            cmds.connectAttr('%s.worldSpace[0]'%curve,'%s.geometryPath'%motionPath)
            
            cmds.connectAttr('%s.allCoordinates'%motionPath,'%s.translate'%locator[0])
            cmds.connectAttr('%s.rotate'%motionPath,'%s.rotate'%locator[0])
            cmds.connectAttr('%s.rotateOrder'%motionPath, '%s.rotateOrder'%locator[0])
            
            
            cmds.setAttr('%s.fractionMode'%motionPath,1)
            cmds.setAttr('%s.frontAxis'%motionPath,1)
            cmds.setAttr('%s.upAxis'%motionPath,1)
            cmds.setAttr('%s.worldUpType'%motionPath,1)
            cmds.setAttr('%s.fractionMode'%motionPath,1)
            
            cmds.setAttr('%s.uValue'%motionPath, uValue)
            cmds.setAttr('%s.worldUpType'%motionPath, 2)
            cmds.setAttr ('%s.frontAxis'%motionPath,0)
            cmds.setAttr ('%s.upAxis'%motionPath,2)
            
            offsetMD = cmds.createNode('multiplyDivide', n = '%s_0%i_Offset_MD'%(locator[0],indexName))
            cmds.connectAttr('%s.Offset'%locator[0],'%s.input1X'%offsetMD)
            cmds.setAttr('%s.input2X'%offsetMD, 0.01)
            offsetPMA = cmds.createNode('plusMinusAverage', n = '%s_0%i_Offset_PMA'%(locator[0],indexName))
            cmds.connectAttr('%s.outputX'%offsetMD,'%s.input1D[0]'%offsetPMA )
            cmds.setAttr('%s.input1D[1]'%offsetPMA,uValue)
            cmds.connectAttr('%s.output1D'%offsetPMA, '%s.uValue'%motionPath)
            
            
            locPos = cmds.xform(locator[0], q = True, ws = True, translation = True)
            locOrient = cmds.xform(locator[0], q = True, ws = True, rotation = True)
            
            cmds.setAttr ('%s.worldUpVectorX'%motionPath,0)
            cmds.setAttr ('%s.worldUpVectorY'%motionPath,0)
            cmds.setAttr ('%s.worldUpVectorZ'%motionPath,1)
            cmds.connectAttr('%s.worldMatrix[0]'%upLocator[0], '%s.worldUpMatrix'%motionPath)
            
            nullGroup = cmds.group(empty = True, n = '%s_Group'%upLocator[0])
            cmds.move(locPos[0], locPos[1],locPos[2],nullGroup)
            cmds.rotate(locOrient[0],locOrient[1],locOrient[2], nullGroup)
            #cmds.connectAttr('%s.output1D'%offsetPMA, '%s.translateX'%upLocator[0])
            
            cmds.parent(upLocator[0], nullGroup,r = True)
            cmds.move(0,0,10,upLocator[0], a = True, os = True)
            
            cmds.group(locator[0],nullGroup,n = '%s_0%i_MP_Loc_Group'%(name,indexName))
            
            uValue += normalValue
            
    
    @staticmethod
    def pointOnCurveLocCV(name,curve):
        
        if not cmds.nodeType(curve) == 'shape':
            
            curve = cmds.listRelatives(curve, type = 'shape')[0]
            
        mobject = GenAPI.getMObject(curve)
        iterCVs = om.MItCurveCV(mobject)
        
        while not iterCVs.isDone():

            index = iterCVs.index()
            nameIndex = index + 1            
            moPath = cmds.createNode('motionPath')
            
            moPath = cmds.createNode('motionPath',n = '%s_0%i_MotionPath'%(name,nameIndex))
            cmds.connectAttr('%s.worldSpace[0]'%curve,'%s.geometryPath'%moPath)
            
            locator = cmds.spaceLocator(n = '%s_0%i_MP_Loc'%(name,nameIndex))
            cmds.addAttr(locator[0],ln = "Offset" ,at = 'double')
            cmds.setAttr('%s.Offset'%locator[0], e = True, keyable = True)
            upLocator = cmds.spaceLocator(n = '%s_0%i_MP_Up_Loc'%(name,nameIndex))
                        
            cmds.connectAttr('%s.allCoordinates'%moPath,'%s.translate'%locator[0])
            cmds.connectAttr('%s.rotate'%moPath,'%s.rotate'%locator[0])
            cmds.connectAttr('%s.rotateOrder'%moPath, '%s.rotateOrder'%locator[0])
            
            uValue = MeasuringTool.curveCVtoU(curve,index)
            cmds.setAttr('%s.uValue'%moPath, uValue)
            cmds.setAttr('%s.worldUpType'%moPath, 2)
            cmds.setAttr ('%s.frontAxis'%moPath,0)
            cmds.setAttr ('%s.upAxis'%moPath,2)
            
            offsetMD = cmds.createNode('multiplyDivide', n = '%s_0%i_Offset_MD'%(locator[0],nameIndex))
            cmds.connectAttr('%s.Offset'%locator[0],'%s.input1X'%offsetMD)
            cmds.setAttr('%s.input2X'%offsetMD, 0.1)
            offsetPMA = cmds.createNode('plusMinusAverage', n = '%s_0%i_Offset_PMA'%(locator[0],nameIndex))
            cmds.connectAttr('%s.outputX'%offsetMD,'%s.input1D[0]'%offsetPMA )
            cmds.setAttr('%s.input1D[1]'%offsetPMA,uValue)
            cmds.connectAttr('%s.output1D'%offsetPMA, '%s.uValue'%moPath)
            
            
            locPos = cmds.xform(locator[0], q = True, ws = True, translation = True)
            locOrient = cmds.xform(locator[0], q = True, ws = True, rotation = True)
            
            cmds.setAttr ('%s.worldUpVectorX'%moPath,0)
            cmds.setAttr ('%s.worldUpVectorY'%moPath,0)
            cmds.setAttr ('%s.worldUpVectorZ'%moPath,1)
            cmds.connectAttr('%s.worldMatrix[0]'%upLocator[0], '%s.worldUpMatrix'%moPath)
            
            nullGroup = cmds.group(empty = True, n = '%s_Group'%upLocator[0])
            cmds.move(locPos[0], locPos[1],locPos[2],nullGroup)
            cmds.rotate(locOrient[0],locOrient[1],locOrient[2], nullGroup)
            
            cmds.parent(upLocator[0], nullGroup,r = True)
            cmds.move(0,0,10,upLocator[0], a = True, os = True)
            
            cmds.group(locator[0],nullGroup,n = '%s_0%i_MP_Loc_Group'%(name,nameIndex))
            
            iterCVs.next()
    
    @staticmethod       
    def pointOnCurveNearLoc(name,curve,controlAttr):

        zero = ''
        i = 0
        
        selection = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(selection)
        selectionItr = om.MItSelectionList(selection )
        
        #iterate through selection
        while not selectionItr.isDone():

            if i<=9:
                zero = '0'
                
            else:
                zero = ''
            
            nameIndex = i + 1
            objPath = om.MDagPath()
            selectionItr.getDagPath(objPath)
            
            transformFn = om.MFnTransform(objPath)
            pos = transformFn.getTranslation(om.MSpace.kWorld)
            mpoint = om.MPoint(pos)
            
            curveFn = om.MFnNurbsCurve(GenAPI.getMObject(curve))
            util =  om.MScriptUtil()
            uValueNull = util.asDoublePtr()
            curveFn.closestPoint(mpoint,uValueNull,om.MSpace.kWorld)
            
            uValue = util.getDouble(uValueNull)
            
            locator = cmds.spaceLocator(n = '%s_%s%i_Loc'%(name,zero,nameIndex))
            cmds.addAttr(locator[0],ln = "Offset" ,at = 'double')
            cmds.setAttr('%s.Offset'%locator[0], e = True, keyable = True)
            motionPath = cmds.createNode('motionPath',n = '%s_%s%i_MotionPath'%(name,zero,nameIndex))
            cmds.connectAttr('%s.worldSpace[0]'%curve,'%s.geometryPath'%motionPath)
                    
            cmds.connectAttr('%s.allCoordinates'%motionPath,'%s.translate'%locator[0])
            cmds.connectAttr('%s.rotate'%motionPath,'%s.rotate'%locator[0])
            cmds.connectAttr('%s.rotateOrder'%motionPath, '%s.rotateOrder'%locator[0])
            
            cmds.setAttr('%s.fractionMode'%motionPath,1)
            cmds.setAttr('%s.frontAxis'%motionPath,1)
            cmds.setAttr('%s.upAxis'%motionPath,1)
            cmds.setAttr('%s.worldUpType'%motionPath,1)
            cmds.setAttr('%s.fractionMode'%motionPath,0)
            
            cmds.setAttr('%s.uValue'%motionPath, uValue)
            cmds.setAttr('%s.worldUpType'%motionPath, 2)
            cmds.setAttr ('%s.frontAxis'%motionPath,0)
            cmds.setAttr ('%s.upAxis'%motionPath,2)
            
            sliderMD = cmds.createNode('multiplyDivide', n = '%s_%s%i_Slider_MD'%(name,zero,nameIndex))
            cmds.connectAttr(controlAttr,'%s.input1X'%sliderMD)
            cmds.setAttr('%s.input2X'%sliderMD, 0.01)
            sliderPMA = cmds.createNode('plusMinusAverage', n = '%s_%s%i_Slider_PMA'%(name,zero,nameIndex))
            cmds.connectAttr('%s.outputX'%sliderMD,'%s.input1D[0]'%sliderPMA )
            cmds.setAttr('%s.input1D[1]'%sliderPMA,uValue)
            
            offsetMD = cmds.createNode('multiplyDivide', n = '%s_%s%i_Slider_MD'%(name,zero,nameIndex))
            cmds.connectAttr('%s.Offset'%locator[0],'%s.input1X'%offsetMD )
            cmds.setAttr('%s.input2X'%offsetMD, 0.001)
            offsetPMA = cmds.createNode('plusMinusAverage', n = '%s_%s%i_Offset_PMA'%(name,zero,nameIndex))
            cmds.connectAttr('%s.outputX'%offsetMD,'%s.input1D[0]'%offsetPMA )
            cmds.connectAttr('%s.output1D'%sliderPMA,'%s.input1D[1]'%offsetPMA )
            
            cmds.connectAttr('%s.output1D'%offsetPMA, '%s.uValue'%motionPath)
        
        
            selectionItr.next()
            
    
                       
    #Creates an aim constraint representing the vertex normal
    @staticmethod      
    def getVertNormal(geo,vert,name):

        #find dag path
        polyPath = GenAPI.getDagPath(geo)
        vertexObject = GenAPI.getComponentsFromList(geo,[vert])

        #create vector instance for vert iterator
        vertNormalVector = om.MVector()

        vertIterator = om.MItMeshVertex(polyPath,vertexObject)
        
        #MIntArray for face indexes
        faceIndexArray = om.MIntArray()
        vertIterator.getNormalIndices(faceIndexArray)

        faceIndexList = []

        for i in faceIndexArray:
            faceIndexList.append(i)

        #store normal vector in MVector instance
        vertIterator.getNormal(vertNormalVector,faceIndexList[0],om.MSpace.kObject)
        vertPos = vertIterator.position(om.MSpace.kWorld)

        #create new vectors form queries
        v1 = om.MVector(vertNormalVector.x,vertNormalVector.y,vertNormalVector.z)
        v2 = om.MVector(vertPos.x,vertPos.y,vertPos.z)
        #add vector1 to vector2 for offset
        v3 = v1 + v2

        #create locators
        vertLoc = cmds.spaceLocator(n = '%s_VertPos_Loc'%(name))
        normalVectorLoc = cmds.spaceLocator(n = '%s_VertNormalVec_Loc'%(name))
        tempLoc = cmds.spaceLocator()

        #move locators into position
        cmds.move(v1.x,v1.y,v1.z,tempLoc[0],ws = True)
        cmds.move(v2.x,v2.y,v2.z,vertLoc[0],ws = True)
        cmds.move(v3.x,v3.y,v3.z,normalVectorLoc[0],ws = True)

        #aim locator2 at locator1
        cmds.aimConstraint(normalVectorLoc,vertLoc, aimVector = (1,0,0), upVector = (0,1,0))
