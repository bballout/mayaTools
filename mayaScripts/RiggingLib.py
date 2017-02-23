'''
Created on May 22, 2012

@author: balloutb
'''
    
import maya.OpenMaya as om
import maya.cmds as cmds
import maya.mel as mel


import GenAPI
import MeasuringLib

class Utilities(object):

    '''Class for creating utility node networks'''
    
    #class attrs...
    def __init__(self,input1 = '',input2 = '',output = ''):
    
        self.input1 = input1    
        self.input2 = input2
        self.output = output

    #multiply input with defined,connect to output
    def multiplyAttrs(self,name,operation):
    
        try:
            mdNode = cmds.createNode('multiplyDivide',n = '%s_MD'%(name))
            
            #connect input1
            if not self.input1[0] == '':
                cmds.connectAttr(self.input1[0],'%s.input1X'%(mdNode))
                
            if not self.input1[1] == '':
                cmds.connectAttr(self.input1[1],'%s.input1Y'%(mdNode))
                
            if not self.input1[2] == '':
                cmds.connectAttr(self.input1[2],'%s.input1Z'%(mdNode))
            
            #connect input2
            if not self.input2[0] == '':
                cmds.connectAttr(self.input1[0],'%s.input2X'%(mdNode))
                
            if not self.input2[1] == '':
                cmds.connectAttr(self.input1[1],'%s.input2Y'%(mdNode))
                
            if not self.input2[2] == '':
                cmds.connectAttr(self.input1[2],'%s.input2Z'%(mdNode))
                
            cmds.setAttr('%s.operation'%(mdNode),operation)        
            return mdNode
            
        except RuntimeError:
            return 'unable to build'
            
    #create dampener from MD node
    
    #create normalized value from MD node
    
    #create offset with PMA
    
    #create  stretchy network
    @staticmethod
    def stretchNodeNetwork(name,measurement,lengthAttr):

        mdNode = cmds.createNode('multiplyDivide', n = '%s_Stretch_MD'%name)
        cmds.connectAttr(lengthAttr ,'%s.input1X'%mdNode)
        cmds.setAttr('%s.input2X'%mdNode,measurement)
        cmds.setAttr('%s.operation'%mdNode, 2)
        
        stretchCondition = cmds.createNode('condition',n = '%s_Stretch_CD'%name)
        cmds.connectAttr('%s.outputX'%mdNode, '%s.firstTerm'%stretchCondition)
        cmds.connectAttr('%s.outputX'%mdNode, '%s.colorIfTrueR'%stretchCondition)
        cmds.setAttr('%s.operation'%stretchCondition, 2)
        cmds.setAttr('%s.secondTerm'%stretchCondition, 1)
        
        lockCondition = cmds.createNode('condition',n = '%s_Lock_CD'%name)
        cmds.connectAttr('%s.outputX'%mdNode, '%s.colorIfTrueR'%lockCondition)
        cmds.connectAttr('%s.outColorR'%stretchCondition, '%s.colorIfFalseR'%lockCondition)
        cmds.setAttr('%s.secondTerm'%lockCondition, 1)
        
        stretchBlendNode = cmds.createNode('blendColors',n = '%s_Stretch_BD'%name)
        cmds.setAttr('%s.color2R'%stretchBlendNode, 1)
        cmds.connectAttr('%s.outColorR'%lockCondition, '%s.color1R'%stretchBlendNode)
        
        return [stretchBlendNode,lockCondition]
    
