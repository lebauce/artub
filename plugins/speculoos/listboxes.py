from editablelistbox import *
from companions import *
from box import *
from poujolobjs import *
import wx
import platform
from choosename import choose_a_name

class SpeculoosEditableListBox(EditableListBox):
    default_class = "object"
    
    def __init__(self, speculoos, parent, id, title):
        EditableListBox.__init__(self, parent, id, title, style = wxEL_ALLOW_EDIT | wxEL_ALLOW_NEW | wxEL_ALLOW_NEW | wxEL_ALLOW_DELETE | wxEL_ALLOW_UPDOWN)
        self.speculoos = speculoos
        self.creating = False
        self.bxmanager = BoxSystemManager()
        button_parent = self.GetNewButton().GetParent()
        
        self.newbox = wx.BitmapButton(button_parent, -1, 
                                      wx.Bitmap(get_image_path('newbox.xpm'), wx.BITMAP_TYPE_XPM))
        self.subsizer.Insert(0, self.newbox, 0, wx.ALIGN_CENTRE_VERTICAL | wx.TOP | wx.BOTTOM, BTN_BORDER)
        self.newbox.SetToolTipString(_("Create a new box"))
        self.newbox.Disable()
        
        self.newpoint = wx.BitmapButton(button_parent, -1,
                                        wx.Bitmap(get_image_path('split_li.xpm'), wx.BITMAP_TYPE_XPM))
        self.subsizer.Insert(1, self.newpoint, 0, wx.ALIGN_CENTRE_VERTICAL | wx.TOP | wx.BOTTOM, BTN_BORDER)
        self.newpoint.SetToolTipString(_("Create a new point"))
        self.newpoint.Disable()
        
        self.delpoint = wx.BitmapButton(button_parent, -1, 
                                        wx.Bitmap(get_image_path('gomme.xpm'), wx.BITMAP_TYPE_XPM))
        self.subsizer.Insert(2, self.delpoint, 0, wx.ALIGN_CENTRE_VERTICAL | wx.TOP | wx.BOTTOM, BTN_BORDER)
        self.delpoint.SetToolTipString(_("Delete a point"))
        self.delpoint.Disable()

        self.subsizer.Fit(self.subp)
        
        wx.EVT_BUTTON(self.newbox, -1, self.on_new_box)
        wx.EVT_BUTTON(self.newpoint, -1, self.on_new_point)
        wx.EVT_BUTTON(self.delpoint, -1, self.on_delete_point)
        wx.EVT_SIZE(self, self.on_size)

        listctrl = self.GetListCtrl()
        wx.EVT_LIST_ITEM_SELECTED(listctrl, listctrl.GetId(), self.on_change_selection)
        wx.EVT_LIST_END_LABEL_EDIT(listctrl, listctrl.GetId(), self.on_end_edit)

        button = self.GetDelButton()
        wx.EVT_BUTTON(button, -1, self.on_delete_boxsystem)
        wx.EVT_CHAR(listctrl, self.OnChar)
        
    def OnChar(self, event):
        pass

    def on_size(self, evt):
        size = self.GetClientSize()
        position = self.GetNewButton().GetPosition()
        taille = self.GetNewButton().GetSize()
        self.newbox.SetPosition((size.width - (taille.width * 8) - 8, position.y))
        self.newpoint.SetPosition((size.width - (taille.width * 7) - 8, position.y))
        self.delpoint.SetPosition((size.width - (taille.width * 6) - 8, position.y))
        self.newbox.SetSize(taille)
        self.newpoint.SetSize(taille)
        self.delpoint.SetSize(taille)
        evt.Skip()

    def create_new_box(self):
        self.speculoos.canvas.CaptureMouse()
        self.speculoos.is_creating = True
        self.speculoos.start_choosing_point()
        return Box()

    def on_end_edit(self, evt):
        ind = evt.GetIndex()
        liste = self.GetListCtrl()
        
        if evt.IsEditCancelled() and self.creating:
                self.creating = False
                liste.SetItemText(ind, "")
                evt.Skip()
                return

        if not self.creating:
            artub = self.speculoos.artub
            ind = liste.GetNextItem(-1, state = wx.LIST_STATE_SELECTED)
            name = liste.GetItemText(ind)
            newname = evt.GetText()
            bxsystem = self.bxmanager.bxsystems[ind]
            artub.active_editor.update(True)
            baseclass = bxsystem.obj.__class__.__bases__[0].__name__
            artub.project.rename_class(bxsystem.obj.__class__.__name__, newname + baseclass)
            res = self.speculoos.active_resource
            res.get_class().remove_property(name)
            res.get_class().set_property(newname, self.speculoos.active_resource.name + '.' + newname + baseclass + '(self)')
            artub.active_editor.update(False)
            return

        if not evt.GetText(): txt = liste.GetItemText(ind)
        else: txt = evt.GetText()

        self.creating = False
        if ind == liste.GetItemCount() - 1 and txt:
            bxsystem = BoxSystem()
            self.on_new(txt, bxsystem)
            self.GetNewButton().Enable()
            self.GetDelButton().Enable()
            self.bxmanager.bxsystems.append(bxsystem)
            self.newbox.Enable()
            self.newpoint.Enable()
            self.delpoint.Enable()
            self.edit_boxsystem(bxsystem)
        evt.Skip()

    def on_delete_boxsystem(self, evt):
        liste = self.GetListCtrl()
        ind = liste.GetNextItem(-1, state = wx.LIST_STATE_SELECTED)
        name = liste.GetItemText(ind)
        bxsystem = self.bxmanager.bxsystems[ind]
        self.delete_graphical_points(bxsystem)
        self.delete_contour(bxsystem)
        del self.bxmanager.bxsystems[ind]
        self.speculoos.current_bxsystem = None
        evt.Skip()
        res = self.speculoos.active_resource
        res.sync()
        res.get_class()
        try: bxsystem.obj.parent.children.remove(bxsystem.obj)
        except: pass
        try: res.get_class().remove_class(bxsystem.obj.__class__.__name__)
        except: raise
        res.get_class().remove_property(name)
        res.ast_has_changed = True
        res.topy()
        res.exec_listing()
        self.speculoos.artub.update_treeitem(res)

    def on_new_box(self, evt):
        self.speculoos.current_box = self.create_new_box()
        self.speculoos.current_contour = None
        self.speculoos.current_bxsystem.boxes.append(self.speculoos.current_box)
        self.speculoos.start_choosing_point()

    def on_new_point(self, evt):
        self.speculoos.is_splitting = True
        self.speculoos.start_choosing_point()

    def on_delete_point(self, evt):
        self.speculoos.is_deleting = True
        self.speculoos.start_choosing_point()

    def create_graphical_points(self, bxsystem):
        for i in bxsystem.boxes:
            for j in i.points:
                gpoint = self.speculoos.create_graphical_point(j)
                gpoint.x, gpoint.y = j
                i.gpoints.append(gpoint)

    def delete_graphical_points(self, bxsystem):
        for i in bxsystem.boxes:
            for j in i.gpoints:
                self.speculoos.game.screen.children.remove(j)
            i.gpoints = []

    def create_contour(self, bxsystem):
        for i in bxsystem.boxes:
            i.contour = Contour(self.speculoos.game.screen, loop=True)
            i.contour.box = i

    def delete_contour(self, bxsystem):
        for i in bxsystem.boxes:
            if i.contour:
                self.speculoos.game.screen.children.remove(i.contour)
            i.contour = None

    def get_properties(self, bxsystem):
        return ChangeSceneCompanion(self.speculoos.active_resource, bxsystem, bxsystem.obj)
    
    def edit_boxsystem(self, bxsystem):
        if self.speculoos.current_bxsystem:
            self.delete_graphical_points(self.speculoos.current_bxsystem)
            self.delete_contour(self.speculoos.current_bxsystem)

        self.speculoos.current_bxsystem = bxsystem
        self.create_graphical_points(bxsystem)
        self.create_contour(bxsystem)
        self.speculoos.select_sprite(bxsystem.obj)
        self.speculoos.artub.pb.set_inspector(self.get_properties(bxsystem))
        
    def on_change_selection(self, evt):
        liste = self.GetListCtrl()
        sel = evt.GetIndex()
        if sel != -1 and evt.GetText():
            try:
                self.edit_boxsystem(self.bxmanager.bxsystems[sel])
                self.newbox.Enable()
                self.newpoint.Enable()
                self.delpoint.Enable()
            except IndexError: print "Can't find boxsytem in", self.bxmanager.bxsystems
        else:
            self.newbox.Disable()
            self.newpoint.Disable()
            self.delpoint.Disable()
        self.speculoos.toolbar.unselect_items()
        evt.Skip()

    def create_object(self, name, bxsystem, baseclass, code, args = "(self)"):
        gns = wx.GetApp().gns
        res = self.speculoos.active_resource
        res.get_class().add_class(name + baseclass, base_classes = [baseclass], body = code)
        res.get_class().set_property(name, self.speculoos.active_resource.name + '.' + name + baseclass + args)
        res.ast_has_changed = True
        res.exec_listing()
        wx.GetApp().artub_frame.update_treeitem(res)
        bxsystem.name = name
        bxsystem.baseclass = baseclass
        bxsystem.obj = gns.eval(self.speculoos.active_resource.name + '.' + name + baseclass + "(None)")
    
    def on_new(self, name, bxsystem):
        code = [ "def __init__(self, parent):",
                 "    " + self.base_class + ".__init__(self, parent)",
                 "    self.__glumolinit__()",
                 "def __glumolinit__(self):",
                 "    self.color = (1.0, 1.0, 1.0)" ]
        self.create_object(name, bxsystem, "LightZone", code)

    def generate_name(self, varname, n):
        return varname + n
        
    def OnNewItem(self, event):
        self.base_class = "" #self.default_class
        pos = wx.GetMousePosition()
        pos = self.ScreenToClient(pos)
        self.PopupMenu(
                self.speculoos.artub.get_templates_menu(
                    callback = self.on_template_select,
                    section = self.default_class),
                    pos)
        n = 1
        if not self.base_class: return
        varname = self.base_class.lower()
        while hasattr(self.speculoos.obj, varname + str(n) + self.base_class) or \
              self.m_listCtrl.FindItem(0, varname + str(n)) != -1:
            n = n + 1
        
        varname = choose_a_name(self.generate_name(varname, str(n)))
        if not varname: return
        
        self.m_listCtrl.InsertStringItem(self.m_listCtrl.GetItemCount(), varname)
        
        bxsystem = BoxSystem()
        self.on_new(varname, bxsystem)
        self.GetNewButton().Enable()
        self.GetDelButton().Enable()
        self.bxmanager.bxsystems.append(bxsystem)
        self.newbox.Enable()
        self.newpoint.Enable()
        self.delpoint.Enable()
        self.edit_boxsystem(bxsystem)

    def OnItemSelected(self, event):
        self.m_selection = event.GetIndex()
        if self.m_style & wxEL_ALLOW_UPDOWN:
            self.m_bUp.Enable(self.m_selection != 0 and self.m_selection < self.m_listCtrl.GetItemCount())
            self.m_bDown.Enable(self.m_selection < self.m_listCtrl.GetItemCount() - 1)
        if self.m_style & wxEL_ALLOW_EDIT:
            self.m_bEdit.Enable(self.m_selection < self.m_listCtrl.GetItemCount())
        if self.m_style & wxEL_ALLOW_DELETE:
            self.m_bDel.Enable(self.m_selection < self.m_listCtrl.GetItemCount())

    def SetStrings(self, strings):
        self.m_listCtrl.DeleteAllItems()
        n = 0
        for i in strings:
            self.m_listCtrl.InsertStringItem(n, i)
            n = n + 1

    def GetStrings(self):
        strings = []

        for i in xrange(m_listCtrl.GetItemCount()):
            strings.append(self.m_listCtrl.GetItemText(i))

    def on_template_select(self, name):
        self.base_class = name

