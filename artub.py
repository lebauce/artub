#!/usr/bin/python
# -*- coding: utf-8 -*-"

__version__ = "1.0"

from depplatform import get_image_path, set_sys_path
set_sys_path()

print "Running Artub version", __version__
import gettext
gettext.install('artub', 'locale', unicode=1)
import locale
import wx
print "Using wxPython", wx.VERSION_STRING
try:
    info = wx.Locale.GetLanguageInfo(wx.Locale.GetSystemLanguage())
    langue = info.CanonicalName[:2]
    lang1 = gettext.translation('artub', 'locale', languages=[langue])
    lang1.install(unicode=1)
except:
    print "Cannot find a translation for your language '", locale.getdefaultlocale(), "'. Defaulting to english"

import os
import os.path
import sys
import time

try: os.chdir(os.path.dirname(__file__))
except: pass

import wx.aui as PyAUI
from artubnotebook import ArtubNotebook
from configmanager import config
from resourceeditor import CEditorManager, AddResource
import log
from startuppage import StartupPage
from toolbarmanager import ToolbarManager
from propertiesbar import PropertiesBar
from project import load_project, CProject
from newproject import new_project
from projectproperties import ProjectProperties
from showoptions import OptionsWindow
from debugger.glumoldebugger import ProjectDebugger
from script import CScript, get_function_args, get_full_name, \
                   get_class_code, make_variable_name, make_class_name 
from glumolresource import VirtualGlumolResource
from dialogue import CDialogue
from glumolfont import CGlumolFont
from glumolobject import CGlumolObject, VirtualGlumolObject
from sound import CSound
from animation import CAnimation, VirtualAnimation
from inspect import getmembers, isclass
from undoredo import undo_manager
import pypoujol
from stackless import tasklet, run, schedule
from redistributable import Redistributable 
from choosename import choose_a_name
from propertiesbar.companions import Companion
import types
game = None

class ArtubTree(wx.TreeCtrl):
    def __init__(self, parent, artub, style = wx.TR_HAS_BUTTONS | wx.TR_EDIT_LABELS | # Crash on Windows !!!
                                              wx.TR_HAS_VARIABLE_ROW_HEIGHT |
                                              wx.TR_LINES_AT_ROOT |
                                              wx.TR_HAS_BUTTONS):
        self.artub = artub
        self.dying = False

        tID = wx.NewId()
        wx.TreeCtrl.__init__(self, parent, tID, style = style)
        wx.EVT_TREE_SEL_CHANGED(self, tID, self.on_sel_changed)
        wx.EVT_RIGHT_UP(self, self.on_default_right_up)
        wx.EVT_KEY_DOWN(self, self.on_key_down)
        wx.EVT_TREE_END_LABEL_EDIT(self, tID, self.on_tree_end_label_edit) # Crash on my Windows
        
    def add_tree_item(self, resource, parent = None):
        if not parent:
            data = wx.TreeItemData(resource)
            item = self.AddRoot(resource.name, -1, -1, data)
        else:
            data = wx.TreeItemData(resource)
            item = self.AppendItem(parent, resource.name, -1, -1, data)
        resource.treeitem = item
        return item
        
    def add_new_resource(self, res):
        self.artub.project.childs.append(res)
        data = wx.TreeItemData(res)
        res.treeitem = self.AppendItem(self.GetRootItem(), res.name, -1, -1, data)
        
    def get_default_resource_menu(this):
        class DefaultMenu(wx.Menu):
            def __init__(self, tree):
                wx.Menu.__init__(self)
                this.artub.populate_resource_menu(self)
      
        return DefaultMenu(this)
    
    def on_key_down(self, evt):
        self.artub.on_key_down(evt)
        
    def on_tree_end_label_edit(self, event):
        self.artub.on_tree_end_label_edit(event)

    def on_right_down(self, event):
        return
        
    def on_default_right_up(self, event):
        if not self.artub.project: return
        self.on_right_up(event)
        
    def on_right_up(self, event):
        item, flag = self.HitTest(event.GetPosition())
        if item.IsOk() and self.GetSelection() != item:
            self.SelectItem(item)
        if not item.IsOk() and self.GetRootItem().IsOk():
            item = self.GetRootItem()
        if item.IsOk():
            resource = self.GetItemData(item).GetData()
            editor = self.artub.get_editor_from_resource(resource)
            menu = None
            if editor:
                menu = editor.get_popup_menu(resource)
            if not menu:
                menu = self.get_default_resource_menu()
            else:
                self.artub.populate_resource_menu(menu)
        else:
            menu = self.get_default_resource_menu()
        
        self.PopupMenu(menu, event.GetPosition())
        #event.Skip()
        
    def on_sel_changed(self, event):
        if self.dying:
            return
        
        item = event.GetItem()
        if item:
            data = self.GetItemData(item).GetData()
            self.artub.edit_resource(data)
            self.artub.project_frame.unselect_items()
            #self.artub.todos.append((self.artub.nb.SetSelection, (self.artub.nb.GetPageCount() - 1,)))
            
