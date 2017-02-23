'''
Created on Jul 11, 2013

@author: Bill
'''
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.mel as mel
import re

import GenAPI

'''string functions'''
def renamer(newName):
    selection = cmds.ls(sl = True,ap = True)
    selectionCount = len(selection)
    
    spaceCount = newName.count('*')
    newNameSpt = newName.split('*')
    
    i = 1
    numberStringArray = []
    while i <= selectionCount:
        
        stringNumber = str(i)
        numberStringArray.append(stringNumber)
        i += 1
    newNumberStringArray  = []  
    for element in numberStringArray:
            
        while element.__len__() < spaceCount:
            element = '%i%s'%(0,element)
        
        newNumberStringArray.append(element)
    
    i = 0    
    for obj in selection:
    
        cmds.rename(obj,'%s%s%s'%(newNameSpt[0],newNumberStringArray[i],newNameSpt[-1]))
        i += 1

def cutit(text,pattern):
    
    match = re.search(pattern, text)
    s = match.start()
    e = match.end() #@UnusedVariable

    return text[0:s]

'''Channel Box Functions'''

def moveAttrUp(direction = 'up'):
    
    currentObj = cmds.ls(sl = True)[0]
    customAttrs = cmds.listAttr(ud = True)
    currentAttr = cmds.channelBox('mainChannelBox',q = True,sma = True)
    customAttrCount = len(customAttrs)
    currentAttrIndexStart = customAttrs.index(currentAttr[0])
    currentAttrIndexEnd = customAttrs.index(currentAttr[-1])
    attrsAbove = customAttrs[0:currentAttrIndexStart] #@UnusedVariable
    attrsBelow = customAttrs[currentAttrIndexEnd+1:customAttrCount]
    
    print attrsBelow
    print attrsAbove
    
    if direction == 'up':
        cmds.deleteAttr(currentObj,attribute = customAttrs[currentAttrIndexStart-1])
        cmds.undo()
                
        for attr in attrsBelow:
            
            cmds.deleteAttr(currentObj,attribute = attr)
            cmds.undo()
            
    if direction == 'down':
        
        for attr in currentAttr:
            cmds.deleteAttr(currentObj,attribute = attr)
            cmds.undo()
        
        for attr in attrsBelow:
            
            if attr == attrsBelow[0]:
                pass
                
            else:
                cmds.deleteAttr(currentObj,attribute = attr)
                cmds.undo()
                
'''rigging functions'''
def buildRibbonSurface(locators,name = '',close = False,vector = [1,0,0],width = 10):

    lineCrvs = []
    
    for locator in locators:
    
        pos = cmds.xform(locator,q = True,ws = True,rp = True)
        
        posVector = om.MVector(pos[0],pos[1],pos[2])
        
        inverseWidth = width * -1
        
        translateVectorForward = om.MVector(vector[0] * width,vector[1] * width,vector[2] * width)
        translateVectorBackward = om.MVector((vector[0] * inverseWidth),(vector[1] * inverseWidth),(vector[2] * inverseWidth))
        
        startTransformationMatrix = om.MTransformationMatrix()
        startTransformationMatrix.setTranslation(posVector,om.MSpace.kWorld)
        startTransformationMatrix.addTranslation(translateVectorForward,om.MSpace.kObject)
        startPosVector = startTransformationMatrix.getTranslation(om.MSpace.kWorld)
        
        endTransformationMatrix = om.MTransformationMatrix()
        endTransformationMatrix.setTranslation(posVector,om.MSpace.kWorld)
        endTransformationMatrix.addTranslation(translateVectorBackward,om.MSpace.kObject)
        endPosVector = endTransformationMatrix.getTranslation(om.MSpace.kWorld)
        
        startPos = [startPosVector.x,startPosVector.y,startPosVector.z]
        endPos = [endPosVector.x,endPosVector.y,endPosVector.z]
        lineCrv = cmds.curve(d = 1,p = (startPos,endPos))
        lineCrvs.append(lineCrv)
        
    ribbonOrig = cmds.loft(lineCrvs,ch = 1,u = 1,c = close,ar = 1,d = 3,ss = 1,rn = 0 ,po = 0, rsn = True,n = '%s_Surface'%name)
    ribbonRebuild = cmds.rebuildSurface(ribbonOrig[0],ch = 1,rpo = 1,rt = 0,end = 1,kr = 0,kcp = 1,kc = 0,su = 8,du = 1,sv = 2,dv = 3,tol = 0.01,fr = 0, dir = 2)
    
    ribbon = []
    
    shape = cmds.listRelatives(ribbonRebuild[0], type = 'shape')[0]
    ribbon.append(ribbonRebuild[0])
    ribbon.append(shape)
    cmds.delete(ribbonOrig[0],ch = True)
    cmds.delete(lineCrvs)
    return ribbon
                
