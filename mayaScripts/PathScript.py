'''
Created on Jan 28, 2014

@author: bballout
'''

import maya.cmds as cmds
import maya.OpenMaya as om
import GenAPI

def build(**kwargs):

    curve = kwargs.get('curve')
    locatorCount = kwargs.get('locatorCount',2)
    wheelCrv = kwargs.get('wheelCrv')
    name =  kwargs.get('name','Path')
    frontAxis = kwargs.get('frontAxis',0)
    reverseFrontAxis = kwargs.get('reverseFrontAxis',False)
    upAxis = kwargs.get('upAxis',1)
    reverseUpAxis = kwargs.get('reverseUpAxis',False)
    upVector = kwargs.get('upVector',[0,1,0])
    controlScale =kwargs.get('controlScale',15)
    
    curveShape = cmds.listRelatives(curve,type = 'shape')[0]
    
    curveInfo = cmds.createNode('curveInfo',name = '%s_CI'%name)
    cmds.connectAttr('%s.worldSpace[0]'%curveShape,'%s.inputCurve'%curveInfo)
    
    driveCtrl = cmds.circle(name = 'Drive_Ctrl')[0]
    driveCtrlGrp = cmds.group(empty = True,name = 'Drive_Ctrl_Grp')
    cmds.parent(driveCtrl,driveCtrlGrp)
    
    cmds.addAttr('Drive_Ctrl',ln =  "FKCtrlVis" ,at = 'bool')
    cmds.setAttr ('Drive_Ctrl.FKCtrlVis',e = True ,cb =  True)
    
    cmds.addAttr('Drive_Ctrl',ln =  "IKCtrlVis" ,at = 'bool')
    cmds.setAttr ('Drive_Ctrl.IKCtrlVis',e = True ,cb =  True)
    
    locGrp = cmds.group(empty = True,name = '%s_Loc_Grp'%name)
    upLocator = cmds.spaceLocator(name = '%s_Up_Loc'%name)[0]
    cmds.move(upVector[0],upVector[1],upVector[2],upLocator)
    cmds.parent(upLocator,locGrp)

    for i in range(locatorCount):
        
        zeroString = '0'
        if i>9:
            zeroString = ''
            
        cmds.addAttr(driveCtrl,ln =  'drive%i'%(i+1) ,at = 'double',min = 0)
        cmds.setAttr ('%s.drive%i'%(driveCtrl,i+1),e = True ,keyable =  True)
        
        cmds.addAttr(driveCtrl,ln =  'initOffset%i'%(i+1) ,at = 'double')
        cmds.setAttr ('%s.initOffset%i'%(driveCtrl,i+1),e = True ,keyable =  True)
        
        cmds.addAttr(driveCtrl,ln =  'offset%i'%(i+1) ,at = 'double')
        cmds.setAttr ('%s.offset%i'%(driveCtrl,i+1),e = True ,keyable =  True)
        
        addOffsetPMA = cmds.createNode('plusMinusAverage',name = '%s_InitOffset_%s%i_PMA'%(name,zeroString,i+1))
        cmds.connectAttr('%s.initOffset%i'%(driveCtrl,i+1),'%s.input1D[0]'%addOffsetPMA)
        cmds.connectAttr('%s.offset%i'%(driveCtrl,i+1),'%s.input1D[1]'%addOffsetPMA)
    
        moPathLoc = cmds.spaceLocator(name = '%s_POC_%s%i_Loc'%(name,zeroString,i+1))[0]
        motionPathNode = cmds.createNode('motionPath',name = '%s_%s%i_MoPath'%(name,zeroString,i+1))
        cmds.connectAttr('%s.worldSpace[0]'%curveShape,'%s.geometryPath'%motionPathNode)
        cmds.setAttr('%s.worldUpType'%motionPathNode,1)
        cmds.connectAttr('%s.worldMatrix[0]'%upLocator,'%s.worldUpMatrix'%motionPathNode)
        
        cmds.connectAttr('%s.allCoordinates'%motionPathNode,'%s.translate'%moPathLoc)
        cmds.connectAttr('%s.rotate'%motionPathNode,'%s.rotate'%moPathLoc)
        
        offsetPMA = cmds.createNode('plusMinusAverage',name = '%s_offset_%s%i_PMA'%(name,zeroString,i+1))
        cmds.connectAttr('%s.drive%i'%(driveCtrl,i+1),'%s.input1D[0]'%offsetPMA)
        cmds.connectAttr('%s.output1D'%addOffsetPMA,'%s.input1D[1]'%offsetPMA)
        
        dampMD = cmds.createNode('multiplyDivide',name = '%s_Damp_%s%i_MD'%(name,zeroString,i+1))
        cmds.connectAttr('%s.output1D'%offsetPMA,'%s.input1X'%dampMD)
        
        cmds.connectAttr('%s.outputX'%dampMD,'%s.uValue'%motionPathNode)
        
        cmds.setAttr('%s.frontAxis'%motionPathNode,frontAxis)
        cmds.setAttr('%s.upAxis'%motionPathNode,upAxis)
        cmds.setAttr('%s.inverseFront'%motionPathNode,reverseFrontAxis)
        cmds.setAttr('%s.inverseUp'%motionPathNode,reverseUpAxis)
        cmds.parent(moPathLoc,locGrp)
        
    for i in range(len(wheelCrv)):
    
        zeroString = '0'
        if i>9:
            zeroString = ''
    
        wheelCrvInfo = cmds.createNode('curveInfo',name = '%s_Wheel_%s%i_CI'%(name,zeroString,i+1))
        cmds.connectAttr('%s.worldSpace[0]'%wheelCrv[i],'%s.inputCurve'%wheelCrvInfo)
        
        divideCircum = cmds.createNode('multiplyDivide',name = '%s_Circum_%s%i_MD'%(name,zeroString,i+1))
        cmds.setAttr('%s.operation'%divideCircum,2)
        cmds.connectAttr('%s.arcLength'%wheelCrvInfo,'%s.input1X'%divideCircum)
        cmds.connectAttr('%s.arcLength'%curveInfo,'%s.input2X'%divideCircum)
    
        cmds.addAttr(driveCtrl,ln =  'rotateMultiply%i'%(i+1) ,at = 'double')
        cmds.setAttr ('%s.rotateMultiply%i'%(driveCtrl,i+1),e = True ,keyable =  True)
        
        circumMult = cmds.createNode('multiplyDivide',name = '%s_RotateMult_%s%i_MD'%(name,zeroString,i+1))
        cmds.connectAttr('%s.outputX'%divideCircum,'%s.input1X'%circumMult)
        cmds.connectAttr('%s.rotateMultiply%i'%(driveCtrl,i+1),'%s.input2X'%circumMult)
        
        cmds.addAttr(driveCtrl,ln =  'outRotate%i'%(i+1) ,at = 'double')
        cmds.setAttr ('%s.rotateMultiply%i'%(driveCtrl,i+1),e = True ,keyable =  True)
    
    defJointGrp = cmds.group(empty = True,name = '%s_Def_Jnt_Grp'%name)
    
    cmds.select(cl = True)
    baseJoint = cmds.joint(name = '%s_Def_Main_Jnt'%name)
    cmds.parent(baseJoint,defJointGrp)
    skincluster = cmds.skinCluster(curve,baseJoint)[0]
    cmds.setAttr('%s.liw'%baseJoint, 0)
    
    curveItr = om.MItCurveCV(GenAPI.getDagPath(curve))
    
    cmds.select(cl = True)
    
    defJoints = []
    fkCtrls = []
    fkCtrlGrps = []
    
    allIKCtrlGrp = cmds.group(empty = True,name = '%s_IK_Ctrl_Grp'%name)
    allFKCtrlGrp = cmds.group(empty = True,name = '%s_FK_Ctrl_Grp'%name)
    
    i = 1
    while not curveItr.isDone():
    
        zeroString = '0'
        if i>9:
            zeroString = ''
        
        cv = curveItr.index()
        
        ikCtrlGrp = cmds.group(empty = True,name = '%s_IK_%s%i_Ctrl_Grp'%(name,zeroString,i))
        ikCtrl = cmds.circle(name = '%s_IK_%s%i_Ctrl'%(name,zeroString,i),r = (5 * controlScale))[0]
        cmds.parent(ikCtrl,ikCtrlGrp)
        cmds.parent(ikCtrlGrp,allIKCtrlGrp)
        
        fkCtrlGrp = cmds.group(empty = True,name = '%s_FK_%s%i_Ctrl_Grp'%(name,zeroString,i))
        fkCtrl = cmds.circle(name = '%s_FK_%s%i_Ctrl'%(name,zeroString,i),r = (10 * controlScale))[0]
        cmds.parent(fkCtrl,fkCtrlGrp)
        cmds.parent(fkCtrlGrp,allFKCtrlGrp)
        fkCtrls.append(fkCtrl)
        fkCtrlGrps.append(fkCtrlGrp)
        
        cmds.connectAttr('Drive_Ctrl.FKCtrlVis','%s.visibility'%fkCtrlGrp)
        cmds.connectAttr('Drive_Ctrl.IKCtrlVis','%s.visibility'%ikCtrlGrp)
        
        cmds.setAttr('%s.overrideEnabled'%ikCtrl,True)
        cmds.setAttr('%s.overrideColor'%ikCtrl,13)
        
        cmds.setAttr('%s.overrideEnabled'%fkCtrl,True)
        cmds.setAttr('%s.overrideColor'%fkCtrl,6)
        
        cmds.parentConstraint(fkCtrl,ikCtrlGrp,mo = True)
        
        cmds.select(cl = True)
        
        joint = cmds.joint(name = '%s_Def_%s%i_Jnt'%(name,zeroString,i),radius = 200)
        cmds.parent(joint,defJointGrp)
        cmds.parentConstraint(ikCtrl,joint,mo = True)
        
        cmds.select(cl = True)
        pointPos = curveItr.position(om.MSpace.kWorld)
        cmds.move(pointPos.x,pointPos.y,pointPos.z,joint,ws = True)
        
        cmds.move(pointPos.x,pointPos.y,pointPos.z,ikCtrlGrp,ws = True)
        cmds.move(pointPos.x,pointPos.y,pointPos.z,fkCtrlGrp,ws = True)
        
        cmds.skinCluster(skincluster,e = True , weight = 0,addInfluence = joint)
        defJoints.append(joint)
        
        i += 1
        curveItr.next()
     
    for joint in defJoints:
        cmds.setAttr('%s.liw'%joint, 0)
        
    for i in range(len(defJoints)):
        cmds.skinPercent( skincluster,'%s.cv[%i]'%(curve,i), transformValue=[(defJoints[i], 1)])
        
    for i in range(len(fkCtrls)):
        try:
            cmds.parentConstraint(fkCtrls[i],fkCtrlGrps[i+1],mo = True)     
        except:
            pass


