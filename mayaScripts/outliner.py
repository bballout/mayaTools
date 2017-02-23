'''
-------- Version 1.0 --------
-Outliner created.

---------------------------
| Created on Aug 20, 2013 |
| @author: Clayton Lantz  |
---------------------------
'''

import maya.cmds as cmds

class Outliner():
    def __init__(self):
        self.control_name = 'clOutliner'
        self.node_types = ['---CONSTRAINTS---',
                           'aimConstraint',
                           'orientConstraint',
                           'parentConstraint',
                           'pointConstraint',
                           'scaleConstraint',
                           '',
                           '----DEFORMERS----',
                           'blendShape',
                           'cluster',
                           'ffd',
                           'follicle',
                           'ikHandle',
                           'joint',
                           'nonLinear',
                           'polySmoothFace',
                           'sculpt',
                           'skinCluster',
                           'wire',
                           'wrap',
                           '',
                           '----GEOMETRY----',
                           'nurbsCurve',
                           'nurbsSurface',
                           'mesh',
                           '',
                           '----UTILITIES----',
                           'animCurveUU',
                           'blendColors',
                           'clamp',
                           'condition',
                           'curveInfo',
                           'distanceBetween',
                           'materialInfo',
                           'motionPath',
                           'multiplyDivide',
                           'plusMinusAverage',
                           'ramp',
                           'reverse',
                           'setRange',
                           'shadingEngine']
        self.node_pane_height = 50
        self.node_pane_width = 50

    def create(self):
        self.delete()
        self.m_window = cmds.window('%sWindow' % self.control_name, w=10)
        self.m_pane = cmds.paneLayout(
                                      parent=self.m_window,
                                      configuration='vertical2',
                                      paneSize=[1, self.node_pane_width, 100],
                                      staticWidthPane=1,
                                      staticHeightPane=1)
        self.node_list = cmds.textScrollList(
                                           parent=self.m_pane,
                                           allowMultiSelection=True,
                                           a=self.node_types,
                                           sc=lambda *args: self.node_to_list())

        self.o_form = cmds.formLayout(parent=self.m_pane)
        self.flatten_box = cmds.checkBox(
                                  parent=self.o_form,
                                  label='Flatten',
                                  ann='List component selections individually.',
                                  height=15)
        self.orientation_box = cmds.checkBoxGrp(
                                          parent=self.o_form,
                                          numberOfCheckBoxes=1,
                                          label='',
                                          ann='Rotate orientation of window.',
                                          cw2=[55,50],
                                          height=15,
                                          cc=lambda *args: self.rotate_layout())
        self.up_button = cmds.button(
                                     parent=self.o_form,
                                     l='Up',
                                     c=lambda *args: self.move_in_list(1))
        self.down_button = cmds.button(
                                       parent=self.o_form,
                                       l='Down',
                                       c=lambda *args: self.move_in_list(-1))
        self.outline_list = cmds.textScrollList(
                                     parent=self.o_form,
                                     allowMultiSelection=True,
                                     sc=lambda *args: self.select_highlighted(),
                                     dcc=lambda *args: self.select_all())

        cmds.formLayout(
                        self.o_form,
                        e=True,
                        attachForm=[(self.flatten_box, 'top', 0),
                                    (self.flatten_box, 'left', 0),
                                    (self.orientation_box, 'top', 0),
                                    (self.orientation_box, 'right', 0),
                                    (self.up_button, 'left', 0),
                                    (self.down_button, 'right', 0),
                                    (self.outline_list, 'left', 0),
                                    (self.outline_list, 'right', 0),
                                    (self.outline_list, 'bottom', 0)],
                        attachControl=[(self.up_button, 'top', 0,
                                        self.flatten_box),
                                       (self.down_button, 'top', 0,
                                        self.flatten_box),
                                       (self.outline_list, 'top', 0,
                                        self.up_button)],
                        attachPosition=[(self.up_button, 'right', 0, 50),
                                        (self.down_button, 'left', 0, 50)],
                        attachNone=[(self.flatten_box, 'bottom'),
                                    (self.up_button, 'bottom'),
                                    (self.down_button,'bottom')])

        self.menu_popup_rmb = cmds.popupMenu(
                                     'outlinerMenuRMB',
                                      parent=self.outline_list,
                                      button=3,
                                      mm=True,
                                      aob=True,
                                      pmc=lambda *args: self.outliner_mm_rmb())

        self.menu_popup_mmb = cmds.popupMenu(
                                      'outlinerMenuMMB',
                                      parent=self.outline_list,
                                      button=2,
                                      mm=True,
                                      aob=True,
                                      pmc=lambda *args: self.outliner_mm_mmb())
        cmds.setParent(self.m_pane)
        self.control_name = cmds.dockControl(
                                             self.control_name,
                                             content=self.m_window,
                                             label=self.control_name,
                                             allowedArea=['right','left'],
                                             area='left',
                                             w=10)

    def delete(self):
        if cmds.dockControl(self.control_name, exists=True):
            cmds.deleteUI(self.control_name)
        if cmds.window('%sWindow' % self.control_name, exists=True):
            cmds.deleteUI('%sWindow' % self.control_name)
        return

    def outliner_mm_rmb(self):
        cmds.menu(self.menu_popup_rmb, e=True, dai=True)
        cmds.menuItem(
                      parent=self.menu_popup_rmb,
                      l='Clear',
                      radialPosition='N',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.clear_list())
        cmds.menuItem(
                      parent=self.menu_popup_rmb,
                      l='Add',
                      radialPosition='E',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.add_to_list())
        cmds.menuItem(
                      parent=self.menu_popup_rmb,
                      l='Sort',
                      radialPosition='S',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.sort_list())
        cmds.menuItem(
                      parent=self.menu_popup_rmb,
                      l='Remove',
                      radialPosition='W',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.remove_from_list())
        cmds.setParent(m=True)
        return

    def outliner_mm_mmb(self):
        cmds.menu(self.menu_popup_mmb, e=True, dai=True)
        cmds.menuItem(
                      parent=self.menu_popup_mmb,
                      l='Clear All',
                      radialPosition='N',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.clear_stored_lists())
        cmds.menuItem(
                      parent=self.menu_popup_mmb,
                      l='Store 1',
                      radialPosition='NE',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.store_list('outliner_list1'))
        cmds.menuItem(
                      parent=self.menu_popup_mmb,
                      l='Store 2',
                      radialPosition='E',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.store_list('outliner_list2'))
        cmds.menuItem(
                      parent=self.menu_popup_mmb,
                      l='Store 3',
                      radialPosition='SE',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.store_list('outliner_list3'))
        cmds.menuItem(
                      parent=self.menu_popup_mmb,
                      l='Restore 1',
                      radialPosition='NW',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.restore_list('outliner_list1'))
        cmds.menuItem(
                      parent=self.menu_popup_mmb,
                      l='Restore 2',
                      radialPosition='W',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.restore_list('outliner_list2'))
        cmds.menuItem(
                      parent=self.menu_popup_mmb,
                      l='Restore 3',
                      radialPosition='SW',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.restore_list('outliner_list3'))
        cmds.menuItem(
                      parent=self.menu_popup_mmb,
                      l='List All',
                      radialPosition='S',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.restore_list())
        cmds.setParent(m=True)
        return     

    def add_to_list(self):
        flatten = cmds.checkBox(self.flatten_box, q=True, v=True)
        s_nodes = cmds.ls(sl=True, fl=flatten)
        try:
            o_nodes = cmds.textScrollList(
                                          self.outline_list,
                                          q=True,
                                          ai=True)
            s_nodes = filter(lambda x:x not in o_nodes, s_nodes)
        except:
            pass

        cmds.textScrollList(
                            self.outline_list,
                            e=True, 
                            deselectAll=True,
                            append=s_nodes, 
                            si=s_nodes)
        return

    def clear_list(self):
        cmds.textScrollList(self.outline_list, e=True, removeAll=True)
        return

    def clear_stored_lists(self):
        cmds.optionVar(remove=['outliner_list1',
                               'outliner_list2',
                               'outliner_list3'])
        return

    def move_in_list(self, direction=1):
        o_nodes = cmds.textScrollList(self.outline_list, q=True, si=True)
        try:
            if direction < 0:
                o_nodes.reverse()
            for n in o_nodes:
                cmds.textScrollList(self.outline_list, e=True, deselectAll=True)
                cmds.textScrollList(self.outline_list, e=True, si=n)
                index = cmds.textScrollList(self.outline_list,
                                            q=True,
                                            sii=True)[0]
                index = max(1, index - direction)
                cmds.textScrollList(self.outline_list, e=True, removeItem=n)
                cmds.textScrollList(self.outline_list, e=True, ap=[index, n])
            cmds.textScrollList(self.outline_list, e=True, si=o_nodes)
        except:
            pass
        return

    def node_to_list(self):
        node_type = cmds.textScrollList(self.node_list, q=True, si=True)
        all_types = cmds.allNodeTypes()
        for n in node_type[:]:
            if n not in all_types:
                node_type.remove(n)
        if node_type:
            nodes = []
            for n_type in node_type:
                n = sorted(cmds.ls(type=n_type), key=lambda s: s.lower())
                if n and n_type in ['nurbsCurve','nurbsSurface','mesh']:
                    n = sorted(set(cmds.listRelatives(n, parent=True)))
                nodes.extend(n)
            cmds.textScrollList(
                                self.outline_list,
                                e=True,
                                append=nodes,
                                removeAll=True)
        return

    def remove_from_list(self):
        sel_items = cmds.textScrollList(
                                        self.outline_list,
                                        q=True,
                                        selectItem=True)
        if sel_items:
            cmds.textScrollList(self.outline_list, e=True, removeItem=sel_items)
        return

    def restore_list(self, var_list=['outliner_list1',
                                     'outliner_list2',
                                     'outliner_list3']):
        if isinstance(var_list, basestring):
            var_list = [var_list]
        saved_lists = []
        for v in var_list:
            if cmds.optionVar(exists=v):
                v_list = cmds.optionVar(q=v)
                v_list = v_list.split(',')
                for l in v_list:
                    if l not in saved_lists:
                        saved_lists.append(l)
        if saved_lists:
            cmds.textScrollList(
                                self.outline_list,
                                e=True,
                                a=saved_lists,
                                ra=True)
        else:
            cmds.warning('Outliner slot(s) empty.')
        return

    def rotate_layout(self):
        if cmds.paneLayout(self.m_pane, q=True, cn=True) == 'vertical2':
            self.node_pane_width = cmds.paneLayout(
                                                   self.m_pane,
                                                   q=True,
                                                   paneSize=True)[0]
            if self.node_pane_width < 20:
                self.node_pane_width = 0
            cmds.paneLayout(
                            self.m_pane,
                            e=True,
                            configuration='horizontal2',
                            paneSize=[(1, 100, self.node_pane_height),
                                      (2, 100, 100 - self.node_pane_height)])
        else:
            self.node_pane_height = cmds.paneLayout(
                                                    self.m_pane,
                                                   q=True,
                                                   paneSize=True)[1]
            if self.node_pane_height < 20:
                self.node_pane_height = 0
            cmds.paneLayout(
                            self.m_pane,
                            e=True,
                            configuration='vertical2',
                            paneSize=[(1, self.node_pane_width, 100),
                                      (2, 100 - self.node_pane_width, 100)])
        cmds.paneLayout(self.m_pane, e=True, swp=True, shp=True)
        return

    def select_all(self):
        all_items = cmds.textScrollList(self.outline_list, q=True, ai=True)
        cmds.textScrollList(self.outline_list, e=True, si=all_items)
        self.select_highlighted()
        return

    def select_highlighted(self):
        o_nodes = cmds.textScrollList(self.outline_list, q=True, si=True)
        cmds.select(o_nodes, r=True)
        return

    def sort_list(self):
        sel_items = cmds.textScrollList(self.outline_list, q=True, si=True)
        all_items = cmds.textScrollList(self.outline_list, q=True, ai=True)
        
        
        try:
            all_items = sorted(all_items, key=lambda s: s.lower())
            self.clear_list()
            cmds.textScrollList(self.outline_list, e=True, a=all_items)
            if sel_items:
                cmds.textScrollList(self.outline_list, e=True, si=sel_items)
        except:
            pass
        return

    def store_list(self, var_list):
        list_items = cmds.textScrollList(self.outline_list, q=True, ai=True)
        if list_items:
            list_items = ','.join(list_items)
            cmds.optionVar(sv=[var_list, list_items])
        cmds.savePrefs(general=True)
        return

