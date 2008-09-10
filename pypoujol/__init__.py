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

import animation
from animation import Animation, NoImage, Point, Color, AnimationMetaClass
from sprite import *
from canvas import ClanlibCanvas
from screen import GScreen
from game import Game, GameMetaClass, ResourceManager, StyleManager_Silver, get_game, set_game
from scene import Scene, Plane, scene_dict, SceneMetaClass
from font import Font
from sound import Sound
from zbuffer import ZPlane
from path import Path
import stackless
import time

class SoundOutput:
    def __init__(self, rate): pass
    
class Music:
    def __init__(self, filename): pass
    def play(self): pass

def get_parent_class(c):
    s = c.__name__
    while "parent_class" in dir(c):
        c = c.parent_class
        try:
            s = c.__name__ + "." + s
        except:
            s = c + "." + s
    return s

def draw_text(text = "", x = 0, y = 0):
    pass
    
def get_size(text, maxsize = None):
    return (10, 10)
    
class Character(Sprite): pass

class Pathfinder:
    def __init__(self):
        pass

sleepingTasklets = []

def sleep(delay):
    chan = stackless.channel() 
    sleepingTasklets.append([(time.time() + delay),chan])
    sleepingTasklets.sort()
    chan.receive()
    
class Timer:
    def __init__(self, delay, action, args):
        self.action = action
        self.delay = delay
        self.args = args
        self.repeat = True

    def start(self):
        stackless.tasklet(self.do)()

    def do(self):
        while self.repeat:
            sleep(self.delay)
            self.action(*self.args)
            
        
class Choice:
    def __str__(self):
        s = repr(self)
        start = index = s.find('.') + 1
        while s[index] != ' ':
           index = index + 1
        return s[start:index]
        
    def __setattr__(self, attr, value):
        self.__dict__[attr] = value
        self.__dict__['variables'].append(attr)
        
    def __init__(self):
        self.variables = []
        self.__glumolinit__()
        
    def display_choices(self):
        k = 1
        for i in self.choices:
            print k, i.text
            k = k + 1
    
    def do(self):
        self.choices = []
        for i in self.childs:
            self.choices.append(i())
        self.display_choices()
        i = self.query_response()
        childs[i].do()
        
    def query_response(self):
        return input("Votre choix : ")
        
class Dialog(object):
    def __str__(self):
        s = repr(self)
        start = index = s.find('.') + 1
        while s[index] != ' ':
           index = index + 1
        return s[start:index]
        
    def __glumolinit__(self): pass
        
    def __init__(self, parent = None):
        self.__glumolinit__()
        
    def display_choices(self):
        k = 1
        for i in self.choices:
            print k, i.text
            k = k + 1
    
    def do(self):
        self.choices = []
        for t in self.childs:
            newobj = t()
            self.choices.append(t())
        self.display_choices()
        i = self.query_response()
        childs[i].do()
        
    def query_response(self):
        return input("Votre choix : ")
        
Dialogue = Dialog
global_dict = animation.global_dict