def makeRivets(**kwargs):

    iterations = kwargs.get('iterations')
    surfaceName = kwargs.get('surfaceName')
    nodeNames = kwargs.get('nodeNames')
    closedSurface = kwargs.get('closedSurface',False)
    normalVector = kwargs.get('normalVector',(0,1,0))
    tangentVector = kwargs.get('tangentVector',(-1,0,0))

    if closedSurface:
        iterationsNum = iterations + 0.0
    else:
        iterationsNum = iterations - 1.0
    
    i = 0
    vValue = 1.0
    
    group = cmds.group(n = '%s_Rivet_Grp'%nodeNames, empty = True)

    rivets = []
    
    while(i < iterations):

        if i >= 9:
            zero = ''
        else:
            zero = '0'
        
        vValue = i/(iterationsNum); 
        nodes = cmds.kSurfaceRivetCmd(s = surfaceName, u = 0.5, v = vValue, nv = normalVector, tv = tangentVector)
        cmds.rename(nodes[0],('%s_%s%i_Rivet'%(nodeNames,zero,(i+1))))
        cmds.rename(nodes[1],('%s_Rivet_%s%i_Loc'%(nodeNames,zero,(i+1))))
        
        nodes[0] = '%s_%s%i_Rivet'%(nodeNames,zero,(i+1))
        nodes[1] = '%s_Rivet_%s%i_Loc'%(nodeNames,zero,(i+1))
        
        rivets.append(nodes[0])
        cmds.parent(nodes[1],group)
        
        i += 1
    return rivets

def deleteRivets():

    rivets = cmds.ls(type = 'kSurfaceRivetNode')
    rivets.remove('L_Eye_LookAt_Rivet')
    rivets.remove('R_Eye_LookAt_Rivet')
    rivets.remove('L_Eye_Spec_Rivet')
    rivets.remove('R_Eye_Spec_Rivet')
    
    for rivet in rivets:
        
        uValue = cmds.getAttr('%s.uValue'%rivet)
        vValue = cmds.getAttr('%s.vValue'%rivet)
        
        surfaceConnection = cmds.connectionInfo('%s.input'%rivet,sfd = True)
        
        follicle = cmds.createNode('follicle')
        follicleTransform = cmds.listRelatives(follicle,parent = True)[0]
        cmds.connectAttr('%s.outTranslate'%follicle,'%s.translate'%follicleTransform)
        cmds.connectAttr('%s.outRotate'%follicle,'%s.rotate'%follicleTransform)
        
        cmds.setAttr('%s.parameterU'%follicle,uValue)
        cmds.setAttr('%s.parameterV'%follicle,vValue)
        cmds.connectAttr(surfaceConnection, '%s.inputSurface'%follicle)
        
        name = ('%s_Follicle')%(rivet.split('_Rivet')[0])
        cmds.rename(follicleTransform,name)
        
        rivetLocatorConnection = cmds.connectionInfo('%s.outTranslation'%rivet,dfs = True)[0]
        rivetLocator = rivetLocatorConnection.split('.')[0]
        
        locatorGrp = cmds.listRelatives(rivetLocator,parent = True)[0]
        
        constraintConnection = cmds.connectionInfo('%s.parentMatrix[0]'%rivetLocator,dfs = True)[0]
        constraint = constraintConnection.split('.')[0]
        
        targtConnection = cmds.connectionInfo('%s.constraintTranslateX'%constraint,dfs = True)[0]
        target = targtConnection.split('.')[0]
        
        cmds.delete(constraint)
        cmds.parentConstraint(name,target, mo = True)
        
        cmds.delete(rivet)
        cmds.delete(rivetLocator)
        
        cmds.parent(name, locatorGrp)   
        
