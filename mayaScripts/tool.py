'''
-------- Version 1.0.1 --------
-Added Match function for all transforms and pivots.

-------- Version 1.0 --------
-Tools created.

---------------------------
| Created on Aug 15, 2013 |
| @author: Clayton Lantz  |
---------------------------
'''

import maya.cmds as cmds
import maya.mel as mel
import re


def add_attr(name, attr_type, limit=False, sels=[]):
    sels = get_sels(sels)
    if not name:
        cmds.error('Specify name of new attribute.')
    name = name.strip().replace(' ', '_')
    name = re.sub('[\W]', '', name)
    
    for sel in sels:
        if attr_type == 'int':
            cmds.addAttr(sel, ln=name, attributeType='long')
        elif attr_type == 'float':
            cmds.addAttr(sel, ln=name, attributeType='double')
        elif attr_type == 'bool':
            cmds.addAttr(sel, ln=name, attributeType='bool')
        else:
            cmds.warning('Invalid attribute type. Skipping %s' % sel)
            continue
        
        cmds.setAttr('%s.%s' % (sel, name), e=True, keyable=True)
        if limit:
            cmds.addAttr('%s.%s' % (sel, name), e=True, min=0.0, max=1.0, dv=0)
    return

def add_shape(sels=[], alternate=False, each=True, replace=True):
    sels = get_sels(sels)
    if len(sels) < 2:
        cmds.error('Select at least two objects in order to add/replace shape.')
        
    pairs = {}
    targets = []  #used to select targets in proper order after operations
    
    if each:
        obj, tgt = split_sels(sels, alternate=alternate)
        for i in range(len(tgt)):
            pairs[tgt[i]] = [obj[i]]
        targets = tgt
    else:
        pairs[sels[-1]] = sels[:-1]
        targets = sels[-1]
         
    for tgt, objs in pairs.items():
        if replace:
            t_shapes = cmds.listRelatives(tgt, shapes=True, f=True)
            cmds.delete(t_shapes)
        for obj in objs:
            for attr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
                cmds.setAttr('%s.%s' % (obj, attr), lock=False)
            try:
                obj = cmds.parent(obj, tgt, a=True)
            except:
                pass
            
            cmds.delete(obj, ch=True)
            cmds.makeIdentity(obj, apply=True, t=True, r=True, s=True, n=False)
            try:
                obj_shape = cmds.listRelatives(obj, shapes=True, f=True)
                for o in obj_shape:
                    cmds.parent(o, tgt, shape=True, r=True)
                cmds.delete(obj)    
            except:
                pass
              
        for t_shape in cmds.listRelatives(tgt, shapes=True):
            cmds.rename(t_shape, 'ambiguousShape')
        for t_shape in cmds.listRelatives(tgt, shapes=True):
            cmds.rename(t_shape, '%sShape' % tgt.rpartition('|')[2])
 
    cmds.select(targets, r=True)
    return targets

def cleanup():
    '''Closes all windows/panels and sets viewport to bounding box.'''
    win_exceptions = ['MayaWindow',
                      'clToolBoxWindow',
                      'clOutlinerWindow',
                      'clShowConnectionsWindow']
    windows = cmds.lsUI(windows=True)
    windows = list(set(windows).difference(win_exceptions))
    for w in windows:
        cmds.deleteUI(w)
    clear_panels()
    for p in ['modelPanel1','modelPanel2','modelPanel3','modelPanel4']:
        cmds.modelEditor(p, e=True, displayAppearance='boundingBox')
    
    for func in [lambda *args: cmds.setAttr(
                             'Transform_Ctrl.GeoRes', 
                             cmds.attributeQuery(
                                  'GeoRes',
                                  n='Transform_Ctrl',
                                  listEnum=True)[0].split(':').index('Proxy')),
                 lambda *args: cmds.setAttr('Transform_Ctrl.GeoVis', 1),
                 lambda *args: cmds.setAttr('Transform_Ctrl.GeoSmooth', 0),
                 lambda *args: cmds.setAttr('COG_Ctrl.PivotCtrlVis', 0),
                 lambda *args: cmds.setAttr('COG_Ctrl.BendCtrlVis', 0),
                 lambda *args: cmds.setAttr('COG_Ctrl.SquashCtrlVis', 0),
                 lambda *args: cmds.setAttr('COG_Ctrl.DefCtrlVis', 0),
                 lambda *args: cmds.setAttr('Smooth.visibility', 1),
                 lambda *args: cmds.setAttr('NoSmooth.visibility', 1),
                 lambda *args: cmds.setAttr('Geo_Layer.visibility', 1),
                 lambda *args: cmds.setAttr('Geometry_Layer.visibility', 1),
                 lambda *args: cmds.setAttr('Controls_Layer.visibility', 1),
                 lambda *args: cmds.setAttr('LgtRg_Layer.visibility', 1),
                 lambda *args: cmds.setAttr('Smooth.displayType', 0),
                 lambda *args: cmds.setAttr('NoSmooth.displayType', 0),
                 lambda *args: cmds.setAttr('Geo_Layer.displayType', 2),
                 lambda *args: cmds.setAttr('Geometry_Layer.displayType', 2),
                 lambda *args: cmds.setAttr('Controls_Layer.displayType', 0),
                 lambda *args: cmds.setAttr('LgtRg_Layer.displayType', 0),
                 lambda *args: cmds.setAttr('Transform_Ctrl.t', 0,0,0),
                 lambda *args: cmds.setAttr('Transform_Ctrl.r', 0,0,0),
                 lambda *args: cmds.setAttr('Transform_Ctrl.s', 1,1,1),
                 lambda *args: cmds.setAttr('COG_Ctrl.t', 0,0,0),
                 lambda *args: cmds.setAttr('COG_Ctrl.r', 0,0,0),
                 lambda *args: cmds.setAttr('COG_Ctrl.s', 1,1,1),
                 lambda *args: cmds.setAttr('COG_Pivot_Ctrl.t', 0,0,0)]:
        try:
            func()
        except:
            pass
    cmds.viewFit(allObjects=True, animate=False, f=.9)
    return

