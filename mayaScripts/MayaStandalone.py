'''
Created on Oct 17, 2016

@author: bballout
'''
import maya.cmds as cmds
import maya.standalone as standalone
import sys



filePath = 'x:/i20/devel/assets/source/missions/gp_a2_esu/ms_a2_esu_universityfight_intro/ms_a2_esu_universityfight_intro.mb'

def start(filePath):
  standalone.initialize("Python")
  
  sys.path.append('x:/tech_art/maya/shared/scripts') 
  import userSetup
  import igMBatCine2Export
  reload(igMBatCine2Export)
  openFile = cmds.file(filePath, o=True)
  exporter = igMBatCine2Export.MBatExport()
  exporter.export()

  standalone.uninitialize()

start(filePath)