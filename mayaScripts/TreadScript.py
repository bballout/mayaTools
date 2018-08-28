'''
Created on Dec 14, 2013

@author: Bill
'''
import maya.cmds as cmds
import maya.OpenMaya as om
import MayaScripts
reload(MayaScripts)

cmds.loadPlugin('surfaceRivet.py',qt = True)

def build(**kwargs):
    
    
    selection = cmds.ls(sl = True)
    selection.sort()
    name =  kwargs.get('name','TempName')
    vector = kwargs.get('vector',[1,0,0])
    width = kwargs.get('width',1)
    normalVector = kwargs.get('normalVector',[0,1,0])
    tangentVector = kwargs.get('tangentVector',(-1,0,0))
    close = kwargs.get('close',True)

    locators = []
    
    for obj in selection:

        try:
            cluster = cmds.cluster(obj)
            pos = cmds.xform(cluster[1],q = True, ws = True, rp = True)
            locator = cmds.spaceLocator()
            cmds.move(pos[0],pos[1],pos[2],locator[0])
            locators.append(locator[0])
            cmds.delete(cluster)
            
        except RuntimeError:
            cmds.error('selection must be polyTransforms or verts')
        

    numLocators = len(locators)
    
    if numLocators == 0:
        cmds.error('locators were not created')
    
    #create ribbon
    ribbon = MayaScripts.buildRibbonSurface(locators = locators,name = name,close = close,vector = vector,width = width)
    cmds.addAttr(ribbon[0],ln = 'minVisParam',at = 'double',min = -0.001 , max = 1,dv = -0.001)
    cmds.setAttr('%s.minVisParam'%ribbon[0],e = True,keyable = True)
    cmds.addAttr(ribbon[0],ln = 'maxVisParam',at = 'double',min = 0 , max = 1,dv = 1)
    cmds.setAttr('%s.maxVisParam'%ribbon[0],e = True,keyable = True)
    
    #args for rivets
    iterations = numLocators
    
    rivets = MayaScripts.makeRivets(iterations = iterations,surfaceName = ribbon[1],nodeNames = name,
                closedSurface = close,normalVector = normalVector,tangentVector = tangentVector)
                
    #tread anim attr
    cmds.addAttr(ribbon[0],ln = 'tread',at = 'double')
    cmds.setAttr('%s.tread'%ribbon[0],e = True,keyable = True)
    
    rivetLocators = []
    
    inc = 0
    
    for rivet in rivets:
        vValue = cmds.getAttr('%s.vValue'%rivet)
        mdNode = cmds.createNode('multiplyDivide',n = '%s_MD'%rivet)
        cmds.setAttr('%s.input1X'%mdNode,0.005)
        pmaNode = cmds.createNode('plusMinusAverage',n = '%s_PMA'%rivet)
        cmds.connectAttr('%s.tread'%ribbon[0],'%s.input2X'%mdNode)
        cmds.connectAttr('%s.outputX'%mdNode,'%s.input1D[0]'%pmaNode)
        cmds.setAttr('%s.input1D[1]'%pmaNode,vValue)
        cmds.connectAttr('%s.output1D'%pmaNode,'%s.vValue'%rivet)
        
        locator = (cmds.connectionInfo('%s.outTranslation'%rivet, dfs = True))[0].split('.')[0]
        locatorName = locator.split('_Loc')[0]
        
        cmds.addAttr(locator,ln = 'outVis',at ='bool')
        cmds.setAttr('%s.outVis'%locator,e = True , keyable = True)
        
        dmNode = cmds.createNode('decomposeMatrix',name = '%s_DM'%locatorName)
        cpsNode = cmds.createNode('closestPointOnSurface',name = '%s_CPS'%locatorName)
        
        visMinCDNode = cmds.createNode('condition',name = '%s_Vis_Min_CD'%locatorName)
        visMaxCDNode = cmds.createNode('condition',name = '%s_Vis_Max_CD'%locatorName)
        visMainCDNode = cmds.createNode('condition',name = '%s_Vis_Main_CD'%locatorName)
        
        cmds.connectAttr('%s.worldMatrix[0]'%locator,'%s.inputMatrix'%dmNode)
        cmds.connectAttr('%s.worldSpace[0]'%ribbon[1],'%s.inputSurface'%cpsNode)
        cmds.connectAttr('%s.outputTranslate'%dmNode,'%s.inPosition'%cpsNode)
        
        cmds.connectAttr('%s.minVisParam'%ribbon[0],'%s.firstTerm'%visMinCDNode)
        cmds.connectAttr('%s.maxVisParam'%ribbon[0],'%s.firstTerm'%visMaxCDNode)
        cmds.connectAttr('%s.parameterV'%cpsNode,'%s.secondTerm'%visMinCDNode)
        cmds.connectAttr('%s.parameterV'%cpsNode,'%s.secondTerm'%visMaxCDNode)
        cmds.connectAttr('%s.outColorR'%visMinCDNode,'%s.firstTerm'%visMainCDNode)
        cmds.connectAttr('%s.outColorR'%visMaxCDNode,'%s.secondTerm'%visMainCDNode)
        
        cmds.setAttr('%s.colorIfTrueR'%visMinCDNode,0)
        cmds.setAttr('%s.colorIfFalseR'%visMinCDNode,1)
        cmds.setAttr('%s.operation'%visMinCDNode,4)
        
        cmds.setAttr('%s.colorIfTrueR'%visMaxCDNode,1)
        cmds.setAttr('%s.colorIfFalseR'%visMaxCDNode,0)
        cmds.setAttr('%s.operation'%visMaxCDNode,2)
        
        cmds.setAttr('%s.colorIfTrueR'%visMainCDNode,0)
        cmds.setAttr('%s.colorIfFalseR'%visMainCDNode,1)
        cmds.setAttr('%s.operation'%visMainCDNode,0)
        
        cmds.connectAttr('%s.outColorR'%visMainCDNode,'%s.outVis'%locator)
        cmds.connectAttr('%s.outVis'%locator,'%s.visibility'%selection[inc])
        
        rivetLocators.append(locator)
        
        inc += 1
        
    joints = MayaScripts.makeFloatingJoints(locators = rivetLocators, name = name)
    latticeMainGrp = cmds.group(name = '%s_Lattice_Grp'%name,empty = True)
    
    for i in range(len(joints)):
        
        zeroString = '0'

        if i> 9:
            zeroString = '' 
               
        cmds.select(cl = True)
        jointA = joints[i]
        jointB = joints[i-1]
            
        latticeName = '%s_%s%i_Lattice'%(name,zeroString,i+1)
        latticeShape = '%s_%s%i_LatticeShape'%(name,zeroString,i+1)
        
        lattice = cmds.lattice(divisions = (2,2,2),objectCentered = True, ldv = (2,2,2))
        latticeGrp = cmds.group(lattice,name = '%s_%s%i_Lattice_Grp'%(name,zeroString,i+1))
        
        cmds.setAttr ('%s.outsideLattice'%lattice[0], 1)
        cmds.parent(latticeGrp,latticeMainGrp)
        
        cmds.rename(lattice[0],'%s_%s%i_FFD'%(name,zeroString,i+1))
        cmds.rename(lattice[1],latticeName)
        cmds.rename(lattice[2],'%s_%s%i_Lat_Base'%(name,zeroString,i+1))

        positionA = cmds.xform(jointA, q = True, ws = True, translation = True)
        positionB = cmds.xform(jointB, q = True, ws = True, translation = True)
        vectorA = om.MVector(positionA[0],positionA[1],positionA[2])
        vectorB = om.MVector(positionB[0],positionB[1],positionB[2])
        vectorC = vectorA - vectorB
        
        latticeLength = (vectorC.length()*-1)
        latticeWidth = width*2.0
        '''
        scaleUnitA = om.MVector(normalVector[0],normalVector[1],normalVector[2])
        scaleUnitB = om.MVector(tangentVector[0],tangentVector[1],tangentVector[2])
        
        scaleA = scaleUnitA * latticeLength
        scaleB = scaleUnitB * latticeWidth
        
        latticeScaleX = scaleA.x +scaleB.x
        latticeScaleY = scaleA.y +scaleB.y 
        latticeScaleZ = scaleA.z +scaleB.z 
        latticeScale = [latticeScaleX,latticeScaleY,latticeScaleZ]
        '''
        
        cmds.setAttr('%s.rotatePivotX'%latticeGrp, 0.5)
        cmds.setAttr('%s.scalePivotX'%latticeGrp,0.5)
        
        nullPosGrp = cmds.group(empty = True)
        nullPosA = cmds.group(empty = True)
        nullPosB = cmds.group(empty  = True)
        nullPosC = cmds.group(empty = True)
        cmds.parent(nullPosA,nullPosB)
        cmds.parent(nullPosA,nullPosGrp)
        cmds.parent(nullPosB,nullPosGrp)
        cmds.parent(nullPosC,nullPosGrp)
        
        jointAPos = cmds.xform(jointA,q = True,ws = True,translation = True)
        jointARotation = cmds.xform(jointA,q = True,ws = True,rotation = True)
        
        jointBPos = cmds.xform(jointB,q = True,ws = True,translation = True)
        
        cmds.move(jointAPos[0],jointAPos[1],jointAPos[2],nullPosGrp,ws = True)
        cmds.rotate(jointARotation[0],jointARotation[1],jointARotation[2],nullPosGrp,ws = True)

        aimVector = (tangentVector[0] * -1,tangentVector[1] * -1,tangentVector[2] * -1)
        upVector = normalVector
        
        cmds.move(upVector[0],upVector[1],upVector[2],nullPosC, os = True)
        
        aimConstraint = cmds.aimConstraint(jointB,nullPosA,
                                           aim = (aimVector[0],aimVector[1],aimVector[2]),
                                           u = (upVector[0],upVector[1],upVector[2]))[0]
                                           
        preBindRotate = cmds.xform(nullPosA,q = True,ws = True,rotation = True)
        
        cmds.setAttr('%s.worldUpType'%aimConstraint,1)
        cmds.connectAttr( '%s.worldMatrix[0]'%nullPosC, '%s.worldUpMatrix'%aimConstraint)
        parentConstarint = cmds.parentConstraint(nullPosA,latticeGrp)
        cmds.delete(parentConstarint)
        
        cmds.move(jointBPos[0],jointBPos[1],jointBPos[2],nullPosB,ws = True)
        
        cmds.connectAttr('%s.outVis'%rivetLocators[i],'%s.scaleX'%latticeName)
        cmds.connectAttr('%s.outVis'%rivetLocators[i],'%s.scaleY'%latticeName)
        cmds.connectAttr('%s.outVis'%rivetLocators[i],'%s.scaleZ'%latticeName)
        cmds.scale(latticeLength,latticeWidth,1,latticeGrp,r = True)
        
        parentConstraintA = cmds.parentConstraint(nullPosA,jointA,st = ['x','y','z'])
        parentConstraintB = cmds.parentConstraint(nullPosA,jointB,st = ['x','y','z'])
        
        #cmds.rotate(preBindRotate[0],preBindRotate[1],preBindRotate[2],jointA,a = True,ws = True)
        #cmds.rotate(preBindRotate[0],preBindRotate[1],preBindRotate[2],jointB,a = True,ws = True)
        
        cmds.delete(parentConstraintA,parentConstraintB)

        cmds.skinCluster(jointA,jointB,latticeShape,mi = 1)
        cmds.skinCluster(jointA,selection[i])
        
        cmds.rotate(0,0,0,jointA,os = True)
        cmds.rotate(0,0,0,jointB,os = True)
        
        cmds.delete(nullPosGrp)
        
    cmds.delete(locators)