class TemplatesTree(ArtubTree):
    def __init__(self, parent, artub):
        ArtubTree.__init__(self, parent, artub,
                             style = wx.TR_HAS_BUTTONS |
                             wx.TR_HAS_VARIABLE_ROW_HEIGHT |
                             wx.TR_HIDE_ROOT |
                             wx.TR_LINES_AT_ROOT |
                             wx.TR_HAS_BUTTONS)

    def get_default_resource_menu(this):
        class DefaultMenu(wx.Menu):
            def __init__(self, tree):
                wx.Menu.__init__(self)
                propID = wx.NewId()
                self.Append(propID, _("Import"), _("Import"))
                wx.EVT_MENU(self, propID, this.artub.on_import)

        return DefaultMenu(this)

    def find_item(self, parent, name):
        if not parent.IsOk(): return None
        item = self.GetFirstChild(parent)[0]
        while item.IsOk():
            if self.GetItemText(item) == name:
                return item
            item = self.GetNextSibling(item)
        return None
    
    def add_template(self, resource, exec_script = True):
        if exec_script: resource.exec_listing()
        c = wx.GetApp().gns.getattr(resource.name)
        item = self.GetRootItem()
        def popo(c):
            res = []
            if len(c.__bases__):
                for i in c.__bases__:
                    if i.__name__ == "object":
                        if not self.find_item(self.GetRootItem(), c.__name__):
                            res.append(self.GetRootItem())
                            return res
                    item2 = popo(i)
                    for j in item2:
                        item3 = self.find_item(j, c.__name__)
                        if item3:
                            res.append(item3)
                        else:
                            res.append(self.AppendItem(j, c.__name__))
            else:
                res.append(self.GetRootItem())
            return res
        self.Refresh()
                
        def add_template_aux(item, bases):
            for b in bases:
                if type(b) == types.ListType:
                    add_template_aux(b)
                else:
                    item2 = self.find_item(item, b[0].__name__)
                    if item2:
                        item = item2
                    else:
                        item = self.AppendItem(item, b[0].__name__)
                    add_template_aux(item, b[1])
        import inspect
        bases = inspect.getclasstree([c])
        l = popo(c)
        for i in l:
            self.SetPyData(i, resource)
            
    def on_new(self, event):
        item = self.GetSelection()
        resource = self.GetItemData(item).GetData()
        if resource:
            res = CGlumolObject(resource)
            base_classes = [wx.GetApp().gns.getattr(resource.name)]
        else:
            res = CGlumolObject(wx.GetApp().frame.project)
            base_classes = [wx.GetApp().gns.getattr(self.GetItemText(item))]
        res.name = choose_a_name(_("New_") + self.GetItemText(item))
        if not res.name: return
        res.template = True
        res.sync()
        if base_classes:
            args = get_function_args(base_classes[0].__init__)
            args2 = get_function_args(base_classes[0].__init__, nodefaults=True)
            if args.endswith(", extras"):
                code = [ "def __init__(" + args[:-7] + "*extras):" ]
                code += [ "    " + base_classes[0].__name__ + ".__init__(" + args2[:-7] + "*extras)" ]
            else:
                code = [ "def __init__(" + args + "):" ]
                code += [ "    " + base_classes[0].__name__ + ".__init__(" + args2 + ")" ]
            code += ["    self.__glumolinit__()",
                 "def __glumolinit__(self):",
                 "    super(" + res.name + ", self).__glumolinit__()" ]
        else:
            code = ["pass"]
        self.Refresh()
        c = res.add_class(res.name, base_classes = map(lambda x: x.__name__, base_classes), body = code)
        res.topy()
        res.exec_listing()
        self.add_tree_item(res, item)
            
    def on_delete(self, event):
        pass
        
    def on_right_up(self, event):
        if not self.artub.project: return
        item, flag = self.HitTest(event.GetPosition())
        if item.IsOk():
            resource = self.GetItemData(item).GetData()
            class AMenu(wx.Menu):
                def __init__(this):
                    wx.Menu.__init__(this)
                    propID = wx.NewId()
                    this.Append(propID, _("New"), _("New"))
                    wx.EVT_MENU(this, propID, self.on_new)
                    if resource:
                        propID = wx.NewId()
                        this.Append(propID, _("Delete"), _("Delete"))
                        wx.EVT_MENU(this, propID, self.on_delete)
                            
            menu = AMenu()
            self.PopupMenu(menu, event.GetPosition())
            event.Skip()
            return
                
        menu = self.get_default_resource_menu()
        self.PopupMenu(menu, event.GetPosition())
        event.Skip()
        
    def populate(self, project):
        self.DeleteAllItems()
        root = self.AddRoot(" ")
        item = self.AppendItem(self.GetRootItem(), "Sprite")
        item = self.AppendItem(self.GetRootItem(), "Game")
        item = self.AppendItem(self.GetRootItem(), "Region")
        item = self.AppendItem(self.GetRootItem(), "Behaviour")
        
    def on_sel_changed(self, event):
        if self.dying: return
        item = event.GetItem()
        if item:
            resource = self.GetItemData(item).GetData()
            if resource:
                self.artub.edit_resource(resource, self.artub.get_editor('akiki'))
                self.artub.project_frame.unselect_items()
    
class RoomTree(ArtubTree):
    def __init__(self, parent, artub):
        ArtubTree.__init__(self, parent, artub,
                             style = wx.TR_HAS_BUTTONS |
                             wx.TR_HAS_VARIABLE_ROW_HEIGHT |
                             wx.TR_HIDE_ROOT |
                             wx.TR_LINES_AT_ROOT |
                             wx.TR_HAS_BUTTONS)
        self.root = self.AddRoot(" ")

    def get_default_resource_menu(self):
        return self.artub.get_templates_menu(
                callback = self.artub.on_new_class,
                section = "Scene", prefix = "New ")
        
class SoundsTree(ArtubTree):
    def get_default_resource_menu(this):
        class DefaultMenu(wx.Menu):
            def __init__(self, tree):
                wx.Menu.__init__(self)
                propID = wx.NewId()
                self.Append(propID, _("New sound"), _("New sound"))
                wx.EVT_MENU(self, propID, this.on_new_sound)
                
        return DefaultMenu(this)
            
    def on_new_sound(self, evt):
        name = choose_a_name(_("New_sound"))
        if not name: return
        sound = CSound()
        base_class = "Sound"
        sound.name = self.artub.project.get_resource_name(name)
        sound.listing = "class %s(%s):\n" % (sound.name, base_class)
        sound.listing = sound.listing + "    filename = ''\n"
        sound.listing = sound.listing + "    def __init__(self):\n"
        sound.listing = sound.listing + "        %s.__init__(self)\n" % base_class
        sound.listing = sound.listing + "        self.__glumolinit__()\n"
        sound.listing = sound.listing + "    def __glumolinit__(self):\n"
        sound.listing = sound.listing + "        super(" + sound.name + ", self).__glumolinit__()\n\n"
        self.add_new_resource(sound)
        self.add_new_resource(sound)
        
