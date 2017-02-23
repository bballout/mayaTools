'''
Created on Oct 2, 2013

@author: bballout
'''
import maya.OpenMaya as om
import maya.cmds as cmds
import pickle
import GenAPI


class SetFn():
    
    def __init__(self,sets = []):

        self.sets = sets
        self.__setFn = om.MFnSet()

    def getMemberSet(self,filePath):
        
        output = open(filePath,'wb')
        
        selectionList = om.MSelectionList()
        self.__setFn.getMembers(selectionList,True)
        selectionListItr = om.MItSelectionList(selectionList)
        
        setList = []
        
        for set in self.sets:
        
            members = dict()
            members['setName'] = set 
            members['dagMembers'] = []
            members['components'] = dict()
            
            while not selectionListItr.isDone():
                
                dagPath = om.MDagPath()
                component = om.MObject()
                
                selectionListItr.getDagPath(dagPath,component)
                
                pathName = dagPath.fullPathName()
                
                if not component.isNull():
                    
                    if component.apiTypeStr() == 'kMeshPolygonComponent':
                        
                        members['components'][pathName] = []
                        
                        componentFn = om.MFnSingleIndexedComponent(component)
                        elementArray = om.MIntArray()
                        componentFn.getElements(elementArray)
                        
                        for element in elementArray:
                            
                            members['components'][pathName].append(element)
                
                else:
                    members['dagMembers'].append(pathName) 
                
                setList.append(members)
                selectionListItr.next()
            
        pickle.dump(setList,output)
        output.close()
        
    def setMemberSet(self,filePath):
        
        inputFile = open(filePath,'rb')
        sets = pickle.load(inputFile)
        inputFile.close()
        
        for set in sets:
            
            newSet = cmds.sets(name = set['name'])
            
            for member in set['dagMembers']:
                cmds.sets(newSet,e = True,add = member)
                
            for dagMember in set['components']:
                pass

class SaveShave():
    
    def __init__(self,shaveNode = ''):
        
        self.shaveNode = shaveNode

    def getMemberSet(self,filePath):
        
        output = open(filePath,'wb')
        
        selectionList = om.MSelectionList()
        self.__setFn.getMembers(selectionList,True)
        selectionListItr = om.MItSelectionList(selectionList)
        
        members = dict()
        members['setName'] = self.set 
        members['dagMembers'] = []
        members['components'] = dict()
        
        while not selectionListItr.isDone():
            
            dagPath = om.MDagPath()
            component = om.MObject()
            
            selectionListItr.getDagPath(dagPath,component)
            
            pathName = dagPath.fullPathName()
            
            if not component.isNull():
                
                if component.apiTypeStr() == 'kMeshPolygonComponent':
                    
                    members['components'][pathName] = []
                    
                    componentFn = om.MFnSingleIndexedComponent(component)
                    elementArray = om.MIntArray()
                    componentFn.getElements(elementArray)
                    
                    for element in elementArray:
                        
                        members['components'][pathName].append(element)
            
            else:
                members['dagMembers'].append(pathName) 
            
            selectionListItr.next()
            
        pickle.dump(members,output)
        output.close()
        
    def getShaveAttrs(self,filePath):
        
        output = open(filePath,'wb')
        attrDict = dict()
        shaveAttrs = cmds.listAttr(self.shaveNode,se = True)
        valueSetAttrs = []
        connectedAttrs = []
        
        for attr in shaveAttrs:
            
            try:
                if cmds.connectionInfo('%s.%s'%(self.shaveNode,attr),id = True):
                    connection = cmds.connectionInfo('%s.%s'%(self.shaveNode,attr),sfd = True)
                    connectedAttrs.append([connection,attr])
                    
                else:
                    attrValue = cmds.getAttr('%s.%s'%(self.shaveNode,attr))
                    print attr,attrValue
                    valueSetAttrs.append([attr,attrValue])
            except (RuntimeError,ValueError):
                pass
        
        attrDict['valueSet'] =  valueSetAttrs      
        attrDict['connected'] = connectedAttrs
        
        pickle.dump(attrDict,output)
        output.close()

    def setShaveAttrs(self,filePath):
        
        inputFile = open(filePath,'rb')
        attrDict = pickle.load(inputFile)
        inputFile.close()
        
        for attr in attrDict['valueSet']:
            
            try:
                cmds.setAttr('%s.%s'%(self.shaveNode,attr[0]),attr[1])
                
            except:
                print 'couldnt set %s to %s'%(attr[0],attr[1])
                
            for attr in attrDict['connected']:
                
                try:
                    print attr[0],attr[1]
                    cmds.connectAttr(attr[0],'%s.%s'%(self.shaveNode,attr[1]),f = True)
                
                except:
                    pass

