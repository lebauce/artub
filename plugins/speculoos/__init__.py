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

from resourceeditor import CResourceEditor
from glumolobject import CGlumolObject, VirtualGlumolObject
from speculoosoptions import SpeculoosOptions
from propertiesbar.propertiesbar_actions import PropertiesBarChangeValue
import pypoujol
import wx
import wx.gizmos as gizmos
import wx.lib.ogl as ogl
from math import sqrt
from companions import *
from listboxes import *
from box import *
from poujolobjs import *
import wx.aui as PyAUI
import wx.lib.flatnotebook as fnb

def guess_class(j):
    baseclass = repr(j.obj)
    return baseclass[baseclass.find(".") + 1 : baseclass.find(" ")]

class SpeculoosMiniFrame(wx.Panel):
    def __init__(
        self, speculoos, parent = None, id = -1, pos=wx.DefaultPosition, size=wx.DefaultSize,
        style=wx.DEFAULT_FRAME_STYLE
        ):

        self.speculoos = speculoos
        wx.Panel.__init__(self, parent, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.nb = PyAUI.AuiNotebook(self, -1, style = PyAUI.AUI_NB_SCROLL_BUTTONS)
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.planes = PlanesListBox(speculoos, self.nb, -1, _("Planes"))
        self.objects = ObjectListBox(speculoos, self.nb, -1, _("Objects"))
        self.lights = LightZoneListBox(speculoos, self.nb, -1, _("Lights"))
        self.sprites = SpriteListBox(speculoos, self.nb, -1, _("Sprites"))
        self.walk_zones = WalkBoxesListBox(speculoos, self.nb, -1, _("Walk areas"))
        self.change_scene_zones = ChangeSceneListBox(speculoos, self.nb, -1, _("Change scene"))
        self.entry_points = EntryPointsListBox(speculoos, self.nb, -1, _("Entry points"))
        self.scale_zones = ScaleBoxesListBox(speculoos, self.nb, -1, _("Scale zones"))
        self.characters = CharactersListBox(speculoos, self.nb, -1, _("Characters"))
        self.areas = OtherZonesListBox(speculoos, self.nb, -1, _("Special areas"))
        self.SetSizer(sizer)

        self.nb.AddPage(self.planes, _('Planes'))
        self.nb.AddPage(self.objects, _('Objects'))
        self.nb.AddPage(self.characters, _('Characters'))
        self.nb.AddPage(self.sprites, _('Sprites'))
        self.nb.AddPage(self.lights, _('Lights'))
        self.nb.AddPage(self.walk_zones, _('Walk areas'))
        self.nb.AddPage(self.change_scene_zones, _('Change scene'))
        self.nb.AddPage(self.entry_points, _('Entry points'))
        self.nb.AddPage(self.scale_zones, _('Scale zones'))
        self.nb.AddPage(self.areas, _('Others'))

    def unselect_items(self, all=False):
        for i in self.get_list_list():
            if all or (i != self.get_active_list()):
                item = -1
                while True:
                    item = i.m_listCtrl.GetNextItem(item,
                                     wx.LIST_NEXT_ALL,
                                     wx.LIST_STATE_SELECTED)
                    if item == -1: break

                    i.m_listCtrl.SetItemState(item, 0,
                                     wx.LIST_STATE_SELECTED)
                                     
    def get_list_list(self):
        return [ self.planes, self.objects, self.characters, self.sprites,
                 self.lights, self.walk_zones, self.change_scene_zones,
                 self.entry_points, self.scale_zones, self.areas ]

    def get_active_list(self):
        return self.get_list_list()[self.nb.GetSelection()]
 
    def edit_boxsystem(self, bxsystem):
        self.get_active_list().edit_boxsystem(bxsystem)

    def set_object(self, obj):
        l = self.get_list_list()
        for i in l:
            i.SetStrings([])
            i.bxmanager = BoxSystemManager()
        
        for i in dir(obj):
            if i == "contour": continue
            if isinstance(getattr(obj, i), pypoujol.Region) or \
               isinstance(getattr(obj, i), pypoujol.Plane) or \
               isinstance(getattr(obj, i), pypoujol.Sprite):
                reg = getattr(obj, i)
                gns = wx.GetApp().gns
                l = [ (gns.getattr(self.lights.default_class), self.lights),
                      (gns.getattr("WalkZone"), self.walk_zones),
                      (gns.getattr("ZPlane"), self.planes),
                      (gns.getattr(self.characters.default_class), self.characters),
                      (gns.getattr(self.planes.default_class[0]), self.planes),
                      (gns.getattr(self.objects.default_class), self.objects),
                      (gns.getattr(self.sprites.default_class), self.sprites),
                      (gns.getattr(self.entry_points.default_class), self.entry_points),
                      (gns.getattr(self.change_scene_zones.default_class), self.change_scene_zones),
                      (gns.getattr(self.scale_zones.default_class), self.scale_zones),
                      (gns.getattr(self.areas.default_class), self.areas)
                    ]
                liste = None
                for j in l:
                    if isinstance(reg, j[0]):
                        liste = j[1].GetListCtrl()
                        break
                if not liste: continue
                liste.InsertImageStringItem(liste.GetItemCount(), i, 0)
                bxsystem = BoxSystem()
                bxsystem.name = i
                bxsystem.obj = reg
                if isinstance(reg, pypoujol.Region):
                    bxsystem.boxes = reg.boxes
                    for i in bxsystem.boxes: i.gpoints = []
                j[1].bxmanager.bxsystems.append(bxsystem)

class Speculoos(CResourceEditor):
   known_resources = [ CGlumolObject, VirtualGlumolObject ]
   options = ( SpeculoosOptions, "Speculoos" )
   name = 'speculoos'
   
   def __init__(self):
      CResourceEditor.__init__(self)
      self.is_creating = False
      self.is_dragging = False
      self.is_splitting = False
      self.is_deleting = False
      self.is_dragging_object = False
      self.setting_walk_point = False
      self.current_object = None
      self.current_bxsystem = BoxSystem()
      self.current_bxmanager = BoxSystemManager()
      self.successful = True
      self.stencil_test = False
      self.previous_selection = None
      
   def set_editing_mode(self, state1, state2):
      pass

   def create_window(self, resource, parent_window):
      self.parent = parent_window
      
      speculoos = self

      game = pypoujol.Game()
      pypoujol.set_game(game)
      self.game = game

      class SpeculoosClanlibCanvas(pypoujol.ClanlibCanvas):
          def __init__(self, parent, game):
              pypoujol.ClanlibCanvas.__init__(self, parent, game)

              wx.EVT_PAINT(self.canvas, self.OnPaint)
              wx.EVT_IDLE(self.canvas, self.OnIdle)
              wx.EVT_LEFT_DOWN(self.canvas, speculoos.on_left_button_down)
              wx.EVT_LEFT_UP(self.canvas, speculoos.on_left_button_up)
              wx.EVT_RIGHT_DOWN(self.canvas, speculoos.on_right_button_down)
              wx.EVT_MOTION(self.canvas, speculoos.on_mouse_motion)
              
          def OnIdle(self, event):
              if not speculoos.artub.debugging:
                  self.Refresh()

          def OnPaint(self, evt):
              if not speculoos.artub.debugging:
                  if speculoos.successful:
                      pypoujol.ClanlibCanvas.OnPaint(self, evt)
      
      self.pypoujol_canvas = SpeculoosClanlibCanvas(parent_window, game)
      self.wnd = self.canvas = self.pypoujol_canvas.canvas
      self.canvas.SetScrollbar(wx.HORIZONTAL, 0, self.canvas.GetClientSize().GetWidth(), 5000)
      self.canvas.SetScrollbar(wx.VERTICAL, 0, self.canvas.GetClientSize().GetHeight(), 5000)

      if not hasattr(Speculoos, "toolbar"):
          Speculoos.toolbar = self.artub.toolbar_manager.create_toolbar(
              SpeculoosMiniFrame, [self], { },
              infos = PyAUI.AuiPaneInfo().Name("Scene editor").
                        Caption(_("Scene editor")).Left().
                        MinSize(wx.Size(200,150)).Float())
          Speculoos.toolbar.use_count = 1
          self.artub._mgr.Update()
      else:
          Speculoos.toolbar.use_count += 1
      
      return (self.wnd, resource.name)

   def get_object_at_pos(self, pos):
       pass
       
   def create_graphical_point(self, point):
       gpoint = RegionPoint(self.game.screen)
       return gpoint
       
   def on_right_button_down(self, evt):
       if self.is_creating:
           if self.canvas.GetCapture() is self.canvas:
               self.canvas.ReleaseMouse()
           self.is_creating = False
           self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))    
           for i in self.current_contour.gpoints:
               self.game.screen.children.remove(i)
           self.game.screen.children.remove(self.current_contour)
           self.current_contour = None
           self.toolbar.edit_boxsystem(self.current_bxsystem)

       obj = self.get_object_at_pos(evt.GetPosition())

   def start_choosing_point(self):
       cursor = wx.StockCursor(wx.CURSOR_CROSS)
       self.canvas.SetCursor(cursor)    
    
   def end_choosing_point(self):
       cursor = wx.StockCursor(wx.CURSOR_DEFAULT)
       self.canvas.SetCursor(cursor)    
   
   def on_mouse_motion(self, evt):
       point = (evt.GetPosition().x + self.wnd.GetScrollPos(wx.HORIZONTAL), \
                evt.GetPosition().y + self.wnd.GetScrollPos(wx.VERTICAL))
       self.artub.SetStatusText(str(point), 0)
       if self.is_dragging:
           box = self.current_point[0]
           index = self.current_point[1]
           box.points[index] = point
           box.gpoints[index].x = point[0]
           box.gpoints[index].y = point[1]
           
       elif self.is_dragging_object:
           self.current_object.position = \
               (point[0] - self.current_offset[0],
                point[1] - self.current_offset[1])

   def on_left_button_up(self, evt):
       if self.is_dragging:
           self.is_dragging = False
           del self.current_point
       elif self.is_dragging_object:
           self.is_dragging_object = False
           position = self.current_object.position
           self.current_object.position = self.initial_position
           del self.current_offset
           del self.initial_position
           self.save_selection()
           PropertiesBarChangeValue(self.active_resource,
                                    self.current_object,
                                    "position", position)
           
   def on_left_button_down(self, evt):
       point = (evt.GetPosition().x + self.wnd.GetScrollPos(wx.HORIZONTAL), \
                evt.GetPosition().y + self.wnd.GetScrollPos(wx.VERTICAL))
       if self.is_creating:
           self.current_box.points.append(point)
           if not self.current_contour:
               hotspot = getattr(self.current_bxsystem.obj, "hotspot", (0, 0))
               self.current_contour = Contour(self.game.screen, hotspot = hotspot)
               self.current_contour.box = self.current_box
           gpoint = self.create_graphical_point(point)
           gpoint.x, gpoint.y = point
           self.current_contour.gpoints.append(gpoint)
           
       elif self.is_deleting:
           self.end_choosing_point()
           self.is_deleting = False
           if self.current_bxsystem:
               i = self.current_bxsystem.get_point_at(point)
               if i:
                  i, index = i
                  del i.points[index]
                  self.game.screen.children.remove(i.gpoints[index])
                  del i.gpoints[index]
                          
       elif self.is_splitting:
           self.end_choosing_point()
           self.is_splitting = False
           bx = self.current_bxsystem
           goodindex = reallygoodindex = -1
           minvinicity, mingoodvinicity = 666666666, 666666666 # L'infini quoi
           for i in bx.boxes:
              next_index = 0
              l = len(i.points)
              for p1 in i.points:
                 p2 = i.points[(next_index + 1)% l]
                 dx, dy = p2[0] - p1[0], p2[1] - p1[1]
                 r = sqrt(dx * dx + dy * dy)
                 x1, y1 = point[0] - p1[0], point[1] - p1[1]
                 x2 = (x1 * dx + y1 * dy) / r
                 y2 = (-x1 * dy + y1 * dx) / r
                 
                 if x2 >= 0 and x2 <= r:
                    if abs(y2) < abs(mingoodvinicity):
                        reallygoodindex = next_index
                        mingoodvinicity = y2

                 if abs(y2) < abs(minvinicity):
                    minvinicity = y2
                    goodindex = next_index
                    
                 next_index = next_index + 1
           
              if reallygoodindex != -1:
                 goodindex = reallygoodindex
              if goodindex != -1:
                 gpoint = self.create_graphical_point(point)
                 gpoint.x, gpoint.y = point
                 i.points.insert((goodindex + 1) % l, point)
                 i.gpoints.insert((goodindex + 1) % l, gpoint)
                 break
                      
       elif self.setting_walk_point:
           self.end_choosing_point()
           baseclass = self.current_bxsystem.obj.__class__.__name__
           self.active_resource.change_property_no_sync("walk_point",
                                                        "Point" + str(point),
                                                        class_name = baseclass)           
       else:
           if self.current_bxsystem:
               t = self.current_bxsystem.get_point_at(point)
               if t:
                   self.current_point = t
                   self.is_dragging = True
                   return
                   
           if self.current_object:
               obj = self.current_object
               oldpos = self.current_object.position
               def set_pos(obj):
                   if hasattr(obj, "parent") and isinstance(obj.parent, pypoujol.Sprite):
                       return obj.screen_to_client(set_pos(obj.parent))
                   else:
                       return obj.screen_to_client(point)
               p = set_pos(self.current_object)
               self.current_object.position = oldpos
               rect = pypoujol.Rect(0, 0, obj.size[0], obj.size[1])
               if rect.is_inside(p):
                   self.is_dragging_object = True
                   self.current_offset = (point[0] - obj.position[0], point[1] - obj.position[1])
                   self.initial_position = obj.position
                   return

           inspector = SpeculoosCompanion(self.active_resource, self.obj)
           self.artub.pb.set_inspector(inspector)
           self.toolbar.unselect_items(True)
           self.select_sprite(self.obj)
           evt.Skip()
           
   def get_boxes_repr(self, bxsystem):
      code = '['
      for i in bxsystem.boxes:
         code = code + "Box(["
         for j in i.points:
            code = code + str(j) + ','
         code = code + "]),"
      code = code + ']'
      return code
   
   def select_sprite(self, obj, state = True):
       if state:
           if self.current_object:
               self.select_sprite(self.current_object, False)
           if isinstance(obj, pypoujol.Sprite):
               obj.contour = Contour(obj, loop=True, hotspot = obj.hotspot)
               obj.contour.color = (1.0, 0.0, 0.0, 1.0)
               box = Box()
               box.points.append((0,1))
               box.points.append((obj.size[0],1))
               box.points.append((obj.size[0], obj.size[1]))
               box.points.append((0,obj.size[1]))
               obj.contour.set_box(box)
               self.current_object = obj
       else:
           if hasattr(obj, "contour"):
                obj.children.remove(obj.contour)
                del obj.contour
           self.current_object = None
   
   def on_scroll_up_button(self, event):
       self.canvas.SetScrollPos(event.GetOrientation(), self.canvas.GetScrollPos(event.GetOrientation()) - 5)
       
   def on_scroll_down_button(self, event):
       self.canvas.SetScrollPos(event.GetOrientation(), self.canvas.GetScrollPos(event.GetOrientation()) + 5)

   def on_scroll_up_page(self, event):
       self.canvas.SetScrollPos(event.GetOrientation(), self.canvas.GetScrollPos(event.GetOrientation()) - 25)

   def on_scroll_down_page(self, event):
       self.canvas.SetScrollPos(event.GetOrientation(), self.canvas.GetScrollPos(event.GetOrientation()) + 25)

   def on_scroll_event(self, event):
        self.canvas.SetScrollPos(event.GetOrientation(), event.GetPosition())
        self.pypoujol_canvas.OnDraw()
        event.Skip()
            
   def to_call(self):
       self.successful = False
       obj = wx.GetApp().gns.create_from_script(self.active_resource, (self.game.screen,))
       self.select_sprite(obj)
       if not obj.current_anim:
           obj.current_anim = wx.GetApp().gns.eval("NoImage()")
       self.obj = obj
       self.obj.playing = False
       self.game.screen.children = []
       self.game.screen.children.append(obj)
       wx.EVT_SCROLLWIN(self.canvas, self.on_scroll_event)
       wx.EVT_SCROLLWIN_THUMBTRACK(self.canvas, self.on_scroll_event)
       wx.EVT_SCROLLWIN_BOTTOM(self.canvas, self.on_scroll_down_button)
       wx.EVT_SCROLLWIN_LINEUP(self.canvas, self.on_scroll_up_button)
       wx.EVT_SCROLLWIN_LINEDOWN(self.canvas, self.on_scroll_down_button)
       wx.EVT_SCROLLWIN_TOP(self.canvas, self.on_scroll_up_button)
       wx.EVT_SCROLLWIN_PAGEUP(self.canvas, self.on_scroll_up_page)
       wx.EVT_SCROLLWIN_PAGEDOWN(self.canvas, self.on_scroll_down_page)
       self.toolbar.set_object(obj)
       self.successful = True
       
       # Restore previous selection
       self.current_bxsystem = None
       if self.previous_selection:
           l, item = self.previous_selection
           l.GetListCtrl().SetItemState(item, -1, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
       else:
           inspector = SpeculoosCompanion(self.active_resource, self.obj)
           self.artub.pb.set_inspector(inspector)

   def close(self):
        if self.toolbar.use_count == 1: 
            self.artub.toolbar_manager.remove_toolbar(self.toolbar)
            del Speculoos.toolbar
        else: self.toolbar.use_count -= 1

   def unactivate(self):
       self.current_bxsystem = None
       self.artub.toolbar_manager.show_toolbar(self.toolbar, False)
       
   def save_selection(self):
       self.previous_selection = None
       for l in self.toolbar.get_list_list():
           item = l.GetListCtrl().GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
           if item != -1:
               self.previous_selection = (l, item)
               break
   
   def update(self, save=True):
      if save:
         self.successful = True
         for i in self.toolbar.get_list_list():
            for j in i.bxmanager.bxsystems:
                baseclass = j.obj.__class__.__name__
                try:
                    self.active_resource.change_global_property("boxes", self.get_boxes_repr(j), class_name = baseclass)
                except AttributeError:
                    import sys
                    print sys.excepthook(*sys.exc_info())
                    print "Cannot modify", baseclass, "'s boxes"
         self.save_selection()
      else:
         for i in self.toolbar.get_list_list():
             i.speculoos = self
         self.game.screen.children = []
         self.game.to_call = self.to_call
         self.artub.toolbar_manager.show_toolbar(self.toolbar, True)

   def get_parent_resource(self, resource):
       parent = resource.parent
       while isinstance(parent, VirtualGlumolObject):
           parent = parent.parent
       return parent

   def close_window(self):
      self.parent.remove_page(self.wnd)
      
   def get_options_page(self):
      return (1, 2)

   def get_popup_menu(self, resource):
       class SpeculoosContextMenu(wx.Menu):
            def __init__(self2):
                wx.Menu.__init__(self2)
                propID = wx.NewId()
                self2.resource = resource
                self2.Append(propID, _("View as script"), _("View as script"))
                wx.EVT_MENU(self2, propID, self.on_view_as_script)
                menu = wx.Menu()
                menu.AppendMenu(wx.NewId(), "Animations",
                                self.artub.get_templates_menu(
                                    section = "Animation",
                                    callback = self.artub.on_new_class,
                                    parent_menu = self.artub.tree, id = 10000))
                menu.AppendMenu(wx.NewId(), "Regions",
                                self.artub.get_templates_menu(
                                    section = "Region",
                                    callback = self.artub.on_new_class,
                                    parent_menu = self.artub.tree, id = 11000))
                menu.AppendMenu(wx.NewId(), "Sprites",
                                self.artub.get_templates_menu(
                                    section = "Sprite",
                                    callback = self.artub.on_new_class,
                                    parent_menu = self.artub.tree, id = 12000))
                self2.AppendMenu(wx.NewId(), "New", menu)
                
       return SpeculoosContextMenu()
                
   def on_view_as_script(self, event):
        wx.GetApp().frame.view_as_script(event.GetEventObject().resource)
       

editor = Speculoos
