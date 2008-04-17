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

from propertiesbar.companions import Companion
from resourceeditor import CResourceEditor
from sound import CSound
import wx
from depplatform import get_image_path

[wxID_WXPANEL1] = map(lambda _init_ctrls: wx.NewId(), range(1))

class VeneficusCompanion(Companion):
    def __init__(self, resource, obj):
        Companion.__init__(self, obj, resource)
        self.resource = resource
        self.obj = obj
        self.variables = ["filename"]
        
    def change_value(self, script, name, value):
        setattr(self.obj, name, value)
        self.resource.change_property(name, "'" + str(value) + "'", class_name = self.obj.__class__.__name__)
        
class VeneficusOptions(wx.Panel):
    def _init_ctrls(self, prnt):
        wx.Panel.__init__(self, style=wx.TAB_TRAVERSAL, name='', parent=prnt, pos=wx.DefaultPosition, id=wxID_WXPANEL1, size=wx.Size(200, 100))

    def __init__(self, parent, id):
        self._init_ctrls(parent)
        
class Veneficus(CResourceEditor):
    known_resources = [ CSound ]
    options = ( VeneficusOptions, "Veneficus" )
    name = "veneficus"

    def __init__(self):
        CResourceEditor.__init__(self)
    
    def create_window(self, resource, parent_window):
        self.wnd = wx.Panel(parent_window, -1)
        return (self.wnd, resource.name)
        
    def update(self, save=True):
        if save:
            pass
        else:
            obj = wx.GetApp().gns.create_from_script(self.active_resource, tuple())
            self.artub.pb.set_inspector(VeneficusCompanion(self.active_resource, obj))
            
    def close_window(self):
        self.parent.remove_page(self.wnd)
    
    def get_popup_menu(self, resource):
        class VeneficusContextMenu(wx.Menu):
            def __init__(self2):
                wx.Menu.__init__(self2)
                
                propID = wx.NewId()
                self2.resource = resource
                self2.Append(propID, _("Play"), _("Play"))
                wx.EVT_MENU(self2, propID, self.on_play)
                
                propID = wx.NewId()
                self2.resource = resource
                self2.Append(propID, _("View source"), _("View source"))
                wx.EVT_MENU(self2, propID, self.on_view_source)
                    
        return VeneficusContextMenu()
                    
    def on_play(self, event):
        pass
        
    def on_view_source(self, event):
        self.artub.on_view_source(event, self.active_resource)
        
editor = Veneficus
