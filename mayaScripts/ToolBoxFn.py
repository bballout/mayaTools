'''
Created on Nov 28, 2012

@author: Bill
'''

import maya.cmds as cmds
import maya.mel as mel
import SkinningLib
import DeformerLib
import MayaScripts

'''Create Clusters'''

#extrap to clusters
def extrapToCluster(sel):
    
    transform = sel[0]
    meshes = sel[1:]
    
    DeformerLib.extrapToCluster(transform,meshes)
    
    
#set weights from transform
def extrapToExistingDeformer(deformer):
    
    sel = cmds.ls(sl = True)
    transform = sel[0]
    meshes = sel[1:]
    DeformerLib.extrapWeightsToExistingDeformer(transform,meshes,deformer)
    
#create cluster from soft selection   
def softSelToCluster():
    
    try:
        DeformerLib.createClusterFromSoftSelection('SoftSelection_CL')
    except:
        pass
    
    
#combine clusters
def combinClusters():
    
    clusterHandles = cmds.ls(sl = True)
    
    for cluster in clusterHandles:
        clusterTransform = cluster
        clusterDeformer = cmds.connectionInfo('%s.worldMatrix[0]'%clusterTransform,dfs = True)[0].split('.')[0]

        if cmds.nodeType(clusterDeformer) == 'cluster':
            DeformerLib.combineCluster(clusterHandles,True)
    
#mesh to cluster
def meshToCluster():
    
    fromMesh = cmds.ls(sl = True)[0]
    toMesh = cmds.ls(sl = True)[1]
    DeformerLib.createClusterFromMesh(fromMesh, toMesh)

    
#extrap skincluster from lattice
def latticeToSkincluster():

    SkinningLib.extrapFromLattice(cmds.ls(sl = True))

#extrap skincluster from wire
def wireToSkincluster():
    
    curveTransform = cmds.ls(sl = True)[0]
    curveShape = cmds.listRelatives(curveTransform, type = 'shape')[0]
    curveConnection = cmds.connectionInfo('%s.worldSpace[0]'%curveShape,dfs = True)[0]
    wire = curveConnection.split('.')[0]
    SkinningLib.extrapFromWire(wire)
    
#deformer to joint
def clusterToJoint(geoName,fromDeformer,fromJoint,toJoint):
    
    if cmds.nodeType(geoName) == 'transform':
        geoName = cmds.listRelatives(geoName,type = 'shape')[0]
    
    SkinningLib.clusterWeightToJoints(geoName,fromDeformer,fromJoint,toJoint)
    
#mesh to skincluster
def meshToSkincluster(meshFrom,meshTo,joints):
    
    SkinningLib.skinclusterFromMesh(meshFrom,meshTo,joints)

#mirror cluster 
def mirrorDeformer(transform,deformerName,prefix,oppPrefix,direction ,axis, table):
    
    DeformerLib.mirrorCluster(transform, deformerName, prefix, oppPrefix,direction,axis, table )
      
    
def mirrorDeformerWeights(deformerName,prefix,oppPrefix,direction ,axis, table):
    
    DeformerLib.mirrorDeformerWeights(deformerName, prefix, oppPrefix, axis,direction, table )
    
    
def flipClusterWeights(deformer,prefix,oppPrefix,direction ,axis, table):
    
    DeformerLib.flipDeformerWeights(deformer, prefix, oppPrefix, direction, axis, table)
#transfer
def transferWeights(fromMesh,toMesh,fromDeformer,toDeformer):
    
    deformerTool = DeformerLib.WeightListTool(fromMesh,fromDeformer)
    membershipList = deformerTool.getMembershipList()
    weightList = deformerTool.getWeightList()
    
    deformerTool.__init__(toMesh,toDeformer)
    deformerTool.setMembershipList(membershipList)
    deformerTool.setWeightList(weightList)
    
def transferMirroredWeights(fromMesh,toMesh,fromDeformer,toDeformer,axis,direction,table):
    
    deformerTool = DeformerLib.WeightListTool(fromMesh,fromDeformer)
    weightList = deformerTool.mirrorWeightList(axis, direction, table)
    
    deformerTool.__init__(toMesh,toDeformer)
    deformerTool.setMembershipList(weightList[1])
    deformerTool.setWeightList(weightList[0])
    
def transferReversedWeights(fromMesh,toMesh,fromDeformer,toDeformer):
    
    deformerTool = DeformerLib.WeightListTool(fromMesh,fromDeformer)
    weightList = deformerTool.reverseWeightList()
    
    deformerTool.__init__(toMesh,toDeformer)
    deformerTool.setWeightList(weightList)
    
#optimize deformer
def optimizedDeformer(deformer,prune):
    DeformerLib.WeightListTool.optimizeMembership(deformer, prune)

#save/load clusters

def saveClusters():
    
    clusters = cmds.ls(sl = True)
    filePath = cmds.fileDialog2(dialogStyle =  0)
    DeformerLib.WeightListTool.saveWeights(clusters,'%s.txt'%filePath[0])
    
def loadClusters():
    
    filePath = cmds.fileDialog2(dialogStyle =  4,okc = 'Open', cap = 'Open')
    clusterDict = DeformerLib.WeightListTool.readWeights(filePath[0])
    DeformerLib.loadClusters(clusterDict)

def reorderHistory():
    geos = cmds.ls(sl = True,l =True)
    listOrder = ['sculpts','nonLinears','wires','ffds','skinClusters','clusters','blendshapes']
    for geo in geos:
        print geo,'.............................................'
        cmds.select(geo)
        MayaScripts.reorderHistory(listOrder, [geo])
   
#skinning tool

def skinningTool():
    
    try:
        mel.eval('source \"weightWindow.mel\"')
        
    except:
        pass
    
    mel.eval('weightWindow;')


    
    