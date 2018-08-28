'''
Created on Oct 30, 2012

@author: balloutb
'''

import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import GenAPI

class AnimTool():
    
    transformObjects = []
    transformDagPaths = []
    
    def __init__(self,transformNodes = []):

        self.transformNodes = transformNodes
        
        for node in self.transformNodes:
            
            self.transformObjects.append(GenAPI.getMObject(node))
            self.transformDagPaths.append(GenAPI.getDagPath(node))
            
    @staticmethod
    #method for finding all animation curves
    #output animList (MObjectArray)
    def getAllAnimation():
        
        animCurveTU = cmds.ls(type = 'animCurveTU')
        animCurveTA = cmds.ls(type = 'animCurveTA')
        animCurveTL = cmds.ls(type = 'animCurveTU')
        
        animCurves = animCurveTU + animCurveTA + animCurveTL
        
        objectArray = om.MObjectArray()
        
        for curve in animCurves:
            
            mobject = GenAPI.getMObject(curve)
            objectArray.add(mobject)
            
        return objectArray
        
        
    
    #method for collecting animation
    #output animationList (python list [MObjectArray,''....])
    def getAnimation(self,curveArray):
        
        
        animUtil = oma.MAnimUtil()
        animationList = []
        
        for path in self.transformDagPaths:
        
            animatedPlugArray = om.MPlugArray()
            animUtil.findAnimatedPlugs(path,animatedPlugArray,False)
            
            for plug in animatedPlugArray:
                
                print plug.name()
            
                animUtil.findAnimation(plug,curveArray)
                
                animationList.append(curveArray)
                
        return animationList                   