def clear_grp_id():
    groupIDs = cmds.ls(type='groupId')
    for node in groupIDs:
        connections = cmds.listConnections(node)
        if not connections:
            cmds.delete(node)
            print 'Deleted %s'%node
    return

def clear_panels():
    '''Description: Removes all panels and resets to default panels.
       Input: None
       Return: None'''
    default_panels = {'modelPanel1': 'Top View',
                      'modelPanel2': 'Side View',
                      'modelPanel3': 'Front View',
                      'modelPanel4': 'Persp View',
                      'outlinerPanel1': 'Outliner', 
                      'graphEditor1': 'Graph Editor',
                      'dopeSheetPanel1': 'Dope Sheet',
                      'clipEditorPanel1': 'Trax Editor',
                      'sequenceEditorPanel1': 'Camera Sequencer',
                      'hyperGraphPanel1': 'Hypergraph Hierarchy',
                      'hyperShadePanel1': 'Hypershade',
                      'visorPanel1': 'Visor',
                      'nodeEditorPanel1': 'Node Editor',
                      'createNodePanel1': 'Create Node',
                      'polyTexturePlacementPanel1': 'UV Texture Editor',
                      'renderView': 'Render View',
                      'blendShapePanel1': 'Blend Shape',
                      'dynRelEdPanel1': 'Dynamic Relationships Editor',
                      'relationshipPanel1': 'Relationship Editor',
                      'referenceEditorPanel1': 'Reference Editor',
                      'componentEditorPanel1': 'Component Editor',
                      'dynPaintScriptedPanel': 'Paint Effects',
                      'scriptEditorPanel1': 'Script Editor'}
    default_layouts = set(['hyperGraphInfo',
                           'hyperGraphLayout',
                           'hyperView1',
                           'hyperLayout1',
                           'nodeEditorPanel1Info'])
    
    dagContainers = cmds.ls(type='dagContainer')
    for dc in dagContainers:
        hl = cmds.listConnections('%s.hyperLayout' % dc)
        if hl:
            if not hl[0] == ('%s_hyperLayout' % dc):
                hl[0] = cmds.rename(hl[0], '%s_hyperLayout' % dc)
            default_layouts.add(hl[0])
    
    p_names = set(default_panels.keys())
    panels = set(cmds.getPanel(allPanels=True))
    panels = list(panels.difference(p_names))
    p_num = 0
    for panel in panels:
        cmds.deleteUI(panel, panel=True)
        p_num += 1
    
    layouts = set(cmds.ls(type=['hyperView', 'hyperLayout', 'hyperGraphInfo']))

    layouts = list(layouts.difference(default_layouts))
    l_num = 0
    for layout in layouts:
        try:
            cmds.delete(layout)
        except:
            pass
        finally:
            l_num += 1
        
    print '%i panels / %i layouts deleted' % (p_num, l_num)
    
    #Rebuild model panels if missing
    model_panels = ['modelPanel1','modelPanel2','modelPanel3','modelPanel4']
    gMainPane = mel.eval('global string $gMainPane; $temp = $gMainPane;')
    for m_panel in model_panels:
        if not cmds.modelPanel(m_panel, exists=True):
            cmds.modelPanel(m_panel, parent=gMainPane)
    
    for name, label in default_panels.items():
        try:
            cmds.panel(name, e=True, label=label)
        except:
            pass

    mel.eval('lookThroughModelPanel top modelPanel1')
    mel.eval('lookThroughModelPanel side modelPanel2')
    mel.eval('lookThroughModelPanel front modelPanel3')
    mel.eval('lookThroughModelPanel persp modelPanel4')
    mel.eval('setNamedPanelLayout "Single Perspective View"')
    return

