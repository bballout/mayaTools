'''
Created on Feb 3, 2014

@author: bballout
'''

import maya.cmds as cmds
import maya.OpenMaya as om
import GenAPI
import pickle

eyeTransform = 'Eye_Transform_Ctrl_Offset'
leftEyeTransform = 'L_Eye_Transform_Offset'
rightEyeTransform = 'R_Eye_Transform_Offset'
leftEyeLookAt = 'L_Eye_LookAt_Placement_Ctrl'
rightEyeLookAt = 'R_Eye_LookAt_Placement_Ctrl'
leftEyeCorner01 = 'L_Eye_L_Corner_Ctrl_Offset'
leftEyeCorner02 = 'L_Eye_R_Corner_Ctrl_Offset'
rightEyeCorner01 = 'R_Eye_L_Corner_Ctrl_Offset'
rightEyeCorner02 = 'R_Eye_R_Corner_Ctrl_Offset'
leftEyeUpperLid = 'L_Eye_UpperLid_Ctrl_Offset'
leftEyeLowerLid = 'L_Eye_LowerLid_Ctrl_Offset'
rightEyeUpperLid = 'R_Eye_UpperLid_Ctrl_Offset'
rightEyeLowerLid = 'R_Eye_LowerLid_Ctrl_Offset'
leftEyeLat = 'L_Eye_Placement_LatticeShape'
rightEyeLat = 'R_Eye_Placement_LatticeShape'

placementAttrs =  ['Eye_Transform_Ctrl.leftEyeIrisScale',
                    'Eye_Transform_Ctrl.leftEyeIrisWidth',
                    'Eye_Transform_Ctrl.leftEyeIrisHeight',
                    'Eye_Transform_Ctrl.leftEyePupilScale',
                    'Eye_Transform_Ctrl.leftEyePupilWidth',
                    'Eye_Transform_Ctrl.leftEyePupilHeight',
                    'Eye_Transform_Ctrl.rightEyeIrisScale',
                    'Eye_Transform_Ctrl.rightEyeIrisWidth',
                    'Eye_Transform_Ctrl.rightEyeIrisHeight',
                    'Eye_Transform_Ctrl.rightEyePupilScale',
                    'Eye_Transform_Ctrl.rightEyePupilWidth',
                    'Eye_Transform_Ctrl.rightEyePupilHeight',
                    'Eye_Transform_Ctrl.leftEyeLidThickness',
                    'Eye_Transform_Ctrl.rightEyeLidThickness']

