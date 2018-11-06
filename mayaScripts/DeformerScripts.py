'''
Created on Sep 9, 2018

@author: Bill
'''

import maya.cmds as cmds

def getGeo(group='HiRes'):
    geos = cmds.listRelatives(group,ad=True,type='mesh',ni=True)
    geoTransforms = []
    geoList = []
    for geo in geos:
        transform = cmds.listRelatives(geo,p=True,type='transform')[0]
        geoTransforms.append(transform)
    geoSet = set()
    print geoTransforms
    for geo in geoTransforms:
        geoSet.add(geo)
    for geo in geoSet:
        geoList.append(geo)
    return geoList
