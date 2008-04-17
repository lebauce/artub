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

from resourceeditor import Template
from glumolobject import CGlumolObject

class InventoryTemplate(Template):
    name = "An inventory"
    description = "An basic inventory"
    section = "Inventories"

    def do(self, evt):
        project = self.artub.project
        resource = CGlumolObject(project)
        resource.template = True
        resource.name = "Inventory"
        resource.listing = """class Inventory(Sprite):
    class InventoryBitmap(Animation):
        filenames = ['inventory.png'] 
        nbframes = 1 
        virtual_frames = 1 
        def __init__(self):
            Animation.__init__(self)
            
        def __glumolinit__(self):
            pass 
            self.delays[:] = [1] 
            self.orders[:] = [0] 
            self.hotspots[:] = [Point(0, 0)] 
            self.move_offsets[:] = [Point(0, 0)] 
            
        
    def __init__(self, parent):
        Sprite.__init__(self, parent)
        self.__glumolinit__()
        
    def __glumolinit__(self):
        self.current_anim = Inventory.InventoryBitmap() 
        self.current_order = 0 
        self.z = 100 
        self.alpha = 0.0 
        self.angle = 0.0 
        
    def on_lose_focus(self, newobj):
        self.fade_out(1)

"""

        project.add_template(self.name)
        self.artub.add_template(resource)