class Controllers(object):

    '''Class for Rig Controllers'''
    
    
    #nothing to initialize...
    def __init__(self):
        pass
    
    @staticmethod
    def diamondCurve(name):
        
        curve = mel.eval('''curve -d 3 -p 0 0.809437 0 -p 0 0 0 -p 1.071098 0.000156484 0 
            -p 0 0 0 -p 0 -0.988362 0 -p 0 0 0 -p -1.071411 -0.000156484 0 -p 0 0 0 -p 0 0.809437 0 
            -k 0 -k 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 6 -k 6 ;''')
        
        cmds.closeCurve(curve,ch  = 1,ps = 2,rpo = 1, bb = 0,bki =  1, p = 0.1)
        
        cmds.rename(curve,name)
        curveShapes = cmds.listRelatives(name, s = True)
        
        return curveShapes
    
    @staticmethod
    def diamondCurve3D(name):
    
        curveX = mel.eval('''curve -d 3 -p 0 0.809437 0 -p 0 0 0 -p 0 0.000151268 -1.035395 -p 0 0 0 
            -p 0 -0.988362 0 -p 0 0 0 -p 0 -0.000151268 1.035697 -p 0 0 0 -p 0 0.809437 0 -k 0 -k 0 
            -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 6 -k 6 ;''')
            
        cmds.closeCurve(curveX,ch  = 1,ps = 2,rpo = 1, bb = 0,bki =  1, p = 0.1)
            
            
        curveZ = mel.eval('''curve -d 3 -p 0 0.809437 0 -p 0 0 0 -p 1.071098 0.000156484 0 
            -p 0 0 0 -p 0 -0.988362 0 -p 0 0 0 -p -1.071411 -0.000156484 0 -p 0 0 0 -p 0 0.809437 0 
            -k 0 -k 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 6 -k 6 ;''')
        
        cmds.closeCurve(curveZ,ch  = 1,ps = 2,rpo = 1, bb = 0,bki =  1, p = 0.1)
        
        curveZShape = cmds.listRelatives(curveZ,s = True)
        
        cmds.parent(curveZShape,curveX,r = True, s = True)
        
        
        cmds.rename(curveX,name)
        cmds.delete(curveZ)    
        curveShapes = cmds.listRelatives(name,s = True)
        
        return curveShapes
        
    @staticmethod
    def fourArrowCurve(name):
        
        curve = mel.eval('''curve -d 1 -p -1 1 0 -p -1 3 0 -p -2 3 0 -p 0 6 0 -p 2 3 0 -p 1 3 0 
            -p 1 1 0 -p 3 1 0 -p 3 2 0 -p 6 0 0 -p 3 -2 0 -p 3 -1 0 -p 1 -1 0 -p 1 -3 0 -p 2 -3 0 
            -p 0 -6 0 -p -2 -3 0 -p -1 -3 0 -p -1 -1 0 -p -3 -1 0 -p -3 -2 0 -p -6 0 0 -p -3 2 0 
            -p -3 1 0 -p -1 1 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 
            -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 -k 19 -k 20 -k 21 -k 22 -k 23 -k 24 ;''')

        cmds.rename(curve,name)
        curveShape = cmds.listRelatives(name,s = True)
        
        return curveShape
    
    @staticmethod
    def singleArrowCurve(name):
        
        curve = mel.eval('''curve -d 1 -p -1 6 0 -p 1 6 0 -p 1 3 0 -p 2 3 0 -p 0 0 0 
            -p -2 3 0 -p -1 3 0 -p -1 6 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 ;''')
            
        cmds.rename(curve,name)
        curveShape = cmds.listRelatives(name,s = True)
        
        return curveShape

    @staticmethod
    def cubeCurve(name):
            
        curve = mel.eval('''curve -d 1 -p -1 1 1 -p 1 1 1 -p 1 1 -1 -p -1 1 -1 -p -1 1 1 -p -1 -1 1 -p 1 -1 1 
            -p 1 1 1 -p -1 1 1 -p -1 1 -1 -p -1 -1 -1 -p -1 -1 1 -p -1 1 1 -p 1 1 1 -p 1 -1 1 -p 1 -1 -1 -p 1 1 -1 
            -p 1 1 1 -p 1 -1 1 -p -1 -1 1 -p -1 -1 -1 -p 1 -1 -1 -p 1 -1 1 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 
            -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 -k 19 -k 20 -k 21 -k 22 ; ''')
        
        cmds.rename(curve,name)
        curveShape = cmds.listRelatives(name,s = True)

        return curveShape
        
    @staticmethod
    def sphereCurve(name):

        circleX = cmds.circle(nrx = 1,nry = 0, nrz = 0)
        circleY = cmds.circle(nrx = 0,nry = 1, nrz = 0)
        circleZ = cmds.circle(nrx = 0,nry = 0, nrz = 1)
        
        circleYShape = cmds.listRelatives(circleY[0],s  = True)
        cmds.parent(circleYShape,circleX,r = True, s = True)
        
        circleZShape = cmds.listRelatives(circleZ[0],s  = True)
        cmds.parent(circleZShape,circleX[0],r = True, s = True)

        cmds.delete(circleX[1])
        cmds.delete(circleY[0])
        cmds.delete(circleZ[0])
        cmds.delete(circleY[1])
        cmds.delete(circleZ[1])
        cmds.rename(circleX[0],name)
        curveShape = cmds.listRelatives(name,s = True)

        return curveShape
        
        
