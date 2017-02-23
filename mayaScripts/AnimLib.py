'''
Created on Oct 30, 2012

@author: balloutb
'''

import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import GenAPI

class AnimTool():
    
    curveData = dict()
    
    def __init__(self,transformNodes = []):

        self.transformNodes = transformNodes
        self.curves = dict()
            
    #method for finding all animation curves
    def getAnimCurveNodes(self):
        
        animCurves = []
        
        for transform in self.transformNodes:
            
            self.curves
            
            
            animCurveTU = cmds.listConnections(transform,type = 'animCurveTU')
            animCurveTA = cmds.listConnections(transform,type = 'animCurveTA')
            animCurveTL = cmds.listConnections(transform,type = 'animCurveTL')
        
            for curve in animCurveTU:
                animCurves.append(curve)
                
            for curve in animCurveTA:
                animCurves.append(curve)
                
            for curve in animCurveTL:
                animCurves.append(curve)
            
        return animCurves
        self.curves = animCurves
        
    
        def decomposeCurves(self):
            pass