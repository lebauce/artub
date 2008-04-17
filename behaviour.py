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

behaviours = []
import pypoujol
from script import is_derived_from

class BehaviourFoo(object):
    pass
    
class BehaviourMetaClass(pypoujol.SceneMetaClass, pypoujol.AnimationMetaClass, pypoujol.GameMetaClass):
    def __init__(self, name, bases, dict):
        append = True
        for i in bases:
            if not is_derived_from(i, BehaviourFoo):
                append = False
                break
        if bases[0].__bases__[0] != BehaviourFoo:
            append = False
        if append:
            behaviours.append(name)
        super(type, self).__init__(name, bases, dict)

class Behaviour(BehaviourFoo):
    __metaclass__ = BehaviourMetaClass
    
    def __init__(self):
        pass

class Blinking(Behaviour):
    apply_on = "Scene"
    
    def __init__(self):
        self.blinking = True