def makeFloatingJoints(locators = [],name = ''):
    
    joints = []
    jointsGroup = cmds.group(n = '%s_Jnt_Grp'%name,empty = True)
    
    i = 1
    
    for locator in locators:
        
        zeroString = '0'
        
        if i > 9:
            zeroString = ''
        
        group = cmds.group(empty = True, name = '%s_%s%i_Grp'%(name,zeroString,i))
        cmds.parentConstraint(locator,group)
        cmds.select(cl = True)
        joint = cmds.joint(name = '%s_Floating_%s%i_Jnt'%(name,zeroString,i))
        cmds.parent(joint,group)
        cmds.move(0,0,0,joint,os = True) 
        cmds.setAttr('%s.jointOrientX'%joint,0)
        cmds.setAttr('%s.jointOrientY'%joint,0)
        cmds.setAttr('%s.jointOrientZ'%joint,0)
        joints.append(joint)
        cmds.parent(group,jointsGroup)
        
        i += 1
        
    return joints

def orientJoint(joint = '',aimAxis = (1,0,0),upAxis = (0,1,0)):
    
    try:
        child = cmds.listRelatives(joint,children = True)[0]
        pos = cmds.xform(child,q = True,ws = True,rp = True)
        transform = cmds.group(empty = True) 
        cmds.move(pos[0],pos[1],pos[2],transform)
        cmds.parent(child,transform)
        cmds.setAttr('%s.jointOrient'%joint,0,0,0)
        aimConstriant = cmds.aimConstraint(child,joint,aim = aimAxis,u = upAxis,wut = 'scene')[0]
        jointOrient = cmds.xform(joint,q = True,os = True,rotation = True)
        cmds.setAttr('%s.jointOrient'%joint,jointOrient[0],jointOrient[1],jointOrient[2])
        cmds.delete(aimConstriant)
        cmds.parent(child,joint)
        cmds.delete(transform)
        cmds.select(joint)
    except:
        cmds.setAttr('%s.jointOrient'%joint,0,0,0)
    
       

def createDistanceNode(**kwargs):
    
    startTransform = kwargs.get('start')
    endTransform = kwargs.get('end')
    name = kwargs.get('name')
    
    startPos = cmds.xform(startTransform,q = True,ws = True, translation = True)
    endPos = cmds.xform(endTransform,q = True,ws = True, translation = True)
    
    group = cmds.group(empty = True, name = '%s_Locator_Group'%name)
    startGroup = cmds.group(empty = True, name = '%s_Start_Locator_Group'%name)
    endGroup = cmds.group(empty = True, name = '%s_End_Locator_Group'%name)
    
    cmds.parent(startGroup,group)
    cmds.parent(endGroup,group)
    
    startLocator = cmds.spaceLocator(name = '%s_Start_Locator'%name)[0]
    endLocator = cmds.spaceLocator(name = '%s_End_Locator'%name)[0]
    
    cmds.parent(startLocator,startGroup)
    cmds.parent(endLocator,endGroup)
    
    cmds.move(startPos[0],startPos[1],startPos[2],startLocator,ws = True)
    cmds.move(endPos[0],endPos[1],endPos[2],endLocator,ws = True)
    
    lengthNode = cmds.createNode('kLengthNode',name = '%s_Length'%name)
    
    cmds.connectAttr('%s.worldMatrix[0]'%startLocator, '%s.startWorldMatrix'%lengthNode)
    cmds.connectAttr('%s.parentInverseMatrix[0]'%startLocator, '%s.startParentInverseMatrix'%lengthNode)
    
    cmds.connectAttr('%s.worldMatrix[0]'%endLocator, '%s.endWorldMatrix'%lengthNode)
    cmds.connectAttr('%s.parentInverseMatrix[0]'%endLocator, '%s.endParentInverseMatrix'%lengthNode)
    
    return lengthNode
    
        