class PlanesListBox(SpeculoosEditableListBox):
    default_class = ["Plane", "ZPlane"]
    
    def __init__(self, speculoos, parent, id, title):
        SpeculoosEditableListBox.__init__(self, speculoos, parent, id, title)

    def get_properties(self, bxsystem):
        return SpeculoosCompanion(self.speculoos.active_resource, bxsystem.obj)

    def on_new(self, name, bxsystem):
        code = [ "def __init__(self, parent):",
                 "    " + self.base_class + ".__init__(self, parent)",
                 "    self.__glumolinit__()",
                 "def __glumolinit__(self):",
                 "    self.current_anim = NoImage()" ]
        self.create_object(name, bxsystem, self.base_class, code)

class LightZoneListBox(SpeculoosEditableListBox):
    default_class = "LightZone"
    
    def on_new(self, name, bxsystem):
        code = [ "def __init__(self, parent):",
                 "    " + self.base_class + ".__init__(self, parent)",
                 "    self.__glumolinit__()",
                 "def __glumolinit__(self):",
                 "    self.color = (1.0, 1.0, 1.0)" ]
        self.create_object(name, bxsystem, self.base_class, code)

    def get_properties(self, bxsystem):
        return LightZoneCompanion(self.speculoos.active_resource, bxsystem, bxsystem.obj)
    
