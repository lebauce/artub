import wx
import wx.lib.ogl as ogl
from script import guess_free_name
from propertiesbar.companions import Companion, ColorCompanion

class WoolseyCompanion(Companion):
    def __init__(self, resource, item, classe):
        Companion.__init__(self, item.obj, resource)
        self.classe = classe
        self.item = item
        self.add_variables([ ["color", ColorCompanion(item.obj, None)] ])
        
    def change_value(self, script, name, value):
        setattr(self.obj, name, value)
        if type(value) == type('') or type(value) == type(u''):
            ponct = ""
            if value.find("'") != -1 and value.find('"') == -1:
                ponct = '"'
            else:
                ponct = "'"
                value = value.replace("'", "\\'")
            self.classe.set_property(name, ponct + value + ponct)
        else:
            self.classe.set_property(name, str(value))
        if name == "text":
            self.item.ClearText()
            self.item.AddText(str(value))
            self.item.redraw()

        
class Choice: pass
    
class DiamondShape(ogl.PolygonShape):
    def __init__(self, w=0.0, h=0.0):
        ogl.PolygonShape.__init__(self)
        if w == 0.0:
            w = 60.0
        if h == 0.0:
            h = 60.0

        points = [ (0.0,    -h/2.0),
                   (w/2.0,  0.0),
                   (0.0,    h/2.0),
                   (-w/2.0, 0.0),
                   ]

        self.Create(points)
        
class DialogItem(ogl.RectangleShape):
    def __init__(self, size = (0.0, 0.0)):
        ogl.RectangleShape.__init__(self, size[0], size[1])
        self.SetCornerRadius(-0.1)
        self.childs = []
        self.links = []
    
    def redraw(self):
        canv = self.GetCanvas()
        dc = wx.ClientDC(canv)
        canv.PrepareDC(dc)
        self.Move(dc, self.GetX(), self.GetY(), True)

    def SetCanvas(self, canvas):
        ogl.RectangleShape.SetCanvas(self, canvas)
        self.canvas = canvas
        
    def GetCanvas(self):
        return self.canvas

    def link_to(self, item):
        canv = self.canvas
        line = ogl.LineShape()
        line.SetCanvas(canv)
        line.SetPen(wx.BLACK_PEN)
        line.SetBrush(wx.BLACK_BRUSH)
        line.AddArrow(ogl.ARROW_ARROW)
        line.MakeLineControlPoints(2)
        self.AddLine(line, item)
        canv.diagram.AddShape(line)
        line.Show(True)
        self.links.append(line)

        dc = wx.ClientDC(canv)
        canv.PrepareDC(dc)
        
        # for some reason, the shapes have to be moved for the line to show up...
        self.Move(dc, self.GetX(), self.GetY())
        
    def is_linked_to(self, item):
        for i in self.links:
            if i.GetTo() == item:
                return True
        
class MyEvtHandler(ogl.ShapeEvtHandler):
    def __init__(self, frame):
        ogl.ShapeEvtHandler.__init__(self)
        self.statbarFrame = wx.GetApp().frame.statusbar

    def UpdateStatusBar(self, shape):
        x,y = shape.GetX(), shape.GetY()
        width, height = shape.GetBoundingBoxMax()
        self.statbarFrame.SetStatusText("Pos: (%d,%d)  Size: (%d, %d)" %
                                        (x, y, width, height))


    def OnLeftClick(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        wx.GetApp().frame.pb.set_inspector(WoolseyCompanion(wx.GetApp().frame.active_editor.active_resource, shape, shape.classe))
        print shape.__class__, shape.GetClassName()
        canvas = shape.GetCanvas()
        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)

        if shape.Selected():
            shape.Select(False, dc)
            canvas.Redraw(dc)
        else:
            redraw = False
            shapeList = canvas.GetDiagram().GetShapeList()
            toUnselect = []
            for s in shapeList:
                if s.Selected():
                    # If we unselect it now then some of the objects in
                    # shapeList will become invalid (the control points are
                    # shapes too!) and bad things will happen...
                    toUnselect.append(s)

            shape.Select(True, dc)

            if toUnselect:
                for s in toUnselect:
                    s.Select(False, dc)
                canvas.Redraw(dc)

        self.UpdateStatusBar(shape)

    def OnEndDragLeft(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        ogl.ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment)
        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)
        self.UpdateStatusBar(shape)

    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
        ogl.ShapeEvtHandler.OnSizingEndDragLeft(self, pt, x, y, keys, attch)
        self.UpdateStatusBar(self.GetShape())

    def OnMovePost(self, dc, x, y, oldX, oldY, display):
        ogl.ShapeEvtHandler.OnMovePost(self, dc, x, y, oldX, oldY, display)
        self.UpdateStatusBar(self.GetShape())

    def OnRightClick(self, x, y, keys = 0, attachment = 0):
        shape = self.GetShape()
        canvas = shape.GetCanvas()
        canvas.current_position = (x, y)
        canvas.PopupMenu(canvas.item_context_menu, wx.Point(x, y))

