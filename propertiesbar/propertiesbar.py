# Glumol - An adventure game creator
# Copyright (C) 1998-2008  Sylvain Baubeau & Alexis Contour

# This file is part of Glumol.

# Glumol is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# Glumol is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Glumol.  If not, see <http://www.gnu.org/licenses/>.

#!/usr/bin/python
# -*- coding: utf-8 -*-

from depplatform import get_image_path
import wx
import wx.html as html
import string
from propertyeditors import *
from propertyeditorcontrols import *
import new
from log import *
from behaviorswindow import BehaviorsWindow
import os.path
from types import ClassType, ListType
from inspect import isclass
from propertiesbar_actions import PropertiesBarChangeValue
from Queue import Queue
import wx.aui

stock_size = 50
IECWidthFudge = 3
oiLineHeight = 20

[wxID_ENTER, wxID_UNDOEDIT, wxID_CRSUP, wxID_CRSDOWN, wxID_CONTEXTHELP, wxID_SWITCHDESIGNER, wxID_SWITCHEDITOR, wxID_OPENITEM, wxID_CLOSEITEM] = map(lambda _init_ctrls: wx.NewId(), range(9))

class PropertiesBar(wx.Panel):
    name = _('Properties Bar')

    """Frame-based object editor"""
    def __init__(
        self, parent=None, id=-1, title = "ObjectEditor",
        pos = wx.DefaultPosition, size = wx.DefaultSize,
        style = wx.DEFAULT_FRAME_STYLE,
        name = "objecteditor",
        value = None,
    ):
        wx.Panel.__init__(self, parent, -1)
        panel = self
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.newprop = wx.BitmapButton(self, 100, 
                                       wx.Bitmap(get_image_path('new.xpm'), wx.BITMAP_TYPE_XPM))
        self.newprop.SetToolTipString(_("Create a new property"))
        sizer2.Add(self.newprop, 0)
        
        self.delprop = wx.BitmapButton(self, 101, 
                                       wx.Bitmap(get_image_path('delete.xpm'), wx.BITMAP_TYPE_XPM))
        self.delprop.SetToolTipString(_("Delete property"))
        self.delprop.Enable(False)
        sizer2.Add(self.delprop, 0)

        self.filter = wx.BitmapButton(self, 102, 
                                       wx.Bitmap(get_image_path('filter.xpm'), wx.BITMAP_TYPE_XPM))
        self.filter.SetToolTipString(_("Filter properties"))
        sizer2.Add(self.filter, 0)
        
        sizer.Add(sizer2)
        
        self.nb = wx.aui.AuiNotebook(self, id, pos, wx.DefaultSize, style = wx.aui.AUI_NB_SCROLL_BUTTONS)
        sizer.Add(self.nb, 4, wx.EXPAND)
        self.artub_frame = parent
        self.inspector = InspectorPropScrollWin(self.nb, -1, wx.DefaultPosition, wx.DefaultSize) # wx.Size(size[0], size[1]))
        self.inspector.pb = self
        self.events = InspectorScrollWin(self.nb, -1, wx.DefaultPosition, wx.DefaultSize)
        self.events.pb = self
        self.nb.AddPage(self.inspector, _("Properties"))
        self.nb.AddPage(self.events, _("Events"))
        self.help = html.HtmlWindow(panel, -1, style=wx.BORDER | wx.NO_FULL_REPAINT_ON_RESIZE)
        class MyPanel(wx.Panel):
            def OnSize(self, event):
                w,h = self.GetClientSizeTuple()
                self.list.SetDimensions(0, 0, w, h)
                
            def __init__(self, parent):
                wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)
                self.Bind(wx.EVT_SIZE, self.OnSize)

        panel2 = MyPanel(self.nb)        
        panel2.list = self.behaviors = BehaviorsWindow(panel2, 10001)
        self.nb.AddPage(panel2, _("Behaviors"))
        sizer.Add(self.help, 1, wx.EXPAND)
        self.dict = {}
        self.active_resource = None
        self.dont_select = False
        self.sizer = sizer
        self.panel = panel
        ignore = set()
        for i in ('variables', 'class_name'):
            ignore.add(i)
        self.ignore = ignore
        self.name_values_stock = []
        self.events_name_values_stock = []
        panel.SetSizer(sizer)
        sizer.Fit(self)
        
        wx.EVT_BUTTON(self, 100, self.inspector.on_new_property)
        wx.EVT_BUTTON(self, 101, self.inspector.on_del_property)

    def on_close_window(self, event):
        self.manager.toggle_bar(self.menu_id)
        
    def create_property(self, name, value, tipe, script, constraints = None, idx = -1, indent = 0):
        if idx == -1:
            idx = len(self.inspector.nameValues)
        self.namevalue = self.get_name_value(self.inspector, self.inspector.panelNames, self.inspector.panelValues, name, idx, indent, value, tipe, script, constraints)
        self.inspector.nameValues.append(self.namevalue)
            
    def get_name_value(self, *args):
        l = len(self.name_values_stock)
        if l > args[4]:
            nv = self.name_values_stock[args[4]]
            nv.reset(*args)
            return nv
        else:
            nv = NameValue(*args)
            if l < stock_size: self.name_values_stock.append(nv)
            return nv
        
    def get_event(self, *args):
        l = len(self.events_name_values_stock)
        if l > args[4]:
            nv = self.events_name_values_stock[args[4]]
            nv.reset(*args)
            return nv
        else:
            nv = NameValue(*args)
            if l < stock_size: self.events_name_values_stock.append(nv)
            return nv

    def create_event(self, name, value, tipe, script, idx = -1, indent = 0):
        events = self.events
        if idx == -1:
            idx = len(events.nameValues)
        self.namevalue = self.get_event(events, events.panelNames, events.panelValues, name, idx, indent, value, tipe, script)
        events.nameValues.append(self.namevalue)
    
    def create_values(self, cm):
        newobj = cm
            
        for i in dir(cm.obj):
            if i[:3] == 'on_':
                self.create_event(i, getattr(cm.obj, i).im_func, 1, cm.obj)
                continue
        
        def cmp(a, b):
            if type(a) == ListType:
                _a = a[0].lower()
            else: _a = a.lower()
            if type(b) == ListType:
                _b = b[0].lower()
            else: _b = b.lower()
            if _a < _b: return -1
            elif _a == _b: return 0
            else: return 1
     
        cm.variables.sort(cmp)
        obj = cm.obj
        for i in cm.variables:
            try:
                if type(i) == ListType:
                    i, j = i
                    if i != '_' and (not i in self.ignore) and (not i in cm.ignore) and hasattr(obj, i):
                        self.create_property(i, getattr(obj, i), 1, obj, j)
                elif (not i in self.ignore) and (not i in cm.ignore) and (i[0] != '_'):
                    self.create_property(i, getattr(obj, i), 1, obj)
            except: pass        
        return obj

    def reload(self):
        self.set_inspector(self.cm)
        
    def set_inspector(self, cm):
        if self.inspector.prevSel:
            self.inspector.prevSel.hideEditor()
        if self.dont_select or self.artub_frame.debugging: return
        self.inspector.SetScrollPos(wx.VERTICAL, 0)
        self.Freeze()
        self.cm = cm
        self.clear()
        try:
            if cm:
                self.newprop.Enable(True)
                self.active_resource = cm.resource
                self.behaviors.set_inspector(cm)
                import profile
                loc = {}
                loc["cm"] = cm
                loc["self"] = self
                self.create_values(cm)
        except:
            print "Error while creating items in properties bar (set_inspector function)", sys.exc_info()
            import traceback
            traceback.print_stack()
            self.Thaw()
            raise
        try: self.Thaw()
        except: pass # Because of a strange behaviour on Windows
        self.delprop.Enable(False)
        self.events.refreshSplitter()
        self.inspector.refreshSplitter()
            
    def clear(self):
        n = min(max(0, stock_size - len(self.name_values_stock)),
                len(self.inspector.nameValues))
        for i in xrange(n):
            nv = self.inspector.nameValues[i]
            nv.nameCtrl.Show(False)
            nv.value.Show(False)
            nv.separatorN.Show(False)
            nv.separatorV.Show(False)
            nv.hideEditor(True)
            nv.destr = True

        self.inspector.nameValues = self.inspector.nameValues[len(self.name_values_stock):]

        n = len(self.events.nameValues)
        for i in xrange(n):
            nv = self.events.nameValues[i]
            nv.nameCtrl.Show(False)
            nv.value.Show(False)
            nv.separatorN.Show(False)
            nv.separatorV.Show(False)
            nv.hideEditor(True)

        self.events.nameValues = self.events.nameValues[len(self.events_name_values_stock):]
        
        self.events.cleanup()
        self.inspector.cleanup()

    def select(self, resource):
        raise
        if self.dont_select: return
        self.inspector.cleanup()
        self.events.cleanup()
        self.active_resource = resource
        return self.create_values(resource)