def save(filePath):
    
    output = open(filePath,'wb')
    
    eyePlacement = dict()
    
    try:
        eyeTransformPos = cmds.xform(eyeTransform,q = True, ws = True,translation = True)
        eyeTransformRotate = cmds.xform(eyeTransform,q = True, ws = True,rotation = True)
        eyeTransformScale = cmds.xform(eyeTransform,q = True, r = True,scale = True)
        
    except:
        eyeTransformPos = [0,0,0]
        eyeTransformRotate = [0,0,0]
        eyeTransformScale = [1,1,1]
    
    try:
        leftEyeTransformPos = cmds.xform(leftEyeTransform,q = True, ws = True,translation = True)
        leftEyeTransformRotate = cmds.xform(leftEyeTransform,q = True, ws = True,rotation = True)
        leftEyeTransformScale = cmds.xform(leftEyeTransform,q = True, r = True,scale = True)
        
    except:
        leftEyeTransformPos = [0,0,0]
        leftEyeTransformRotate = [0,0,0]
        leftEyeTransformScale = [1,1,1]
    
    try:
        rightEyeTransformPos = cmds.xform(rightEyeTransform,q = True, ws = True,translation = True)
        rightEyeTransformRotate = cmds.xform(rightEyeTransform,q = True, ws = True,rotation = True)
        rightEyeTransformScale = cmds.xform(rightEyeTransform,q = True, r = True,scale = True)
        
    except:
        rightEyeTransformPos = [0,0,0]
        rightEyeTransformRotate = [0,0,0]
        rightEyeTransformScale = [1,1,1]
        
    try:
        leftEyeLookAtPos = cmds.xform(leftEyeLookAt,q = True, ws = True, translation = True)
        rightEyeLookAtPos = cmds.xform(rightEyeLookAt,q = True, ws = True, translation = True)
        
    except:
        leftEyeLookAtPos = [0,0,0]
        rightEyeLookAtPos = [0,0,0]
        
    try:
        leftEyeCorner01Rotation = cmds.xform(leftEyeCorner01,q = True, ws = True, rotation = True)
        leftEyeCorner02Rotation = cmds.xform(leftEyeCorner02,q = True, ws = True, rotation = True)
        rightEyeCorner01Rotation = cmds.xform(rightEyeCorner01,q = True, ws = True, rotation = True)
        rightEyeCorner02Rotation = cmds.xform(rightEyeCorner02,q = True, ws = True, rotation = True)
        
    except:
        leftEyeCorner01Rotation = [0,0,0]
        leftEyeCorner02Rotation = [0,0,0]
        rightEyeCorner01Rotation = [0,0,0]
        rightEyeCorner02Rotation = [0,0,0]
    
    try:
        leftEyeUpperLidRotation = cmds.xform(leftEyeUpperLid,q = True, ws = True, rotation = True)
        leftEyeLowerLidRotation = cmds.xform(leftEyeLowerLid,q = True, ws = True, rotation = True)
        rightEyeUpperLidRotation = cmds.xform(rightEyeUpperLid,q = True, ws = True, rotation = True)
        rightEyeLowerLidRotation = cmds.xform(rightEyeLowerLid,q = True, ws = True, rotation = True)
        
    except:
        leftEyeUpperLidRotation = [0,0,0]
        leftEyeLowerLidRotation = [0,0,0]
        rightEyeUpperLidRotation = [0,0,0]
        rightEyeLowerLidRotation = [0,0,0]
    
    eyePlacement['eyeTransformPos'] = eyeTransformPos
    eyePlacement['eyeTransformRotate'] = eyeTransformRotate
    eyePlacement['eyeTransformScale'] = eyeTransformScale
    
    eyePlacement['leftEyeTransformPos'] = leftEyeTransformPos
    eyePlacement['leftEyeTransformRotate'] = leftEyeTransformRotate
    eyePlacement['leftEyeTransformScale']  = leftEyeTransformScale
    
    eyePlacement['rightEyeTransformPos'] = rightEyeTransformPos
    eyePlacement['rightEyeTransformRotate'] = rightEyeTransformRotate
    eyePlacement['rightEyeTransformScale']  = rightEyeTransformScale
    
    eyePlacement['leftEyeLookAtPos'] = leftEyeLookAtPos
    eyePlacement['rightEyeLookAtPos'] = rightEyeLookAtPos
    
    eyePlacement['leftEyeCorner01Rotation'] = leftEyeCorner01Rotation
    eyePlacement['leftEyeCorner02Rotation'] = leftEyeCorner02Rotation
    eyePlacement['rightEyeCorner01Rotation']  = rightEyeCorner01Rotation
    eyePlacement['rightEyeCorner02Rotation'] = rightEyeCorner02Rotation
    
    eyePlacement['leftEyeUpperLidRotation'] = leftEyeUpperLidRotation
    eyePlacement['leftEyeLowerLidRotation'] = leftEyeLowerLidRotation
    eyePlacement['rightEyeUpperLidRotation']  = rightEyeUpperLidRotation
    eyePlacement['rightEyeLowerLidRotation'] = rightEyeLowerLidRotation
    
    attrValues = []
    
    for attr in placementAttrs:
        value = cmds.getAttr(attr)
        attrValues.append(value)
        
    eyePlacement['attrs'] = attrValues
    
    leftEyeLatPointPos = getLatticePointPos(leftEyeLat)
    rightEyeLatPointPos = getLatticePointPos(rightEyeLat)
    
    eyePlacement['leftEyeLatPointPos'] = leftEyeLatPointPos
    eyePlacement['rightEyeLatPointPos'] = rightEyeLatPointPos
    
    pickle.dump(eyePlacement,output)
    output.close()
    
    print 'saved %s'%filePath
    
