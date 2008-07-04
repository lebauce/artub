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

from glumolobject import CGlumolObject
from project import CProject
from log import log
import os, os.path
import sys
import wx
from script import is_derived_from, get_full_name
import types
import new
from undoredo import Action

failed_loading_module_critical = 0

PLUGINS_DIR = "plugins"

class CPlugin:
    def __init__(self):
        pass

    def get_infos(self):
        pass

class CRedistributablePlugin:
    dist_platform = ""
    
    def on_build(self, event):
        self.build(wx.GetApp().artub_frame.project)
        
    def __init__(self):
        pass

    def get_infos(self):
        pass

class CResourceEditor(CPlugin):
    # options = ( None, "None" )
    # name = "unamed editor"
        
    def __init__(self):
        CPlugin.__init__(self)
        self.active_resource = None
        self.editing_resources = []
        self.known_resources = []
        self.loc = {}

    def set_project(self, project):
        pass

    def create_window(self, resource, parent_window):
        pass

    def activate(self):
        pass

    def unactivate(self):
        pass

    def update(self, save=True):
        pass

    def edit_resource(self, resource):
        pass
        
    def get_popup_menu(self, resource):
        pass
    
    def is_editing(self, resource):
        return self.active_resource is resource
        
    def close(self):
        pass


class Template(CPlugin):
    def check_class(self, name):
        return wx.GetApp().gns.getattr(name)
    
    def get_companions(self):
        return {}

    def check_classes(self, classes):
        for i in classes:
            try:
                self.check_class(i)
            except:
                dlg = wx.MessageDialog(None,
                                       _("You need to import a template of type ") + i,
                                       _("Failed to import"),
                                       wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return -1
    
class AutoTemplate(Template):
    needed_classes = []
    listing = ""
    def do(self, evt, name=""):
        project = self.artub.project
        resource = CGlumolObject(project)
        resource.template = True
        if not name: name = self.resource_name
        resource.name = name
        if self.needed_classes and self.check_classes(self.needed_classes):
            return
        resource.listing = self.listing
        project.add_template(self.name)
        self.artub.add_template(resource)
        return resource
        
class CEditorManager:
    def __init__(self):
        self.plugins = []
        self.editors = []
        self.templates = {}
        self.alive_editors = []
        self.active_editor = None

    def load_plugins(self):
        path = sys.path
        plugins_dir = os.path.join(wx.GetApp().artub_path, PLUGINS_DIR)
        sys.path.append(plugins_dir)
        files = os.listdir(plugins_dir)
        for f in files:
           if f.find('.') != -1: continue
           inf = os.path.splitext(f)
           if inf[1] in [".py", ".pyc"]:
               modul = inf[0]
               code = "import %s" % inf[0]
           else:
               modul = f
               code = "import %s" % f
           try:
               log("importing", modul)
               exec code
           except:
               raise
               if failed_loading_module_critical:
                   raise
               else:
                   log("failed loading", modul, "module")
                   log(sys.exc_info()[2])
           try:
               code = "%s.editor" % modul
               editor = eval(code, globals(), locals())
               editor.artub = self
               self.editors.append(editor)
           except AttributeError:
               try:
                   code = "%s.plugin" % modul
                   plugin = eval(code)()
                   plugin.artub = self
                   plugin.path = os.path.join(wx.GetApp().artub_path, PLUGINS_DIR, modul)
                   self.plugins.append(plugin)
               except:
                   code = "%s.templates" % modul
                   templates = eval(code)
                   for i in templates:
                       i.artub = self
                       i.path = os.path.join(wx.GetApp().artub_path, PLUGINS_DIR, modul)
                       sections = i.section.split('/')
                       section = self.templates
                       for j in sections:
                           if section.has_key(j):
                               section = section[j]
                           else:
                               section[j] = section = {}
                       section[i.name] = i()
        sys.path = path
    
    def dump(self):
        print "Loaded modules :"
        for i in self.editors:
            print "Module", editor.name
            
    def close_all(self):
        count = self.nb.GetPageCount()
        while count > 1:
            self.nb.DeletePage(1)
            count = count - 1
        for i in self.alive_editors:
            i.close()
        self.alive_editors = []
        self.active_editor = None
        
    def get_resource_editor(self, resource):
        for editor in self.editors:
            for i in editor.known_resources:
                if resource.__class__ == i:
                    return editor
        log("Warning : no editor for resource", resource, isinstance(resource, CProject), str(resource.type), i.__name__)
        return None

    def rename_tab(self, res, newname):
        for i in self.alive_editors:
            if i.active_resource is res:
                if i.name == "akiki": newname += ' (code)'
                self.nb.SetPageText(self.get_page(i.window), newname)

    def refresh_editor(self):
        if self.active_editor:
            self.active_editor.update(True)
            self.active_editor.update(False)
            
    def get_editor(self, name):
        for editor in self.editors:
            if editor.name == name:
                return editor
        return None

    def unactivate_editor(self, editor):
        self.pb.set_inspector(None)
        if editor.unactivate() or editor.update():
            return -1
        self.active_editor = None

    def activate_editor(self, editor, change_page = True):
        activepage = self.get_page(editor.window)
        self.active_editor = editor
        editor.update(False)
        if change_page:
            self.nb.dont_select = True
            self.nb.SetSelection(activepage)
            self.nb.dont_select = False
        return activepage
            
    def view_as_script(self, resource):
        for i in self.editors:
            if i.name == "akiki":
                self.dontselect =  True
                n = self.edit_resource(resource, i)
                self.nb.SetSelection(n)
        
    def edit_resource(self, resource, editor_class = None, change_page = True):
        #if isinstance(resource, VirtualGlumolResource):
        #    resource = resource.parent
        #    while isinstance(resource, VirtualGlumolResource):
        #        resource = resource.parent

        if not editor_class:
            editor_class = self.get_resource_editor(resource)

        if self.active_editor and (self.active_editor.active_resource != resource or \
                                   self.active_editor.__class__ != editor_class):
            if self.unactivate_editor(self.active_editor):
                return -1
        
        if not editor_class: # Toujours pas ?
            self.pb.clear()
            return -1

        fullname = get_full_name(resource.name)
        for i in self.alive_editors:
            if (i.is_editing(resource) and isinstance(i, editor_class)) or \
               (hasattr(self, "realname")  and (get_full_name(i.active_resource.name) == fullname)):
                return self.activate_editor(i, change_page)
                
        editor = editor_class()
        editor.editor_class = editor_class
        editor.active_resource = resource
        self.alive_editors.append(editor)
        try:
            rets = editor.create_window(resource, self.nb)
            editor.window = rets[0]
            self.nb.AddPage(rets[0], rets[1], False)
            # self.nb.dont_select = True
            if not editor:
                dsflkjfds
            self.active_editor = editor
            editor.update(False)
            self.nb.SetSelection(self.nb.GetPageCount() - 1)
            return self.nb.GetPageCount() - 1
        except: 
            log("Cannot create window for resource", resource)
            raise

    def close_editor(self, editor, close_page = True):
        self.alive_editors.remove(editor)
        editor.unactivate()
        editor.close()
        self.active_editor = None
        if close_page:
            self.nb.DeletePage(self.get_page(editor.wnd))
    
    def remove_page(self, window):
        page = self.get_page(window)
        if page != -1:
            self.nb.DeletePage(page)

    def get_page(self, window):
        i = 0
        count = self.nb.GetPageCount()
        while i < count:
           if self.nb.GetPage(i) == window:
              return i
           i = i + 1
        return -1
        
    def get_editor_from_page(self, page):
        wnd = self.nb.GetPage(page)
        for i in self.alive_editors:
            if i.wnd == wnd:
                return i 

    def get_editor_from_resource(self, resource):
        for i in self.alive_editors:
            if i.active_resource == resource:
                return i 
        return None

    def get_templates_menu(self, section="", callback = None, prefix = "", suffix = "", parent_menu = None, id = 10000):
        sections = section
        already_added = set()
        gns = wx.GetApp().gns
        class MyMenu(wx.Menu):
            def on_select_template(self2, event):
                if callback:
                    if suffix:
                        callback(self2.GetLabel(event.GetId())[len(prefix):-len(suffix)])
                    else:
                        callback(self2.GetLabel(event.GetId())[len(prefix):])
        menu = MyMenu()
        menu.prefix = prefix
        menu.suffix = suffix
        n = 0
        l2 = []
        if type(sections) is str: sections = [sections]
        for section in sections:
            obj = gns.getattr(section, None)
            self.callback = callback
            l = []
            
            def aux(resource):
                name = resource.name
                obj2 = gns.getattr(name)
                if name in already_added: return
                if obj:
                    if obj != obj2 and is_derived_from(obj2, obj):
                        l.append(prefix + name + suffix)
                        already_added.add(name)
                else:
                    l.append(prefix + name + suffix)
                    already_added.add(name)

            def is_template(resource): return resource.template
            self.project.filter_apply(aux, is_template)
        
            l2.insert(n, prefix + section + suffix)
            n += 1
        
        l.sort()
        
        if len(l): l.insert(0, '')
        
        if not parent_menu: parent_menu = menu
            
        _id = id
        for i in l2 + l:
            if i: menu.Append(id, i)
            else: menu.AppendSeparator()
            id += 1
            wx.NewId()

        parent_menu.Bind(wx.EVT_MENU_RANGE, menu.on_select_template, None, _id, id)
        return menu
        
    def for_each_template(self, templates, do):
        for k, i in templates.items():
            if type(i) == type({}):
                self.for_each_template(i, do)
            else:
                do(i)

    def get_template_list(self):
        l = []
        def for_each_template(templates, l):
            for k, i in templates.items():
                if type(i) == type({}):
                    for_each_template(i, l)
                else:
                    l.append((k, i))
        for_each_template(self.templates, l)
        return l
        
    def show_templates(self):
        pass

class AddResource(Action):
    def __init__(self, resource, text = None, refresh_editor = False):
        if not text: text = _("add ") + resource.name
        self.resource = resource
        self.refresh_editor = refresh_editor
        Action.__init__(self, text)
    
    def do(this):
        artub = wx.GetApp().frame
        item = artub.tree.GetSelection()
        if item: data = artub.tree.GetItemData(item)
        else: data = artub.tree.GetItemData(artub.tree.GetRootItem())
        this.resource.parent = data.GetData()
        this.resource.exec_listing()
        artub.set_resource_treeitem(this.resource, this.resource.parent.treeitem)
        if this.refresh_editor:
            artub.refresh_editor()

    def undo(this):
        artub = wx.GetApp().frame
        artub.project.remove(this.resource)
        artub.tree.Delete(this.resource.treeitem)
        try: artub.close_editor(artub.get_editor_from_resource(this.resource))
        except: pass
