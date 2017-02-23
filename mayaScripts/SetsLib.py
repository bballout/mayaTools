'''
Created on Nov 12, 2013

@author: bballout
'''

import maya.cmds as cmds
import maya.OpenMaya as om
import GenAPI
import pickle

class SetFn():
    
    def __init__(self,sets = []):

        self.sets = sets
        self.__setFn = om.MFnSet()

    def getMemberSet(self,filePath):
        
        output = open(filePath,'wb')
        
        setsToDump = []
        
        for objectSet in self.sets:
            
            print 'saving %s set...'%objectSet
            
            setObject = GenAPI.getMObject(objectSet)
            self.__setFn.setObject(setObject)
            
            selectionList = om.MSelectionList()
            self.__setFn.getMembers(selectionList,True)
            selectionListItr = om.MItSelectionList(selectionList)
            
            members = dict()
            members['setName'] = objectSet 
            members['dagMembers'] = []
            members['components'] = []
            
            while not selectionListItr.isDone():
                
                dagPath = om.MDagPath()
                component = om.MObject()
                
                selectionListItr.getDagPath(dagPath,component)
                
                pathName = dagPath.partialPathName()
                
                if not component.isNull():
                    
                    if component.apiTypeStr() == 'kMeshPolygonComponent':
                        
                        componentFn = om.MFnSingleIndexedComponent(component)
                        elementArray = om.MIntArray()
                        componentFn.getElements(elementArray)
                        
                        for element in elementArray:
                            
                            members['components'].append('%s.f[%i]'%(pathName,element))
                
                else:
                    members['dagMembers'].append(pathName) 
                
                selectionListItr.next()
                
            setsToDump.append(members)
            
                
        pickle.dump(setsToDump,output)
        output.close()
        print 'I\'m Done!'
        
    def setMemberSet(self,filePath):
        
        inputFile = open(filePath,'rb')
        sets = pickle.load(inputFile)
        inputFile.close()
        
        for objectSet in sets:
            
            print 'creating %s set.....'%objectSet['setName']
            
            newSet = cmds.sets(name = objectSet['setName'])
            
            for member in objectSet['dagMembers']:
                cmds.sets(member,e = True,add = newSet)
                
            for member in objectSet['components']:
                cmds.sets(member,e = True,add = newSet)
                
        print 'I\'m Done!'