class NameValueEditorScrollWin(wx.ScrolledWindow):
    """ Window that hosts a list of name values. Also provides capability to
        scroll a line at a time, depending on the size of the list """

    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize,
                style=wx.HSCROLL | wx.VSCROLL, name='scrolledWindow'):
        wx.ScrolledWindow.__init__(self, parent, id,
                style=style)
        self.nameValues = []
        self.prevSel = None
        self.splitter = wx.SplitterWindow(self, -1, wx.Point(0, 0),
          parent.GetSize(),
          style = wx.NO_3D|wx.SP_3D|wx.SP_NOBORDER|wx.SP_LIVE_UPDATE)
        self.splitter.SetSashGravity(0.5)

        self.panelNames = wx.Panel(self.splitter, -1,
          wx.DefaultPosition, wx.Size(100, 1), style=0)#
        wx.EVT_SIZE(self.panelNames, self.OnNameSize)
        self.panelValues = wx.Panel(self.splitter, -1, style=0)
        wx.EVT_SIZE(self.panelValues, self.OnNameSize)

        self.splitter.SplitVertically(self.panelNames, self.panelValues)
        self.splitter.SetSashPosition(100)
        self.splitter.SetMinimumPaneSize(20)
        self.splitter.SetSashSize(4)

        wx.EVT_SIZE(self, self.OnSize)

    def cleanup(self):
        # XXX Does this always have to be inited here?
        self.prevSel = None
        #clean up
        for i in self.nameValues:
            i.destroy(True)
        self.nameValues = []
        # self.refreshSplitter()

    def getNameValue(self, name):
        for nv in self.nameValues:
            if nv.propName == name:
                return nv
        return None

    def getWidth(self):
        return self.GetSize().x

    def getHeight(self):
        return len(self.nameValues) *oiLineHeight + 5

    def getValueWidth(self):
        return self.panelValues.GetClientSize().x + IECWidthFudge

    def refreshSplitter(self):
        s = wx.Size(self.GetClientSize().GetWidth(), self.getHeight())
        wOffset, hOffset = self.GetViewStart()
        wOffset = 0
        hOffset = 0
        puw, puh = self.GetScrollPixelsPerUnit()
        if hOffset and len(self.nameValues) < s.y /hOffset:
            hOffset = 0
        if s.x:
            self.splitter.SetDimensions(wOffset * puw, hOffset * puh * -1, s.x, s.y)
        self.updateScrollbars(wOffset, hOffset)

    def updateScrollbars(self, wOffset, hOffset):
        height = len(self.nameValues)
        self.SetScrollbars(oiLineHeight, oiLineHeight, 0, height + 1, wOffset, hOffset) #height + 1

    def propertySelected(self, nameValue):
        """ Called when a new name value is selected """
        if self.prevSel:
            if nameValue == self.prevSel: return
            self.prevSel.hideEditor()
        nameValue.showEdit()
        if hasattr(self.pb.cm.obj, "class_name"):
            page = os.path.join("docs", self.pb.cm.obj.class_name, nameValue.propName + ".html")
            if os.path.exists(page):
                self.pb.help.LoadPage(page)
            else:
                self.pb.help.LoadPage(os.path.join(wx.GetApp().artub_path, "docs", "blank.html"))
        self.prevSel = nameValue

    def resizeNames(self):
        for nv in self.nameValues:
            nv.resize(self.panelNames.GetSize().x, self.getValueWidth())

    def initSash(self):
        self.splitter.SetSashPosition(int(self.GetSize().x / 2.25))

    def getSubItems(self, nameValue):
        idx = nameValue.idx + 1
        idnt = nameValue.indent + 1
        res = []
        while 1:
            if idx >= len(self.nameValues): break
            nameValue = self.nameValues[idx]
            if nameValue.indent < idnt: break
            res.append(nameValue)
            idx = idx + 1
        return res

    def initFromComponent(self, name):
        """ Update a property and it's sub properies from the underlying
            control """

        nv = self.getNameValue(name)
        if nv:
            nv.initFromComponent()
            for nv in self.getSubItems(nv):
                nv.propEditor.companion.updateObjFromOwner()
                nv.propEditor.propWrapper.connect(nv.propEditor.companion.obj, nv.propEditor.companion)
                nv.initFromComponent()

    def OnSize(self, event):
        size = self.GetSize()
        width = event.GetSize().width
        size.width = width
        self.refreshSplitter()
        
    def OnNameSize(self, event):
        self.resizeNames()
        event.Skip()