def clear_ref_nodes():
    referencedNodes = cmds.ls(type='reference')
    for node in referencedNodes:
        cmds.lockNode(node, lock=False)
        cmds.delete(node)
        print 'Deleted: %s' % node
    return

def constrain(sels=[],
              parent=False,
              scale=False,
              point=False,
              orient=False,
              offset=True,
              match=False,
              each=False,
              alternate=False):
    sels = get_sels(sels)
    pairs = {}
    s_objs = []
    
    if each:
        tgt, obj = split_sels(sels, alternate=alternate)
        if match:
            tgt, obj = obj, tgt
        for i in range(len(tgt)):
            pairs[tgt[i]] = [obj[i]]
    else:
        if match:
            pairs[sels[-1]] = sels[:-1]
        else:
            pairs[sels[0]] = sels[1:]
    
    for tgt, objs in pairs.items():
        for obj in objs:
            c = []
            if parent:
                c.extend(cmds.parentConstraint(tgt, obj, mo=offset, weight=1))
            if scale:
                c.extend(cmds.scaleConstraint(tgt, obj, mo=offset, weight=1))
            if point:
                c.extend(cmds.pointConstraint(tgt, obj, mo=offset, weight=1))
            if orient:
                c.extend(cmds.orientConstraint(tgt, obj, mo=offset, weight=1))
            
            if match and c:
                cmds.delete(c)
                s_objs.extend((tgt, obj))
            else:
                s_objs.append(tgt)
                
    cmds.select(s_objs, r=True)
    return

def constrain_proxy(sels=[], alternate=False, rename=True):
    sels = split_sels(sels, alternate=alternate)
    s_pairs = map(None, *sels)
    
    for jnt, obj in s_pairs:
        if node_type(jnt) != 'joint' or node_type(obj) != 'mesh':
            if alternate:
                cmds.error('Selection must be joint, geo, joint, geo, etc.')
            else:
                cmds.error('Select all joints then equal number of geo.')

        proxy_group = 'Proxy'
        if not cmds.objExists(proxy_group):
            proxy_group = cmds.group(name=proxy_group, empty=True, world=True)
            if cmds.objExists('Geometry'):
                proxy_group = cmds.parent(proxy_group, 'Geometry')[0]
        obj = obj.rpartition('|')[2]
        if rename and jnt.endswith('_Jnt'):
            n_name = jnt.replace('_Jnt','_Proxy_Geo')
            n_name = n_name.rpartition('|')[2]
            obj = cmds.rename(obj, n_name)
        group = cmds.group(obj, name='%s_Grp' % obj, world=True)
        group = cmds.parent(group, proxy_group)[0]
        cmds.parentConstraint(jnt, group, mo=True, weight=1)
        cmds.scaleConstraint(jnt, group, mo=True, weight=1)
        for a in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
            cmds.setAttr('%s.%s' % (obj, a), lock=True)
    cmds.select(sels[0], r=True)
    return

def curve_from_selection(sels=[]):
    sels = get_sels(sels)
    if len(sels) < 2:
        cmds.error('Select at least two objects to create curve.')
    positions = get_position(sels)
    points = []
    
    for pos in positions:
        obj = pos[0]
        p = pos[1]
        if obj == sels[0] or obj == sels[-1]:
            points.extend([p, p, p])
        else:
            points.append(p)
    curve = cmds.curve(degree=3, p=points)
    return curve
            
def debug_eclipse():
    import debugmaya
    debugmaya.debugmaya.startDebug()
    return

def del_limits(attr):
    sels = get_sels()
    first_key = 0
    last_key = 100

    if attr == 'all':
        attr = ['translate', 'rotate', 'scale']
    else:
        attr = [attr]
    
    for sel in sels:
        for a in attr:
            cmds.cutKey('%s.%s' % (sel, a), cl=True)
            if a == 'translate' or a == 'rotate':
                cmds.setAttr('%s.%s' % (sel, a), 0, 0, 0)
            elif a == 'scale':
                cmds.setAttr('%s.%s' % (sel, a), 1, 1, 1)
            else:
                cmds.setAttr('%s.%s' % (sel, a), 0)
    keys = cmds.keyframe(q=True)
    if keys:
        first_key = min(keys)
        last_key = max(keys)
    cmds.playbackOptions(minTime=first_key, maxTime=last_key)
    return

def display_axis(sels=[]):
    sels = get_sels(sels)
    for sel in sels:
        state = not cmds.getAttr('%s.displayLocalAxis' % sel, k=True)
        cmds.setAttr('%s.displayLocalAxis' % sel, state, k=state)
        try:
            cmds.setAttr('%s.jointOrientX' % sel, k=state)
            cmds.setAttr('%s.jointOrientY' % sel, k=state)
            cmds.setAttr('%s.jointOrientZ' % sel, k=state)
        except:
            pass
    return