class WoolseyWindow(ogl.ShapeCanvas):
    def __init__(self, parent):
        ogl.ShapeCanvas.__init__(self, parent)

        self.frame = wx.GetApp().frame

        maxWidth  = 1000
        maxHeight = 1000

        self.diagram = ogl.Diagram()
        self.SetDiagram(self.diagram)
        self.diagram.SetCanvas(self)
        self.shapes = []
        self.save_gdi = []
        
        self.linking = False
                
        rRectBrush = wx.Brush("MEDIUM TURQUOISE", wx.SOLID)
        dsBrush = wx.Brush("WHEAT", wx.SOLID)

        self.item_context_menu = wx.Menu()
        propID = wx.NewId()
        self.item_context_menu.Append(propID, "Delete", "Delete")
        wx.EVT_MENU(self, propID, self.on_delete)
        propID = wx.NewId()
        self.item_context_menu.Append(propID, "Link to", "Link to")
        wx.EVT_MENU(self, propID, self.on_link_to)
        propID = wx.NewId()
        self.item_context_menu.Append(propID, "New child", "New child")
        wx.EVT_MENU(self, propID, self.on_new_child)
        
        wx.EVT_MOTION(self, self.on_mouse_move)

        self.context_menu = wx.Menu()
        propID = wx.NewId()
        self.context_menu.Append(propID, "New", "New")
        wx.EVT_MENU(self, propID, self.on_new)

        wx.EVT_LEFT_DOWN(self, self.on_lbutton_down)
        wx.EVT_RIGHT_DOWN(self, self.on_rbutton_down)

    def on_mouse_move(self, event):
        if not self.linking:
            event.Skip()
            return
        changed = False
        for shape in self.shapes:
            l = shape.HitTest(event.GetPosition()[0], event.GetPosition()[1])
            if l:
                if shape != self.current_shape:
                    if self.current_shape:
                        self.current_shape.SetBrush(wx.RED_BRUSH)
                    if shape != self.Current_shape:
                        shape.SetBrush(wx.GREEN_BRUSH)
                        shape.GetCanvas().Refresh()
                        self.current_shape = shape
                changed = True
        if not changed and self.current_shape:
            self.current_shape.SetBrush(wx.RED_BRUSH)
            self.current_shape.GetCanvas().Refresh()
            self.current_shape = None

    def set_childs(self, item):
        print "item, item.obj.childs", item, item.obj.childs
        s = "["
        for i in item.obj.childs:
            s += self.woolsey.active_resource.name + '.' + i.__name__  + ','
        s += ']'
        item.classe.set_property("childs", s)
        
    def on_lbutton_down(self, event):
        if not self.linking:
            event.Skip()
            return
        self.linking = False
        self.ReleaseMouse()
        if self.current_shape:
            if not self.Current_shape.is_linked_to(self.current_shape):
                self.Current_shape.link_to(self.current_shape)
                self.Current_shape.obj.childs.append(self.current_shape.obj.__class__)
                self.set_childs(self.Current_shape)
                
            self.current_shape.SetBrush(wx.RED_BRUSH)
            self.current_shape.GetCanvas().Refresh()
            self.current_shape = None
        del self.Current_shape
        
    def on_rbutton_down(self, event):
        current_position = (event.GetPosition()[0], event.GetPosition()[1])
        for shape in self.shapes:
            l = shape.HitTest(*current_position)
            if l:
                dc = wx.MemoryDC()
                shape.Recentre(dc)
                self.current_shape = shape
                event.Skip()
                return
        self.current_position = wx.Point(*current_position)
        self.PopupMenu(self.context_menu, self.current_position)
        
    def on_delete(self, event):
        shape = self.current_shape
        self.diagram.RemoveShape(shape)
        self.shapes.remove(shape)
        canvas = shape.GetCanvas()
        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)
        if shape.Selected():
            shape.Select(False, dc)
            canvas.Redraw(dc)
        lines = shape.GetLines()
        
        print lines
        for i in lines: # Destroy link in the others choices
            self.diagram.RemoveShape(i)
            if i.GetTo() == shape:
                for j in i.GetFrom().obj.childs:
                   if isinstance(shape.obj, j):
                      i.GetFrom().RemoveLine(i)
                      i.GetFrom().obj.childs.remove(j)
                      continue
            else:
                for j in i.GetTo().obj.childs:
                   if isinstance(shape.obj, j):
                      i.GetTo().obj.childs.remove(j)
            shape.RemoveLine(i)
        self.current_shape = None
        shape.lines = []
        del self.current_shape
        canvas.Refresh()

    def on_new(self, event):
        body = [ "def __init__(self):",
                 "    Choice.__init__(self)",
                 "    self.__glumolinit__()",
                 "def __glumolinit__(self):",
                 "    self.text = 'Say something'" ]
        
        name = "Choice" + str(len(self.shapes) + 1)
        c = self.woolsey.classe.add_class(name, ["Choice"], body)

        newname = guess_free_name("Choice")
        
        from compiler.misc import set_filename
        from compiler.pycodegen  import ModuleCodeGenerator
        set_filename("__foo__.py", self.woolsey.active_resource.ast)
        gen = ModuleCodeGenerator(self.woolsey.active_resource.ast)
        self.classe = classe = self.woolsey.active_resource.get_class()
        wx.GetApp().gns.run(gen.getCode())
                 
        obj = self.woolsey.create_dialog_item(name)
               
        item = self.woolsey.create_child("Say something")
        item.classe = c
        item.obj = obj
        
        self.Refresh()
        del self.current_position
        return item
        
    def on_new_child(self, event):
        t = self.on_new(event)
        self.current_shape.link_to(t)

    def on_link_to(self, event):
        self.Current_shape = self.current_shape
        self.current_shape = None
        self.linking = True
        self.CaptureMouse()
        
    def clear(self):
        self.diagram.DeleteAllShapes()
        self.shapes = []
        self.save_gdi = []    
        
    def create_dialog_item(self, text):
        w, h = wx.MemoryDC().GetTextExtent(text)
        return DialogItem((w + 10, h + 8))

    def add_dialog_item(self, text, size, pen = None, brush = None, shape = None):
        print "add_dialog_item", size
        if not pen:
            pen = wx.Pen(wx.BLUE, 1, wx.SOLID)
        if not brush:
            brush = wx.WHITE_BRUSH
        if not shape:
            shape = DialogItem(wx.MemoryDC().GetTextExtent(text))
        x, y = size[0], size[1]
        shape.SetDraggable(True, True)
        shape.SetCanvas(self)
        shape.SetX(x)
        shape.SetY(y)
        if pen:    shape.SetPen(pen)
        if brush:  shape.SetBrush(brush)
        if text:   shape.AddText(text)
        self.diagram.AddShape(shape)
        shape.Show(True)

        evthandler = MyEvtHandler(self.frame)
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)

        self.shapes.append(shape)
        return shape
