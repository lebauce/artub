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

import types
import new
from propertiesbar_actions import PropertiesBarChangeValue
import pypoujol

class Companion(object):
    float_constraints = [1, 2, False, 0.0, 1.0, True, False]
    ext_companions = {}
        
    def __init__(self, obj = None, resource = None):
        self.obj = obj
        self.ignore = set()
        self.variables = []
        self.resource = resource
        ignore_types = set()
        ignore_types.add(types.FunctionType)
        ignore_types.add(types.ClassType)
        ignore_types.add(new.instancemethod)
        self.ignore_types = ignore_types
        if obj: self.variables = self.get_variables(obj)

    def get_variables(self, obj):
        ignore_types = self.ignore_types
        vars = []
        descr = self.get_descriptor(obj)
        ignore = set()
        cpy = Companion.ext_companions
        Companion.ext_companions = { }
        if descr:
            for i in descr:
                def get_variables(self, obj): return self.variables
                i.get_variables = get_variables
                comp = i(obj)
                vars.extend(comp.variables)
                for v in comp.variables: ignore.add(v[0])
        Companion.ext_companions = cpy
        for i in dir(obj):
            if type(getattr(obj, i)) in ignore_types or i in ignore: continue
            vars.append(i)
        return vars        
        
    def get_descriptor(self, obj):
        for i in self.ext_companions.values():
            if isinstance(obj, i[0]):
                return [i[1]]
        
    def change_value(self, name, value):
        setattr(self.obj, name, value)

    def add_variables(self, l):
        def find(i, v):
            n = 0
            for j in v:
                if type(j) == types.StringType and i == j: return n
                elif i == j[0]: return n
                n = n + 1
            return -1
        for i in l:
            ind = -1
            z = None
            if type(i) == tuple:  # Only insert lists so that we can call sort
                ind = find(i[0], self.variables)
                z = list(i)
            elif type(i) != list:
                ind = find(i, self.variables)
                z = [i, None]
            else:
                ind = find(i[0], self.variables)
                z = i
            if ind == -1:
                self.variables.append(z)
            else:
                self.variables[ind] = z
        
        self.variables.sort()

class ResourceCompanion(Companion):
    def __init__(self, obj, classe, context = None, as_string = False):
        Companion.__init__(self, obj)
        self.classe = classe
        self.context = context
        self.as_string = as_string

class AdvancedCompanion(Companion):
    def change_value(self, name, value):
        PropertiesBarChangeValue(self.resource, self.obj, name, value, update_now = False)

class ColorCompanion(Companion):
    def __init__(self, obj, classe):
        Companion.__init__(self, obj)
        self.classe = classe
                
class AnimationCompanion(Companion): pass
class EnumCompanion(Companion): pass
class PointCompanion(Companion): pass
class FilenameCompanion(Companion): pass
class FontCompanion(Companion): pass

# Companion.ext_companions["Sprite"] = (pypoujol.Sprite, ["music_path", FilenameCompanion()])