class ObjectListBox(SpeculoosEditableListBox):
    default_class = "Object"
    
    def __init__(self, speculoos, parent, id, title):
        SpeculoosEditableListBox.__init__(self, speculoos, parent, id, title)
        
        taille = self.GetNewButton().GetSize()
        
        self.set_walk_point = wx.BitmapButton(self.GetNewButton().GetParent(), -1, 
                                              wx.Bitmap(get_image_path('walkpoint.xpm')))
        self.subsizer.Insert(2, self.set_walk_point, 0, wx.ALIGN_CENTRE_VERTICAL | wx.TOP | wx.BOTTOM, BTN_BORDER)
        self.set_walk_point.SetToolTipString("Set the point the character will go to before using this object")
        self.set_walk_point.Disable()
        self.set_walk_point.SetSize(taille)
        wx.EVT_BUTTON(self.set_walk_point, -1, self.on_set_walk_point)
        
    def on_change_selection(self, evt):
        SpeculoosEditableListBox.on_change_selection(self, evt)
        sel = evt.GetIndex()
        if sel != -1 and evt.GetText():
            self.set_walk_point.Enable()
        else:
            self.set_walk_point.Disable()
    
    def on_size(self, evt):
        SpeculoosEditableListBox.on_size(self, evt)
        size = self.GetClientSize()
        position = self.GetNewButton().GetPosition()
        taille = self.GetNewButton().GetSize()
        self.set_walk_point.SetPosition((size.width - (taille.width * 9) - 8, position.y))
    
    def on_set_walk_point(self, evt):
        self.speculoos.setting_walk_point = True
        self.speculoos.start_choosing_point()

    def on_new(self, name, bxsystem):
        baseclass = self.base_class
        code = [ "def __init__(self, parent):",
                 "    " + baseclass + ".__init__(self, parent)",
                 "    self.__glumolinit__()",
                 "    self.set_boxes()",
                 "def __glumolinit__(self):",
                 "    pass" ]
        self.create_object(name, bxsystem, baseclass, code)

    def get_properties(self, bxsystem):
        return ObjectCompanion(self.speculoos.active_resource, bxsystem, bxsystem.obj)

