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

import wx
from undoredo import Action
from inspect import isclass
import pypoujol
from script import get_full_name

class PropertiesBarChangeValue(Action):
    def __init__(self, resource, obj, name, value, to_str = repr, update_now = True,
                 update_later = True, multiple = False, do_anyway = False, method = None):
        if (not do_anyway) and getattr(obj, name) == value:
            return
        self.update_now = update_now
        self.update_later = update_later
        self.resource, self.obj, self.propname, self.newvalue, self.to_str = resource, obj, name, value, to_str
        self.editor = wx.GetApp().artub_frame.active_editor
        self.multiple = multiple
        self.method = method
        Action.__init__(self, _("change ") + name)
        
    def do(self):
        self.resource.sync()
        if self.multiple:
            self.value = []
            for name2, value2 in self.newvalue:
                self.value.append((name2, getattr(self.obj, name2, value2)))
        else:
            self.value = getattr(self.obj, self.propname, self.newvalue)
        if self.propname.startswith("on_"):
            return
        self.change(self.obj, self.propname, self.newvalue)

    def change_property(self, obj, name, value):
        setattr(obj, name, value)
        keywords = {}
        if not self.method and hasattr(obj.__class__, name) and type(getattr(obj.__class__, name)) != property:
            change_property = self.resource.change_global_property
        else:
            change_property = self.resource.change_property
            if self.method: keywords["method"] = self.method
        if isinstance(value, pypoujol.Animation):
            change_property(name, get_full_name(value.__class__.__name__) + '()', class_name = obj.__class__.__name__, **keywords)
        elif isclass(value):
            if value == type(None):
                change_property(name, 'None', class_name = obj.__class__.__name__, **keywords)
            else:
                change_property(name, get_full_name(value.__name__), class_name = obj.__class__.__name__, **keywords)
        else:
            if type(value) == type('') or type(value) == type(u''):
                change_property(name, self.to_str(value), class_name = obj.__class__.__name__, **keywords)
            else:
                change_property(name, self.to_str(value), class_name = obj.__class__.__name__, **keywords)

    def change(self, obj, name, value):
        if self.multiple:
            for name2, value2 in value:
                self.change_property(obj, name2, value2)
        else:
            self.change_property(obj, name, value)
        active_editor = wx.GetApp().artub_frame.active_editor
        if self.editor is active_editor:
            if not self.first and self.update_later and active_editor.artub.pb.active_resource == self.resource:
                active_editor.artub.pb.reload()
                wx.GetApp().artub_frame.todos.append((active_editor.update, (False,)))
            else:
                if self.update_now:
                    wx.GetApp().artub_frame.todos.append((active_editor.update, (False,)))
                    wx.GetApp().artub_frame.todos.append(active_editor.artub.pb.reload)
            
    def undo(self):
        self.change(self.obj, self.propname, self.value)