class ProjectFrame(wx.Panel):
    name = _("Project bar")
    def __init__(
        self, parent, id=-1, title="", pos=wx.DefaultPosition, size=wx.DefaultSize,
        style=wx.DEFAULT_FRAME_STYLE
        ):
        self.artub = artub = parent
        wx.Panel.__init__(self, artub, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        project_nb = artub.project_nb = PyAUI.AuiNotebook(self, -1, wx.DefaultPosition,
                                              wx.DefaultSize, style = PyAUI.AUI_NB_SCROLL_BUTTONS)
        sizer.Add(parent.project_nb, 1, wx.EXPAND)

        tree = artub.tree = ArtubTree(project_nb, artub)
        project_nb.AddPage(tree, _("Project"))
        
        imagelist = wx.ImageList(16, 16, True)
        imagelist.Add(
                    wx.Bitmap(get_image_path("cost.xpm"), wx.BITMAP_TYPE_XPM))
        imagelist.Add(
                    wx.Bitmap(get_image_path("talk.xpm"), wx.BITMAP_TYPE_XPM))
        imagelist.Add(
                    wx.Bitmap(get_image_path("object.xpm"), wx.BITMAP_TYPE_XPM))
        imagelist.Add(
                    wx.Bitmap(get_image_path("script.xpm"), wx.BITMAP_TYPE_XPM))
        imagelist.Add(
                    wx.Bitmap(get_image_path("project.xpm"), wx.BITMAP_TYPE_XPM))
        imagelist.Add(
                    wx.Bitmap(get_image_path("font.xpm"), wx.BITMAP_TYPE_XPM))
        imagelist.Add(
                    wx.Bitmap(get_image_path("scene.xpm"), wx.BITMAP_TYPE_XPM))
        
        tree.AssignImageList(imagelist)

        #self.rooms = RoomTree(self.project_nb, self)
        #self.project_nb.AddPage(self.rooms, _("Scenes"))

        artub.templ_tree = TemplatesTree(project_nb, artub)
        project_nb.AddPage(artub.templ_tree, _("Templates"))
        
        # self.costs = ArtubTree(self.project_nb, self)
        # self.project_nb.AddPage(self.costs, _("Sprites"))

        artub.sounds = SoundsTree(project_nb, artub)
        project_nb.AddPage(artub.sounds, _("Sounds"))

        self.SetSizer(sizer)

    def get_active_tree(self):
        return self.get_tree_list()[self.artub.project_nb.GetSelection()]
    
    def get_tree_list(self):
        return [ self.artub.tree, self.artub.templ_tree, self.artub.sounds ]

    def unselect_items(self, all=False):
        if sys.platform != "win32":
            n = 0
            for i in [self.artub.tree, self.artub.templ_tree, self.artub.sounds]:
                if all or (n != self.artub.project_nb.GetSelection()):
                    i.dying = True
                    i.UnselectAll()
                    i.dying = False
                n = n + 1

    def on_close_window(self, evt):
        self.manager.toggle_bar(self.menu_id)

class ArtubFrame(wx.Frame, CEditorManager):
    resource_icons = { CDialogue : 1, CAnimation : 0, CGlumolObject : 2,
                       CProject : 4, CScript : 3, VirtualGlumolObject : 2,
                       CGlumolFont : 5, VirtualAnimation : 0 }

    def __init__(self, parent, id, title, config):
        CEditorManager.__init__(self)

        wx.Frame.__init__(self, parent, -1, title, size = (800, 600),
                                style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        self.cwd = os.getcwd()
        sys.path.append(self.cwd)
        self.window = None
        self.config = config
        self.context = None
        self.todos = []
        
        self.new_anim_id = wx.NewId()
        self.new_scene_id = wx.NewId()
        self.new_sprite_id = wx.NewId()
        self.new_script_id = wx.NewId()
        self.new_dialog_id = wx.NewId()
        self.new_font_id = wx.NewId()

        self.quitte = False

        self.app = wx.GetApp()
        self.app.artub_frame = self
        self.app.frame = self

        self.path = os.getcwd()
        self.debugging = False
        
        self.metaclasses = ["BehaviourMetaClass", "SpriteMetaClass", "AnimationMetaClass", "GameMetaClass", "SceneMetaClass"]
        
        if __name__ != "__main__":
            frame = wx.Frame(self, -1)
            self.log = wx.TextCtrl(frame, -1,
                                   style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
            log.set_text_ctrl(self.log)
            frame.Show(True)
            
        self._mgr = PyAUI.AuiManager()

        def OnFloatingPaneClosed(window):
            self.toolbar_manager.on_close_toolbar(window)
            return True
        
        def OnPaneClosed(window):
            self.toolbar_manager.on_close_toolbar(window)
            return True
        
        self._mgr.OnFloatingPaneClosed = OnFloatingPaneClosed
        self._mgr.OnPaneClosed = OnPaneClosed
        
        self._mgr.SetManagedWindow(self)
        self._mgr.SetFlags(self._mgr.GetFlags() ^ PyAUI.AUI_MGR_ALLOW_ACTIVE_PANE)
        self._mgr.GetArtProvider()._gradient_type = PyAUI.AUI_GRADIENT_NONE
        
        self.toolbar_manager = ToolbarManager(self)

        greta = wx.Icon(get_image_path("greta.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(greta)
        
        self.create_menus()
        self.create_standard_toolbar()

        self.load_plugins()
        self.dist = Redistributable()

        self.otherWin = None
        wx.EVT_IDLE(self, self.on_idle)
        wx.EVT_CLOSE(self, self.on_close_window)
        wx.EVT_ICONIZE(self, self.on_iconify)
        wx.EVT_MAXIMIZE(self, self.on_maximize)

        self.Centre(wx.BOTH)
        self.statusbar = self.CreateStatusBar(1, wx.ST_SIZEGRIP)

        # Shell
        import __builtin__
        globals()["artub"] = self
        class MyShell(wx.py.shell.Shell):
            def push(command, silent = False):
                __ = __builtin__.__dict__["_"]
                wx.py.shell.Shell.push(command, silent)
                __builtin__.__dict__["_"] = __ 

        self.shell = self.toolbar_manager.create_toolbar(MyShell,
                            keywords = { "locals" : globals(), "introText" : "Welcome to the Glumol debugger" },
                            infos = PyAUI.AuiPaneInfo().Name(_("Shell")).
                            Caption(_("Shell")).Left().Float().MinSize(wx.Size(200, 100)))
        
        # Project frame
        self.project_frame = self.toolbar_manager.create_toolbar(
                                ProjectFrame,
                                infos = PyAUI.AuiPaneInfo().Name(_("Project bar")).
                                Caption(_("Project")).Left().
                                MinSize(wx.Size(200,100)))
        
        # Notebook
        self.nb = ArtubNotebook(self, -1, wx.CLIP_CHILDREN)
        self._mgr.AddPane(self.nb, PyAUI.AuiPaneInfo().Name(_("Notebook")).
                                   Caption(_("Notebook")).CenterPane())

        wx.EVT_MENU_RANGE(self, wx.ID_FILE1, wx.ID_FILE9, self.on_file_history)

        # Startup page
        self.ovr = StartupPage(self.nb, -1, self)
        self.ovr.update_recent_files()
        self.nb.AddPage(self.ovr, _("Startup"))
        self.ovr.Refresh()
        
        self.Show(True)

        self.project = None
        
        self.debugger = ProjectDebugger(self, self)
        
        self.pb = self.toolbar_manager.create_toolbar(PropertiesBar,
                      infos = PyAUI.AuiPaneInfo().Name(PropertiesBar.name).
                      Caption(PropertiesBar.name).MinSize(wx.Size(200, 100)).Left())
        
        self.toolbar_manager.care_of_menu(self.windows)
        self.SetMenuBar(self.mainmenu)
        self.care_of_auto_load()
        self._mgr.Update()
        self._mgr.HideHint()

    def CloseWindow(self, event):
        self.Close()
    
    def on_toggle_breakpoint(self, evt):
        self.active_editor.on_toggle_breakpoint(evt)
    
    def on_toggle_breakpoint_update_ui(self, evt):
        if self.project and self.active_editor and self.active_editor.name == "akiki": evt.Enable(True) # Smart way didn't work
        else: evt.Enable(False)

    def create_standard_toolbar(self):
        class MainToolBar(wx.ToolBar):
            name = _("Main toolbar")
            def __init__(
                this, parent=None, id=-1, title = "",
                pos = wx.DefaultPosition, size = wx.DefaultSize,
                style = wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_DOCKABLE | wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_HORIZONTAL,
                name = _(""),
                value = None):
                
                wx.ToolBar.__init__(this, parent, id, pos, size, style | wx.TB_HORIZONTAL)
                this.SetToolBitmapSize(wx.Size(16, 16))
                this.AddSimpleTool(10, self.bitmaps['new2.xpm'], _("New project"), _("Create a new project"))
                this.Bind(wx.EVT_TOOL, self.on_new, id=10)
                this.AddSimpleTool(11, self.bitmaps['open.xpm'], _("Open a project"), _("Open a project"))
                this.Bind(wx.EVT_TOOL, self.on_open, id=11)
                this.AddSimpleTool(12, self.bitmaps['save.xpm'], _("Save your project"), _("Save your project"))
                this.Bind(wx.EVT_TOOL, self.on_save, id=12)
                this.AddSimpleTool(13, self.bitmaps['cut.xpm'], _("Cut to the clipboard"), _("Cut to the clipboard"))
                this.AddSimpleTool(14, self.bitmaps['copy.xpm'], _("Copy to the clipboard"), _("Copy to the clipboard"))
                this.AddSimpleTool(15, self.bitmaps['paste.xpm'], _("Paste from the clipboard"), _("Paste from the clipboard"))
                this.AddSimpleTool(self.undoID, self.bitmaps['undo.xpm'], _("Undo last change"), _("Undo last change"))
                this.Bind(wx.EVT_TOOL, self.undo, id=self.undoID)
                this.AddSimpleTool(self.redoID, self.bitmaps['redo.xpm'], _("Redo last change"), _("Redo last change"))
                this.Bind(wx.EVT_TOOL, self.undo, id=self.redoID)
                
                this.Realize()

        self.maintoolbar = self.toolbar_manager.create_toolbar(MainToolBar,
                           infos = PyAUI.AuiPaneInfo().Name(_("Main toolbar")).
                           Caption(_("Main toolbar")).
                           ToolbarPane().Top())
                           
    def get_bitmap(self, filename):
        item = self.bitmaps.get(filename, None)
        if not item:
            return self.load_and_store_bitmap(filename)
        else:
            return item

    def load_and_store_bitmap(self, filename):
        bmp = wx.Bitmap(get_image_path(filename), wx.BITMAP_TYPE_XPM)
        self.bitmaps[filename] = bmp
        return bmp
        
    def create_menus(self):
        self.mainmenu = wx.MenuBar()
        menu = wx.Menu()
        newID = wx.NewId()
        self.bitmaps = {}
        menuitem = wx.MenuItem(menu, newID, _("New project") + '\tCtrl-N', _("Create a new project"))
        menuitem.SetBitmap(self.load_and_store_bitmap("new2.xpm"))
        menu.AppendItem(menuitem)
        openID = wx.NewId()
        menuitem = wx.MenuItem(menu, openID, _("Open") + '\tCtrl-O', _("Open a project"))
        menuitem.SetBitmap(self.load_and_store_bitmap("open.xpm"))
        menu.AppendItem(menuitem)
        saveID = wx.NewId()
        menuitem = wx.MenuItem(menu, saveID, _("Save") + '\tCtrl-S', _("Save your project"))
        menuitem.SetBitmap(self.load_and_store_bitmap("save.xpm"))
        menu.AppendItem(menuitem)
        saveasID = wx.NewId()
        menuitem = wx.MenuItem(menu, saveasID, _("Save as") + '\tCtrl-Shift-S', _("Save as..."))
        menuitem.SetBitmap(self.load_and_store_bitmap("saveas.xpm"))
        menu.AppendItem(menuitem)
        exitID = wx.NewId()
        wx.App_SetMacExitMenuItemId(exitID)
        menu.Append(exitID, _("Exit"), _("Exit Artub"))
        self.mainmenu.Append(menu, _("File"))
        
        self.filehistory = wx.FileHistory()
        self.filehistory.UseMenu(menu)
        self.filehistory.Load(self.config)        
        
        wx.EVT_MENU(self, newID, self.on_new)
        wx.EVT_MENU(self, openID, self.on_open)
        wx.EVT_MENU(self, saveID, self.on_save)
        wx.EVT_MENU(self, saveasID, self.on_saveas)
        wx.EVT_MENU(self, exitID, self.on_exit)
        
        edit = wx.Menu()
        undoID = wx.NewId()
        self.undoID = undoID
        menuitem = wx.MenuItem(menu, undoID, _("Undo") + '\tCtrl-Z', _("Undo last change"))
        menuitem.SetBitmap(self.get_bitmap("undo.xpm"))
        edit.AppendItem(menuitem)
        redoID = wx.NewId()
        self.redoID = redoID
        menuitem = wx.MenuItem(menu, redoID, _("Redo") + '\tCtrl-Y', _("Redo last change"))
        menuitem.SetBitmap(self.get_bitmap("redo.xpm"))
        edit.AppendItem(menuitem)
        cutID = wx.NewId()
        menuitem = wx.MenuItem(menu, cutID, _("Cut") + '\tCtrl-X', _("Cut selection and put it into the clipboard"))
        menuitem.SetBitmap(self.get_bitmap("cut.xpm"))
        edit.AppendItem(menuitem)
        copyID = wx.NewId()
        menuitem = wx.MenuItem(menu, copyID, _("Copy") + '\tCtrl-C', _("Copy selection into the clipboard"))
        menuitem.SetBitmap(self.get_bitmap("copy.xpm"))
        edit.AppendItem(menuitem)
        pasteID = wx.NewId()
        self.pasteID = pasteID
        menuitem = wx.MenuItem(menu, pasteID, _("Paste") + '\tCtrl-V', _("Paste from clipboard"))
        menuitem.SetBitmap(self.get_bitmap("paste.xpm"))
        edit.AppendItem(menuitem)
        self.mainmenu.Append(edit, _("Edit"))
        edit.AppendSeparator()
        findID = wx.NewId()
        menuitem = wx.MenuItem(menu, findID, _("Find") + '\tCtrl-F')
        menuitem.SetBitmap(self.get_bitmap("find.xpm"))
        edit.AppendItem(menuitem)
        wx.EVT_MENU(self, findID, self.on_find)
        findnextID = wx.NewId()

        self.undo_manager = undo_manager
        self.undo_manager.care_of_menu(self)
        
        debugmenu = wx.Menu()
                
        breakID = wx.NewId()
        self.breakID = breakID
        runprojectID = wx.NewId()
        self.runprojectID = runprojectID
        
        if sys.platform == 'darwin':
            menuitem = wx.MenuItem(edit, findnextID, _("Find next") + '\tCtrl-G')
            edit.AppendItem(menuitem)
            menuitem = wx.MenuItem(debugmenu, runprojectID, _("Run") + '\tCtrl-R', _("Run your game"))
            menuitem.SetBitmap(self.get_bitmap("go.xpm"))
            debugmenu.AppendItem(menuitem)
            menuitem = wx.MenuItem(debugmenu, breakID, _("Toggle breakpoint") + '\tCtrl-T', _("Toggle breakpoint at current line"))
            menuitem.SetBitmap(self.get_bitmap("breakpoint.xpm"))
            debugmenu.AppendItem(menuitem)
        else:
            edit.Append(findnextID, _("Find next") + '\tF3')
            menuitem = wx.MenuItem(debugmenu, runprojectID, _("Run") + '\tCtrl-F5', _("Run your game"))
            menuitem.SetBitmap(self.get_bitmap("go.xpm"))
            debugmenu.AppendItem(menuitem)
            menuitem = wx.MenuItem(debugmenu, breakID, _("Toggle breakpoint") + '\tF9', _("Toggle breakpoint at current line"))
            menuitem.SetBitmap(self.get_bitmap("breakpoint.xpm"))
            debugmenu.AppendItem(menuitem)
        
        wx.EVT_MENU(self, runprojectID, self.on_run)
        wx.EVT_MENU(self, findnextID, self.on_find_next)
        wx.EVT_MENU(self, breakID, self.on_toggle_breakpoint)
        wx.EVT_UPDATE_UI(self, breakID, self.on_toggle_breakpoint_update_ui)
        
        self.debugmenu = debugmenu
        
        self.set_debug_mode(True)
        
        projmenu = wx.Menu()
        propID = wx.NewId()
        menuitem = wx.MenuItem(projmenu, propID, _("Properties") + '\tCtrl-P', _("Show and change your project's properties"))
        menuitem.SetBitmap(self.get_bitmap("options.xpm"))
        projmenu.AppendItem(menuitem)
        self.propID = propID
        
        self.mainmenu.Append(projmenu, _("Project"))

        wx.EVT_MENU(self, propID, self.on_properties)

        options = wx.Menu()

        optionsID = wx.NewId()
        menuitem = wx.MenuItem(options, optionsID, _("Options") + '\tAlt-O', _("Show Artub's options"))
        options.AppendItem(menuitem)
        wx.EVT_MENU(self, optionsID, self.on_options)
        wx.GetApp().SetMacPreferencesMenuItemId(optionsID)
        
        optionsID = wx.NewId()
        menuitem = wx.MenuItem(options, optionsID, _("Check for updates") + '\tCtrl-U', _("Show Artub's options"))
        menuitem.SetBitmap(self.get_bitmap("softupdate.xpm"))
        options.AppendItem(menuitem)
        wx.EVT_MENU(self, optionsID, self.on_check_for_updates)

        self.mainmenu.Append(options, _("Tools"))

        self.windows = wx.Menu()
        self.mainmenu.Append(self.windows, _("View"))
        wx.EVT_MENU(self, propID, self.on_properties)

        help = wx.Menu()
        helpID = wx.NewId()
        menuitem = wx.MenuItem(help, helpID, _("Help") + '\tCtrl-H', _("Get help"))
        menuitem.SetBitmap(self.get_bitmap("help.xpm"))
        help.AppendItem(menuitem)
        wx.EVT_MENU(self, helpID, self.on_help)
        aboutID = wx.NewId()
        help.Append(aboutID, _("About Artub"))
        wx.EVT_MENU(self, aboutID, self.on_about)
        wx.GetApp().SetMacAboutMenuItemId(aboutID)
        self.mainmenu.Append(help, _("&Help"))

        self.finddata = wx.FindReplaceData()

        self._enable_menus = [undoID, redoID, cutID, copyID, pasteID, findID, findnextID,
                              saveID, saveasID, breakID, runprojectID, propID]
        
        self.enable_menus(False)
        
    def enable_menus(self, state = True):
        for id in self._enable_menus:
            self.mainmenu.Enable(id, state)
            
    def on_view_source(self, event = None, resource = None):
        if not resource:
            item = self.tree.GetSelection()
            resource = self.tree.GetItemData(item).GetData()
        self.edit_resource(resource, self.get_editor('akiki'))
    
    def add_member_class(self, name, cl2, resource, newid, recurse = True):
        if cl2.__name__ != name: return
        if name != "__class__" and issubclass(cl2, pypoujol.Animation):
            vres = VirtualAnimation()
            vres.name = name
            vres.parent = resource
            vres.realname = get_full_name(name)
            item = self.tree.add_tree_item(vres, newid)
            vres.treeitem = item
            icon = self.get_resource_icon(vres)
            self.tree.SetItemImage(item, icon)
            self.tree.SetItemImage(item, icon, wx.TreeItemIcon_Expanded)
            return vres
        else:
          if issubclass(cl2, pypoujol.Sprite):
            vres = VirtualGlumolObject()
            vres.name = name
            vres.parent = resource
            vres.realname = get_full_name(name)
            item = self.tree.add_tree_item(vres, newid)
            vres.treeitem = item
            icon = self.get_resource_icon(vres)
            if icon:
                self.tree.SetItemImage(item, icon)
                self.tree.SetItemImage(item, icon, wx.TreeItemIcon_Expanded)
            l = getmembers(cl2, isclass)
            if recurse:
                for (name, cl) in l: # Name, class
                    self.add_member_class(name, cl, resource, item, False)
            return vres
    
    def get_resource_icon(self, resource):
        icon = self.resource_icons.get(resource.__class__, -1)
        if icon == 2:
            char = self.app.gns.getattr("Character", None)
            obj = self.app.gns.getattr(resource.name, None)
            if obj and char and issubclass(obj, char):
                return 1
            else:
                char = self.app.gns.getattr("Scene", None)
                if obj and char and issubclass(obj, char):
                    return 6
        return icon
    
    def update_treeitem(self, resource):
        self.tree.DeleteChildren(resource.treeitem)
        if not resource.template and isinstance(resource, CGlumolObject):
            gns = self.app.gns
            try:
                cl = gns.get_value(resource.name)
            except: cl = gns.getattr(get_full_name(resource.name))
            l = getmembers(cl, isclass)
            for (name, cl2) in l: # Name, class
                self.add_member_class(name, cl2, resource, resource.treeitem)

    def set_resource_treeitem(self, resource, parent_tree_id=None, exec_script = True):
        if resource.template:
            newid = self.templ_tree.add_template(resource, exec_script)
        else:
            newid = self.tree.add_tree_item(resource, parent_tree_id)
            icon = self.get_resource_icon(resource)
            if icon != -1:
                self.tree.SetItemImage(newid, icon)
                self.tree.SetItemImage(newid, icon, wx.TreeItemIcon_Expanded)
        for i in resource.childs:
            self.set_resource_treeitem(i, newid, exec_script)
        if not resource.template and (isinstance(resource, CGlumolObject) or \
                                      isinstance(resource, CProject)):
            gns = self.app.gns
            try:
                cl = gns.getattr(get_full_name(resource.name))
                if not cl: return
                #if issubclass(cl, pypoujol.Scene):
                #    self.rooms.add_room(resource)
                l = getmembers(cl, isclass)
                for (name, cl2) in l: # Name, class
                    self.add_member_class(name, cl2, resource, newid)
            except KeyError: raise
        return newid
    
    def populate_scene_list(self):
        """
        from pypoujol import scene_dict
        root = self.rooms.AddRoot(_("Scenes"), -1, -1, None)
        for i in scene_dict:
            vres = CGlumolObject()
            vres.name = i
            vres.parent = None
            data = wx.TreeItemData(vres)
            item = self.rooms.AppendItem(root, vres.name, -1, -1, data)
        """
        
    def populate_sound_list(self):
        root = self.sounds.AddRoot(_("Sounds"), -1, -1, None)
        for i in pypoujol.sounds_dict:
            pass
        
    def set_project(self, project):
        self.enable_menus()
        self.clear()
        self.debugger.attach(project)
        self.templ_tree.populate(project)
        project.exec_all_scripts() # Hack : Also set listing_has_changed to True 
        self.root = self.set_resource_treeitem(project, exec_script = False)
        self.tree.Expand(self.tree.GetRootItem())
        self.populate_scene_list()
        self.edit_resource(project)
        pypoujol.animation.anim_classes = {}
        pypoujol.animation.parent_sprite = []
        pypoujol.animation.global_dict = {}
        wx.GetApp().gns.clear()
        def add_ext_companions(t):
            if t.name in project.templates:
                comps = t.get_companions()
                for k, v in comps.items():
                    i = wx.GetApp().gns.getattr(k)
                    Companion.ext_companions[k] = (i, v)
        self.for_each_template(self.templates, add_ext_companions)

    def remove_debug_menu(self):
        self.mainmenu.Remove(3)
    
    def add_debug_menu(self):
        self.mainmenu.Append(self.debugmenu, _("Debug"))

    def set_dying(self, state):
        self.tree.dying = state
        self.sounds.dying = state
        # self.rooms.dying = state
        # self.costs.dying = state
        
    def set_debug_mode(self, state):
        if state:
            if not self.debugging:
                self.add_debug_menu()
        else:
            if self.debugging:
                self.remove_debug_menu()

    def care_of_auto_load(self):
        try:
           config["auto_load"]
           try:
               if config["auto_load"] and str(config["auto_load"]) != "False":
                   path = self.filehistory.GetHistoryFile(0)
                   print "autoloading :", path
                   self.project = load_project(path)
                   self.set_project(self.project)
           except:
               print "Error while loading project", path
               print sys.exc_info()[0], sys.exc_info()[1]
        except IndexError: pass
            
    def undo(self, evt):
        undo_manager.on_event(evt)
            
    def undo_update_ui(self, evt):
        undo_manager.on_update_ui(evt)
    
    def logEvt(self, name, event):
        print name, event.GetLong1(), event.GetLong2(), event.GetText1()

    def on_window_toggle_bar(self, evt):
        self.toolbar_manager.toggle_bar(evt.GetId())
        
    def on_tree_end_label_edit(self, event):
        self.dying = False
        item = event.GetItem()
        res = self.tree.GetItemData(item)
        if res: res = res.GetData()
        newname = event.GetLabel()
        if not newname: return
        self.project.rename_class(res.name, newname)
        self.rename_tab(res, newname)
        if hasattr(res, "realname"): res.realname = get_full_name(res.parent.name, newname)
        res.name = newname
        self.update_treeitem(res)
        self.refresh_editor()

    def on_find(self, evt):
        if self.active_editor and self.active_editor.name == "akiki":
            self.active_editor.on_find(evt)

    def on_find_next(self, evt):
        if self.active_editor and self.active_editor.name == "akiki":
            self.active_editor.on_find_next(evt)
            
    def on_key_down(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            pass

    def populate_resource_menu(self, menu):
        propID = wx.NewId()
        menu.Append(propID, _("Delete"), _("Delete"))
        wx.EVT_MENU(menu, propID, self.on_delete)
        propID = wx.NewId()
        menu.Append(propID, _("Export"), _("Export"))
        wx.EVT_MENU(menu, propID, self.on_export)
        propID = wx.NewId()
        menu.Append(propID, _("Import"), _("Import"))
        wx.EVT_MENU(menu, propID, self.on_import_resource)

    def on_new_animation(self, event):
        name = choose_a_name(_("New_animation"))
        name = self.project.get_resource_name(name)
        if not name: return
        item = self.tree.GetSelection()
        if item:
            data = self.tree.GetItemData(item)
            anim = data.GetData()
            m = anim.get_class()
        else:
            anim = CAnimation()
            anim.name = name
            anim.filename = "noimage.png"
            m = anim
        m.add_class(name, ["Animation"],
            [ "filenames = []", \
              "nbframes = 0\n", \
              "virtual_frames = 0\n", \
              "def __init__(self):\n", \
              "    Animation.__init__(self)" ])

        anim.ast_has_changed = True
        anim.exec_listing()
        
        if not item:
            self.tree.add_tree_item(anim, self.tree.GetRootItem())
        else:
            anim = self.add_member_class(name,
                getattr(wx.GetApp().gns.getattr(anim.name), name), anim, item)
            data.GetData().add(anim)
        
    def on_new_script(self, event):
        name = choose_a_name("new_script")
        if not name: return
        script = CScript()
        script.name = self.project.get_resource_name(name)
        AddResource(script)
                
    def on_new_dialog(self, event):
        name = choose_a_name("new_dialog")
        if not name: return
        diag = CDialogue()
        diag.listing = "class " + name + "(Dialog): pass"
        diag.name = self.project.get_resource_name(name)
        AddResource(diag)
        
    def on_new_font(self, event):
        name = self.project.get_resource_name(_("New_font"))
        name = choose_a_name(_("New_font"))
        if not name: return
        artub = wx.GetApp().frame
        class_name = "Font"
        font = CGlumolFont(artub.project)
        font.name = name
        font.listing = "class " + name + "(" + class_name + "):\n"
        font.listing = font.listing + "    filename = ''\n"
        font.listing = font.listing + "    widths = []\n"
        font.listing = font.listing + "    def __init__(self):\n"
        font.listing = font.listing + "        " + class_name + ".__init__(self, self.letters, self.filename, self.widths)\n"
        AddResource(font)

    def get_resource_class(self, base_class):
        if issubclass(base_class, pypoujol.Animation):
            return (CAnimation, False)
        elif issubclass(base_class, pypoujol.Font):
            return (CGlumolFont, False)
        return (CGlumolObject, True)

    def get_virtual_resource_class(self, base_class):
        if issubclass(base_class, pypoujol.Animation):
            return (VirtualAnimation, False)
        elif issubclass(base_class, pypoujol.Font):
            return (CGlumolFont, False)
        return (VirtualGlumolObject, True)
    
    def on_new_class(self, class_name, name = '', parent = None, no_undo = False, auto = True):
        tree = self.tree
        base_classes = [wx.GetApp().gns.getattr(class_name)]
        base_class = base_classes[0]
        if not name:
            name = self.project.get_resource_name("New_" + class_name)
            name = choose_a_name(name)
            if not name: return
        if not parent:
            item = tree.GetSelection()
            if item: parent = tree.GetItemData(item).GetData()
            else: parent = tree.GetItemData(tree.GetRootItem()).GetData()
        if parent == self.project:
            klass, _auto = self.get_resource_class(base_class)
            res = klass(self.project)
            res.parent = parent
            mod = res
        else:
            klass, _auto = self.get_virtual_resource_class(base_class)
            res = klass()
            res.parent = parent
            res.parent.ast_has_changed = True
            mod = parent.get_class()
        name = self.project.get_resource_name(name)
        new_class_name = make_class_name(name)
        res.name = new_class_name
        parent_class = wx.GetApp().gns.getattr(res.parent.name, None)

        if auto and _auto and hasattr(parent_class, "__autos__"):
            parent_class.__autos__.append(
                (new_class_name,
                 get_full_name(res.parent.name) + '.' + new_class_name)) # Important

        code = get_class_code(base_class)
        self.Refresh()
        
        c = mod.add_class(new_class_name, base_classes = (class_name,), body = code)
        
        if auto:
            c.set_global_property("auto", `make_variable_name(name)`)

        for i in dir(base_class):
            i = getattr(base_class, i)
            if isclass(i) and (i.__name__ not in self.get_meta_classes()):
                c.add_class(i.__name__,
                            base_classes = map(lambda x: x.__name__, i.__bases__),
                            body = ["pass"])
        
        res.ast_has_changed = True
        res.topy()
        if not no_undo: AddResource(res, _("add ") + class_name, refresh_editor = True)
        return res
    
    def add_template(self, resource):
        self.templ_tree.add_template(resource)
        
    def on_import(self, evt):
        self.ovr.show_templates_page()
        
    def on_new_sprite(self, evt):
        name = choose_a_name()
        if not name: return
        sprite = CGlumolObject(self.project)
        base_class = "Sprite"
        sprite.name = self.project.get_resource_name(name)
        sprite.listing = "class %s(%s):\n" % (sprite.name, base_class)
        sprite.listing = sprite.listing + "    def __init__(self, parent):\n"
        sprite.listing = sprite.listing + "        %s.__init__(self, parent)\n" % base_class
        sprite.listing = sprite.listing + "        self.__glumolinit__()\n"
        sprite.listing = sprite.listing + "    def __glumolinit__(self):\n"
        sprite.listing = sprite.listing + "        self.current_anim = None\n\n"
        sprite.listing = sprite.listing + "        super(" + sprite.name + ", self).__glumolinit__()\n\n"
        self.tree.add_new_resource(sprite)
        
    def on_view_source_evt(self, event):
        wx.GetApp().frame.on_view_source(resource = self.resource)

    def on_delete(self, event):
        item = self.tree.GetSelection()
        if item == self.tree.GetRootItem(): return
        res = self.tree.GetItemData(item).GetData()
        class Delete(Action):
            def do(this):
                item = self.tree.GetSelection()
                res = self.tree.GetItemData(item).GetData()
                editor = self.get_editor_from_resource(res)
                while editor:
                    self.close_editor(editor)
                    editor = self.get_editor_from_resource(res)
                this.res = res
                if res.parent:
                    res.parent.remove(res)
                self.tree.Delete(item)
                
            def undo(this):
                self.set_resource_treeitem(this.res, this.res.parent.treeitem)
                this.res.parent.add(this.res)
                
        Delete(_("delete ") + res.name)
        
    def on_import_resource(self, event):
        from xmlmarshall.xmlmarshaller import unmarshal
        item = self.tree.GetSelection()
        res = self.tree.GetItemData(item).GetData()
        wildcard = _("Glumol resource") + "(*.glr)|*.glr|" + _("All files") + "(*.*)|*.*"
        dlg = wx.FileDialog(self, message=_("Import from ..."), defaultDir = os.getcwd(),
                            defaultFile = "", wildcard = wildcard, style = wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            newres = unmarshal(open(dlg.GetPaths()[0], 'r').read())
            res.add(newres)
            AddResource(newres)
        dlg.Destroy()

    def on_export(self, event):
        from xmlmarshall.xmlmarshaller import marshal
        item = self.tree.GetSelection()
        if item == self.tree.GetRootItem(): return
        res = self.tree.GetItemData(item).GetData()
        wildcard = _("Glumol resource") + "(*.glr)|*.glr|" + _("All files") + "(*.*)|*.*"
        dlg = wx.FileDialog(self, message=_("Export to ..."), defaultDir = os.getcwd(),
                            defaultFile = "", wildcard = wildcard, style = wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            open(dlg.GetPaths()[0], "w").write(marshal(res, prettyPrint=True))
        dlg.Destroy()
        
    """
    def OnScenesRightUp(self, event):
        menu = None
        item, flag = self.rooms.HitTest(event.GetPosition())
        if self.rooms.GetSelection() != item:
            self.rooms.SelectItem(item)
        if item:
            resource = self.rooms.GetItemData(item).GetData()
            editor = self.get_editor_from_resource(resource)
            if editor:
                menu = editor.get_popup_menu(resource)
        if menu:
            self.PopupMenu(menu, event.GetPosition())
        else:
            class DefaultMenu(wx.Menu):
                def __init__(self, tree):
                    wx.Menu.__init__(self)
                    propID = wx.NewId()
                    self.tree = tree
                    self.Append(propID, _("New scene"), _("New scene"))
                    #wx.EVT_MENU(self, propID, self.on_new_scene)

                def on_new_scene(self, evt):
                    pass

            menu = DefaultMenu(self.rooms)
        self.rooms.PopupMenu(menu, event.GetPosition())
        event.Skip()
    """
    
    def on_idle(self, event):
        if self.todos:
            todo = self.todos[0]
            del self.todos[0]
            
            try:
                if type(todo) == types.TupleType:
                    todo[0](*todo[1])
                else:
                    todo()
            except: raise
        schedule()

    def on_file_history(self, evt):
        filenum = evt.GetId() - wx.ID_FILE1
        path = self.filehistory.GetHistoryFile(filenum)
        self.open_project(path)
    
    def on_close_window(self, event):
        self.on_exit(event)
        
    def on_iconify(self, evt):
        evt.Skip()

    def on_maximize(self, evt):
        evt.Skip()
        
    def on_options(self, evt):
        options = OptionsWindow(self)
        options.ShowModal()
    
    def on_run(self, evt):
        self.sync()
        self.debugger.run()
        
    def on_check_for_updates(self, evt):
        try:
            path = os.getcwd()
            os.chdir(wx.GetApp().artub_path)
            oldstdout = sys.stdout
            class svn_output:
                def __init__(self):
                    self.buffer = ""
                    
                def write(self, txt):
                    self.buffer += txt
                    #oldstdout.write(txt)
                    
            out = svn_output()
            import tempfile
            tmpf = tempfile.mktemp()
            os.system("svn update > %s" % tmpf)
            update_output = open(tmpf, "r").read().split("\n")
            sys.stdout = out
            os.system("svn info >> %s" % tmpf)
            output = open(tmpf, "r").read().split("\n")
            os.remove(tmpf)
            sys.stdout = oldstdout
            version = int(output[5].split(':')[1])
            if len(update_output) == 2 and not update_output[1].strip():
                dlg = wx.MessageDialog(self, 
                    _('You are already running the lastest version (') + str(version) + ')',
                    _('No update available'),
                    wx.OK | wx.ICON_INFORMATION)

                dlg.ShowModal()
                dlg.Destroy()
            else:
                dlg = wx.MessageDialog(self,
                          _('Artub has been successfully updated to version ') + str(version),
                          _('Update successfull'),
                          wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
        except:
            sys.stdout = oldstdout
            os.chdir(path)
            raise
            
    def on_properties(self, evt):
        pp = ProjectProperties(self)
        pp.ShowModal()

    def on_help(self, evt):
        self.ovr.load_page(os.path.join("docs", "index.html"))
        self.ovr.show()

    def on_about(self, evt):
        from wx.lib.wordwrap import wordwrap
        info = wx.AboutDialogInfo()
        info.Name = _("Artub")
        info.Version = _("0.99")
        info.Copyright = _("(C) 2006 B&c International Software Inc.")
        info.Description = wordwrap(
            _("Artub is the Glumol's graphical interface " \
            "that allows you to easily create adventure games.\n\n" \
            "This software is released under the GNU licence v2, " \
            "see COPYING in the Glumol main folder."),
            350, wx.ClientDC(self))
        info.WebSite = ("http://www.glumol.com", _("The Glumol Homepage"))
        info.Developers = [ "Sylvain Baubeau",
                            "Alexis Contour" ]

        # Render looks terrible
        #info.License = wordwrap(open(os.path.join(wx.GetApp().artub_path, "COPYING")).read(),
        #                        350, wx.ClientDC(self))
        
        wx.AboutBox(info)
        
    def clear(self):
        self.tree.DeleteAllItems()
        # self.costs.DeleteAllItems()
        # self.rooms.DeleteAllItems()
        self.sounds.DeleteAllItems()
        self.close_all()
        
    def on_new(self, evt):
        if self.project and self.ask_save_changes(): return
        project = new_project(self)
        if project:
            self.filehistory.AddFileToHistory(project.filename)
            self.clear()
            self.project = project
            self.set_project(project)
            undo_manager.set_modified(True)

    def get_meta_classes(self):
        return self.metaclasses
        
    def open_project(self, filename):
        if self.project and self.ask_save_changes(): return
        self.dontselect = True
        self.project = load_project(filename)
        self.set_project(self.project)
        self.filehistory.AddFileToHistory(filename)
        self.ovr.update_recent_files()
        self.ovr.Refresh()
        
        for i in self.get_meta_classes():
            try: del global_dict[i]
            except: pass
            
        if self.nb.GetPageCount() > 1: self.nb.SetSelection(1)

    def on_open(self, evt):
        wildcard = _("Glumol project") + "(*.glu)|*.glu|" + _("All files") + "(*.*)|*.*"

        dlg = wx.FileDialog(self, message=_("Choose a file"), defaultDir=os.getcwd(), defaultFile="", wildcard=wildcard, style=wx.OPEN)
                           
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            self.open_project(paths[0])
        
        dlg.Destroy()
        
    def sync(self):
        if self.active_editor: self.active_editor.update(True)
           
    def on_save(self, evt):
        self.sync()
        if self.project.filename:
            self.project.save()
            undo_manager.reset()
        else:
            self.on_saveas(evt)
        
    def on_saveas(self, evt):
        wildcard = _("Glumol project") + " (*.glu)|*.glu|" + _("All files") + "(*.*)|*.*"

        dlg = wx.FileDialog(self, _("Save file as..."), os.getcwd(), "", wildcard, wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            self.project.filename = str(dlg.GetPath())
            self.on_save(evt)
        
        dlg.Destroy()
        
    def ask_save_changes(self):
        if undo_manager.is_modified():
            dlg = wx.MessageDialog(self, _('Some changes has been made. Would you like to save your projet ?'),
                                   _('Save project ?'),
                                   wx.YES_NO | wx.CANCEL | wx.ICON_INFORMATION)
            code = dlg.ShowModal()
            if code == wx.ID_CANCEL:
                return 1
            elif code == wx.ID_YES:
                self.on_save(None)
            dlg.Destroy()

    def on_exit(self, evt):
        if self.ask_save_changes(): return
        self.debugger.kill()
        self.toolbar_manager.care_of_exit()
        self.filehistory.Save(self.config)
        
        self.dying = True
        self.mainmenu = None
        self.quitte = True
        wx.GetApp().ExitMainLoop()
        self.Destroy()
        self._mgr.UnInit()

    def on_debug_run(self, evt):
        self.sync()
        self.debugger.run()

class ArtubApp(wx.App):
    def __init__(self):
        self.config = config.config
        self.artub_path = os.path.dirname(os.path.abspath(__file__))
        from glumolnamespace import GlumolNamespace
        self.gns = GlumolNamespace()
        wx.App.__init__(self, False)

    def ExitMainLoop(self):
        self.mainloop_running = False

    def OnInit(self):
        ArtubFrame(None, -1, _("Artub"), self.config)
        return True

    def MainLoop(self):
        evtloop = wx.EventLoop()
        old = wx.EventLoop.GetActive()
        wx.EventLoop.SetActive(evtloop)
        self.mainloop_running = True
        while self.mainloop_running:
            schedule()

            while evtloop.Pending():
                evtloop.Dispatch()

            self.ProcessIdle()
            time.sleep(0.01)

        wx.EventLoop.SetActive(old)

def main():
    app = ArtubApp()
    app.MainLoop()

main()
#task = tasklet(main)()
#task.insert()
#run()
