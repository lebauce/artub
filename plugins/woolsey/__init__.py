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

# Clic droit :
# Crer un item : fond et item
# Detruire un item
# Lier un item
# Afficher dans l'ObjectEditor
# Tester le dialogue
# Undo/Redo

from resourceeditor import *
from script import CScript, emit_script
from dialogue import CDialogue
from woolseyoptions import WoolseyOptions
from woolseywindow import WoolseyWindow
import wx
import wx.lib.ogl as ogl
import new
from pypoujol import Choice, Dialogue

class WoolseyContextMenu(wx.Menu):
    def __init__(self, woolsey):
        wx.Menu.__init__(self)
        self.woolsey = woolsey
        propID = wx.NewId()
        self.Append(propID, "View source", "View source")
        wx.EVT_MENU(self, propID, self.on_view_source)
        propID = wx.NewId()
        self.Append(propID, "Test", "Test dialog")
        wx.EVT_MENU(self, propID, self.on_test_dialog)

    def on_view_source(self, event):
        wx.GetApp().frame.on_view_source(resource = self.resource)
        
    def on_test_dialog(self, event):
        wx.GetApp().frame.debugbar.gouzi(self.woolsey.active_resource.obj)

class Choice: pass
    
class listener:
  def __init__(self, shape):
    self.shape = shape
            
  def modified_data(self, obj, attr, value):
    if attr == 'text':
      try:
        self.shape.ClearText()
        self.shape.AddText(value)
        self.shape.redraw()
      except:
        raise

class Woolsey(CResourceEditor):
   known_resources = [ CDialogue ]
   options = ( WoolseyOptions, "Woolsey" )
   name = "woolsey"

   def __init__(self):
      CResourceEditor.__init__(self)
      ogl.OGLInitialize()
      self.loc["Choice"] = Choice
      self.loc["Dialogue"] = Dialogue
      
   def __del__(self, cleanup=ogl.OGLCleanUp):
      cleanup()       

   def create_window(self, resource, parent_window):
      self.parent = parent_window
      
      self.wnd = WoolseyWindow(parent_window)
      self.wnd.woolsey = self
      
      pos = 10

      return (self.wnd, resource.name)

   def update(self, save=True):
      if save:
         self.active_resource.topy()
      else:
         self.wnd.clear()
         self.obj = wx.GetApp().gns.create_from_script(self.active_resource, (None,))
         self.create_from_obj(self.obj)

   def set_listing(self, shape):
       try:
           self.active_resource.replace_glumolinit(emit_script(shape.obj), shape.obj.name)
       except:
           print "Error while set_listing", emit_script(shape.obj)
       
   def close_window(self):
      self.parent.remove_page(self.wnd)

   def create_child(self, name, parent = None, pos = None):
       if not pos:
           import random
           pos = (random.randint(0, 500), random.randint(0, 500))
       
       t = self.wnd.create_dialog_item(name)
       ret = self.wnd.add_dialog_item(name, pos, shape = t)
       if parent:
           parent.link_to(t)
       return ret
      
   def get_popup_menu(self, resource):
        menu = WoolseyContextMenu(self)
        menu.resource = resource
        return menu
       
   def create_dialog_item(self, name):
       return wx.GetApp().gns.eval(self.active_resource.name + '.' + name + '()')

   def create_childs(self, obj, parent = None):
           if obj in self.treated: return
           self.treated.append(obj)
           self.active_resource.sync()
           self.classe = classe = self.active_resource.get_class()
           items = {}
           
           classes = classe.get_all_classes()
           for i in classes:
               obj = self.create_dialog_item(i.name)
               item = self.create_child(obj.text)
               item.classe = i
               item.obj = obj
               items[i.name] = item
               
           for i in classes:
               item = items[i.name]
               obj = item.obj
               for j in obj.childs:
                   item.link_to(items[j.__name__])    
              
   def create_single_obj(self, obj, parent = None):
       self.treated = []
       self.create_childs(obj, parent)
       del self.treated

   def create_from_obj(self, obj):
       self.treated = []
       self.create_childs(obj)
       del self.treated

editor = Woolsey