'''deformer scripts'''
def reorderHistory (listOrder,geos):
    for geo in geos:
        
        blendShapes = []
        
        clusters = []
        mainClusters = []
        
        ffds = []
        skinClusters = []
        wires = []
        
        nonLinears = []
        bends = []
        squashes = []
        
        sculpts = [] 

        if cmds.nodeType(geo) == 'transform':
            geo = cmds.listRelatives(type = 'shape')
        
        history = cmds.listHistory(geo,il = 2,pdo = 1)
        for input in history:
            
            if cmds.nodeType(input) == 'blendShape':
                blendShapes.append(input)
                
            if cmds.nodeType(input) == 'cluster':
                clusters.append(input)
                
            if cmds.nodeType(input) == 'ffd':
                ffds.append(input)

            if cmds.nodeType(input) == 'wire':
                wires.append(input)
                
            if cmds.nodeType(input) == 'nonLinear':
                nonLinears.append(input)
                
            if cmds.nodeType(input) == 'sculpt':
                sculpts.append(input)
                
            if cmds.nodeType(input) == 'skinCluster':
                skinClusters.append(input)
       
        for cluster in clusters[:]:
               
            try:
                match = re.search('Main',cluster)
                s = match.start()
                mainClusters.append(cluster)
                clusters.remove(cluster)
            except:
                pass

        for deformer in nonLinears[:]:
           
            try:
                match = re.search('squash',deformer.lower())
                s = match.start()
                squashes.append(deformer)
                nonLinears.remove(deformer)
                print 'added squash'
            except:
                try:
                    match = re.search('bend',deformer.lower())
                    s = match.start()
                    bends.append(deformer)
                    nonLinears.remove(deformer)
                    print 'added bend'
                except:
                    pass

        blendShapes.sort()       
        clusters.sort()
        mainClusters.sort()
        ffds.sort()
        skinClusters.sort()
        wires.sort()
        nonLinears.sort()
        bends.sort()
        squashes.sort()
        sculpts.sort()
        
        allDeformers = {}
        allDeformers['blendshapes'] = blendShapes
        allDeformers['clusters'] = [mainClusters,clusters]
        allDeformers['ffds'] = ffds
        allDeformers['skinClusters'] = skinClusters
        allDeformers['wires'] = wires
        allDeformers['nonLinears'] = [bends,squashes,nonLinears]
        allDeformers['sculpts'] = sculpts
        
        orderedDeformers = []
        
        for i in range(len(listOrder)):
              
            if listOrder[i] == 'clusters':
                
                for set in allDeformers['clusters']:
                    for deformer in set:
                        orderedDeformers.append(deformer)
        
            elif listOrder[i] == 'nonLinears':
                
                for set in allDeformers['nonLinears']:
                    for deformer in set:
                        orderedDeformers.append(deformer)
        
            else:
                deformers = allDeformers.get(listOrder[i])
                if not deformers == None:
                    for deformer in deformers:
                        orderedDeformers.append(deformer)  
        
        print orderedDeformers            
        for i in range(len(orderedDeformers)-1):
            print (orderedDeformers[i],orderedDeformers[i-1])
            try:
                cmds.reorderDeformers(orderedDeformers[i],orderedDeformers[i+1],geo)
                print 'reodered'
            except:
                pass
            