def createTreadWin():
    
        if cmds.window('treadWin',q = True, exists = True):

            cmds.deleteUI('treadWin')
            
        window = cmds.window('treadWin',title = 'Treads Rig Builder',wh = (125,100),s = False)
        cmds.columnLayout('mainLayout',adj = True,cal = 'left')
        cmds.text('Name:')
        cmds.textField('nameField',text = 'Temp_Name_01')
        cmds.intFieldGrp ('worldVectorField',numberOfFields = 3,l = 'World Vector',value1 = 1)
        cmds.text('Width:')
        cmds.floatSliderGrp('widthSlider',value = 1,field = True,ss = 5)
        cmds.showWindow('treadWin')
        cmds.intFieldGrp ('normalVector',numberOfFields = 3,l = 'Normal Vector',value2 = 1)
        cmds.intFieldGrp ('tangentVector',numberOfFields = 3,l = 'Tangent Vector',value1 = -1)

        name = cmds.textField('nameField',q = True,text =True)
        
        worldVectorX = cmds.intFieldGrp ('worldVectorField',q =True,value1 = True)
        worldVectorY = cmds.intFieldGrp ('worldVectorField',q =True,value2 = True)
        worldVectorZ = cmds.intFieldGrp ('worldVectorField',q =True,value3 = True)
        worldVector = [worldVectorX,worldVectorY,worldVectorZ]
        
        width = cmds.floatSliderGrp('widthSlider',q = True,value = True)
        
        normalVectorX = cmds.intFieldGrp ('normalVector',q =True,value1 = True)
        normalVectorY = cmds.intFieldGrp ('normalVector',q =True,value2 = True)
        normalVectorZ = cmds.intFieldGrp ('normalVector',q =True,value3 = True)
        normalVector = [normalVectorX,normalVectorY,normalVectorZ]
        
        tangentVectorX = cmds.intFieldGrp ('tangentVector',q =True,value1 = True)
        tangentVectorY = cmds.intFieldGrp ('tangentVector',q =True,value2 = True)
        tangentVectorZ = cmds.intFieldGrp ('tangentVector',q =True,value3 = True)
        tangentVector = [tangentVectorX,tangentVectorY,tangentVectorZ]
        
        cmds.button('buildButton',l = 'Build',c = lambda name = name,width = width,vector = worldVector,normalVector = normalVector,tangentVector = tangentVector,close = True:build())
        