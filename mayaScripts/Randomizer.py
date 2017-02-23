'''
Created on Feb 24, 2014

@author: bballout
'''

import maya.cmds as cmds
import random

def randomize(objList = []):
    
    random.shuffle(objList)
    return objList

def listPercent(percent,selection):
    
    count = len(selection)
    percentPoint = percent/100.00
    
    print count,percentPoint
    newCount =  int(percentPoint * count)
    print newCount
    newList = selection[0:newCount]
    return newList

def win():
    
    if cmds.window('randWin',q = True ,exists = True):
        cmds.deleteUI('randWin')
    
    window = cmds.window('randWin',title = 'Selection Randomizer')
    cmds.columnLayout(adj = True)
    intField = cmds.intField('randField')
    cmds.button('selectButton',l = 'Select',c = 'uiFunc()',min = 0, max = 100)
    cmds.showWindow(window)
    
def uiFunc():
    
    percent = cmds.intField('randField',q = True, value = True)
    selection = cmds.ls(sl = True)
    if selection:
        
        randomize(selection)
        listA = listPercent(percent,selection)
        if listA:
            cmds.select(listA)
            