'''Misc stuff '''  
def zeroOut():
    
    sel = cmds.ls(sl = True)
    
    for obj in sel:
    
        cmds.move(0,0,0,obj,os = True)
        cmds.rotate(0,0,0,obj,os = True)
        cmds.scale(1,1,1,obj,os = True) 

def switchInfluece(): 

    obj = cmds.ls(sl = True)[0]
    
    history = cmds.listHistory(obj,pdo = 1, il = 2)
    skinCluster = ''
    
    for node in history:
        if cmds.nodeType(node) == 'skinCluster':
            skinCluster = node
    

    joints = cmds.skinCluster(skinCluster,q = True,inf = True)
    
    unlockedJoints = []
    
    print joints
    
    for joint in joints:
        lock = cmds.getAttr('%s.liw'%joint)

        if not lock:
            unlockedJoints.append(joint)
    
    currentItem = cmds.artAttrSkinPaintCtx('artAttrSkinPaintCtx1',q = True,inf = True)
    try:
        i = unlockedJoints.index(currentItem)
    except:
        i = 0    
    i += 1
    if i == len(unlockedJoints):
        i = 0
    
    print 'unlocked:',unlockedJoints
    
    cmds.artAttrSkinPaintCtx('artAttrSkinPaintCtx1',e = True,inf = unlockedJoints[i])
    
    mel.eval('artSkinInflListChanging %s 0'%currentItem)
    mel.eval('artSkinInflListChanging %s 1'%unlockedJoints[i])
    mel.eval('artSkinInflListChanged artAttrSkinPaintCtx')
    
    om.MGlobal.displayInfo('Paint Weights on %s'%unlockedJoints[i])

def setShapeDisplay():
    sel = cmds.ls(sl = True)
    
    for obj in sel:
        shapes = cmds.listRelatives(obj,type = 'shape')
        
        for shape in shapes:
            cmds.setAttr('%s.divisionsU'%shape,0)
            cmds.setAttr('%s.divisionsV'%shape,0)
            
            
def createSmoothProxyGeo(selection):
    
    for mesh in selection:
        if not cmds.objExists('SmoothProxy_Geo_Grp'):
            grp = cmds.group(empty = True)
            cmds.parent(grp,'Geometry')
            cmds.rename(grp,'SmoothProxy_Geo_Grp')
            
        proxyNode = cmds.createNode('polySmoothProxy')
        newMesh = cmds.duplicate(mesh)
        cmds.parent(newMesh[0],'SmoothProxy_Geo_Grp')
        meshShape = cmds.listRelatives(mesh,type = 'shape')[0]
        newMeshShape = cmds.listRelatives(newMesh,type = 'shape')[0]
        
        cmds.connectAttr('%s.outMesh'%meshShape,'%s.inputPolymesh'%proxyNode)
        cmds.connectAttr('%s.output'%proxyNode,'%s.inMesh'%newMeshShape)
        
        newMeshName = '%s_SmoothProxy_Geo'%newMesh[0].split('_Geo')[0]
        cmds.setAttr('%s.exponentialLevel'%proxyNode,0)
        
        cmds.rename(newMesh,newMeshName)
        
def createFollicle():

    sel = cmds.ls(sl = True,fl = True)
    
    for i in range(len(sel)):
    
        surfaceTransform = sel[i].split('.')[0]
        surfaceShape = cmds.listRelatives(surfaceTransform,type = 'shape')[0]
        uvPoint = sel[i]
        
        uvValues = cmds.polyEditUV(uvPoint,query = True)
        uValue = uvValues[0]
        vValue = uvValues[1]
        
            
        follicle = cmds.createNode('follicle')
        follicleTransform = cmds.listRelatives(follicle,parent = True)[0]
        cmds.connectAttr('%s.outTranslate'%follicle,'%s.translate'%follicleTransform)
        cmds.connectAttr('%s.outRotate'%follicle,'%s.rotate'%follicleTransform)
        
        cmds.setAttr('%s.parameterU'%follicle,uValue)
        cmds.setAttr('%s.parameterV'%follicle,vValue)
        
        cmds.connectAttr('%s.outMesh'%surfaceShape, '%s.inputMesh'%follicle,f = True)
        cmds.connectAttr('%s.worldMatrix[0]'%surfaceShape, '%s.inputWorldMatrix'%follicle)
        