class InspectorScrollWin(NameValueEditorScrollWin):
    """ Derivative of NameValueEditorScrollWin that adds knowledge about the
        Inspector and implements keyboard events """
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.HSCROLL | wx.VSCROLL, name='scrolledWindow'):
        NameValueEditorScrollWin.__init__(self, parent, id, pos, size, style, name)
        
        self.EnableScrolling(False, True)

        self.selObj = None
        self.selCmp = None

        self.prevSel = None

        wx.EVT_MENU(self, wxID_ENTER, self.OnEnter)
        wx.EVT_MENU(self, wxID_UNDOEDIT, self.OnUndo)
        wx.EVT_MENU(self, wxID_CRSUP, self.OnCrsUp)
        wx.EVT_MENU(self, wxID_CRSDOWN, self.OnCrsDown)
        wx.EVT_MENU(self, wxID_CONTEXTHELP, self.OnContextHelp)
        wx.EVT_MENU(self, wxID_OPENITEM, self.OnOpenItem)
        wx.EVT_MENU(self, wxID_CLOSEITEM, self.OnCloseItem)

        
        self.SetAcceleratorTable(wx.AcceleratorTable([\
          (0, wx.WXK_RETURN, wxID_ENTER),
          (0, wx.WXK_ESCAPE, wxID_UNDOEDIT),
          #(keyDefs['ContextHelp'][0], keyDefs['ContextHelp'][1], wxID_CONTEXTHELP),
          (0, wx.WXK_UP, wxID_CRSUP),
          (0, wx.WXK_DOWN, wxID_CRSDOWN),
          (wx.ACCEL_CTRL, wx.WXK_RIGHT, wxID_OPENITEM),
          (wx.ACCEL_CTRL, wx.WXK_LEFT, wxID_CLOSEITEM),
          ])) 
          
        self.parent = parent
        self.propertyRegistry = PropertyRegistry()
        registerEditors(self.propertyRegistry)
       
    def test(self):
        self.parent.select(self.parent.artub_frame.project["Script1"])
  
    def create_name_value(self, prop, script, idx = -1, indent = 0):
        if idx == -1:
            idx = len(self.nameValues)
        if idx == None:
            self.zobi
        self.namevalue = NameValue(self, self.panelNames, self.panelValues, prop.name, idx, indent, prop.value, prop.type, script)
        self.nameValues.append(self.namevalue)
        
    def create_value(self, tipe, name, value, type_value, script, idx = -1, indent = 0):
        if idx == -1:
            idx = len(self.nameValues)
        self.namevalue = tipe(self, self.panelNames, self.panelValues, name, idx, indent, value, type_value, script)
        self.nameValues.append(self.namevalue)
        
    def add_name_value(self, nv, idx = -1, index = 0):
        if idx == -1:
            idx = len(self.nameValues)
        self.nameValues.append(self.namevalue)
        
    def setInspector(self, inspector):
        self.inspector = inspector

    def destroy(self):
        self.inspector = None

    def readObject(self, propList):
        """ Override this method in derived classes to implement the
            initialisation and construction of the name value list """

    def findEditingNameValue(self):
        for idx in range(len(self.nameValues)):
            if self.nameValues[idx].editing:
                return idx
        return -1

    def deleteNameValues(self, idx, count, cancel = False):
        """ Removes a range of name values from the Inspector.
            Used to collapse sub properties
        """
        deleted = 0
        if idx < len(self.nameValues):
            # delete sub properties
            while (idx < len(self.nameValues)) and (deleted < count):
                if self.nameValues[idx] == self.prevSel: raise "caca"; self.prevSel = None
                self.nameValues[idx].destroy(cancel)
                del self.nameValues[idx]
                deleted = deleted + 1

            # move properties up
            for idx in range(idx, len(self.nameValues)):
                self.nameValues[idx].setPos(idx)

    def extendHelpUrl(self, wxClass, url):
        return wxClass, url

    def show_indents(self):
        log("show_indents")
        for i in self.nameValues:
            log(i.propName, i.indent, i.idx)
        log("end show_indents")
        
    def collapse(self, nameValue):
        # delete all NameValues until the same indent, count them
        startIndent = nameValue.indent
        idx = nameValue.idx + 1

        # Move deletion into method and use in removeEvent of EventWindow
        self.show_indents()
        i = idx
        if i < len(self.nameValues):
            while (i < len(self.nameValues)) and \
              (self.nameValues[i].indent > startIndent):
                i = i + 1
        count = i - idx

        self.deleteNameValues(idx, count)
        self.refreshSplitter()
        nameValue.propEditor.expanded = False
        
    def OnEnter(self, event):
        for nv in self.nameValues:
            if nv.editing:
                nv.propEditor.inspectorPost(False)

    def OnUndo(self, event):
        # XXX Implement!
        pass

    def OnCrsUp(self, event):
        if len(self.nameValues) > 1:
            for idx in range(1, len(self.nameValues)):
                if self.nameValues[idx].editing:
                    self.propertySelected(self.nameValues[idx-1])
                    break
            else:
                self.propertySelected(self.nameValues[0])

            x, y = self.GetViewStart()
            if y >= idx:
                self.Scroll(x, y-1)

    def OnCrsDown(self, event):
        if len(self.nameValues) > 1:
            for idx in range(len(self.nameValues)-1):
                if self.nameValues[idx].editing:
                    self.propertySelected(self.nameValues[idx+1])
                    break
            else:
                self.propertySelected(self.nameValues[-1])

            dx, dy = self.GetScrollPixelsPerUnit()
            cs = self.GetClientSize()
            x, y = self.GetViewStart()
            if y <= idx + 1 - cs.y / dy:
                self.Scroll(x, y+1)

    def OnContextHelp(self, event):
        if self.inspector.selCmp:
            wxClass, url = self.extendHelpUrl(self.inspector.selCmp.GetClass(), '')
            if wxClass:
                Help.showCtrlHelp(wxClass, url)

    def OnOpenItem(self, event):
        idx = self.findEditingNameValue()
        if idx != -1:
            nameValue = self.nameValues[idx]
            if nameValue.expander and not nameValue.propEditor.expanded:
                self.expand(nameValue)
                nameValue.expander.SetValue(False)

    def OnCloseItem(self, event):
        idx = self.findEditingNameValue()
        if idx != -1:
            nameValue = self.nameValues[idx]
            if nameValue.expander and nameValue.propEditor.expanded:
                self.collapse(nameValue)
                nameValue.expander.SetValue(True)

