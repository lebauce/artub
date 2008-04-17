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
from resourceeditor import AutoTemplate, Template
from glumolobject import CGlumolObject

class SeparateHeadTemplate(AutoTemplate):
    name = "Separate head"
    description = "The head of a character whose head is an other sprite."
    section = "Characters/Behaviours"
    resource_name = "SeparateHead"
    listing = """class SeparateHead(Behaviour):
    class HeadTalkSouthWest(Animation): pass
    class HeadTalkNorthWest(Animation): pass
    class HeadTalkNorth(Animation): pass
    class HeadTalkEast(Animation): pass
    class HeadTalkNorthEast(Animation): pass
    class HeadTalkSouth(Animation): pass
    class HeadTalkSouthEast(Animation): pass
    class HeadAnim(Animation): pass

    def __init__(self, parent):
        self.head_anim = Guybrush.HeadAnim() 
        self.talk_anim = [self.HeadTalkEast(),self.HeadTalkNorthEast(),self.HeadTalkNorth(),self.HeadTalkNorthWest(),self.HeadTalkSouthWest(),self.HeadTalkSouthWest(),self.HeadTalkSouth(),self.HeadTalkSouthEast()] 
        self.current_anim = self.head_anim 
        self.z = (parent.z - 1) 
        self.head_positions = [(44,2),(31,2),(41,3),(37,2),(31,2),(31,2),(40,3),(43,2)] 
"""


class BasicCharacter(AutoTemplate):
    name = "Basic character"
    description = "A character that can't do anything."
    section = "Characters"
    resource_name = "BasicCharacter"
    listing = """class BasicCharacter(Sprite):
    name = 'Roger'
    
    def add_task(self, task, args, callback=None):
        l = len(self.threads) 
        self.threads.append((task,args))
        if not hasattr(self, "mainthread"):
            self.mainthread = tasklet(self.main_thread)() 
            
    def get_move_offset(self, x, y):
        if self.position.x == x and self.position.y == y: return
        dist = ((x - self.position.x) * (x - self.position.x) + (y - self.position.y) * (y - self.position.y)) 
        dist = math.sqrt(dist) 
        self.destination = (x,y) 
        self.move_x = (x - self.position.x) / dist 
        self.move_y = (y - self.position.y) / dist 
        self.inc_x = self.move_x * 10 
        self.inc_y = self.move_y * 10 
        if abs(self.move_x) > abs(self.move_y):
            self.coeff = (y - self.position.y) / abs((x - self.position.x)) 
            self.step = x 
            if self.move_x < 0:
                self.direction = -1 
                
            else:
                self.direction = 1 
                
            
        else:
            self.coeff = (x - self.position.x) / abs((y - self.position.y)) 
            self.step = y 
            if self.move_y < 0:
                self.direction = -1 
                
            else:
                self.direction = 1 

    def main_thread(self):
        while not self.quit:
            while not self.threads and not self.quit: schedule()
            self.terminated = False 
            terminated = False 
            (task,args,) = self.threads.pop(0) 
            def aux():
                task(*args)
                self.terminated = True 
                
            task2 = tasklet(aux) 
            task2.setup()
            while  not self.terminated:
                schedule()
                
            schedule()

    def play_cost(self, cost):
        self.current_anim = cost 
        self.playing = True 

    def stand(self):
        self.current_anim = self.stand_anim 
        self.current_frame = self.to 

    def start_main_thread(self):
        self.main_thread = threading.Thread(target=self.main_thread, args=()) 
        
    def get_walk_direction(self, x, y):
        w = (x - self.position.x) 
        h = (y - self.position.y) 
        if w:
            angle = abs(math.atan(h / w)) 
            
        else:
            angle = math.pi / 2 
            
        if w < 0:
            angle = (math.pi - angle) 
            
        if h > 0:
            angle = (2 * math.pi - angle) 
            
        print 'get_walk_direction', x, y, self.position.x, self.position.y, w, h, angle, angle / math.pi * 8, ((int(round(angle / math.pi * 8)) + 1) / 2 % 8)
        return ((int(round(angle / math.pi * 8)) + 1) / 2 % 8)
        
"""
    
class StandardCharacter(AutoTemplate):
    name = "A character"
    description = "A character that can walk, talk, etc... May be the main character of your game."
    section = "Characters"
    resource_name = "Character"
    needed_classes = ["BasicCharacter"]
    listing = """class Character(CanWalk, CanTurn, CanTalk, BasicCharacter):
    def __init__(self, parent):
        super(BasicCharacter, self).__init__(parent)
        CanTalk.__init__(self)
        CanWalk.__init__(self)
        CanTurn.__init__(self)
        self.track_position = True
        
    def __glumolinit__(self):
        pass

    def use(self, obj):
        obj.on_hand()
        
    def look_at(self, obj):
        obj.on_look()
        
    def hand_action(self, obj):
        obj.on_hand_action()
    
"""

class MainCharacterTemplate(AutoTemplate):
    name = "Main character"
    description = "The main character of your game."
    section = "Characters"
    resource_name = "Ego"
    needed_classes = ["Character"]
    listing = """class Ego(Character):
    def __init__(self, parent):
        Character.__init__(self, parent)
        global ego
        ego = self
"""

        