def get_position(sels=[], space=''):
    #default space: 'Pivot'
    sels = get_sels(sels)
    
    s_position = []
    pos=[0,0,0]
    rot=[0,0,0]
      
    if space == 'world':
        s_position.append(['world', pos, rot])
    elif space == 'center':
        comps = []
        n_objs = []
        n_sels = []
        for sel in sels:
            #separate component/joint/transform selections
            if '.' in sel:
                comps.append(sel)
            elif cmds.nodeType(sel) == 'joint':
                #create locator at joint position
                pos = cmds.xform(sel, q=True, rp=True, ws=True)
                loc = cmds.spaceLocator(p=[0,0,0], a=True)
                cmds.xform(loc, t=pos, s=[0,0,0], ws=True)
                n_objs.extend(loc)
            else:
                #duplicate and reset bounding boxes to world without xforms
                n_obj = cmds.duplicate(sel, renameChildren=True)
                attrs = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
                for a in attrs:
                    cmds.setAttr('%s.%s' % (n_obj[0], a),
                                 lock=False,
                                 keyable=True,
                                 channelBox=False)
                cmds.makeIdentity(n_obj, a=True, t=True, r=True, s=True)
                n_objs.extend(n_obj)
        n_sels = comps + n_objs
        bb_pos = cmds.exactWorldBoundingBox(n_sels, ignoreInvisible=True)
        pos_x = (bb_pos[0] + bb_pos[3]) / 2
        pos_y = (bb_pos[1] + bb_pos[4]) / 2
        pos_z = (bb_pos[2] + bb_pos[5]) / 2
        pos = [pos_x, pos_y, pos_z]
        s_position.append(['center', pos, rot])
        if n_objs: cmds.delete(n_objs)
        cmds.select(sels, r=True)
    elif space == 'center_each':
        for sel in sels:
            if cmds.nodeType(sel) == 'joint':
                pos = cmds.xform(sel, q=True, rp=True, ws=True)
            else:
                bb_pos = cmds.xform(sel, q=True, boundingBox=True, ws=True)
                pos_x = (bb_pos[0] + bb_pos[3]) / 2
                pos_y = (bb_pos[1] + bb_pos[4]) / 2
                pos_z = (bb_pos[2] + bb_pos[5]) / 2
                pos = [pos_x, pos_y, pos_z]
            s_position.append([sel, pos, rot])
    else:
        objs = []
        for sel in sels:
            if '.' in sel:
                obj = sel.rpartition('.')[0]
                if obj not in objs:
                    objs.append(obj)
            else:
                objs.append(sel)
        for obj in objs:    
            pos = cmds.xform(obj, q=True, rp=True, ws=True)
            rot = cmds.xform(obj, q=True, ro=True, ws=True)
            s_position.append([obj, pos, rot])
    return s_position

def get_sels(sels=[], error=True):
    if not sels:
        sels = cmds.ls(sl=True, fl=True, long=True)
        if error and not sels:
            cmds.error('Nothing selected. Make a selection and try again.')
    if isinstance(sels, basestring):
        sels = [sels]
    for sel in sels:
        if not cmds.objExists(sel):
            cmds.error('Object %s does not exist.' % sel)
    if sels: #Reselecting forces undo to maintain selection.
        cmds.select(sels, r=True) 
    return sels
 
def group(sels=[], space=''):
    #default space: 'pivot'
    sels = get_sels(sels)
    n_groups=[]
    n_sels=[]
       
    for sel in sels:
        s_pivot=[]
        sel_name = sel.rpartition('|')[2]
        n_group = cmds.group(empty=True,
                             parent=sel,
                             r=True)
        #parent new group under objects parent
        try:
            s_parent = cmds.listRelatives(sel, p=True, fullPath=True)[0]
            n_group = cmds.parent(n_group, s_parent)
        except:
            n_group = cmds.parent(n_group, world=True)
            
        #set pivot for new group
        if space == 'world':
            s_pivot = [0,0,0]
        elif space == 'local':
            try:
                s_parent = cmds.listRelatives(n_group, p=True, fullPath=True)[0]
            except:
                #if parent is world, match to object's pivot
                s_parent = sel
            s_pivot = cmds.xform(s_parent, q=True, rp=True, ws=True) 
        else: #defaults to to pivot
            s_pivot = cmds.xform(sel, q=True, rp=True, ws=True)
        cmds.xform(n_group, pivots=s_pivot, ws=True)
     
        #unlock transformation attrs for grouping and relock afterwards
        l_attrs = []
        for attr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
            if cmds.getAttr('%s.%s' % (sel, attr), lock=True):
                cmds.setAttr('%s.%s' % (sel, attr), e=True, lock=False)
                l_attrs.append(attr)
        n_sel = cmds.parent(sel, n_group)[0]
        for attr in l_attrs:
            cmds.setAttr('%s.%s' % (n_sel, attr), e=True, lock=True)
        
        if cmds.objExists('%s_Grp' % sel_name):
            cmds.warning('Creating object with duplicate name: '
                         '%s_Grp' % sel_name)
        
        #rename group node and fix variable references to hierarchy
        try:
            n_group_path = cmds.listRelatives(n_group, p=True, fullPath=True)[0]
        except:
            n_group_path = '|'
        n_group = cmds.rename(n_group, '%s_Grp' % sel_name)
        n_group = '%s|%s' % (n_group_path, n_group.rpartition('|')[2])
        n_sel = '%s|%s' % (n_group, n_sel.rpartition('|')[2])
        n_groups.extend(n_group)
        n_sels.append(n_sel)
        
    cmds.select(n_sels, r=True)    
    return n_groups 

