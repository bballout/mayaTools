#extract deformers
#marking menus to mouse 2/3  modelEdMenu.mel/dagMenuProc.mel
#hotbox marking menu tweaks
#doc tags for functions

import maya.cmds as cmds
import maya.mel as mel
import itertools

try:
    from .. import tool
except ValueError:
    import tool

#from functools import partial


class ChannelBox():
    def __init__(self):
        self.control_name = 'clChannelBox'
        self.speed_index = 0
        self.speed = pow(2.0, self.speed_index)
        self.connect_source = []
        self.attr_values = []

    def create(self):
        self.delete()
        self.m_window = cmds.window('%sWindow' % self.control_name)
        self.m_form = cmds.formLayout(parent=self.m_window)
        self.tool_frame = cmds.frameLayout(parent=self.m_form,
                                        label='Tools',
                                        collapse=True,
                                        collapsable=True)
        #TAB LAYOUT
        self.tool_tabs = cmds.tabLayout(p=self.tool_frame,
                                   w=10)
        
        #Rename section
        self.rename_row = cmds.rowLayout(
                                         parent=self.tool_tabs,
                                         numberOfColumns=3,
                                         adj=1,
                                         ct2=['left', 'right'])
        self.rename_field = cmds.textField(
                                           parent=self.rename_row,
                                           ann='xxxx_##_xxxx',
                                           aie=True,
                                           ec=lambda *args: self.rename())
        self.start_num_field = cmds.intField(
                                             parent=self.rename_row,
                                             ann='Start value',
                                             value=1,
                                             min=0,
                                             max=99,
                                             step=1,
                                             editable=True,
                                             w=25,
                                             ec=lambda *args: self.rename())
        self.rename_btn = cmds.button(
                                      parent=self.rename_row,
                                      label='Rename',
                                      w=55,
                                      c=lambda *args: self.rename())
        
        #Search/Replace section
        cmds.setParent(self.tool_tabs)
        self.replace_row = cmds.rowLayout(
                                          parent=self.tool_tabs,
                                          numberOfColumns=3,
                                          adj=1,
                                          ct2=['left', 'right'],
                                          manage=False)
        self.replace_pane = cmds.paneLayout(
                                            parent=self.replace_row,
                                            configuration='vertical2',
                                            w=10)
        self.search_field = cmds.textField(
                                        parent=self.replace_pane,
                                        ann='Search string',
                                        aie=True,
                                        ec= lambda *args: self.search_replace())
        self.replace_field = cmds.textField(
                                        parent=self.replace_pane,
                                        ann='Replace string',
                                        aie=True,
                                        ec= lambda *args: self.search_replace())
        self.replace_children_box = cmds.checkBox(
                                                 p=self.replace_row,
                                                 l='',
                                                 ann='Search/Replace Hierarchy',
                                                 value=False)
        self.replace_btn = cmds.button(
                                       parent=self.replace_row,
                                       label='Replace',
                                       c=lambda *args: self.search_replace(),
                                       w=55)
        
        #Attributes section
        cmds.setParent(self.tool_tabs)
        self.attr_row = cmds.rowLayout(
                                       parent=self.tool_tabs,
                                       numberOfColumns=3,
                                       ann='Add attribute to selected objects.',
                                       adj=1,
                                       ct3=['left','both','right'])
        self.attr_field = cmds.textField(
                                         parent=self.attr_row,
                                         aie=True,
                                         ec=lambda *args: self.add_attr())
        self.attr_radio = cmds.radioButtonGrp(
                                       'attr_radio',
                                       parent=self.attr_row,
                                       la3=['Int','Float','Bool'],
                                       numberOfRadioButtons=3,
                                       select=1,
                                       ct3=['left','both','right'],
                                       cw3=[36,46,46],
                                       onc=lambda *args: self.ui_manage_limit())
        self.attr_limit_box = cmds.checkBox(
                                            ann='Limit attribute from 0 to 1',
                                            p=self.attr_row,
                                            l='0-1')
        cmds.tabLayout(self.tool_tabs,
                       e=True,
                       tli=[(1,'Rename'), (2,'Replace'), (3,'Add Attr')])
        #END TAB LAYOUT

        #Speed buttons section
        cmds.setParent(self.m_form)
        self.speed_row = cmds.rowLayout(
                                        parent=self.m_form,
                                        numberOfColumns=5,
                                        ct5=['left',
                                             'left',
                                             'both',
                                             'right',
                                             'right'],
                                        adj=3)
        self.speed_down2_btn = cmds.button(
                                           parent=self.speed_row,
                                           label='<--',
                                           annotation='Decrease Speed',
                                           c=lambda *args:self.change_speed(-2)) 
        self.speed_down_btn = cmds.button(
                                          parent=self.speed_row,
                                          label='<-',
                                          annotation='Decrease Speed',
                                          width=48,
                                          c=lambda *args: self.change_speed(-1))                                  
        self.speed_reset_btn = cmds.button(
                                           parent=self.speed_row,
                                           label=self.speed,
                                           annotation='Reset',
                                           c=lambda *args: self.change_speed(0))
        self.speed_up_btn = cmds.button(
                                        parent=self.speed_row,
                                        label='->',
                                        annotation='Increase Speed',
                                        width=48,
                                        c=lambda *args: self.change_speed(1))
        self.speed_up2_btn = cmds.button(
                                         parent=self.speed_row,
                                         label='-->',
                                         annotation='Increase Speed',
                                         c=lambda *args: self.change_speed(2))
        
        #ChannelBox section
        cmds.setParent(self.m_form)
        self.c_box = cmds.channelBox(
                                     parent=self.m_form,
                                     precision=6,
                                     speed=self.speed,
                                     useManips='invisible')


        cmds.formLayout(self.m_form,
                        e=True,                        
                        attachForm=[(self.tool_frame, 'top', 0),
                                    (self.tool_frame, 'left', 0),
                                    (self.tool_frame, 'right', 0),
                                    (self.speed_row, 'left', 0),
                                    (self.speed_row, 'right', 0),
                                    (self.c_box, 'left', 0),
                                    (self.c_box, 'right', 0),
                                    (self.c_box, 'bottom', 0)],
                        attachControl=[(self.speed_row, 'top', 0,
                                        self.tool_frame),
                                       (self.c_box, 'top', 0,
                                        self.speed_row)],
                        attachNone=[(self.tool_frame, 'bottom'),
                                    (self.speed_row, 'bottom')])
        
        self.menu_popup_mmb = cmds.popupMenu(
                                     'cboxMenuMMB',
                                      parent=self.c_box,
                                      button=2,
                                      mm=True,
                                      aob=True,
                                      pmc=lambda *args: self.mm_edit_attrs())
        self.menu_popup_rmb = cmds.popupMenu(
                                     'cboxMenuRMB',
                                      parent=self.c_box,
                                      button=3,
                                      mm=True,
                                      aob=True,
                                      pmc=lambda *args: self.mm_connect())
        self.menu_popup_ctrl_mmb = cmds.popupMenu(
                                     'cboxMenuCtrlMMB',
                                      parent=self.c_box,
                                      ctl=True,
                                      button=2,
                                      mm=True,
                                      aob=True,
                                      pmc=lambda *args: self.mm_key_attrs())
        self.menu_popup_ctrl_rmb = cmds.popupMenu(
                                     'cboxMenuCtrlRMB',
                                      parent=self.c_box,
                                      ctl=True,
                                      button=3,
                                      mm=True,
                                      aob=True,
                                      pmc=lambda *args: self.mm_set_attrs())
        self.menu_popup_shift_rmb = cmds.popupMenu(
                                     'cboxMenuShiftRMB',
                                      parent=self.c_box,
                                      sh=True,
                                      button=3,
                                      mm=True,
                                      aob=True,
                                      pmc=lambda *args: self.mm_destroy())
        
        self.control_name = cmds.dockControl(
                                             self.control_name,
                                             content=self.m_window,
                                             label=self.control_name,
                                             allowedArea=['right','left'],
                                             area='right')
        return
    
    def delete(self):
        if cmds.dockControl(self.control_name, exists=True):
            cmds.deleteUI(self.control_name)
        if cmds.window('%sWindow' % self.control_name, exists=True):
            cmds.deleteUI('%sWindow' % self.control_name)
        return             
    
    def mm_connect(self):
        popup_menu = self.menu_popup_rmb
        cmds.menu(popup_menu, e=True, dai=True)
        cmds.menuItem(
                      parent=popup_menu,
                      l='Connect From',
                      radialPosition='W',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.connect_from())
        cmds.menuItem(
                      parent=popup_menu,
                      l='Connect To',
                      radialPosition='E',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.connect_to())
        cmds.menuItem(
                      parent=popup_menu,
                      l='SDK',
                      radialPosition='N',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.connect_sdk())
        cmds.menuItem(
                      parent=popup_menu,
                      l='SDK Forward',
                      radialPosition='NE',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.connect_sdk(action='forward'))
        cmds.menuItem(
                      parent=popup_menu,
                      l='SDK Reverse',
                      radialPosition='SE',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.connect_sdk(action='reverse'))
        cmds.menuItem(
                      parent=popup_menu,
                      l='Reverse To',
                      radialPosition='S',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.connect_utility(u_type='reverse'))
        cmds.menuItem(
                      parent=popup_menu,
                      l='MD To',
                      radialPosition='SW',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.connect_utility(u_type='md'))
        cmds.menuItem(
                      parent=popup_menu,
                      l='PMA To',
                      radialPosition='NW',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.connect_utility(u_type='pma'))
        cmds.setParent(self.m_form)
        return
    
    def mm_destroy(self):
        popup_menu = self.menu_popup_shift_rmb
        cmds.menu(popup_menu, e=True, dai=True)
        cmds.menuItem(
                      parent=popup_menu,
                      l='Delete Connection',
                      radialPosition='N',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.delete_connection())
        cmds.menuItem(
                      parent=popup_menu,
                      l='Delete History',
                      radialPosition='W',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.delete_history())
        cmds.menuItem(
                      parent=popup_menu,
                      l='Freeze Transforms',
                      radialPosition='E',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.freeze_transforms())
        cmds.setParent(self.m_form)
        return

    def mm_edit_attrs(self):
        popup_menu = self.menu_popup_mmb
        cmds.menu(popup_menu, e=True, dai=True)
        lock_menu = cmds.menuItem(parent=popup_menu,
                                  l='Lock',
                                  radialPosition='N',
                                  enableCommandRepeat=False,
                                  ec=False,
                                  subMenu=True)
        cmds.menuItem(parent=lock_menu,
                      l='Lock',
                      radialPosition='N',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.set_attr_state(lock=True))
        cmds.menuItem(parent=lock_menu,
                      l='Unlock',
                      radialPosition='S',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.set_attr_state(lock=False))
        #---
        hide_menu = cmds.menuItem(parent=popup_menu,
                                  l='Hide',
                                  radialPosition='NE',
                                  enableCommandRepeat=False,
                                  ec=False,
                                  subMenu=True)
        cmds.menuItem(parent=hide_menu,
                      l='Hide',
                      radialPosition='NE',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.set_attr_state(keyable=False,
                                                          channelbox=False))
        cmds.menuItem(parent=hide_menu,
                      l='Unhide',
                      radialPosition='SW',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.set_attr_state(keyable=True,
                                                          channelbox=False))
        #---
        lock_hide_menu = cmds.menuItem(parent=popup_menu,
                                       l='Lock/Hide',
                                       radialPosition='E',
                                       enableCommandRepeat=False,
                                       ec=False,
                                       subMenu=True)
        cmds.menuItem(parent=lock_hide_menu,
                      l='Lock/Hide',
                      radialPosition='E',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.set_attr_state(lock=True,
                                                          keyable=False,
                                                          channelbox=False))
        cmds.menuItem(parent=lock_hide_menu,
                      l='Unlock/Unhide',
                      radialPosition='W',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.set_attr_state())
        #---
        keyable_menu = cmds.menuItem(parent=popup_menu,
                                     l='Nonkeyable',
                                     radialPosition='SE',
                                     enableCommandRepeat=False,
                                     ec=False,
                                     subMenu=True)
        cmds.menuItem(parent=keyable_menu,
                      l='Nonkeyable',
                      radialPosition='SE',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.set_attr_state(keyable=True,
                                                          channelbox=True))
        cmds.menuItem(parent=keyable_menu,
                      l='Keyable',
                      radialPosition='NW',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.set_attr_state(keyable=True,
                                                          channelbox=False))
        #---
        cmds.menuItem(
                      parent=popup_menu,
                      l='Edit',
                      radialPosition='SW',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: mel.eval('RenameAttribute'))
        cmds.menuItem(
                      parent=popup_menu,
                      l='Add',
                      radialPosition='W',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: mel.eval('AddAttribute'))
        cmds.menuItem(
                      parent=popup_menu,
                      l='Delete',
                      radialPosition='S',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.delete_attr())
        cmds.menuItem(
                      parent=popup_menu,
                      l='Channels',
                      radialPosition='NW',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: mel.eval('ChannelControlEditor'))
        return
    
    def mm_key_attrs(self):
        popup_menu = self.menu_popup_ctrl_mmb
        cmds.menu(popup_menu, e=True, dai=True)
        key_menu = cmds.menuItem(
                                 parent=popup_menu,
                                 l='Key',
                                 radialPosition='E',
                                 enableCommandRepeat=False,
                                 ec=False,
                                 subMenu=True)
        cmds.menuItem(
                      parent=key_menu,
                      l='Key',
                      radialPosition='E',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.set_attr_key(action='key'))
        cmds.menuItem(
                      parent=key_menu,
                      l='Delete Key',
                      radialPosition='W',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.set_attr_key(action='delete'))
        #---
        mute_menu = cmds.menuItem(
                                  parent=popup_menu,
                                  l='Mute',
                                  radialPosition='NE',
                                  enableCommandRepeat=False,
                                  ec=False,
                                  subMenu=True)
        cmds.menuItem(
                      parent=mute_menu,
                      l='Mute',
                      radialPosition='NE',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.set_attr_key(action='mute'))
        cmds.menuItem(
                      parent=mute_menu,
                      l='Unmute',
                      radialPosition='SW',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.set_attr_key(action='unmute'))
        #---
        cmds.menuItem(
                      parent=popup_menu,
                      l='SDK',
                      radialPosition='W',
                      enableCommandRepeat=False,
                      ec=False,
                      c=lambda *args: self.window_sdk())
        cmds.menuItem(
                      parent=popup_menu,
                      l='Copy',
                      radialPosition='N',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.copy_attr_values())
        #---
        paste_menu = cmds.menuItem(parent=popup_menu,
                                   l='Paste',
                                   radialPosition='S',
                                   enableCommandRepeat=False,
                                   ec=False,
                                   subMenu=True)
        cmds.menuItem(
                      parent=paste_menu,
                      l='Paste',
                      radialPosition='S',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.paste_attr_values())
        cmds.menuItem(
                      parent=paste_menu,
                      l='Paste Flip',
                      radialPosition='N',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.paste_attr_values(scalar=-1))
        #---
        cmds.menuItem(
                      parent=popup_menu,
                      l='Flip',
                      radialPosition='SE',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.flip_attr_value())
        return

    def mm_set_attrs(self):
        popup_menu = self.menu_popup_ctrl_rmb
        cmds.menu(popup_menu, e=True, dai=True)
        cmds.menuItem(
                      parent=popup_menu,
                      l='One',
                      radialPosition='N',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.set_attr_value(value=1))
        cmds.setParent(self.m_form)
        cmds.menuItem(
                      parent=popup_menu,
                      l='Zero',
                      radialPosition='S',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.set_attr_value(value=0))
        cmds.setParent(self.m_form)
        cmds.menuItem(
                      parent=popup_menu,
                      l='Shoot Out',
                      radialPosition='W',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.shoot_out())
        cmds.menuItem(
                      parent=popup_menu,
                      l='Reset',
                      radialPosition='E',
                      enableCommandRepeat=True,
                      ec=True,
                      c=lambda *args: self.shoot_out(reset=True))
        cmds.setParent(self.m_form)
        return
    

    def add_attr(self):
        attr_list = ['int','float','bool']
        name = cmds.textField(self.attr_field, q=True, text=True)
        index = cmds.radioButtonGrp('attr_radio', q=True, select=True)
        attr_type = attr_list[index-1]
        limit = cmds.checkBox(self.attr_limit_box, q=True, value=True)
        if name:
            tool.add_attr(name, attr_type, limit)
        cmds.textField(self.attr_field, e=True, text='')
        return
    
    def change_speed(self, direction=0):
        self.speed_index += direction
        if not direction:
            self.speed_index = 0
        self.speed = pow(2, self.speed_index)
        cmds.button(self.speed_reset_btn, e=True, label=round(self.speed, 10))
        cmds.channelBox(self.c_box, e=True, speed=self.speed)
        return
    
    def connect_from(self):
        source = self.get_selected_attrs()
        if not source:
            source = self.get_default_attrs()
        self.connect_source = source
        return source
    
    def connect_utility(self, u_type='md'):
        '''Create utility node connecting source to input and selected
           attributes to output.
           Types: md/reverse.'''
        plugs = self.get_plugs(self.connect_source)
        source_sels = []
        util_nodes = []
        for s, d in plugs:
            u_node=[]
            if u_type == 'md':
                u_node = cmds.shadingNode('multiplyDivide',
                                        name='%s_MD' % s.partition('.')[0],
                                        asUtility=True)
                cmds.connectAttr(s, '%s.input1X' % u_node, f=True)
                cmds.connectAttr('%s.outputX' % u_node, d, f=True)
            elif u_type == 'reverse':
                u_node = cmds.shadingNode('reverse',
                                        name='%s_RV' % s.partition('.')[0],
                                        asUtility=True)
                cmds.connectAttr(s, '%s.inputX' % u_node, f=True)
                cmds.connectAttr('%s.outputX' % u_node, d, f=True)
            elif u_type == 'pma':
                u_node = cmds.shadingNode('plusMinusAverage',
                                        name='%s_PMA' % s.partition('.')[0],
                                        asUtility=True)
                cmds.connectAttr(s, '%s.input1D[0]' % u_node, f=True)
                cmds.connectAttr(s, '%s.input1D[1]' % u_node, f=True)
                cmds.disconnectAttr(s, '%s.input1D[1]' % u_node)
                cmds.connectAttr('%s.output1D' % u_node, d, f=True)
            util_nodes.append(u_node)
            source_sels.append(s.rpartition('.')[0])
        #cmds.select(source_sels, r=True)
        return util_nodes
    
    def connect_sdk(self, action='current'):
        '''Create Set Driven Keys for selected attributes using 
           source member as driver. (set in connect_from()).
           Actions: current/forward/reverse.'''
        plugs = self.get_plugs(self.connect_source)
        source_sels = []
        for s, d in plugs:
            if action == 'current':
                cmds.setDrivenKeyframe(d,
                                       currentDriver=s,
                                       itt='spline',
                                       ott='spline')
            elif action == 'reverse':
                cmds.setDrivenKeyframe(d,
                                       currentDriver=s,
                                       itt='spline',
                                       ott='spline',
                                       driverValue=0,
                                       value=1)
                cmds.setDrivenKeyframe(d,
                                       currentDriver=s,
                                       itt='spline',
                                       ott='spline',
                                       driverValue=1,
                                       value=0)
            elif action == 'forward':
                cmds.setDrivenKeyframe(d,
                                       currentDriver=s,
                                       itt='spline',
                                       ott='spline',
                                       driverValue=0,
                                       value=0)
                cmds.setDrivenKeyframe(d,
                                       currentDriver=s,
                                       itt='spline',
                                       ott='spline',
                                       driverValue=1,
                                       value=1)
            source_sels.append(s.rpartition('.')[0])
        #cmds.select(source_sels, r=True)
        return
    
    def connect_to(self):
        plugs = self.get_plugs(self.connect_source)
        source_sels = []
        for s, d in plugs:
            cmds.connectAttr(s, d, f=True)
            source_sels.append(s.rpartition('.')[0])
        #cmds.select(source_sels, r=True)
        return
    
    def copy_attr_values(self):
        '''Get values of selected attributes and store in list.'''
        attrs = self.get_selected_attrs(mains=True,
                                        shapes=True,
                                        history=True,
                                        outputs=True,
                                        error=False)
        if not attrs:
            attrs = self.get_default_attrs()
        values = []
        for obj in attrs:
            o_value = []
            for a in obj:
                v = cmds.getAttr(a)
                o_value.append(v)
            values.append(o_value)
        self.attr_values = values
        return values
    
    def delete_attr(self):
        attrs = self.get_selected_attrs(mains=True,
                                        flatten=True,
                                        error=False)        
        for a in attrs:
            try:
                cmds.deleteAttr(a)
            except:
                pass
        return
    
    def delete_connection(self):
        attrs = self.get_selected_attrs(mains=True,
                                        shapes=True,
                                        history=True,
                                        outputs=True,
                                        flatten=True,
                                        error=False)
        for a in attrs:
            mel.eval('source channelBoxCommand')
            mel.eval('CBdeleteConnection %s' % a)
        return 
    
    def delete_history(self):
        sels = tool.get_sels()
        cmds.delete(sels, constructionHistory=True)
        return
    
    def flip_attr_value(self):
        '''Multiply attribute value by -1.'''
        attrs = self.get_selected_attrs(mains=True,
                                        shapes=True,
                                        history=True,
                                        outputs=True,
                                        flatten=True,
                                        error=False)
        for a in attrs:
            value = cmds.getAttr(a)
            try:
                cmds.setAttr(a, value*-1)
            except:
                pass
        return
    
    def freeze_transforms(self):
        sels = tool.get_sels()
        main_attrs = self.get_selected_attrs(error=False, mains=True)
        
        if sels and not main_attrs:
            cmds.makeIdentity(sels,
                              apply=True,
                              translate=True,
                              rotate=True,
                              scale=True,
                              normal=False)
        else:
            for attrs in main_attrs:
                trans = False
                rot = False
                scale = False
                obj = set()
                for attr in attrs:
                    o = attr.rpartition('.')[0]
                    a = attr.rpartition('.')[2]
                    if a in ['tx','ty','tz']:
                        obj.add(o)
                        trans = True
                    elif a in ['rx','ry','rz']:
                        obj.add(o)
                        rot = True
                    elif a in ['sx','sy','sz']:
                        obj.add(o)
                        scale = True
                obj = ''.join(obj)
                if obj:
                    cmds.makeIdentity(obj,
                                      apply=True,
                                      translate=trans,
                                      rotate=rot,
                                      scale=scale,
                                      normal=False)
        return
    
    def get_default_attrs(self, flatten=False):
        sels = tool.get_sels()
        attrs=[]
        for s in sels:
            s_attrs = []
            for a in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
                s_attrs.append('%s.%s' % (s, a))
            attrs.append(s_attrs)
        if flatten:
            attrs = list(itertools.chain.from_iterable(attrs))
        return attrs
    
    def get_selected_attrs(self,
                           mains=True,
                           shapes=False, 
                           history=False,
                           outputs=False,
                           flatten=False,
                           error=True):
        
        m = cmds.channelBox(self.c_box, q=True, mol=True)
        s = cmds.channelBox(self.c_box, q=True, sol=True)
        h = cmds.channelBox(self.c_box, q=True, hol=True)
        o = cmds.channelBox(self.c_box, q=True, ool=True)
        m_attrs = cmds.channelBox(self.c_box, q=True, sma=True)
        s_attrs = cmds.channelBox(self.c_box, q=True, ssa=True)
        h_attrs = cmds.channelBox(self.c_box, q=True, sha=True)
        o_attrs = cmds.channelBox(self.c_box, q=True, soa=True)
        
        if not m:
            cmds.error('Nothing selected. Select object(s} before running.')
        
        nodes = []
        attrs = []
        sel_attrs = []
        count = len(m)
        if m and m_attrs and mains:
            m.append(m.pop(0))
            nodes.extend([m])
            attrs.extend([m_attrs])
        if s and s_attrs and shapes:
            s.append(s.pop(0))
            nodes.extend([s])
            attrs.extend([s_attrs])
        if h and h_attrs and history:
            h.append(h.pop(0))
            nodes.extend([h])
            attrs.extend([h_attrs])
        if o and o_attrs and outputs:
            o.append(o.pop(0))
            nodes.extend([o])
            attrs.extend([o_attrs])
        
        for n in nodes:
            if len(n) != count:
                cmds.error('Highlighted attributes do not exist for all '
                           'selected objects.')
        
        if len(attrs) > 1:
            nodes = map(None, *nodes)
        else:
            nodes = [[n] for node in nodes for n in node]
        
        for i in range(len(nodes)):
            sel_attrs.insert(i, [])
            for j in range(len(nodes[i])):
                for a in attrs[j]:
                    obj_name = '%s.%s' % (nodes[i][j], a)
                    if cmds.objExists(obj_name):
                        sel_attrs[i].append(obj_name)
                    else:
                        if error:
                            cmds.error('"%s" does not exist.' % obj_name)
                        else:
                            cmds.warning('"%s" does not exist. Skipped for '
                                         'this operation.' % obj_name)
        if flatten:
            sel_attrs = list(itertools.chain.from_iterable(sel_attrs))
        return sel_attrs
    
    def get_plugs(self, source):
        dest = self.get_selected_attrs(mains=True,
                                       shapes=True,
                                       history=True,
                                       outputs=True,
                                       error=False)
        plugs = []
        
        #Default to transform attrs if none are specified
        if not dest:
            dest = self.get_default_attrs()
        flat_source = list(itertools.chain.from_iterable(source))
        flat_dest = list(itertools.chain.from_iterable(dest))

        #No source 
        if not source:
            cmds.error('No source variable(s) specified.')
        #One source attribute
        if len(flat_source) == 1:
            try:
                for d in flat_dest:
                    plugs.append([flat_source[0], d])
            except:
                pass
        #One source object
        elif len(source) == 1:
            s = source[0]
            for d in dest:
                for i in range(len(d)):
                    try:
                        plugs.append([s[i], d[i]])
                    except IndexError:
                        cmds.warning('Not enough source variables specified. '
                                     'Skipping %s.' % d[i])      
        #Multiple source objects
        else:
            for s, d in map(None, source, dest):
                #End loop if no more dest attributes
                if not d:
                    break
                for i in range(len(d)):
                    try:
                        plugs.append([s[i], d[i]])
                    except IndexError:
                        cmds.warning('Not enough source variables specified. '
                                     'Skipping %s.' % d[i])
                    except TypeError:
                        cmds.warning('Not enough source objects specified. '
                                     'Skipping %s.' % d[i].partition('.')[0])
                        break
        return plugs
    
    def paste_attr_values(self, scalar=1):
        '''Set values of selected attributes using the stored values in
            attr_values member (set in copy_attr_values()).'''
        plugs = self.get_plugs(self.attr_values)
        for s, d in plugs:
            cmds.setAttr(d, s*scalar)
        return    

    def rename(self):
        '''Rename the selected node(s).'''
        name = cmds.textField(self.rename_field, q=True, text=True)
        start = cmds.intField(self.start_num_field, q=True, v=True)
        n_names = tool.rename(name=name, start=start)
        return n_names
    
    def search_replace(self):
        '''Search for instance in string and replace and user defined string.'''
        search_str = cmds.textField(self.search_field, q=True, text=True)
        replace_str = cmds.textField(self.replace_field, q=True, text=True)
        hierarchy = cmds.checkBox(self.replace_children_box, q=True, v=True)
        n_names = tool.search_replace(search_str, replace_str, hierarchy)
        return n_names

    def set_attr_state(self, lock=False, keyable=True, channelbox=False):
        '''Set attributes to lock/keyable/hidden state.'''
        attrs = self.get_selected_attrs(mains=True,
                                        shapes=True,
                                        history=True,
                                        outputs=True,
                                        flatten=True,
                                        error=False)
        if not attrs:
            attrs = self.get_default_attrs(flatten=True)
        for a in attrs:
            try:
                cmds.setAttr(a,
                             lock=lock,
                             keyable=keyable,
                             channelBox=channelbox)
            except RuntimeError as e:
                cmds.warning('%s' % e)
        return
    
    def set_attr_value(self, value):
        '''Set selected attributes to a specific value.'''
        attrs = self.get_selected_attrs(mains=True,
                                        shapes=True,
                                        history=True,
                                        outputs=True,
                                        flatten=True,
                                        error=False)
        for a in attrs:
            try:
                cmds.setAttr(a, value)
            except RuntimeError as e:
                cmds.warning('%s' % e)
                
        return
    
    def set_attr_key(self, action='key'):
        """Set/delete/mute/unmute keys.
           Actions: 'key', 'delete', 'mute', 'unmute'"""
        attrs = self.get_selected_attrs(mains=True,
                                        shapes=True,
                                        history=True,
                                        outputs=True,
                                        flatten=True,
                                        error=False)
        if not attrs:
            attrs = self.get_default_attrs(flatten=True)
        for a in attrs:
            if action == 'key':
                try:
                    cmds.setKeyframe(a)
                except RuntimeError as e:
                    cmds.warning('%s' % e)
            elif action == 'delete':
                try:
                    cmds.cutKey(a, cl=True)
                except RuntimeError as e:
                    cmds.warning('%s' % e)
            elif action == 'mute':
                try:
                    cmds.mute(a)
                except RuntimeError as e:
                    cmds.warning('%s' % e)
            elif action == 'unmute':
                try:
                    cmds.mute(a, disable=True, force=True)
                except RuntimeError as e:
                    cmds.warning('%s' % e)
        return
    
    def shoot_out(self, sels=[], reset=False):
        sels = tool.get_sels(sels)
        t=[99,99,99]
        s=[.1,.1,.1]
        sh=[0,0,0]
        
        if reset:
            t=[0,0,0]
            s=[1,1,1]
        
        for sel in sels:
            allowed_types = ['transform','joint']
            if cmds.nodeType(sel) in allowed_types:
                cmds.xform(
                           sel,
                           translation=t,
                           rotation=t,
                           scale=s,
                           shear=sh)
        return sels
    
    def ui_manage_limit(self):
        '''Toggles editable state of 0-1 checkbox when adding attributes.'''
        r_state = cmds.radioButtonGrp('attr_radio',
                                      q=True,
                                      select=True)
        if r_state == 3:
            cmds.checkBox(self.attr_limit_box, e=True, editable=False)
        else:
            cmds.checkBox(self.attr_limit_box, e=True, editable=True)
        return
    
    def window_sdk(self, sels=[]):
        '''Open the "Set Driven Key" window with selections as driver/driven.'''
        if not sels:
            sels = tool.get_sels(sels, False)
        mel.eval('setDrivenKeyWindow "" {}')
        if sels:
            cmds.select(cl=True)
            mel.eval('updateSetDrivenWnd("driver","",{})')
            mel.eval('updateSetDrivenWnd("driven","",{})')
            try:
                cmds.select(sels[0], r=True)
                mel.eval('updateSetDrivenWnd("driver","",{})')
                cmds.select(sels[1:], r=True)
                mel.eval('updateSetDrivenWnd("driven","",{})')
            except:
                pass
            cmds.select(sels)
        return
    
    
            