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
from propertiesbar.companions import *
import pypoujol

class BasicSpeculoosCompanion(Companion):
    def __init__(self, resource, obj):
        Companion.__init__(self, obj, resource)
        self.classe = resource.get_class()
        self.ignore.update(["fade_delay", "fade_time", "fading", "set_to_zero",
                            "parent", "delta", "children"])
        self.add_variables([ ["alpha", Companion.float_constraints],
                             ["angle", [3, 1, True, -360.0, 360.0, True, False] ],
                             ["color", ColorCompanion(obj, pypoujol.Scene)],
                             ["current_anim", AnimationCompanion()],
                             "playing", "x", "y", "z",
                             ["scale", [3, 1, True, -360.0, 360.0, True, False] ],
                             "size", "visible" ]) # "position", "color" ]
        self.functions = [ "on_before_draw" ]

    def change_value(self, name, value):
        if isinstance(getattr(self.obj, name), pypoujol.Animation):
            parent_class = pypoujol.get_parent_class(value.__class__)
            if value: self.obj.size = value.size
            wx.GetApp().artub_frame.active_editor.select_sprite(self.obj)
            PropertiesBarChangeValue(self.resource, self.obj, name, value,
                                     lambda v: pypoujol.get_parent_class(value.__class__) + '()',
                                     update_now = False, update_later = False)
        else:
            PropertiesBarChangeValue(self.resource, self.obj, name, value,
                                     update_now = False, update_later = True)

class SpeculoosCompanion(BasicSpeculoosCompanion): pass

class LightZoneCompanion(Companion):
    def __init__(self, resource, bxsystem, obj):
        Companion.__init__(self, obj, resource)
        self.classe = resource.get_class()
        self.ignore = []
        self.add_variables([ "active", ["color", ColorCompanion(obj, pypoujol.Scene)] ])
        self.bxsystem = bxsystem
        
    def change_value(self, name, value):
        PropertiesBarChangeValue(self.resource, self.obj, name, value,
                                 update_now = False, update_later = True)

class ObjectCompanion(Companion):
    def __init__(self, resource, bxsystem, obj):
        Companion.__init__(self, obj, resource)
        self.classe = resource.get_class()
        self.bxsystem = bxsystem
        self.ignore = ["fade_delay", "fade_time", "fading", "set_to_zero",
                       "parent", "delta", "children"]
        self.add_variables([ "active", 
                             ["alpha", Companion.float_constraints],
                             ["angle", [3, 1, True, -360.0, 360.0, True, False] ],
                             ["color", ColorCompanion(obj, pypoujol.Scene)],
                             ["current_anim", AnimationCompanion()],
                             "playing", "x", "y", "z",
                             ["scale", [3, 1, True, -360.0, 360.0, True, False] ],
                             "size", "visible" ]) # "position", "color" ]
        self.functions = [ "on_before_draw" ]
        
    def change_value(self, name, value):
        if isinstance(getattr(self.obj, name), pypoujol.Animation) or name == "current_anim":
            PropertiesBarChangeValue(self.resource, self.obj, name, value,
                                     update_now = False, update_later = True)
        elif name in ["x", "y"]:
            setattr(self.obj, name, value)
            PropertiesBarChangeValue(self.resource, self.obj, "position", self.obj.position,
                                     update_now = False, update_later = True)
        else:
            PropertiesBarChangeValue(self.resource, self.obj, name, value,
                                     update_now = False, update_later = True)

class ChangeSceneCompanion(Companion):
    def __init__(self, resource, bxsystem, obj):
        Companion.__init__(self, obj, resource)
        self.classe = resource.get_class()
        self.ignore = []
        self.add_variables([ "active",
                           ["to_scene", ResourceCompanion(obj, pypoujol.Scene)],
                           ["entry_point", ResourceCompanion(obj, wx.GetApp().gns.getattr("EntryPoint"), context = "to_scene")],
                           ["cursor_direction", EnumCompanion(pypoujol.direction)]
                           ])
        self.bxsystem = bxsystem
        
    def change_value(self, name, value):
        PropertiesBarChangeValue(self.resource, self.obj, name, value,
                                 update_now = False, update_later = True)
        
class WalkZoneCompanion(Companion):
    def __init__(self, resource, bxsystem, obj):
        Companion.__init__(self, obj, resource)
        self.classe = resource.get_class()
        self.ignore = []
        self.add_variables([ "active" ])
        self.bxsystem = bxsystem
        
    def change_value(self, name, value):
        PropertiesBarChangeValue(self.resource, self.obj, name, value,
                                 update_now = False, update_later = True)

class ScaleZoneCompanion(Companion):
    def __init__(self, resource, bxsystem, obj):
        Companion.__init__(self, obj, resource)
        self.classe = resource.get_class()
        self.ignore = []
        self.add_variables([ "active" ])
        self.bxsystem = bxsystem
        
    def change_value(self, name, value):
        PropertiesBarChangeValue(self.resource, self.obj, name, value,
                                 update_now = False, update_later = True)