def joints_from_sels(sels=[]):
    sels = get_sels()
    jnts = []
    
    for i in range(len(sels)):
        name = sels[i].rpartition('|')[2].partition('.')[0]
        for suffix in ['_Ctrl', '_Geo', '_Loc']:
            if name.endswith(suffix):
                name = name.rpartition(suffix)[0]
                break
        name += '_Jnt'
        
        pos = get_position(sels[i])[0]
        cmds.select(clear=True)
        jnt = cmds.joint(n=name, p=pos[1])
        if i > 0:
            cmds.joint(jnts[i-1],
                       e=True,
                       zeroScaleOrient=True,
                       orientJoint='xyz',
                       secondaryAxisOrient='yup')
            cmds.joint(jnt, e=True, orientation=[0,0,0])
        jnts.append(jnt)
    cmds.select(jnts, replace=True)
    return jnts

def key_limits(attr, combine=False):
    sels = get_sels()
    tgt_attr = []
    first_key = 0
    last_key = 0
    def_value = 0
    step=10
    keys = cmds.keyframe(q=True)
    if keys:
        first_key = min(keys)
        last_key = max(keys)

    if attr == 'translate':
        tgt_attr = ['tx','ty','tz']   
    elif attr == 'rotate':
        tgt_attr = ['rx','ry','rz'] 
    elif attr == 'scale':
        tgt_attr = ['sx','sy','sz']
        def_value = 1
    else:
        tgt_attr = [attr]
        
    for sel in sels:
        values = []
        for t in tgt_attr:
            values.append(cmds.getAttr('%s.%s' % (sel, t)))
        attr_pairs = zip(tgt_attr, values)
        for a,v in attr_pairs:
            c_key = last_key
            if v:
                cmds.setKeyframe('%s.%s' % (sel, a),
                                 time = c_key+step*0,
                                 value = def_value)
                cmds.setKeyframe('%s.%s' % (sel, a),
                                 time = c_key+step*1,
                                 value = v)
                cmds.setKeyframe('%s.%s' % (sel, a),
                                 time = c_key+step*2,
                                 value = -v)
                cmds.setKeyframe('%s.%s' % (sel, a),
                                 time = c_key+step*3,
                                 value = def_value)
                if not combine:
                    last_key = last_key + (step * 3)
        if combine:
            last_key = last_key + (step * 3)
                
    cmds.playbackOptions(minTime=first_key, maxTime=last_key)
    return

def locator(sels=[], space=''):
    #default space: pivot
    #space var goes through get_position() to determine position
    error=True
    if space == 'world':
        error = False
    sels = get_sels(sels, error)
    s_pos = get_position(sels, space)
    n_locs = []
    for obj, pos, rot in s_pos:
        name = obj.rpartition('|')[2].partition('.')[0]
        if not name.lower().endswith('loc'):
            name += '_Loc'
        loc = cmds.spaceLocator(n=name, p=[0,0,0], a=True)
        cmds.xform(loc, t=pos, ro=rot, ws=True)
        n_locs.extend(loc)
    cmds.select(n_locs, r=True)
    return n_locs

