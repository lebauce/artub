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

from resourceeditor import AutoTemplate
from glumolobject import CGlumolObject
from os.path import join

class InventoryTemplate(AutoTemplate):
    name = "An inventory"
    description = "A basic inventory"
    section = "Inventories"
    template = False
    resource_name = "Inventory"
    data = [ join('plugins', 'basic_templates', 'fleche.tga'),
             join('plugins', 'basic_templates', 'fleche2.tga'),
             join('plugins', 'basic_templates', 'inventory.png') ]
    
    listing = """class Inventory(Sprite):
    class InventoryBitmap(Animation):
        filenames = ['inventory.png'] 
        nbframes = 1 
        virtual_frames = 1
        
    class ArrowUp(Sprite):
        class ArrowUpAnim(Animation):
            filenames = ['fleche.tga']
            nbframes = 2
            virtual_frames = 2
        animation = ArrowUpAnim
        
    class ArrowDown(Sprite):
        class ArrowDownAnim(Animation):
            filenames = ['fleche2.tga']
            nbframes = 2
            virtual_frames = 2
        animation = ArrowDownAnim
        
    def __init__(self, parent):
        Sprite.__init__(self, parent)
        self.__glumolinit__()
        
    def __glumolinit__(self):
        self.arrow_down = Inventory.ArrowDown(self)
        self.arrow_up = Inventory.ArrowUp(self)
        self.current_anim = Inventory.InventoryBitmap() 
        self.angle = 0
        self.line = 0
        self.width = 683
        self.height = 483
        self.nb_lines = 3
        self.items_by_line = 5
        self.item_width = 70
        self.item_height = 70
        self.vertical_space = 10
        self.horizontal_space = 10
        self.offset_x = 96
        self.offset_y = 180
        self.objects = []
        self.selection = None
        self.current_page = 0
        self.x = 20

    def on_lose_focus(self, newobj):
        self.fade_out(1)

    def on_left_button_down(self):
        game.input.mouse_sprite = None
        self.selection = None
        
    def add_object(self, obj):
        item = InventoryItem(self, obj)
        self.objects.append(item)
        self.sort_objects(len(self.objects) - 1)
        item.visible = True
        r = item.size.cx
        item.scale = max(self.item_width, self.item_height) / max(item.size.cx, item.size.cy)
      
    def remove_object(self, obj):
        item = self.get_item_from_object(obj)
        if item:
            self.objects.remove(item[0])
            self.sort_objects(item[1])
         
    def show_next_page(self):
        self.current_page = self.current_page + 1
        self.sort_objects(self.current_page * self.nb_lines * self.items_by_line)
        
    def show_prev_page(self):
        self.current_page = self.current_page - 1
        if self.current_page < 0:
            self.current_page = 0
        self.sort_objects(self.current_page * self.nb_lines * self.items_by_line)
        
    def sort_objects(self, ifrom):
        slice = self.objects[ifrom:]
        IFrom = ifrom
        maxitems = self.nb_lines * self.items_by_line
        for obj in slice:
            if ifrom >= maxitems:
                break
            pos = self.get_item_position(ifrom)
            obj.position = Point(pos[0], pos[1])
            obj.index = ifrom
            obj.visible = True
            ifrom = ifrom + 1
        slice = self.objects[ifrom:]
        for i in slice:
            i.visible = False

    def get_item_line(self, i):
        return i / self.items_by_line
 
    def get_item_position(self, i):
        return [(i % self.items_by_line) * (self.item_width + self.horizontal_space) + self.offset_x, (i / self.items_by_line) * (self.item_height + self.vertical_space) + self.offset_y]
         
    def get_item_from_object(self, obj):
        index = 0
        for i in self.objects:
            if i.obj == obj:
                return (i, index)
            index = index + 1
        return None

    def care_of_up_and_down(self):
        if self.line > 0:
            self.uparrow.visible = True
        else:
            self.uparrow.visible = False
        if self.get_item_line(len(self.objects)) > self.line + self.nb_lines:
            self.downarrow.visible = True
        else:
            self.downarrow.visible = False
"""