class InspectorPropScrollWin(InspectorScrollWin):
    """ Specialised InspectorScrollWin that understands properties """
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.HSCROLL | wx.VSCROLL, name='scrolledWindow'):
        InspectorScrollWin.__init__(self, parent, id, pos, size, style, name)
        wx.EVT_RIGHT_DOWN(self, self.on_right_button_down)

    def on_right_button_down(self, evt):
        if not self.pb.artub_frame.project: return
        menu = wx.Menu()
        id = wx.NewId()
        menu.Append(id, _("New property"))
        wx.EVT_MENU(self, id, self.on_new_property)
        self.PopupMenu(menu, self.ScreenToClient(wx.GetMousePosition()))
    
    def propertySelected(self, nameValue):
        resource = self.pb.cm.resource
        cond = False
        try: cond |= resource.get_class().get_global_prop(nameValue.propName).ast != None
        except: pass
        try: cond |= resource.get_class().get_prop(nameValue.propName).ast != None
        except: pass
        self.pb.delprop.Enable(cond)
        return InspectorScrollWin.propertySelected(self, nameValue)

    def on_del_property(self, evt):
        gns = wx.GetApp().gns
        resource = self.pb.cm.resource
        klass = gns.getattr(resource.name)
        if not resource.get_class().get_global_prop(self.prevSel.propName).ast and \
           not resource.get_class().get_prop(self.prevSel.propName).ast:
            raise "Class " + resource.name + " has not property " + self.prevSel.propName
        if self.prevSel.propName in klass.__dict__.keys():
            resource.get_class().remove_global_property(self.prevSel.propName)
        else:
            resource.get_class().remove_property(self.prevSel.propName)
        resource.ast_has_changed = True
        self.pb.artub_frame.active_editor.update(False)
        
    def on_new_property(self, evt):
        if not self.pb.artub_frame.project: return
        import newproperty
        new_prop_dlg = newproperty.NewPropertyDialog(self, -1)
        new_prop_dlg.CenterOnScreen()
        if new_prop_dlg.ShowModal() == wx.ID_OK:
            if self.pb.cm:
                if new_prop_dlg.scope.GetSelection():
                    self.pb.cm.resource.get_class().add_global_property(
                        new_prop_dlg.name.GetValue(),
                        new_prop_dlg.value.GetValue())
                else:
                    self.pb.cm.resource.get_class().add_property(
                        new_prop_dlg.name.GetValue(),
                        new_prop_dlg.value.GetValue())

                self.pb.cm.resource.ast_has_changed = True
                self.pb.artub_frame.active_editor.update(False)
        new_prop_dlg.Destroy()
        del newproperty

    def setNameValues(self, compn, rootCompn, nameValues, insIdx, indent, ownerPropEdit = None):
        top = insIdx
        # Add NameValues to panel
        for nameValue in nameValues:
            # Check if there is an associated companion
            if compn:
                self.nameValues.insert(top, PropNameValue(self, self.panelNames,
                  self.panelValues, compn, rootCompn, nameValue.name,
                  nameValue, top, indent,
                  compn.getPropEditor(nameValue.name),
                  compn.getPropOptions(nameValue.name),
                  compn.getPropNames(nameValue.name),
                  ownerPropEdit))
            top = top + 1

        self.refreshSplitter()

    def extendHelpUrl(self, wxClass, url):
        if self.prevSel:
            return self.prevSel.createHelpUrl()
        return wxClass, url

    # read in the root object
    def readObject(self, propList):
        self.setNameValues(self.inspector.selCmp, self.inspector.selCmp,
          propList, 0, 0)

    def expand(self, nameValue):
        nv = self.nameValues[nameValue.idx]
        obj = nv.propValue
        
        nvs = nv.propEditor.getSubCompanion()
        indt = self.nameValues[nameValue.idx].indent + 1
        sze = len(nvs)
        # move properties down
        startIdx = nameValue.idx + 1
        for idx in range(startIdx, len(self.nameValues)):
            self.nameValues[idx].setPos(idx +sze)

        # add sub properties in the gap
        j = 0
        for i in nvs:
            self.nameValues.insert(startIdx + j, # nameValue.idx, 
                                   NameValue(self.pb, self.panelNames,
                                             self.panelValues, i[0],
                                             startIdx + j, indt,
                                             i[1], None, self.pb.cm))
            j = j + 1
        nv.propEditor.expanded = True
        nv.updateDisplayValue()
        self.show_indents()