def load(filePath):
        
    inputFile = open(filePath,'rb')
    eyePlacement = pickle.load(inputFile)
    inputFile.close()
    
    eyeTransformPos = eyePlacement['eyeTransformPos']
    eyeTransformRotate = eyePlacement['eyeTransformRotate']
    eyeTransformScale = eyePlacement['eyeTransformScale']
    cmds.move(eyeTransformPos[0],eyeTransformPos[1],eyeTransformPos[2],eyeTransform,ws = True)
    cmds.rotate(eyeTransformRotate[0],eyeTransformRotate[1],eyeTransformRotate[2],eyeTransform,ws = True)
    cmds.scale(eyeTransformScale[0],eyeTransformScale[1],eyeTransformScale[2],eyeTransform,ws = True)
    
    leftEyeTransformPos = eyePlacement['leftEyeTransformPos']
    leftEyeTransformRotate = eyePlacement['leftEyeTransformRotate']
    leftEyeTransformScale = eyePlacement['leftEyeTransformScale']
    cmds.move(leftEyeTransformPos[0],leftEyeTransformPos[1],leftEyeTransformPos[2],leftEyeTransform,ws = True)
    cmds.rotate(leftEyeTransformRotate[0],leftEyeTransformRotate[1],leftEyeTransformRotate[2],leftEyeTransform,ws = True)
    cmds.scale(leftEyeTransformScale[0],leftEyeTransformScale[1],leftEyeTransformScale[2],leftEyeTransform,ws = True)
    
    rightEyeTransformPos = eyePlacement['rightEyeTransformPos']
    rightEyeTransformRotate = eyePlacement['rightEyeTransformRotate']
    rightEyeTransformScale = eyePlacement['rightEyeTransformScale']
    cmds.move(rightEyeTransformPos[0],rightEyeTransformPos[1],rightEyeTransformPos[2],rightEyeTransform,ws = True)
    cmds.rotate(rightEyeTransformRotate[0],rightEyeTransformRotate[1],rightEyeTransformRotate[2],rightEyeTransform,ws = True)
    cmds.scale(rightEyeTransformScale[0],rightEyeTransformScale[1],rightEyeTransformScale[2],rightEyeTransform,ws = True)
    
    leftEyeLookAtPos = eyePlacement['leftEyeLookAtPos'] 
    rightEyeLookAtPos = eyePlacement['rightEyeLookAtPos']
    cmds.move(leftEyeLookAtPos[0],leftEyeLookAtPos[1],leftEyeLookAtPos[2],leftEyeLookAt,ws = True)
    cmds.move(rightEyeLookAtPos[0],rightEyeLookAtPos[1],rightEyeLookAtPos[2],rightEyeLookAt,ws = True)
    try:
        leftEyeCorner01Rotation = eyePlacement['leftEyeCorner01Rotation']
        leftEyeCorner02Rotation = eyePlacement['leftEyeCorner02Rotation']
        rightEyeCorner01Rotation = eyePlacement['rightEyeCorner01Rotation'] 
        rightEyeCorner02Rotation = eyePlacement['rightEyeCorner02Rotation']
        cmds.rotate(leftEyeCorner01Rotation[0],leftEyeCorner01Rotation[1],leftEyeCorner01Rotation[2],leftEyeCorner01,ws = True)
        cmds.rotate(leftEyeCorner02Rotation[0],leftEyeCorner02Rotation[1],leftEyeCorner02Rotation[2],leftEyeCorner02,ws = True)
        cmds.rotate(rightEyeCorner01Rotation[0],rightEyeCorner01Rotation[1],rightEyeCorner01Rotation[2],rightEyeCorner01,ws = True)
        cmds.rotate(rightEyeCorner02Rotation[0],rightEyeCorner02Rotation[1],rightEyeCorner02Rotation[2],rightEyeCorner02,ws = True)
        
    except:
        pass
    
    try:
    
        leftEyeUpperLidRotation = eyePlacement['leftEyeUpperLidRotation']
        leftEyeLowerLidRotation = eyePlacement['leftEyeLowerLidRotation']
        rightEyeUpperLidRotation = eyePlacement['rightEyeUpperLidRotation']
        rightEyeLowerLidRotation = eyePlacement['rightEyeLowerLidRotation']
        cmds.rotate(leftEyeUpperLidRotation[0],leftEyeUpperLidRotation[1],leftEyeUpperLidRotation[2],leftEyeUpperLid,ws = True)
        cmds.rotate(leftEyeLowerLidRotation[0],leftEyeLowerLidRotation[1],leftEyeLowerLidRotation[2],leftEyeLowerLid,ws = True)
        cmds.rotate(rightEyeUpperLidRotation[0],rightEyeUpperLidRotation[1],rightEyeUpperLidRotation[2],rightEyeUpperLid,ws = True)
        cmds.rotate(rightEyeLowerLidRotation[0],rightEyeLowerLidRotation[1],rightEyeLowerLidRotation[2],rightEyeLowerLid,ws = True)
        
    except:
        pass
        
    for i in range(len(placementAttrs)):
        value = eyePlacement['attrs'][i]
        try:
            cmds.setAttr(placementAttrs[i],value)
        except:
            pass
        
    leftEyeLatPointPos = eyePlacement['leftEyeLatPointPos']
    rightEyeLatPointPos = eyePlacement['rightEyeLatPointPos']
    
    setLatticePointPos(leftEyeLat,leftEyeLatPointPos)
    setLatticePointPos(rightEyeLat,rightEyeLatPointPos)
    
    print 'loaded %s'%filePath


def getLatticePointPos(latticeShape):
    
    dagPath = GenAPI.getDagPath(latticeShape)
    geoItr = om.MItGeometry(dagPath)
    
    latPointPos = []
    
    while not geoItr.isDone():
        
        position = geoItr.position(om.MSpace.kWorld)
        latPointPos.append([position.x,position.y,position.z])
        geoItr.next()
        
    return latPointPos

def setLatticePointPos(latticeShape,positions):
    
    dagPath = GenAPI.getDagPath(latticeShape)
    geoItr = om.MItGeometry(dagPath)
    
    latPointPos = []
    
    while not geoItr.isDone():
        
        index = geoItr.index()
        position = positions[index]
        mpoint = om.MPoint(position[0],position[1],position[2])
        geoItr.setPosition(mpoint,om.MSpace.kWorld)
        
        geoItr.next()      