class ChangeSceneListBox(SpeculoosEditableListBox):
    default_class = "ChangeSceneZone"

    def on_new(self, name, bxsystem):
        code = [ "def __init__(self, parent):",
                 "    " + self.base_class + ".__init__(self, parent)",
                 "    self.__glumolinit__()",
                 "def __glumolinit__(self):",
                 "    self.to_scene = None" ]
        self.create_object(name, bxsystem, self.base_class, code)

    def get_properties(self, bxsystem):
        return ChangeSceneCompanion(self.speculoos.active_resource, bxsystem, bxsystem.obj)

    def generate_name(self, varname, n):
        return "from_" + self.speculoos.active_resource.name + "_to_".lower()
        
class CharactersListBox(SpeculoosEditableListBox):
    default_class = "Character"

    def on_new(self, name, bxsystem):
        code = [ "def __init__(self, parent):",
                 "    " + self.base_class + ".__init__(self, parent)",
                 "    self.__glumolinit__()",
                 "def __glumolinit__(self):",
                 "    self.to_scene = None" ]
        self.create_object(name, bxsystem, self.base_class, code)

    def get_properties(self, bxsystem):
        return ObjectCompanion(self.speculoos.active_resource, bxsystem, bxsystem.obj)

class WalkBoxesListBox(SpeculoosEditableListBox):
    default_class = ["WalkZone", "ForbiddenZone"]

    def on_new(self, name, bxsystem):
        code = [ "def __init__(self, parent):",
                 "    " + self.base_class + ".__init__(self, parent)",
                 "    self.__glumolinit__()",
                 "def __glumolinit__(self):",
                 "    pass" ]
        self.create_object(name, bxsystem, self.base_class, code)

    def get_properties(self, bxsystem):
        return WalkZoneCompanion(self.speculoos.active_resource, bxsystem, bxsystem.obj)

class ScaleBoxesListBox(SpeculoosEditableListBox):
    default_class = "ScaleZone"

    def on_new(self, name, bxsystem):
        code = [ "def __init__(self, parent):",
                 "    " + self.base_class + ".__init__(self, parent)",
                 "    self.__glumolinit__()",
                 "def __glumolinit__(self):",
                 "    pass" ]
        self.create_object(name, bxsystem, self.base_class, code)

    def get_properties(self, bxsystem):
        return ScaleZoneCompanion(self.speculoos.active_resource, bxsystem, bxsystem.obj)

class SpriteListBox(SpeculoosEditableListBox):
    default_class = "Sprite"

    def on_new(self, name, bxsystem):
        code = [ "def __init__(self, parent):",
                 "    " + self.base_class + ".__init__(self, parent)",
                 "    self.__glumolinit__()",
                 "def __glumolinit__(self):",
                 "    pass" ]
        self.create_object(name, bxsystem, self.base_class, code)

    def get_properties(self, bxsystem):
        return ObjectCompanion(self.speculoos.active_resource, bxsystem, bxsystem.obj)

class OtherZonesListBox(SpeculoosEditableListBox):
    default_class = "Region"

class EntryPointsListBox(SpeculoosEditableListBox):
    default_class = "EntryPoint"
    
    def on_new(self, name, bxsystem):
        code = [ "def __init__(self, parent):",
                 "    " + self.base_class + ".__init__(self, parent)",
                 "    self.__glumolinit__()",
                 "def __glumolinit__(self):",
                 "    pass" ]
        self.create_object(name, bxsystem, self.base_class, code)

    def get_properties(self, bxsystem):
        return ObjectCompanion(self.speculoos.active_resource, bxsystem, bxsystem.obj)