def locator_segments(count, sels=[], from_curve=False):
    sels = get_sels(sels)
    curves = []
    n_locs = []
    step = 1.0 / (count + 1)
    if from_curve:
        step = 1.0 / (count - 1)
    
    #Create/gather selected curves    
    if from_curve:
        for sel in sels[:]:
            sel = sel.partition('.')[0]
            shape = cmds.listRelatives(sel, shapes=True)[0] or []
            if cmds.nodeType(shape) == 'nurbsCurve':
                curves.append(sel)
        if not curves:
            cmds.error('Select curve(s) to build segments.')
    else:
        if len(sels) < 2:
            cmds.error('Select at least 2 objects to build segments between.')
        for i in range(1, len(sels)):
            space1, space2 = 'pivot','pivot'
            if '.' in sels[i-1]: space1='center'
            if '.' in sels[i]: space2='center'
            
            pos1 = get_position(sels[i-1], space=space1)[0][1]
            pos2 = get_position(sels[i], space=space2)[0][1]
            curve = cmds.curve(d=1, p=[(pos1),(pos2)], k=[0,1])
            curves.append(curve)
    
    #Create motion paths and space new locators evenly along curve.
    for curve in curves:
        curve_shape = cmds.listRelatives(curve, shapes=True, fullPath=True)[0]
        motion_path = cmds.createNode('motionPath')
        cmds.setAttr('%s.fractionMode' % motion_path, 1)
        cmds.setAttr('%s.follow' % motion_path, 1)
        cmds.connectAttr('%s.worldSpace[0]' % curve_shape,
                         '%s.geometryPath' % motion_path,
                         f=True)
         
        for i in range(count):
            loc = cmds.spaceLocator(p=[0,0,0])[0]
            c_step = cmds.getAttr('%s.uValue' % motion_path)
            c_step = max(min(.9999, c_step + step), 0.0)
            if i==0 and from_curve:
                c_step=0.0001
            cmds.setAttr('%s.uValue' % motion_path, c_step)
            cmds.connectAttr('%s.allCoordinates' % motion_path,
                             '%s.translate' % loc,
                             f=True)
            cmds.connectAttr('%s.rotate' % motion_path,
                             '%s.rotate' % loc,
                             f=True)
            cmds.disconnectAttr('%s.allCoordinates' % motion_path,
                                '%s.translate' % loc)
            cmds.disconnectAttr('%s.rotate' % motion_path,
                                '%s.rotate' % loc)
            n_locs.append(loc)
        cmds.delete(motion_path)    
        if not from_curve:
            cmds.delete(curve)
    cmds.select(n_locs, r=True)
    return n_locs

def mask(sels=[], solo=True, clear=False):
    allowed_types = [
                     'baseLattice',
                     'clusterHandle',
                     'deformBend',
                     'deformSquash',
                     'follicle',
                     'ikHandle',
                     'joint',
                     'lattice',
                     'locator',
                     'mesh',
                     'nurbsCurve',
                     'nurbsSurface']
    s_types = set()
    sels = get_sels(sels, error=False)
    if sels and not clear:
        for sel in sels:
            s_types.add(node_type(sel))

        s_types = s_types.intersection(allowed_types)
        if s_types:
            if solo:
                cmds.selectType(allObjects = not solo)
                #byName flag not working correctly. using mel.eval instead.
                try:
                    mel.eval('selectType -byName gpuCache %i' % (not solo))
                except:
                    pass
            for s_type in s_types:
                if s_type == 'baseLattice':
                    s_type = 'lattice'
                elif s_type == 'clusterHandle':
                    s_type = 'cluster'
                elif s_type == 'deformBend' or s_type == 'deformSquash':
                    s_type = 'nonlinear'
                elif s_type == 'mesh':
                    s_type = 'polymesh'
                elif s_type == 'nurbsSurface':
                    s_type = 'nurbsSurface'
                    
                eval('cmds.selectType(%s=%s)' % (s_type, solo))    
    else:
        cmds.selectType(allObjects=True)
        try:
            mel.eval('selectType -byName gpuCache true')
        except:
            pass
    return

def match(sels=[], each=False, alternate=False, s_type='all'): 
    types = ['all','position','rotation','scale','pivot']
    if s_type not in types:
        return
            
    sels = get_sels(sels)
    pairs = {}
    s_objs = []
    
    if each:
        obj, tgt = split_sels(sels, alternate=alternate)
        for i in range(len(tgt)):
            pairs[tgt[i]] = [obj[i]]
    else:
        pairs[sels[-1]] = sels[:-1]

    for tgt, objs in pairs.items():
        for obj in objs:
            c = []
            if s_type == 'all':
                c.extend(cmds.pointConstraint(tgt, obj, mo=0, weight=1))
                c.extend(cmds.orientConstraint(tgt, obj, mo=0, weight=1))
                c.extend(cmds.scaleConstraint(tgt, obj, mo=0, weight=1))
            elif s_type == 'position':
                c.extend(cmds.pointConstraint(tgt, obj, mo=0, weight=1))
            elif s_type == 'rotation':
                c.extend(cmds.orientConstraint(tgt, obj, mo=0, weight=1))
            elif s_type == 'scale':
                c.extend(cmds.scaleConstraint(tgt, obj, mo=0, weight=1))
            elif s_type == 'pivot':
                r_pivot = cmds.xform(tgt, q=True, rp=True, ws=True)
                s_pivot = cmds.xform(tgt, q=True, sp=True, ws=True)
                cmds.xform(obj, ws=True, rp=r_pivot, sp=s_pivot)
                shapes = cmds.listRelatives(obj, shapes=True, fullPath=True)
                #Match cluster origin
                for shape in shapes:
                    n_type = cmds.nodeType(shape)
                    if n_type == 'clusterHandle':
                        cmds.setAttr('%s.origin' % shape,
                                     r_pivot[0], r_pivot[1], r_pivot[2])
                    
            if c:
                cmds.delete(c)
            s_objs.append(obj)
                
    cmds.select(s_objs, r=True)
    return