class NameValue:
    """ Base class for all name value pairs that appear in the Inspector """
    def __init__(self, parent, nameParent, valueParent, name, idx, indent,
                 value, tipe, script, constraints = None):
        self.destr = False
        self.lastSizeN = 0
        self.lastSizeV = 0
        self.indent = indent
        self.pb = parent.pb
        self.inspector = parent
        self.propName = name
        self.editing = False

        self.nameParent = nameParent
        self.valueParent = valueParent
        self.idx = idx
        self.nameBevelTop = None
        self.nameBevelBottom = None
        self.valueBevelTop = None
        self.valueBevelBottom = None

        self.isCat = False
            
        self.propEditor = self.inspector.propertyRegistry.factory(name,
              valueParent, idx,
              valueParent.GetSize().x + IECWidthFudge, value, tipe, script, constraints)
        
        self.expander = None

        if self.propEditor:
            self.propEditor.companion = self.pb.cm
            self.propEditor.constraints = constraints
            self.propEditor.ownerPropEdit = None
            self.updatePropValue()
            displayVal = self.propEditor.getDisplayValue()

            # c:heck if it's expandable
            #"""if PropertyEditors.esExpandable in self.propEditor.getStyle():
            mID = wx.NewId()
            # self.expander = wx.CheckBox(nameParent, mID, '',
            #  wx.Point(8 * self.indent, self.idx * oiLineHeight +2),
            #  wx.Size(13, 14))
            #self.expander.SetValue(True)
            # wx.EVT_CHECKBOX(self.expander, mID, self.OnExpand)
        else:
            self.propValue = ''
            displayVal = ''

        if wx.VERSION >= (2,3,3):
            # statext uses wxPyControl only for 2.3.3+
            from wx.lib.stattext import GenStaticText
            StaticText = GenStaticText
        else:
            # pre 2.3.3 compat
            StaticText = wx.StaticText

        # Create name and value controls and separators
        self.nameCtrl = StaticText(nameParent, -1, name,
          wx.Point(8 * self.indent + 12, idx * oiLineHeight +2),
          wx.Size(self.inspector.panelNames.GetSize().x, oiLineHeight -3),
          style = wx.CLIP_CHILDREN | wx.ST_NO_AUTORESIZE)
        # self.nameCtrl.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.nameCtrl.SetToolTipString(name)
        wx.EVT_LEFT_DOWN(self.nameCtrl, self.OnSelect)


        # self.showPropNameModified(self.isCat)
        self.value = wx.StaticText(valueParent, -1, displayVal,
          wx.Point(2, idx * oiLineHeight +2), wx.Size(self.inspector.getValueWidth(),
          oiLineHeight -3), style = wx.CLIP_CHILDREN)
        #self.value.SetForegroundColour(wx.Colour(23, 50, 92))
        # self.value.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.value.SetToolTipString(displayVal)
        wx.EVT_LEFT_DOWN(self.value, self.OnSelect)
        # self.inspector.getValueWidth(), self.value, dir(self.value)

        #if lockEditor and not self.isCat:
        #    self.enboldenCtrl(self.value)

        sepCol = wx.Colour(160, 160, 160)

        self.separatorN = wx.Window(nameParent, -1, wx.Point(0,
          (idx +1) * oiLineHeight), wx.Size(self.inspector.panelNames.GetSize().x, 1),
          style = wx.CLIP_CHILDREN)
        self.separatorN.SetBackgroundColour(sepCol)

        self.separatorV = wx.Window(valueParent, -1, wx.Point(0, ###### 
          (idx +1) * oiLineHeight), wx.Size(self.inspector.getValueWidth(), 1),
          style = wx.CLIP_CHILDREN)
        self.separatorV.SetBackgroundColour(sepCol)

    def checkLockedProperty(self, name, setterName, companion):
        """ Determine if the property is locked """
        # XXX refactor, this is currently ugly
        try:
            srcVal = companion.persistedPropVal(name, setterName)
        except KeyError:
            pass
        else:
            if srcVal is not None:
                if srcVal == 'PROP_CATEGORY':
                    return PropertyEditors.LockedPropEdit, '', True

                if type(srcVal) is type([]):
                    if len(srcVal):
                        srcVal = srcVal[0]
                    else:
                        srcVal = ''
                if Utils.startswith(srcVal, 'self.') and \
                 hasattr(companion.designer.model.specialAttrs['self'], srcVal[5:]):
                    return PropertyEditors.LockedPropEdit, srcVal, False
        return None, '', False

    def destroy(self, cancel = False):
        self.hideEditor(cancel)
        self.destr = True
        self.nameCtrl.Destroy()
        self.value.Destroy()
        self.separatorN.Destroy()
        self.separatorV.Destroy()
        if self.expander:
            self.expander.Destroy()

    def createHelpUrl(self):
        if self.propEditor:
            pw = self.propEditor.propWrapper
            # custom help
            if pw.routeType == 'CompnRoute':
                return '', ''
            # wxWin help
            if pw.routeType == 'CtrlRoute':
                mthName = pw.getSetterName()
                mthObj = getattr(self.propEditor.companion.control, mthName)
                cls = mthObj.im_class.__name__
                if cls[-3:] == 'Ptr': cls = cls[:-3]
                return cls, cls + mthName
        return '', ''

    def updatePropValue(self):
        self.propValue = self.propEditor.getValue()

    def showPropNameModified(self, displayAsCat=False):
        if self.propEditor:# and Preferences.showModifiedProps:
            propEdit = self.propEditor
            #propSetter = propEdit.propWrapper.getSetterName()
            #mod = not propEdit.companion.propIsDefault(propEdit.name, propSetter)
            # self.enboldenCtrl(self.nameCtrl, True) #mod or displayAsCat)
            if displayAsCat:
                self.nameCtrl.SetForegroundColour(wx.Colour(100, 100, 100)) #Preferences.propValueColour)


    def enboldenCtrl(self, ctrl, bold = True):
        fnt = ctrl.GetFont()
        ctrl.SetFont(wx.Font(fnt.GetPointSize(),
          fnt.GetFamily(), fnt.GetStyle(), bold and wx.BOLD or wx.NORMAL,
          fnt.GetUnderlined(), fnt.GetFaceName()))

    def updateDisplayValue(self):
        dispVal = self.propEditor.getDisplayValue()
        self.value.SetLabel(dispVal)
        # XXX if not too expensive, only set Tip if caption does not
        # XXX fit in window
        self.value.SetToolTipString(dispVal)
        self.showPropNameModified(self.isCat)

    def setPos(self, idx):
        self.idx = idx
        if self.expander:
            self.expander.SetPosition(wx.Point(0,
            self.idx * oiLineHeight + 2))
        self.nameCtrl.SetPosition(wx.Point(8 * self.indent + 16, idx * oiLineHeight +2))
        self.value.SetPosition(wx.Point(2, idx * oiLineHeight +2))
        self.separatorN.SetPosition(wx.Point(0, (idx +1) * oiLineHeight))
        self.separatorV.SetPosition(wx.Point(0, (idx +1) * oiLineHeight))
        if self.nameBevelTop:
            self.nameBevelTop.SetPosition(wx.Point(0, idx*oiLineHeight -1))
            self.nameBevelBottom.SetPosition(wx.Point(0, (idx + 1)*oiLineHeight -1))
        if self.propEditor:
            self.propEditor.setIdx(idx)
        elif self.valueBevelTop:
            self.valueBevelTop.SetPosition(wx.Point(0, idx*oiLineHeight -1))
            self.valueBevelBottom.SetPosition(wx.Point(0, (idx + 1)*oiLineHeight -1))

    def resize(self, nameWidth, valueWidth):
        if nameWidth <> self.lastSizeN:
            if self.nameBevelTop:
                self.nameBevelTop.SetSize(wx.Size(nameWidth, 1))
                self.nameBevelBottom.SetSize(wx.Size(nameWidth, 1))

            if nameWidth > 100:
                self.nameCtrl.SetSize(wx.Size(nameWidth - 30, self.nameCtrl.GetSize().y))
            else:
                self.nameCtrl.SetSize(wx.Size(100 - 30, self.nameCtrl.GetSize().y))

            
            self.separatorN.SetSize(wx.Size(nameWidth, 1))

        if valueWidth <> self.lastSizeV:
            if self.valueBevelTop:
                self.valueBevelTop.SetSize(wx.Size(valueWidth, 1))
                self.valueBevelBottom.SetSize(wx.Size(valueWidth, 1))

            self.value.SetSize(wx.Size(valueWidth, self.value.GetSize().y))

            self.separatorV.SetSize(wx.Size(valueWidth, 1))

            if self.propEditor:
                self.propEditor.setWidth(valueWidth)

        self.lastSizeN = nameWidth
        self.lastSizeV = valueWidth

    def showEdit(self):
        self.nameBevelTop = wx.Window(self.nameParent, -1,
          wx.Point(0, self.idx*oiLineHeight -1),
          wx.Size(self.inspector.panelNames.GetSize().x, 1))
        #self.nameBevelTop.SetBackgroundColour(wx.BLACK)
        self.nameBevelBottom = wx.Window(self.nameParent, -1,
          wx.Point(0, (self.idx + 1)*oiLineHeight -1),
          wx.Size(self.inspector.panelNames.GetSize().x, 1))
        #self.nameBevelBottom.SetBackgroundColour(wx.WHITE)
        self.locked = False #################
        if not self.locked and self.propEditor:
            self.value.SetLabel('')
            self.value.SetToolTipString('')
            self.value.SetSize((0, 0))
            self.propEditor.inspectorEdit()
        else:
            self.valueBevelTop = wx.Window(self.valueParent, -1,
              wx.Point(0, self.idx*oiLineHeight -1),
              wx.Size(self.inspector.getValueWidth(), 1))
            #self.valueBevelTop.SetBackgroundColour(wx.BLACK)
            self.valueBevelBottom = wx.Window(self.valueParent, -1,
              wx.Point(0, (self.idx + 1)*oiLineHeight -1),
              wx.Size(self.inspector.getValueWidth(), 1))
            #self.valueBevelBottom.SetBackgroundColour(wx.WHITE)
        self.editing = True

    def hideEditor(self, cancel = False):
        if self.propEditor:# and (not self.destr):
            if cancel:
                self.propEditor.inspectorCancel()
            else:
                self.propEditor.inspectorPost()
                self.updateDisplayValue()
                self.value.SetSize(wx.Size(self.separatorV.GetSize().x,
                  oiLineHeight-3))

        if self.nameBevelTop:
            self.nameBevelTop.Destroy()
            self.nameBevelTop = None
            self.nameBevelBottom.Destroy()
            self.nameBevelBottom = None

        if self.valueBevelTop:
            self.valueBevelTop.Destroy()
            self.valueBevelTop = None
            self.valueBevelBottom.Destroy()
            self.valueBevelBottom = None

        self.editing = False

    def OnSelect(self, event=None):
        self.inspector.propertySelected(self)

    def OnExpand(self, event):
        if event.Checked(): self.inspector.collapse(self)
        else: self.inspector.expand(self)

    def reset(self, parent, nameParent, valueParent, name, idx, indent,
              value, tipe, script, constraints = None):
        self.destr = False
        self.lastSizeN = 0
        self.lastSizeV = 0
        self.indent = indent
        self.pb = parent.pb
        self.inspector = parent
        self.propName = name
        self.editing = False

        self.nameParent = nameParent
        self.valueParent = valueParent
        self.idx = idx
        self.nameBevelTop = None
        self.nameBevelBottom = None
        self.valueBevelTop = None
        self.valueBevelBottom = None

        self.isCat = False
            
        self.propEditor = self.inspector.propertyRegistry.factory(name,
              valueParent, idx,
              valueParent.GetSize().x + IECWidthFudge, value, tipe, script, constraints)
        
        self.expander = None
        
        if self.propEditor:
            self.propEditor.companion = self.pb.cm
            self.propEditor.constraints = constraints
            self.propEditor.ownerPropEdit = None
            self.updatePropValue()
            displayVal = self.propEditor.getDisplayValue()
        
        else:
            self.propValue = ''
            displayVal = ''

        # Create name and value controls and separators
        self.nameCtrl.SetLabel(name)
        self.nameCtrl.SetToolTipString(name)
        self.nameCtrl.Show(True)

        # self.showPropNameModified(self.isCat)
        self.value.SetLabel(displayVal)
        self.value.SetToolTipString(displayVal)
        self.value.Show(True)
        
        # self.inspector.getValueWidth(), self.value, dir(self.value)

        #if lockEditor and not self.isCat:
        #    self.enboldenCtrl(self.value)

        self.separatorN.Show(True)
        self.separatorV.Show(True)
        