from resourceeditor import *
from script import CScript, get_full_name
from animation import CAnimation, VirtualAnimation
from glumolfont import CGlumolFont
from mouquetoptions import MouquetOptions
import wx
from pypoujol import *
from log import output
from propertiesbar.propertyeditors import Filename
from editablelistbox import *
from companions import *
from depplatform import get_image_path
import wx.aui as PyAUI

class MouquetMiniFrame(wx.Panel):
    def __init__(
        self, mouquet, parent=None, pos=wx.DefaultPosition, size=wx.DefaultSize):

        wx.Panel.__init__(self, parent, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        
        tb = wx.ToolBar(self, -1, style=wx.TB_HORIZONTAL \
                                 | wx.NO_BORDER \
                                 | wx.TB_FLAT \
                                 | wx.TB_TEXT \
                                 )
        
        id = wx.NewId()
        tb.AddTool(id, wx.Bitmap(get_image_path("play.xpm"), wx.BITMAP_TYPE_XPM))
        self.Bind(wx.EVT_TOOL, self.on_play, id = id)
        id = wx.NewId()
        tb.AddTool(id, wx.Bitmap(get_image_path("stop.xpm"), wx.BITMAP_TYPE_XPM))
        self.Bind(wx.EVT_TOOL, self.on_stop, id = id)
        id = wx.NewId()
        tb.AddTool(id, wx.Bitmap(get_image_path("split_li.xpm"), wx.BITMAP_TYPE_XPM))
        self.Bind(wx.EVT_TOOL, self.on_set_hotspot, id = id)
        id = wx.NewId()
        tb.AddTool(id, wx.Bitmap(get_image_path("moveoffset.png"), wx.BITMAP_TYPE_PNG))
        self.Bind(wx.EVT_TOOL, self.on_set_move_offset, id = id)
        
        tb.Realize()
        
        sizer.Add(tb, 0, wx.BOTTOM, 5)
        
        self.nb = wx.Notebook(self, -1, wx.DefaultPosition, style=wx.CLIP_CHILDREN)

        sizer.Add(self.nb, 1, wx.EXPAND)
                
        self.vframes_elb = EditableListBox(self.nb, -1, _("Virtual frames"),
                               style=wxEL_ALLOW_NEW | wxEL_ALLOW_DELETE)
        
        button = self.vframes_elb.GetDelButton()
        wx.EVT_BUTTON(button, -1, self.on_delete_vframe)

        button = self.vframes_elb.GetNewButton()
        wx.EVT_BUTTON(button, -1, self.on_add_vframe)

        self.frames_elb = EditableListBox(self.nb, -1, _("Image list"),
                              style=wxEL_ALLOW_NEW | wxEL_ALLOW_DELETE) # | wx.EL_ALLOW_EDIT

        self.nb.AddPage(self.frames_elb, _('Images'))
        self.nb.AddPage(self.vframes_elb, _('Frames'))
        
        listctrl = self.frames_elb.GetListCtrl()
        wx.EVT_LIST_ITEM_SELECTED(listctrl, listctrl.GetId(), self.on_frame_select)
        listctrl = self.vframes_elb.GetListCtrl()
        wx.EVT_LIST_ITEM_SELECTED(listctrl, listctrl.GetId(), self.on_vframe_select)
        # self.vframes_elb.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_vframe_select)
        
        button = self.vframes_elb.GetDelButton()
        wx.EVT_BUTTON(button, button.GetId(), self.on_delete_vframe)
        
        button = self.vframes_elb.GetNewButton()
        wx.EVT_BUTTON(button, button.GetId(), self.on_add_vframe)

        button = self.frames_elb.GetDelButton()
        wx.EVT_BUTTON(button, button.GetId(), self.on_delete_image)

        button = self.frames_elb.GetNewButton()
        wx.EVT_BUTTON(button, button.GetId(), self.on_add_image)

        self.mouquet = mouquet
        
        self.prevent_from_select = False

        self.SetSizer(sizer)
        sizer.Fit(self)
        
    def on_delete_vframe(self, evt):
        self.mouquet.delete_vframe(self.vframes_elb.m_selection)
        self.mouquet.set_strings(self.vframes_elb, _("Frame"),
            self.mouquet.sprite.current_anim.virtual_frames)
    
    def on_add_vframe(self, evt):
        if self.mouquet.sprite.current_anim.nbframes < 1:
            dlg = wx.MessageDialog(self.mouquet.artub,
                             _("You must add an image first"),
                             _("Error"),wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.mouquet.add_vframe(self.vframes_elb.m_selection)
        self.mouquet.set_strings(self.vframes_elb, _("Frame"),
            self.mouquet.sprite.current_anim.virtual_frames)
        self.vframes_elb.GetListCtrl().Select(self.vframes_elb.m_selection)
        
    def on_delete_image(self, evt):
        self.mouquet.delete_image(self.frames_elb.m_selection)
        self.mouquet.set_strings(self.frames_elb, _("Image"),
            self.mouquet.sprite.current_anim.nbframes)
    
    def on_add_image(self, evt):
        self.mouquet.add_image(self.frames_elb.m_selection)
        self.mouquet.set_strings(self.frames_elb, _("Image"), self.mouquet.sprite.current_anim.nbframes)
        self.frames_elb.GetListCtrl().Select(self.frames_elb.m_selection)

    def on_size(self, evt):
        self.SetSize(evt.GetSize())
        size = self.GetClientSize()
        self.nb.SetSize(size)
        self.vframes_elb.SetSize(size)
        self.frames_elb.SetSize(size)

    def on_play(self, evt):
        self.mouquet.set_mode(1)
        
    def on_stop(self, evt):
        self.mouquet.set_mode(0)

    def on_set_move_offset(self, evt):
        self.mouquet.start_choosing_point(1)
    
    def on_set_hotspot(self, evt):
        self.mouquet.start_choosing_point(2)
    
    def on_frame_select(self, evt):
        if not self.prevent_from_select:
            if evt.GetIndex() < self.mouquet.sprite.current_anim.nbframes:
                self.mouquet.set_frame(evt.GetIndex())
                frame_companion = MouquetFrameCompanion(self.mouquet, self.mouquet.sprite, evt.GetIndex())
                self.mouquet.artub.pb.set_inspector(frame_companion)
        evt.Skip()

    def on_vframe_select(self, evt):
        if not self.prevent_from_select:
            if evt.GetIndex() < len(self.mouquet.sprite.current_anim.orders):
                self.mouquet.set_vframe(evt.GetIndex())
                vframe_companion = MouquetVirtualFrameCompanion(self.mouquet.active_resource, self.mouquet.sprite, evt.GetIndex())
                self.mouquet.artub.pb.set_inspector(vframe_companion)
        evt.Skip()
        
class CrossPoint(Sprite):
    def __init__(self, parent = None, frames = 1, virtual_frames = -1):
        Sprite.__init__(self, parent)
        self.x = 0
        self.y = 0
        self.color = (1.0, 1.0, 1.0, 1.0)
        self.visible = True

    def draw(self):
        if not self.visible: return
        glDisable(GL_TEXTURE_2D)
        glPushMatrix()
        glLoadIdentity()
        glBegin(GL_LINES)
        x, y, w, h = self.x, self.y, 10, 10
        glColor4f(*self.color)
        glVertex2f(x - 4, y)
        glColor4f(*self.color)
        glVertex2f(x + 5, y)
        glEnd()
        glBegin(GL_LINES)
        glColor4f(*self.color)
        glVertex2f(x, y + 4)
        glColor4f(*self.color)
        glVertex2f(x, y - 5)
        glEnd()
        glPopMatrix()
        glEnable(GL_TEXTURE_2D)
        
class Mouquet(CResourceEditor):
   known_resources = [ CAnimation, CGlumolFont, VirtualAnimation ]
   options = ( MouquetOptions, "Mouquet" )
   name = "mouquet"

   def __init__(self):
      CResourceEditor.__init__(self)
      self.choosing_point = False
      self.successful = True
      self.to_select = -1

   def load_image(self, filename):
      filename.replace('\\', '\\\\')
      jpg = wx.Image(filename, wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
      return jpg
      
   def set_mode(self, mode = 0):
      if mode == 0:
          self.sprite.stop()
      elif mode == 1:
          self.sprite.start()
          
   def create_window(self, resource, parent_window):
      mouquet = self
      
      class MouquetClanlibCanvas(ClanlibCanvas):
          def __init__(self, parent, game):
              ClanlibCanvas.__init__(self, parent, game)

              wx.EVT_PAINT(self.canvas, self.OnPaint)
              wx.EVT_IDLE(self.canvas, self.OnIdle)
              
          def OnIdle(self, event):
              if not mouquet.artub.debugging:
                  self.Refresh()

          def OnPaint(self, evt):
              if not mouquet.artub.debugging:
                  if mouquet.successful:
                      ClanlibCanvas.OnPaint(self, evt)
              
      self.parent = parent_window
      game = Game()
      set_game(game)
      self.game = game
      self.wnd = self.canvas = MouquetClanlibCanvas(parent_window, game).canvas
      self.canvas.Show(True)
      self.canvas.Bind(wx.EVT_LEFT_DOWN, self.on_left_button_down)
      self.canvas.Bind(wx.EVT_MOTION, self.on_mouse_motion)

      if not isinstance(self.active_resource, CGlumolFont):
          if not hasattr(Mouquet, "toolbar"):
              Mouquet.toolbar = self.artub.toolbar_manager.create_toolbar(
                                 MouquetMiniFrame, args = (self,),
                                 infos = PyAUI.AuiPaneInfo().Name(_("Frames")).
                                 Caption(_("Frames")).Left().Float().MinSize(wx.Size(200, 180)))
              Mouquet.toolbar.use_count = 1
          else:
              Mouquet.toolbar.use_count += 1
      self.game.init()
      return (self.wnd, resource.name)
      
   def OnIdle(self, event):
      self.canvas.Refresh()
          
   def OnPaint(self, evt):
      if self.successful:
          self.canvas.OnPaint(evt)
    
   def edit_resource(self, resource, editor_class = None, change_page = True):
       CResourceEditor.edit_resource(resource, editor_class, change_page)

   def set_strings(self, liste, txt, n):
       strings = []
       for i in xrange(n):
           strings.append(txt + " " + str(i))
       liste.SetStrings(strings)

   def delete_vframe(self, index):
       anim = self.sprite.current_anim
       del anim.orders[index]
       del anim.hotspots[index]
       del anim.move_offsets[index]
       del anim.delays[index]
       anim.virtual_frames = anim.virtual_frames - 1
   
   def add_vframe(self, index):
       anim = self.sprite.current_anim
       anim.orders.insert(index, 0)
       anim.hotspots.insert(index, Point(0, 0))
       anim.move_offsets.insert(index, Point(0, 0))
       anim.delays.insert(index, 100)
       anim.virtual_frames = anim.virtual_frames + 1

   def delete_image(self, index):
       anim = self.sprite.current_anim
       del anim.filenames[index]
       anim.nbframes -= 1

   def add_image(self, index):
       anim = self.sprite.current_anim
       anim.loaded = False
       anim.add_frame(get_image_path("noimage.png"))
       anim.build()

   def start_choosing_point(self, t):
       self.choosing_point = t
       cursor = wx.StockCursor(wx.CURSOR_CROSS)
       self.canvas.SetCursor(cursor)    
    
   def end_choosing_point(self):
       self.choosing_point = 0
       cursor = wx.StockCursor(wx.CURSOR_DEFAULT)
       self.canvas.SetCursor(cursor)    
    
   def on_mouse_motion(self, evt):
       p = evt.GetPosition()
       self.artub.SetStatusText('(' + str(p.x) + ', ' + str(p.y) + ')', 0)
   
   def on_left_button_down(self, evt):
       if self.choosing_point:
           t = self.choosing_point
           self.end_choosing_point()
           p = evt.GetPosition()
           anim = self.sprite.current_anim
           if t == 1:
               anim.move_offsets[self.sprite.current_frame].x = p.x
               anim.move_offsets[self.sprite.current_frame].y = p.y
               self.cross_move_offset.x = p.x
               self.cross_move_offset.y = p.y
           elif t == 2:
               anim.hotspots[self.sprite.current_frame].x = p.x
               anim.hotspots[self.sprite.current_frame].y = p.y
               self.cross_hotspot.x = p.x
               self.cross_hotspot.y = p.y
           vframe_companion = MouquetVirtualFrameCompanion(self.active_resource, self.sprite, self.sprite.current_frame)
           self.artub.pb.set_inspector(vframe_companion)
       else:
           mouquet_inspector = MouquetCompanion(self, self.sprite)
           self.artub.pb.set_inspector(mouquet_inspector)
              
   def set_hotspot_y(self, offset):
       self.anim.hotspots[self.index].y = offset
  
   def set_frame(self, index):
       self.sprite._current_frame = index
       self.sprite.current_anim.set_frame(index)
       if hasattr(self, "cross_hotspot"):
           self.cross_hotspot.x = -1
           self.cross_hotspot.y = -1
           self.cross_move_offset.x = -1
           self.cross_move_offset.y = -1
           self.cross_last_hotspot.x = -1
           self.cross_last_hotspot.y = -1
       
   def set_vframe(self, index):
       if index < len(self.sprite.current_anim.orders):
           self.create_crosses(self.sprite.current_anim)
           self.sprite.current_frame = index
           self.cross_hotspot.x = self.sprite.current_anim.hotspots[index].x
           self.cross_hotspot.y = self.sprite.current_anim.hotspots[index].y
           self.cross_move_offset.x = self.sprite.current_anim.move_offsets[index].x
           self.cross_move_offset.y = self.sprite.current_anim.move_offsets[index].y
           self.cross_last_hotspot.x = self.sprite.current_anim.hotspots[index - 1].x
           self.cross_last_hotspot.y = self.sprite.current_anim.hotspots[index - 1].y

   def populate_frame_list(self, anim):
       self.toolbar.prevent_from_select = True
       self.set_strings(self.toolbar.frames_elb, _("Image"), self.sprite.current_anim.nbframes)
       self.set_strings(self.toolbar.vframes_elb, _("Frame"), self.sprite.current_anim.virtual_frames)
       self.toolbar.prevent_from_select = False
       
   def make_string(self, array, default, aux = str):
       rep = '['
       def is_not_simple(array):
           if len(array) == 1: return True
           elt = array[0]
           for i in array:
               if i != elt:
                   return True
       for i in array:
          rep = rep + aux(i) + ', '
       return rep + ']'
       
   def change_script(self):
       anim = self.sprite.current_anim

       def make_string_from_point(point):
           return _("Point(") + str(point.x) + ", " + str(point.y) + ")"

       if isinstance(self.active_resource, VirtualAnimation):
           parent = self.active_resource.get_first_non_virtual_parent()
           parent.sync()
       else:
           parent = self.active_resource
           parent.sync()

       if hasattr(self.active_resource, "realname"):
           c = self.active_resource.get_class(self.active_resource.realname)
       else:
           c = self.active_resource.get_class(get_full_name(self.active_resource.name))

       c.set_global_property('filenames', str(anim.filenames))
       c.set_global_property('virtual_frames', str(anim.virtual_frames))
       c.set_global_property('delays', self.make_string(anim.delays, '100'))
       c.set_global_property('orders', self.make_string(anim.orders, '0'))
       
       c.set_global_property('hotspots', self.make_string(anim.hotspots, 'Point(0, 0)', make_string_from_point))
       c.set_global_property('move_offsets', self.make_string(anim.move_offsets, 'Point(0, 0)', make_string_from_point))
       
       parent.ast_has_changed = True
       parent.topy()
       
       if hasattr(self.active_resource, "realname"):
          wx.GetApp().gns.run(parent.listing)
          
   def create_crosses(self, obj):
       if not hasattr(self, "cross_move_offset"):
           self.cross_move_offset = CrossPoint()
           self.cross_move_offset.color = (0.0, 1.0, 0.0, 1.0)
           self.cross_move_offset.x = obj.hotspots[0].x
           self.cross_move_offset.y = obj.hotspots[0].y
              
           self.cross_hotspot = CrossPoint()
           self.cross_hotspot.color = (1.0, 0.0, 0.0, 1.0)
           self.cross_hotspot.x = obj.hotspots[0].x
           self.cross_hotspot.y = obj.hotspots[0].y
        
           self.cross_last_hotspot = CrossPoint()
           self.cross_last_hotspot.color = (0.0, 0.0, 1.0, 1.0)
           self.cross_last_hotspot.x = obj.hotspots[-1].x
           self.cross_last_hotspot.y = obj.hotspots[-1].y

   def to_call(self):
      self.successful = True
      self.game.screen.children = []
      obj = wx.GetApp().gns.create_from_script(self.active_resource)
      class MySprite(Sprite):
           def __init__(self, parent):
               Sprite.__init__(self, parent)
               self.current_anim = obj
      set_game(self.game)
      self.sprite = MySprite(self.game.screen)
      if self.sprite.nbframes:
          self.sprite._current_frame = 0
      
      self.set_mode(0)
      self.populate_frame_list(obj)

      
      self.successful = True
      
      mouquet_inspector = MouquetCompanion(self, self.sprite)
      self.artub.pb.set_inspector(mouquet_inspector)
      
      if self.to_select != -1:
          self.sprite._current_frame = self.to_select
          self.to_select = -1

      self.artub.toolbar_manager.show_toolbar(self.toolbar, True)

   def to_call_font(self):
        self.game.screen.children = []
        obj = wx.GetApp().gns.create_from_script(self.active_resource)
        class FontSprite(Sprite):
            class FontAnim(Animation):
                if obj.filename: filenames = [ obj.filename ]
                else: filenames = []
            def __init__(self, parent):
                Sprite.__init__(self, parent)
                self.current_anim = self.FontAnim()

        set_game(self.game)
        self.sprite = FontSprite(self.game.screen)
        self.sprite.color = obj.color
        self.sprite.alpha = obj.alpha
        self.sprite.scale = obj.scale
        mouquet_inspector = MouquetFontCompanion(self, obj, self.active_resource)
        self.artub.pb.set_inspector(mouquet_inspector)

   def close(self):
       if not isinstance(self.active_resource, CGlumolFont):
           if self.toolbar.use_count == 1: 
               self.artub.toolbar_manager.remove_toolbar(self.toolbar)
               del Mouquet.toolbar
               self.artub._mgr.Update()
           else: self.toolbar.use_count -= 1
                   
   def unactivate(self):
        if hasattr(self, "toolbar"):
            self.artub.toolbar_manager.show_toolbar(self.toolbar, False)
          
   def update(self, save=True):
      if save:
         if isinstance(self.active_resource, CGlumolFont):
             pass
         else:
             try:
                self.successful = True
                self.change_script()
                wx.GetApp().gns.run(self.active_resource.listing)
             except:
                sys.excepthook(*sys.exc_info())
      else:
         if isinstance(self.active_resource, CGlumolFont):
             self.game.to_call = self.to_call_font
         else:
             self.game.to_call = self.to_call
             self.wnd.Refresh()
             
   def close_window(self):
      self.parent.remove_page(self.wnd)

   def get_popup_menu(self, resource):
       class MouquetContextMenu(wx.Menu):
            def __init__(self2):
                wx.Menu.__init__(self2)
                propID = wx.NewId()
                self2.resource = resource
                self2.Append(propID, _("View as script"), _("View as script"))
                wx.EVT_MENU(self2, propID, self.on_view_as_script)
                
       return MouquetContextMenu()
                
   def on_view_as_script(self, event):
        wx.GetApp().frame.view_as_script(event.GetEventObject().resource)

editor = Mouquet
