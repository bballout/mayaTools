'''
Created on Oct 17, 2016

@author: bballout
'''
import maya.cmds as cmds
import maya.standalone as standalone

def start(filePath,job):
  standalone.initialize("Python")
  openFile = cmds.file(filePath, o=True)
  job()
  standalone.uninitialize()

for i in range(50):
  def job():
    pass
  start(filePath = 'C:/Users/bballout/Desktop/armPoseTgts.mb',job = job)
  
  joints = cmds.ls(type = 'joint')
  for joint in joints:
    print joint