def getOffset(worldNode = ''):
    nameSpaceList = worldNode.rpartition(':')
    nameSpace = ''
    
    if len(nameSpaceList) > 1:
        nameSpace = nameSpaceList[0]
    
    worldChildren = cmds.listRelatives(worldNode,children = True)
    
    
    for grp in worldChildren:
        
        ctrlGrp = ''
        
        if grp == '%s:Controllers'%nameSpace:
            ctrlGrp = grp
            ctrlGrpChildren = cmds.listRelatives(ctrlGrp,children = True)
            
            offset = ''
            
            for ctrlGrp in ctrlGrpChildren:
                
                if ctrlGrp == '%s:Offset'%nameSpace:
                    
                    offset = ctrlGrp
                    return offset
                
        
def setConstraint(control = '',worldNodes = []):
    
    offsets = []
    
    for node in worldNodes:
        offsetNode = getOffset(node)
        if not offsetNode == None:
            offsets.append(offsetNode)
            
        else:
            om.MGlobal.displayWarning('Cannot find offset for %s'%node)
        
    print offsets
    
    for offset in offsets:
        
        cmds.parentConstraint(control,offset, mo = True)
        cmds.scaleConstraint(control,offset, mo = True)
        
def createTargetRig(name):
    
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
    
def getRootJoint(joint):
    
    '''method for returning root joint in hierarchy'''
    jointObject = GenAPI.getMObject(joint)
    nodeFn = om.MFnDagNode(jointObject)
    
    while not nodeFn.parent(0).apiType() == om.MFn.kWorld:
        if nodeFn.parent(0).apiType() == om.MFn.kJoint:
            nodeFn.setObject(nodeFn.parent(0))
        else:
            break
        
    dagPath = om.MDagPath()
    nodeFn.getPath(dagPath)
    return dagPath.partialPathName()
    
def getJointHeirarchy(joint):
    
    jointObject = GenAPI.getMObject(joint)
    nodeFn = om.MFnDagNode(jointObject)
    
    joints = []
    
    while not nodeFn.child(0).apiType() == om.MFn.kJoint:
        nodeFn.setObject(nodeFn.parent(0))
        dagPath = om.MDagPath()
        nodeFn.getPath(dagPath)
        joints.append(dagPath.partialPathName())
        
    return joints
    
    
def createPocLoc(crv = '',name = '',count = 0):
    
    inc = 1.0/count
    
    newCrv = cmds.duplicate(crv)[0]
    newCrvName = '%s_Master_Crv'%name
    cmds.rename(newCrv,newCrvName)
    
    locGrp = cmds.group(empty = True, name = '%s_Loc_Grp'%name)
    pocLoc = []
    mpNodes = []
    
    uValue = 0.0
    
    for i in range(count+1):
       
        mp = cmds.createNode('motionPath', name = '%s_DynIK_%s_MP'%(name,str(i+1).zfill(2)))
        cmds.setAttr('%s.fractionMode'%mp,1)
        try:
            cmds.setAttr('%s.uValue'%mp,uValue)
        except:
            cmds.setAttr('%s.uValue'%mp,1.0)
        cmds.connectAttr('%s.worldSpace[0]'%newCrvName,'%s.geometryPath'%mp)
        loc = cmds.spaceLocator(name = '%s_%s_Loc'%(name,str(i+1).zfill(2)))[0]
        cmds.connectAttr('%s.allCoordinates'%mp,'%s.translate'%loc)
        cmds.parent(loc,locGrp)
        
        pocLoc.append(loc)
        mpNodes.append(mp)
        
        uValue+=inc
        
    return pocLoc,mpNodes