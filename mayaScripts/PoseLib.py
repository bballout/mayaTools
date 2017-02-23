'''
Created on Jun 28, 2012

@author: balloutb
'''

import maya.cmds as cmds
import UILib
import os

class PoseManager(object):

    '''
    Class for saving and reading poses and controlSets
    '''

    #nothing to initialize
    def __init__(self):
        pass
     
    #method for reading controlSet files    
    @staticmethod   
    def controlsFromSet(path,ctrlSet):
     
        ctrls = []

        if os.path.exists('%s/controlSets/%s'%(path,ctrlSet[0])):
            
            f = open('%s/controlSets/%s'%(path,ctrlSet[0]), 'r')
            lines = f.readlines()
            f.seek(0)
                
            for line in lines:
                if ((f.readline()).split('\n')[0]) == '[CTRL]':
                    ctrls.append((f.readline()).split('\n')[0])
                              
        return ctrls
    
    #method for returning all attributes in a ctrl with the name 'EXAMPLE_Ctrl'
    #addition ctrls can be added in arguments
    @staticmethod    
    def allCtrlAttrs(*additionalCtls):

        ctrlsAttrs = []

        ctrls = cmds.ls('*_Ctrl')
        for ctrl in additionalCtls:
            ctrls.append(ctrl)
            attrs = cmds.listAttr(ctrl, k = True, l = False)
            for attr in attrs:
                ctrlsAttrs.append('ctrl.attr'%(ctrl,attr))

        return ctrlsAttrs
    
    #method for returning keyable attributes of each item in a controlSet 
    @staticmethod
    def controlsAttrsFromSet(path,ctrlSet):    

        ctrls = PoseManager.controlsFromSet()
        ctrlsAttrs = []

        if os.path.exists('%s/controlSets/%s'%(path,ctrlSet)):
        
            for ctrl in ctrls:
                attrs = cmds.listAttr(ctrl, k = True, l = False)
                for attr in attrs:
                    ctrlsAttrs.append('%s.%s'%(ctrl,attr))
        
        return ctrlsAttrs
    
    #method for returning ctrls in a poseFile
    @staticmethod    
    def controlsFromPoseFile(path,poseFileName):
           
        ctrls = []
        
        if os.path.exists('%s/poses/%s'%(path,poseFileName)):
                f = open('%s/poses/%s'%(path,poseFileName), 'r')
                lines = f.readlines()
                f.seek(0)
                
                for line in lines:
                    if ((f.readline()).split('\n')[0]) == '[ATTR]':
                        ctrls.append((f.readline()).split('\n')[0])
                        
                f.close()
                
        return ctrls
    
    #method for writing a poseFile        
    @staticmethod
    def poseWrite(path,poseFileName,ctrlSet):
        
        
        if path != '':
        
            if os.path.exists(path) and poseFileName != "":
            
                if os.path.exists('%s/poses/'%path) != True:
                    os.mkdir('%s/poses/'%path)
                
                ctrlsAttrs = PoseManager.controlsAttrsFromSet()
            
                f = open(path + '/poses/' + poseFileName,'w+')
                
                for attr in ctrlsAttrs:
                    attrVal = str(cmds.getAttr(attr))
                    f.write('[ATTR]\n')
                    f.write(attr + '\n')
                    f.write('[VAL]\n')
                    f.write(attrVal + '\n')

                f.close()
                
                if os.path.exists('%s/images/'%path) != True:
                    os.mkdir('%s/images/'%path)
                    
                #image capture here
                UILib.captureViewport(path = '%s/images/%s.iff'(path,poseFileName) , imageFormat = 'iff')
                
    
    #method for re-writing a poseFile
    @staticmethod            
    def poseReWrite(path,poseFileName):
                
        if os.path.exists('%s/poses/%s'%(path,poseFileName)):
            f = open('%s/poses/%s'%(path,poseFileName), 'r+')
            lines = f.readlines()
            f.seek(0)

            ctrls = []    

            for line in lines:
                if ((f.readline()).split('\n')[0]) == '[ATTR]':
                    ctrls.append((f.readline()).split('\n')[0])

            f.seek(0)

            for ctrl in ctrls:
                attrVal = str(cmds.getAttr(ctrl))
                f.write('[ATTR]\n')
                f.write(ctrl + '\n')
                f.write('[VAL]\n')
                f.write(attrVal + '\n')
                
            if os.path.exists('%s/images/'%path) != True:
                    os.mkdir('%s/images/'%path)
                    
   
            f.close()
            UILib.captureViewport(path = '%s/images/%s.iff'(path,poseFileName) , imageFormat = 'iff')
    
    #method for reading a poseFile
    @staticmethod
    def poseRead(path,poseFileName):
        
        if path != '':
        
            if os.path.exists('%s/poses/'%path) or poseFileName != '':
            
                
                f = open(('%s/poses/%s'%(path,poseFileName)), 'r')

                lines = f.readlines()
                f.seek(0)
            
                for line in lines:
                    if ((f.readline()).split('\n')[0]) == '[ATTR]':
                        ctrlAttr = ((f.readline()).split('\n')[0])
                        if ((f.readline()).split('\n')[0]) == '[VAL]':
                            attrVal = ((f.readline()).split('\n')[0])
                        
                            if attrVal.isdigit() or len(attrVal.split('.')) > 1:
                            
                                try:    
                                    eval('cmds.setAttr( "' + ctrlAttr + '",' + attrVal + ')')

                                except RuntimeError:
                            
                                    ##print(ctrlAttr + ' is locked.\n')
                                    pass
                                    
                            else:
                            
                                try:    
                                    eval('cmds.setAttr( "' + ctrlAttr + '","' + attrVal + '")')

                                except RuntimeError:
                            
                                    ##print(ctrlAttr + ' is locked.\n')
                                    pass
                            
                f.close()
            
    
    #method for writing a controlSet file
    #will write out ctrls that are currently selected
    #if mode == 'init'...a default file will be written for all ctrls
    #the default file will be named 'All' and it will contain all ctrls with the name 'EXAMPLE_Ctrl'
    #additional ctrls can be included in the additionalCtrls argument
    @staticmethod
    def controlSetWrite(path,controlSetName,mode = 'Save',*additionalCtrls):
        
        
        if path != '':
        
            if os.path.exists('%s/controlSets/'%path) != True:
                os.mkdir('%s/controlSets/'%path)
            
            if(mode == 'init'):
                ctrls = cmds.ls('*_Ctrl')
                for ctrl in additionalCtrls:
                    ctrls.append(ctrl)
                controlSetName = 'All'
        
            else:
                ctrls = cmds.ls(sl = True)

            if len(ctrls) > 0 and controlSetName != '':
                
                f = open('%s/controlSets/%s'%(path,controlSetName), 'w+')
            
                for ctrl in ctrls:
                        
                        f.write('[CTRL]\n')
                        f.write(ctrl + '\n')
            
                f.close()
    
    #method for adding ctrls to a controlSet file
    @staticmethod           
    def addToControlSet(path,controlSetName):
    
        
        if path != '':

            f = open('%s/controlSets/%s'%(path,controlSetName), 'r+')
                
            ctrls = PoseManager.controlsFromSet()
            newCtrls = cmds.ls(sl = True)
                
            for ctrl in newCtrls:
                ctrls.append(ctrl)
                    
            setCtrls = set(ctrls)
            cleanCtrlList = []
                
            for item in setCtrls:
                cleanCtrlList.append(item)
                    
            f.seek(0)
                
            for ctrl in cleanCtrlList:
                            
                f.write('[CTRL]\n')
                f.write(ctrl + '\n')
                    
            f.close()        