def node_type(sel):
    n_type = ''
    shape = cmds.listRelatives(sel, shapes=True, fullPath=True)
    if shape:
        n_type = cmds.nodeType(shape[0])
    else:
        n_type = cmds.nodeType(sel)
    return n_type

def none_chuck(var):
    if var == None:
        var = []
    return var
        
def num_padding(name):
    key = '#'
    keys = re.findall(r'#+', name)
    if not len(keys):
        cmds.error('Expected sequence of "%s" characters, got 0.' % key)
    elif len(keys) > 1:
        cmds.error('Expected single sequence of "%s" characters, got %i.' 
                   % (key, len(keys)))
    return len(keys[0])

def parent_each(sels=[], alternate=False):
    child, parent = split_sels(sels, alternate)
    for i in range(len(child)):
        child[i] = cmds.parent(child[i], parent[i])[0]
    cmds.select(child, r=True)
    return

def parent_hierarchy(sels=[]):
    sels = get_sels(sels)
    for i in range(len(sels)):
        last_index = (len(sels) - 1)
        if i < last_index:
            cmds.parent(sels[i], sels[i+1])
    cmds.select(sels[(last_index)], r=True)
    return

def rename_shape(sels=[]):
    sels = get_sels(sels)
    for sel in sels:
        shapes = cmds.listRelatives(sel, shapes=True)
        for shape in shapes:
            cmds.rename(shape, '%sShape' % sel.rpartition('|')[2])
    return
    
def reload_file():
    '''Reload the current file.'''
    confirm = cmds.confirmDialog(title='Reload',
                                 button=['Cancel','Reload'],
                                 cancelButton='Cancel',
                                 defaultButton='Reload',
                                 message='Reload without saving changes?')
    try:
        if confirm == 'Reload':
            f_path = cmds.file(q=True, sceneName=True).replace('\\', '/')
            f_type = cmds.file(q=True, type=True)[0]
            cmds.file(f_path, 
                      open=True,
                      force=True,
                      options='v=0;',
                      typ=f_type)
    except Exception as e:
        cmds.error(str(e))
        
    return

def rename(name, start=1, sels=[]):
    sels = get_sels(sels)
    n_sels = []
    name = re.sub('[^a-zA-Z0-9_# ]', '', name)
    name = name.strip().replace(' ', '_')
    key = '#'
    pad = 1
    
    if not name:
        cmds.error('Must specify a rename string.')
    if key in name:
        pad = num_padding(name)
    if not isinstance(start, (int, long)):
        cmds.warning('Must specify integer for start value. '
                     'Defaulting to 1.')
        start = 1
    start = abs(start)
    
    index = 0
    for sel in sels:
        if not cmds.objExists(sel):
            sels = cmds.ls(sl=True, long=True)
            sel = sels[index]
        n = name.replace(key*pad, str(start).zfill(pad))
        try:
            n_sels = cmds.rename(sel, n)
            start += 1
            index += 1
        except:
            raise RuntimeError('No object matches name: %s' % sel)
    return n_sels

def reorder_nodes(sels=[], sort=False):
    sels = get_sels(sels)
    temp_dir = cmds.group(empty=True, world=True)
    nodes = []
    
    if sort:
        sels = sorted(sels)
    for s in sels:
        try:
            p = cmds.listRelatives(s, parent=True, fullPath=True)[0]
        except:
            p = None
        s = cmds.parent(s, temp_dir)[0]
        nodes.append([s, p])
    for s, p in nodes:
        if p:
            cmds.parent(s, p, a=True)
        else:
            cmds.parent(s, world=True, a=True)
    cmds.delete(temp_dir)
    cmds.select(sels, r=True)
    return