class SkeletalRigs(object):
    
    '''
    Class for building various joint setups
    '''
    startJointObject = ''
    startJointPath = ''
    
    endJointObject = ''
    endJointPath = ''
    
    ##Class Attrs.... 
    def __init__(self,startJoint = '',endJoint = ''):
        
        self.startJoint = startJoint
        self.endJoint = endJoint
        
        self.startJointObject = GenAPI.getMObject(startJoint)
        self.startJointPath = GenAPI.getDagPath(startJoint)
        
        self.endJointObject = GenAPI.getMObject(endJoint)
        self.endJointPath = GenAPI.getDagPath(endJoint)
    
    @staticmethod    
    def curveFromJointChain(name,jointRoot):

        childJoints = cmds.listRelatives(jointRoot, ad = True)
        jointChain = []
        
        for joint in childJoints:
            jointChain.append(joint)
        
        jointChain.append(jointRoot)
        jointChain.reverse()
        
        points = []
        for joint in jointChain:
            pos = cmds.xform(joint, q = True, ws = True, translation = True)
            points.append(pos)
        
        curve = cmds.curve(p = points, n = name)
        return curve
    
    @staticmethod
    def jointsOnCVs(name,curve):
        
        if not cmds.nodeType(curve) == 'shape':
            
            curve = cmds.listRelatives(curve, type = 'shape')[0]
            
        mobject = GenAPI.getMObject(curve)
        iterCVs = om.MItCurveCV(mobject)
        
        while not iterCVs.isDone():

            index = iterCVs.index()
            nameIndex = index + 1         
            pos = iterCVs.position()
            joint = cmds.joint(n = '%s_0%i_Jnt'%(name,nameIndex), p = (pos[0],pos[1],pos[2]))
            
            try:
                cmds.parent(joint,w = True) 
                
            except RuntimeError:
                pass        
            
            iterCVs.next()
                 
    def splineIKShort (self,name,transform,curveFrom = ''):
        
        
        jointChainList = []
        jointChainList.append(self.startJoint)
        childJoints = cmds.listRelatives(self.startJoint,ad = True, type = 'joint')
        
        for joint in childJoints:
            jointChainList.append(joint)
        
        jointChainList.sort(cmp=None, key=None, reverse=False)
        print jointChainList
        ikSpline = cmds.ikHandle(n = '%s_IKHandle'%name, sj = self.startJoint, ee = self.endJoint, sol = 'ikSplineSolver') 
        
        if not curveFrom == '':
            
            curveShape01 = cmds.listRelatives(curveFrom, type = 'shape')
            curveInfoNodeCompress = cmds.createNode('curveInfo', n = '%s_Compress_CurveInfo'%name)
            cmds.connectAttr('%s.worldSpace'%curveShape01[0], '%s.inputCurve'%curveInfoNodeCompress)
            
            curveShape02 = cmds.listRelatives(ikSpline[2], type = 'shape',)
            curveInfoNodeStretch = cmds.createNode('curveInfo', n = '%s_Stretch_CurveInfo'%name)
            cmds.connectAttr('%s.worldSpace'%curveShape02[0], '%s.inputCurve'%curveInfoNodeStretch)
            
            length = cmds.getAttr('%s.arcLength'%curveInfoNodeStretch)
                             
        else:     
            curveShape = cmds.listRelatives(ikSpline[2], type = 'shape',)
            curveInfoNode = cmds.createNode('curveInfo', n = '%s_CurveInfo'%name)
            cmds.connectAttr('%s.worldSpace'%curveShape[0], '%s.inputCurve'%curveInfoNode)        
            length = cmds.getAttr('%s.arcLength'%curveInfoNode)
        
        transformMD = cmds.createNode('multiplyDivide',n = '%s_TransformMult_MD'%name)
        cmds.connectAttr('%s.scaleX'%transform,'%s.input1X'%transformMD)
        cmds.setAttr('%s.input2X'%transformMD,length)
        
        if not curveFrom == '':
            
            stretchMD = cmds.createNode('multiplyDivide', n = '%s_Stretch_MD'%name)
            cmds.connectAttr('%s.outputX'%transformMD, '%s.input2X'%stretchMD)
            cmds.connectAttr('%s.arcLength'%curveInfoNodeStretch, '%s.input1X'%stretchMD)
            cmds.setAttr('%s.operation'%stretchMD,2)
            
            compressMD = cmds.createNode('multiplyDivide', n = '%s_Compress_MD'%name)
            cmds.connectAttr('%s.outputX'%transformMD, '%s.input1X'%compressMD)
            cmds.connectAttr('%s.arcLength'%curveInfoNodeCompress, '%s.input2X'%compressMD)
            cmds.setAttr('%s.operation'%compressMD,2)
        
        else:
            
            stretchMD = cmds.createNode('multiplyDivide', n = '%s_Stretch_MD'%name)
            cmds.connectAttr('%s.outputX'%transformMD, '%s.input2X'%stretchMD)
            cmds.connectAttr('%s.arcLength'%curveInfoNode, '%s.input1X'%stretchMD)
            cmds.setAttr('%s.operation'%stretchMD,2)
                
            compressMD = cmds.createNode('multiplyDivide', n = '%s_Compress_MD'%name)
            cmds.connectAttr('%s.outputX'%transformMD, '%s.input1X'%compressMD)
            cmds.connectAttr('%s.arcLength'%curveInfoNode, '%s.input2X'%compressMD)
            cmds.setAttr('%s.operation'%compressMD,2)
        
        for joint in jointChainList:
        
            cmds.connectAttr('%s.outputX'%stretchMD,'%s.scaleX'%joint)
            cmds.connectAttr('%s.outputX'%compressMD,'%s.scaleY'%joint)
            cmds.connectAttr('%s.outputX'%compressMD,'%s.scaleZ'%joint)
        
        startPos = cmds.xform(self.startJoint, q = True, ws = True, translation = True)
        startOrient = cmds.xform(self.startJoint, q = True, ws = True, rotation = True)
        
        defStartJoint = cmds.joint(n = '%s_Start_Deformer_Jnt'%name, p = (startPos[0],startPos[1],startPos[2]))
        cmds.setAttr('%s.rotateAxisX'%defStartJoint,startOrient[0])
        cmds.setAttr('%s.rotateAxisY'%defStartJoint,startOrient[1])
        cmds.setAttr('%s.rotateAxisZ'%defStartJoint,startOrient[2])
        
        endPos = cmds.xform(self.endJoint,q = True, ws = True, translation = True)
        endOrient = cmds.xform(self.endJoint, q = True, ws = True, rotation = True)
        
        defEndJoint = cmds.joint(n = '%s_End_Deformer_Jnt'%name, p = (endPos[0],endPos[1],endPos[2]))
        cmds.setAttr('%s.rotateAxisX'%defEndJoint,endOrient[0])
        cmds.setAttr('%s.rotateAxisY'%defEndJoint,endOrient[1])
        cmds.setAttr('%s.rotateAxisZ'%defEndJoint,endOrient[2])
        
        cmds.parent(defEndJoint, w = True)
        
        cmds.skinCluster(defStartJoint, defEndJoint, ikSpline[2],tsb=True,dr = 2 )
        
        cmds.setAttr('%s.dTwistControlEnable'%ikSpline[0],1)
        cmds.setAttr('%s.dWorldUpType'%ikSpline[0],4)
        cmds.connectAttr('%s.worldMatrix[0]'%defStartJoint,'%s.dWorldUpMatrix'%ikSpline[0])
        cmds.connectAttr('%s.worldMatrix[0]'%defEndJoint,'%s.dWorldUpMatrixEnd'%ikSpline[0])
        
        cmds.rename(ikSpline[2], '%s_Spline_Curve'%name)
        cmds.group(defStartJoint,defEndJoint,n = '%s_Deformer_Jnt_Group'%name )
        
    def splineIKLong(self,name,transform = '',curve = ''):
        
        jointChainList = []
        jointChainList.append(self.startJoint)
        childJoints = cmds.listRelatives(self.startJoint,ad = True, type = 'joint')
        
        for joint in childJoints:
            jointChainList.append(joint)
        
        if not curve == '':
            
            cmds.ikHandle(n = '%s_IKHandle'%name, sj = self.startJoint, ee = self.endJoint, sol = 'ikSplineSolver',ccv = False, c = curve) 
                            
        else:
            
            jointChainList.sort(cmp=None, key=None, reverse=False)
            curve = SkeletalRigs.curveFromJointChain('%s_Curve'%name,self.startJoint)
            cmds.ikHandle(n = '%s_IKHandle'%name, sj = self.startJoint, ee = self.endJoint, sol = 'ikSplineSolver',ccv = False, c = curve) 
            
            
        curveShape = cmds.listRelatives(curve, type = 'shape',)
        curveInfoNode = cmds.createNode('curveInfo', n = '%s_CurveInfo'%name)
        cmds.connectAttr('%s.worldSpace'%curveShape[0], '%s.inputCurve'%curveInfoNode)
        
        length = cmds.getAttr('%s.arcLength'%curveInfoNode)
        
        transformMD = cmds.createNode('multiplyDivide',n = '%s_TransformMult_MD'%name)
        cmds.connectAttr('%s.scaleX'%transform,'%s.input1X'%transformMD)
        cmds.setAttr('%s.input2X'%transformMD,length)
        
        stretchMD = cmds.createNode('multiplyDivide', n = '%s_Stretch_MD'%name)
        cmds.connectAttr('%s.outputX'%transformMD, '%s.input2X'%stretchMD)
        cmds.connectAttr('%s.arcLength'%curveInfoNode, '%s.input1X'%stretchMD)
        cmds.setAttr('%s.operation'%stretchMD,2)
        
        compressMD = cmds.createNode('multiplyDivide', n = '%s_Compress_MD'%name)
        cmds.connectAttr('%s.outputX'%transformMD, '%s.input1X'%compressMD)
        cmds.connectAttr('%s.arcLength'%curveInfoNode, '%s.input2X'%compressMD)
        cmds.setAttr('%s.operation'%compressMD,2)
        
        for joint in jointChainList:
        
            cmds.connectAttr('%s.outputX'%stretchMD,'%s.scaleX'%joint)
            cmds.connectAttr('%s.outputX'%compressMD,'%s.scaleY'%joint)
            cmds.connectAttr('%s.outputX'%compressMD,'%s.scaleZ'%joint)
            
    @staticmethod
    def FKRig(name,startJoint):
        
        ##get joint chain...
        fkJoints = cmds.listRelatives(startJoint,ad = True)
        fkJoints.append(startJoint)
        fkJoints.reverse()
        
        print fkJoints
        
        inc = 0
        controls= []
        controlGroups = []
        for joint in fkJoints:
                     
            control = cmds.group(empty = True, name = '%s_FK_0%i_Ctrl'%(name,inc+1))
            controlGroup = cmds.group(empty = True, name = '%s_FK_0%i_Ctrl_Group'%(name,inc+1))
            cmds.parent(control,controlGroup)
            controls.append(control)
            controlGroups.append(controlGroup)
            
            matchParentConstraint = cmds.parentConstraint(joint,controlGroup)
            cmds.delete(matchParentConstraint)
            
            if(inc > 0):
                
                print inc - 1
                cmds.parentConstraint(controls[inc-1],controlGroup, mo = True)
                
            cmds.parentConstraint(control,joint) 
            
            inc += 1
            
        mainGroup = cmds.group(empty = True, n = '%s_FK_Ctrl_Group'%name)
        
        for group in controlGroups:
            
            cmds.parent(group, mainGroup)
            
        jointGroup = cmds.group(empty = True, n = '%s_FK_Jnt_Group'%name)
        cmds.parent(fkJoints[0],jointGroup)
            
        return controls,mainGroup,jointGroup
            
                 
    @staticmethod
    def IKFKRig(name,rootJoint,blendAttr,poleVector = [0,0,1]):
            
        ##get joint chain...
        bindJoints = cmds.listRelatives(rootJoint,ad = True)
        bindJoints.append(rootJoint)
        bindJoints.reverse()
        
        ##clear selection
        cmds.select(cl = True)
        
        ikJoints = []
        
        ##create ik joint chain
        inc = 1
        for joint in bindJoints:
        
            prefferedAngle = [cmds.getAttr('%s.preferredAngleX'%joint),
                              cmds.getAttr('%s.preferredAngleY'%joint),
                              cmds.getAttr('%s.preferredAngleZ'%joint)]
        
            ikJoint = cmds.joint(n = '%s_IK_0%i_Jnt'%(name,inc))
            parentConstraint = cmds.parentConstraint(joint,ikJoint)
            cmds.delete(parentConstraint)
            cmds.makeIdentity(a = True)
            cmds.setAttr('%s.preferredAngleX'%ikJoint,prefferedAngle[0])
            cmds.setAttr('%s.preferredAngleY'%ikJoint,prefferedAngle[1])
            cmds.setAttr('%s.preferredAngleZ'%ikJoint,prefferedAngle[2])
            
            ikJoints.append(ikJoint)
            
            inc += 1
        
        ##create ik handle
        ikHandle = cmds.ikHandle(sj = ikJoints[0], ee = ikJoints[-1], sol = 'ikRPsolver', n = '%s_IKHandle'%name)
        poleVectorLoc = cmds.spaceLocator(n = '%s_PoleVector_Loc'%name)
        
        ##create pole vector
        poleVectorLocGroup = cmds.group(empty = True, n = '%s_Group'%poleVectorLoc[0])
        pointConstraint = cmds.pointConstraint(ikJoints[1],ikJoints[-2],poleVectorLocGroup)
        orientConstraint = cmds.orientConstraint(rootJoint,poleVectorLocGroup)
        cmds.delete(pointConstraint);cmds.delete(orientConstraint)
        
        cmds.parent(poleVectorLoc[0],poleVectorLocGroup)
        cmds.move(0,0,0,poleVectorLoc[0],os = True)
        cmds.move(poleVector[0],poleVector[1],poleVector[2],poleVectorLoc[0],os = True)
        cmds.rotate(0,0,0,poleVectorLoc[0],os = True)
        cmds.poleVectorConstraint(poleVectorLoc[0],ikHandle[0])
        
        #measure joint hierarchy length
        rootObject = GenAPI.getMObject(rootJoint)
        measurement = MeasuringLib.MeasuringTool.getLengthOfHierarchy(rootObject)

        
        #build measuring rig
        measuringTool = MeasuringLib.MeasuringTool(ikJoints[0],ikJoints[-1])
        measuringLoc = measuringTool.nullMeasurementRig('%s_Measurement'%name)
        
        #create controls
        ikControl = cmds.group(empty = True, name = '%s_IK_Ctrl'%name)
        ikControlGroup = cmds.group(empty = True, name = '%s_IK_Ctrl_Offset'%name)
        cmds.parent(ikControl, ikControlGroup)
        parentConstraint = cmds.parentConstraint(ikJoints[-1],ikControlGroup)
        cmds.delete(parentConstraint)

        cmds.setAttr('%s.sx'%ikControl,lock = True, keyable = False,channelBox = False)
        cmds.setAttr('%s.sy'%ikControl,lock = True, keyable = False,channelBox = False)
        cmds.setAttr('%s.sz'%ikControl,lock = True, keyable = False,channelBox = False)
        cmds.setAttr('%s.v'%ikControl,lock = True, keyable = False,channelBox = False)
        cmds.addAttr(ikControl, ln = 'stretchy' , at = 'double', min = 0, max = 1, dv = 0)
        cmds.setAttr('%s.stretchy'%ikControl, e = True, keyable = True)       
        cmds.addAttr(ikControl, ln = 'length' , at = 'double', dv = 0)
        cmds.setAttr('%s.length'%ikControl, e = True, keyable = True)        
        cmds.addAttr(ikControl, ln = 'noBend' , at = 'bool', dv = False)
        cmds.setAttr('%s.noBend'%ikControl, e = True, keyable = True)        
        cmds.addAttr(ikControl, ln = 'twist' , at = 'double', dv = 0)
        cmds.setAttr('%s.twist'%ikControl, e = True, keyable = True)
                
        poleVectorCtrl = cmds.group(empty = True, name = '%s_PoleVector_Ctrl'%name)
        poleVectorCtrlGroup = cmds.group(empty = True, name = '%s_PoleVector_Ctrl_Offset'%name)
        cmds.parent(poleVectorCtrl,poleVectorCtrlGroup)
        poleVectorCtrlPos = cmds.xform(poleVectorLoc, q = True, ws = True, translation = True)
        cmds.move(poleVectorCtrlPos[0],poleVectorCtrlPos[1],poleVectorCtrlPos[2],poleVectorCtrlGroup)
        cmds.setAttr('%s.sx'%poleVectorCtrl,lock = True, keyable = False,channelBox = False)
        cmds.setAttr('%s.sy'%poleVectorCtrl,lock = True, keyable = False,channelBox = False)
        cmds.setAttr('%s.sz'%poleVectorCtrl,lock = True, keyable = False,channelBox = False)
        cmds.setAttr('%s.rx'%poleVectorCtrl,lock = True, keyable = False,channelBox = False)
        cmds.setAttr('%s.ry'%poleVectorCtrl,lock = True, keyable = False,channelBox = False)
        cmds.setAttr('%s.rz'%poleVectorCtrl,lock = True, keyable = False,channelBox = False)
        cmds.setAttr('%s.v'%poleVectorCtrl,lock = True, keyable = False,channelBox = False)
        
        #create constraints
        cmds.pointConstraint(ikControl,ikHandle[0])
        cmds.pointConstraint(ikControl,measuringLoc[2])
        cmds.pointConstraint(poleVectorCtrl,poleVectorLoc[0])
        
        #make stretchy
        stretchOutput = Utilities.stretchNodeNetwork(name, measurement, '%s.tx'%measuringLoc[1])
        inc = 0
        for joint in ikJoints:
            
            if inc < ikJoints[-1]:
                
                cmds.connectAttr('%s.outputR'%stretchOutput[0],'%s.sx'%joint)
                
            inc += 1
            
          
        #create elbow stretch
        for joint in ikJoints:
            
            if not joint == ikJoints[0]:
                
                pmaNode = cmds.createNode('plusMinusAverage', n = '%s_IKLength_PMA'%joint)
                translateVal = cmds.getAttr('%s.tx'%joint)
                cmds.setAttr('%s.input1D[0]'%pmaNode,translateVal)
                cmds.connectAttr('%s.length'%ikControl,'%s.input1D[1]'%pmaNode)
                cmds.connectAttr('%s.output1D'%pmaNode, '%s.tx'%joint)
                
        
        
        #connect control attrs
        cmds.connectAttr('%s.stretchy'%ikControl, '%s.blender'%stretchOutput[0])
        cmds.connectAttr('%s.noBend'%ikControl, '%s.firstTerm'%stretchOutput[1])
        cmds.connectAttr('%s.twist'%ikControl, '%s.twist'%ikHandle[0])
        
        ##create fk joint chain
        fkJoints = []
        inc = 1
        cmds.select(cl = True)
        for joint in ikJoints:
        
            prefferedAngle = [cmds.getAttr('%s.preferredAngleX'%joint),
                              cmds.getAttr('%s.preferredAngleY'%joint),
                              cmds.getAttr('%s.preferredAngleZ'%joint)]
        
            fkJoint = cmds.joint(n = '%s_FK_0%i_Jnt'%(name,inc))
            parentConstraint = cmds.parentConstraint(joint,fkJoint)
            cmds.delete(parentConstraint)
            cmds.makeIdentity(a = True)
            cmds.setAttr('%s.preferredAngleX'%fkJoint,prefferedAngle[0])
            cmds.setAttr('%s.preferredAngleY'%fkJoint,prefferedAngle[1])
            cmds.setAttr('%s.preferredAngleZ'%fkJoint,prefferedAngle[2])
            
            fkJoints.append(fkJoint)
            
            inc += 1
            
        #create FK Rig
        fkRig = SkeletalRigs.FKRig(name, fkJoints[0])
            
        #createConstraints
        ikfkReverseBlend = cmds.createNode('reverse',n = '%s_IKFK_Reverse'%name)
        cmds.connectAttr(blendAttr,'%s.inputX'%ikfkReverseBlend)
        inc = 0
        
        for joint in bindJoints:
            
            constraint = cmds.parentConstraint(ikJoints[inc],fkJoints[inc],joint)[0]
            
            cmds.connectAttr(blendAttr, '%s.%sW0'%(constraint,ikJoints[inc]))
            cmds.connectAttr('%s.outputX'%ikfkReverseBlend, '%s.%sW1'%(constraint,fkJoints[inc]))
            
            inc += 1
            

        #clean-up
        ikJointGroup = cmds.group(empty = True, name = '%s_IK_Jnt_Group'%name)
        ikCtrlGroup = cmds.group(empty = True, name = '%s_IK_Ctrl_Group'%name)
        
        cmds.parent(ikHandle[0],ikJointGroup)
        cmds.parent(poleVectorLocGroup,ikJointGroup)
        cmds.parent(measuringLoc[3],ikJointGroup)
        cmds.parent(ikJoints[0],ikJointGroup)
        
        jointGroup = cmds.group(empty = True, n = '%s_Jnt_Group'%name)
        cmds.parent(fkRig[2],jointGroup)
        cmds.parent(ikJointGroup,jointGroup)
        
        cmds.parent(ikControlGroup,ikCtrlGroup)
        cmds.parent(poleVectorCtrlGroup,ikCtrlGroup)
        
        ctrlGroup = cmds.group(empty = True, n = '%s_Ctrl_Group'%name)
        cmds.parent(fkRig[1],ctrlGroup)
        cmds.parent(ikCtrlGroup,ctrlGroup)
        
        cmds.select(cl = True)
        
        return ikControl,poleVectorCtrl,fkRig[1]
    
    @staticmethod
    def IKFKFoot(name = '',startJoint = '',pivots = [],control = ''):
        
        ##get joint chain...
        
        bindJoints = cmds.listRelatives(startJoint,ad = True)
        bindJoints.append(startJoint)
        bindJoints.reverse()
        
        ##create ik joint chain
        cmds.select(cl = True)
        ikJoints = []
        ikHandles = []
        inc = 1
        for joint in bindJoints:
            
            ikJoint = cmds.joint(n = '%s_0%i_IK_Jnt'%(name, inc))
            parentConstraint = cmds.parentConstraint(joint,ikJoint)
            cmds.delete(parentConstraint)
            cmds.makeIdentity(a = True)
            ikJoints.append(ikJoint)
            
            if inc > 1:
                
                ikHandle = cmds.ikHandle(sj = ikJoints[inc - 2], ee = ikJoints[inc - 1], sol = 'ikSCsolver', n = '%s_0%i_IKHandle'%(name, inc-1))
                ikHandles.append(ikHandle[0])
                
                cmds.select(ikJoints[inc - 1])
            inc += 1
          
        #create reverse joint chain
        inc = 1
        cmds.select(cl = True)
        reverseJoints = []
        for pivot in pivots:
            
            pos = cmds.xform(pivot, q = True, ws = True, translation = True)
            reverseJoint = cmds.joint(n = '%s_Reverse_0%i_Jnt'%(name, inc))
            reverseJoints.append(reverseJoint)
            cmds.move(pos[0], pos[1], pos[2],reverseJoint, ws = True)
            inc += 1
            
        #create constraints
        cmds.parentConstraint(reverseJoints[3], ikHandles[1],mo = True)
        cmds.parentConstraint(reverseJoints[4], ikHandles[0],mo = True)
        cmds.parentConstraint(reverseJoints[-1], ikJoints[0],mo = True)
        
        #add attributes to IK Control
        cmds.addAttr(control, ln = 'footRoll' , at = 'double', dv = 0)
        cmds.setAttr('%s.footRoll'%control, e = True, keyable = True)
        
        cmds.addAttr(control, ln = 'toePivot' , at = 'double', dv = 0)
        cmds.setAttr('%s.toePivot'%control, e = True, keyable = True)
        
        cmds.addAttr(control, ln = 'toeRoll' , at = 'double', dv = 0)
        cmds.setAttr('%s.toeRoll'%control, e = True, keyable = True)
        
        cmds.addAttr(control, ln = 'footBank' , at = 'double', dv = 0)
        cmds.setAttr('%s.footBank'%control, e = True, keyable = True) 
        
        #connect foot roll
        clampNode = cmds.createNode('clamp', n = '%s_FootRoll_Clamp'%name)
        cmds.connectAttr('%s.footRoll'%control, '%s.inputR'%clampNode)
        cmds.connectAttr('%s.footRoll'%control, '%s.inputG'%clampNode)
        cmds.setAttr('%s.maxR'%clampNode,360)
        cmds.setAttr('%s.minG'%clampNode,-360)
        cmds.connectAttr('%s.outputR'%clampNode, '%s.rx'%reverseJoints[-2])
        cmds.connectAttr('%s.outputG'%clampNode, '%s.rx'%reverseJoints[2])
        
        #connect toe pivot
        cmds.connectAttr('%s.toePivot'%control, '%s.rx'%reverseJoints[3])
        
        #connect toe roll
        cmds.connectAttr('%s.toeRoll'%control, '%s.ry'%reverseJoints[3])
        
        #connect foot bank
        clampNode02 = cmds.createNode('clamp', n = '%s_FootBank_Clamp'%name)
        cmds.connectAttr('%s.footBank'%control, '%s.inputR'%clampNode02)
        cmds.connectAttr('%s.footBank'%control, '%s.inputG'%clampNode02)
        cmds.setAttr('%s.maxR'%clampNode02,360)
        cmds.setAttr('%s.minG'%clampNode02,-360)
        cmds.connectAttr('%s.outputR'%clampNode02, '%s.rz'%reverseJoints[1])
        cmds.connectAttr('%s.outputG'%clampNode02, '%s.rz'%reverseJoints[0])
        
        #create fk joints
        inc = 1
        cmds.select(cl = True)
        fkJoints = []
        for joint in ikJoints:
            
            fkJoint = cmds.joint(n = '%s_0%i_FK_Jnt'%(name, inc))
            parentConstraint = cmds.parentConstraint(joint, fkJoint)
            cmds.delete(parentConstraint)
            fkJoints.append(fkJoint)
            inc += 1
        
        fkRig = SkeletalRigs.FKRig(name, fkJoints[0])
        
        #clean up
        jointGroup = cmds.group(empty = True, n = '%s_Jnt_Group'%name)
        
        ikJointGroup = cmds.group(empty = True, n = '%s_IK_Jnt_Group'%name)
        cmds.parent(ikJoints[0],ikJointGroup)
        cmds.parent(reverseJoints[0],ikJointGroup)
        
        cmds.parent(ikJointGroup,jointGroup)
        
        ikHandlesGroup = cmds.group(empty = True, n = '%s_IKHandles_Group'%name)
        
        for handle in ikHandles:
            cmds.parent(handle,ikHandlesGroup)
            
        cmds.parent(ikHandlesGroup, ikJointGroup)
        cmds.parent(fkRig[2], jointGroup)
        return fkRig
        
    #method for building short point on curve rig   
    def pointOnCurveShort(self,name,numPoints,aimVector = [1,0,0], upVector = [0,1,0]):
        
        #create end ctrls

        startCtrlGroup = cmds.group(empty = True, name = '%s_Start_Ctrl_Group'%name)
        startCtrl = cmds.group(empty = True, name = '%s_Start_Ctrl'%name)
        cmds.parent(startCtrl,startCtrlGroup)
        cmds.parentConstraint(self.startJoint,startCtrlGroup)
        
        endCtrlGroup = cmds.group(empty = True, name = '%s_End_Ctrl_Group'%name)
        endCtrl = cmds.group(empty = True, name = '%s_End_Ctrl'%name)
        cmds.parent(endCtrl,endCtrlGroup)
        cmds.parentConstraint(self.endJoint,endCtrlGroup)
    
            
        #get measurement
        startPoint = MeasuringLib.MeasuringTool.getMPoint(self.startJointPath)
        endPoint = MeasuringLib.MeasuringTool.getMPoint(self.endJointPath)
        
        distance = MeasuringLib.MeasuringTool.getVectorLengthBetween(startPoint, endPoint)
        
        #create null groups
        
        startNull = cmds.group(empty = True, name = '%s_Start_Null'%name)
        startNullParentConstraint = cmds.parentConstraint(self.startJoint,startNull)
        cmds.delete(startNullParentConstraint)
        
        inc = 0
        floatingNulls =[]
        pointArray = []
        for i in range(numPoints):
            
            zeroString = ''
            if i > 8:
                zeroString = '0'
                
            floatingNull = cmds.group(empty = True, name = '%s_Floating_0%s%i_Null'%(name,zeroString,(i + 1)))
            cmds.move(inc*aimVector[0],inc*aimVector[1],inc*aimVector[2])
            cmds.parent(floatingNull,startNull,r = True)
            
            inc += distance/(numPoints-1)
            pointArray.append(cmds.xform(floatingNull,q = True, ws = True, translation = True))
            floatingNulls.append(floatingNull)
            
        #createCurve
        
        if len(pointArray) > 4:
            
            curve = cmds.curve(p = pointArray, degree = 3,n = '%s_Curve'%name)
            curveShape = cmds.listRelatives(curve, type = 'shape')[0]
            
        else:
        
            curve = cmds.curve(p = pointArray, degree = 1,n = '%s_Curve'%name)
            curveShape = cmds.listRelatives(curve, type = 'shape')[0]
            
        inc = 0
        nameInc = 1
        zeroString = ''
        if len(floatingNulls) > 9:
            zeroString = '0'
            
        locatorGroup = cmds.group(empty = True, name = '%s_Loc_Group'%name)
        floatingJointGroup = cmds.group(empty = True, n = '%s_Floating_Jnt_Group'%name)
        floatingjointArray = []
        locatorArray = []
        
        for null in floatingNulls:
            
            locator = cmds.spaceLocator(n = '%s_Floating_%s0%i_Loc'%(name,zeroString,nameInc))[0]
            motionPathNode = cmds.createNode('motionPath', n = '%s_Floating_%s0%i_MotionPath'%(name,zeroString,nameInc))
            cmds.setAttr('%s.fractionMode'%motionPathNode, 1)
            cmds.connectAttr ('%s.worldSpace[0]'%curveShape, '%s.geometryPath'%motionPathNode)
            
            cmds.connectAttr('%s.xCoordinate'%motionPathNode,'%s.tx'%(locator))
            cmds.connectAttr('%s.yCoordinate'%motionPathNode,'%s.ty'%(locator))
            cmds.connectAttr('%s.zCoordinate'%motionPathNode,'%s.tz'%(locator))
            
            cmds.setAttr('%s.uValue'%motionPathNode, inc)
            cmds.parent(locator,locatorGroup)
            
            cmds.select(cl = True)
            floatingJoint = cmds.joint(n = '%s_Floating_%s0%i_Jnt'%(name,zeroString,nameInc))
            jointGroup = cmds.group(empty = True, n = '%s_Floating_%s0%i_Jnt_Group'%(name,zeroString,nameInc))
            cmds.parent(floatingJoint,jointGroup)
            cmds.parent(jointGroup,floatingJointGroup)
            
            cmds.pointConstraint(locator,jointGroup)
            
            floatingjointArray.append(jointGroup)
            locatorArray.append(locator)
            
            inc += 1.0/(numPoints-1)
            nameInc += 1
            
        #create up vector
        
        upVectorLocGroup = cmds.group(empty = True, n = '%s_UpVector_Loc_Group'%name)
        upVectorLoc = cmds.spaceLocator(n = '%s_UpVector_Loc'%name)[0]
        cmds.parent(upVectorLoc, upVectorLocGroup)
        cmds.parentConstraint(self.startJoint,upVectorLocGroup) 
        cmds.move(upVector[0],upVector[1],upVector[2], upVectorLoc, os = True)
        
        
            
        #create aim constraints
        inc = 0
        for loc in locatorArray:
            
            if not loc == locatorArray[-1]:
                
                aimConstraint = cmds.aimConstraint(floatingjointArray[inc+1],floatingjointArray[inc],aimVector = aimVector, upVector = upVector , worldUpType = 1)[0]
                cmds.connectAttr('%s.worldMatrix[0]'%upVectorLoc,'%s.worldUpMatrix'%aimConstraint)

            inc += 1
            
        #create deformer joints
        
        deformerJointStartGroup = cmds.group(empty = True, n = '%s_Start_Deformer_Jnt_Group'%name)
        cmds.select(cl = True)
        deformerJointStart = cmds.joint(n = '%s_Start_Deformer_Jnt'%name)
        cmds.parent(deformerJointStart, deformerJointStartGroup)
        cmds.pointConstraint(startCtrl,deformerJointStartGroup)
        aimConstraint = cmds.aimConstraint(endCtrl,deformerJointStartGroup,aimVector = aimVector, upVector = upVector , worldUpType = 1)[0]
        cmds.connectAttr('%s.worldMatrix[0]'%upVectorLoc,'%s.worldUpMatrix'%aimConstraint)
        
        deformerJointEndGroup = cmds.group(empty = True, n = '%s_End_Deformer_Jnt_Group'%name)
        cmds.select(cl = True)
        deformerJointEnd = cmds.joint(n = '%s_End_Deformer_Jnt'%name)
        cmds.parent(deformerJointEnd, deformerJointEndGroup)
        cmds.pointConstraint(endCtrl,deformerJointEndGroup)
        aimConstraint = cmds.aimConstraint(startCtrl,deformerJointEndGroup,aimVector = aimVector, upVector = upVector , worldUpType = 1)[0]
        cmds.connectAttr('%s.worldMatrix[0]'%upVectorLoc,'%s.worldUpMatrix'%aimConstraint)
        
        cmds.skinCluster(deformerJointStart, deformerJointEnd, curve)

            
        cmds.delete(startNull)
    
    
    
        

    