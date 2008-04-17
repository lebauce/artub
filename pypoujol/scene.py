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

from sprite import Sprite, SpriteMetaClass
from animation import global_dict

scene_dict = []

class SceneMetaClass(SpriteMetaClass):
    def __init__(self, name, bases, dict):
        super(SpriteMetaClass, self).__init__(name, bases, dict)
        scene_dict.append(name)
        for i in dict.keys():
            if isinstance(dict[i], type) and name != self.__class__.__name__:
                global_dict[dict[i].__name__] = name
        
class Plane(Sprite): pass

class Scene(Sprite):
    __metaclass__ = SceneMetaClass
    
    def __init__(self, parent):
        Sprite.__init__(self, parent)
        self.walk_zones = []
        
    def add_region(self, reg): pass
        
    def on_enter(self, entrypoint = None):
        pass
    
    def on_first_enter(self):
        pass
     