def reorder_history(sels=[]):
    def_types = ['wrap',
                 'sculpt',
                 'deformBend', 
                 'deformSquash', 
                 'deformFlare', 
                 'deformSine', 
                 'deformTwist', 
                 'deformWave',
                 'nonLinear', 
                 'wire', 
                 'ffd', 
                 'skinCluster',
                 'clusterMains',
                 'clusterSquash',
                 'cluster', 
                 'blendShape', 
                 'tweak']
    sels = get_sels(sels)

    for sel in sels:
        input_history = {}
        inputs = cmds.listHistory(sel, interestLevel=2, pruneDagObjects=True)
        for this_input in inputs:
            input_type = cmds.nodeType(this_input)
            if input_type in def_types:
                if input_type == 'nonLinear':
                    handle = cmds.connectionInfo('%s.deformerData' % this_input, sfd=True)
                    input_type = cmds.nodeType(handle)
                if input_type == 'cluster':
                    if 'main' in this_input.lower():
                        input_type = 'clusterMains'
                    elif 'squash' in this_input.lower():
                        input_type = 'clusterSquash'
                
            if input_type in input_history:
                input_history[input_type].append(this_input)
            else:
                input_history[input_type] = [this_input]
        
        last_input = ''
        for def_type in def_types:
            if def_type in input_history:
                for def_input in sorted(input_history[def_type]):
                    if last_input:
                        try:
                            cmds.reorderDeformers(last_input, def_input, sel)
                        except:
                            pass
                    last_input = def_input
    cmds.select(sels, r=True)
    print 'Reordered History'
    return          

def search_replace(search_str, replace_str, hierarchy=False, sels=[]):
    sels = get_sels(sels)
    sels = cmds.ls(sl=True, dag=hierarchy, type='transform', long=True)
    replace_str = replace_str.strip().replace(' ', '_')
    replace_str = re.sub('[\W]', '', replace_str)
    n_sels = []
    dep_sels = cmds.ls(sl=True, dep=True, long=True)
    for d in dep_sels[:]:
        if d in sels:
            dep_sels.remove(d)

    if not search_str:
        cmds.error('Specify a search string.')

    index = 0
    for sel in sels:
        if not cmds.objExists(sel):
            sels = cmds.ls(sl=True, dag=hierarchy, type='transform', long=True)
            sel = sels[index]
        pathless = sel.rpartition('|')[2]
        n_str = pathless.replace(search_str, replace_str, 1)
        if n_str != pathless:
            n_sels.append(cmds.rename(sel, n_str))
        index += 1
    for d in dep_sels:
        n_str = d.replace(search_str, replace_str, 1)
        if n_str != d:
            n_sels.append(cmds.rename(d, n_str))
    return n_sels

def smooth_proxy(sels=[]):
    sels = get_sels(sels)
    p_nodes = []
    for sel in sels:
        name = sel.partition('|')[2].partition('_Geo')[0]
        s_shapes = cmds.listRelatives(sel, shapes=True, type='mesh')

        p_node = cmds.polyDuplicateAndConnect(sel, renameChildren=True)
        p_node = cmds.rename(p_node, '%s_SmoothProxy_Geo' % name)
        p_shapes = cmds.listRelatives(p_node, shapes=True, type='mesh')
        
        shapes = zip(s_shapes, p_shapes)
        for outMesh, inMesh in shapes:
            smooth = cmds.createNode('polySmoothProxy', n='%s_Smooth' % name)
            cmds.setAttr('%s.method' % smooth, 0)
            cmds.setAttr('%s.exponentialLevel' % smooth, 0)
            cmds.setAttr('%s.continuity' % smooth, 1)
            cmds.setAttr('%s.smoothUVs' % smooth, 1)
            cmds.setAttr('%s.keepBorder' % smooth, 1)
            cmds.setAttr('%s.keepHardEdge' % smooth, 0)
            cmds.setAttr('%s.keepMapBorders' % smooth, 1)
            cmds.setAttr('%s.linearLevel' % smooth, 1)
            cmds.setAttr('%s.divisionsPerEdge' % smooth, 1)
            cmds.setAttr('%s.pushStrength' % smooth, 0.1)
            cmds.setAttr('%s.roundness' % smooth, 1)
            cmds.connectAttr('%s.outMesh' % outMesh,
                             '%s.inputPolymesh' % smooth,
                             f=True)
            cmds.connectAttr('%s.output' % smooth,
                             '%s.inMesh' % inMesh,
                             f=True)
        if not cmds.objExists('SmoothProxy_Grp'):
            cmds.group(n='SmoothProxy_Grp', empty=True)  
        p_nodes.extend(cmds.parent(p_node, 'SmoothProxy_Grp', r=True))

    cmds.select(p_nodes, r=True)
    return p_nodes

def split_sels(sels=[], alternate=True):
    sels = get_sels(sels)
    if len(sels) % 2:
        cmds.error('Invalid selection. Select an even number of objects.')
    
    set_1 = []
    set_2 = []
    if alternate:
        for i in range(0, len(sels), 2):
            set_1.append(sels[i])
            set_2.append(sels[i+1])
    else:
        mid = len(sels) / 2
        set_1 = sels[:mid]
        set_2 = sels[mid:]
    return set_1, set_2
            

        
    

