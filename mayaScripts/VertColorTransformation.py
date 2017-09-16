import maya.cmds as cmds
import maya.OpenMaya as om
import GenAPI

class ColorDeta():
  def __init__(self,baseMesh,blends):
    self.baseMesh = baseMesh
    self.blends = blends

  def getTranslationVectors(self,fromMesh):
    '''
    method build an array of vectors for translation
    input fromMesh (python string)
    '''
    fromMeshPath = GenAPI.getDagPath(fromMesh)
    geoItr = om.MItGeometry(fromMeshPath)
    pointArrayA = om.MPointArray()
    geoItr.allPositions(pointArrayA, om.MSpace.kObject)
    
    if cmds.nodeType(self.baseMesh) == 'transform':
          shape = cmds.listRelatives(shape, type = 'shape')[0]
    else:
      shape = self.baseMesh
    
    pointArrayB = ShapeTool.getPointArray(self.baseMesh)
    
    if pointArrayA.length() == pointArrayB.length():
        outVectorArray = om.MVectorArray()
        itr = 0
        while itr <= pointArrayA.length(): 
            vectorA = pointArrayA[itr]
            vectorB = pointArrayB[itr]
            vectorC = vectorA - vectorB               
            outVectorArray.append(vectorC)
            itr += 1        
    return  outVectorArray
      
  @staticmethod    
  def getPointArray(shape):  
      '''
      method gathers point array from verts
      output pointArray(mPointArray)
      '''
      if cmds.nodeType(shape) == 'transform':
          shape = cmds.listRelatives(shape, type = 'shape')[0]
      
      geoPath = GenAPI.getDagPath(shape)
      geoItr = om.MItGeometry(geoPath)
      pointArray = om.MPointArray()
      
      geoItr.allPositions(pointArray, om.MSpace.kObject)
      
      return pointArray
    
  def getNormalizeValue(self):
    pass
  
  def setColor(self):
    pass
  
  def addUVSet(self):
      pass