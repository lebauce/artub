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

from screen import GScreen
from animation import global_dict
import wx

class GameMetaClass(type):
    def __init__(self, name, bases, dict):
        super(GameMetaClass, self).__init__(name, bases, dict)
        for i in dict.keys():
            if isinstance(dict[i], type):
                dict[i].parent_class = name
                global_dict[dict[i].__name__] = name

game = None

class ResourceManager:
    def __init__(self, filename): pass

class StyleManager_Silver:
    def __init__(self, manager): pass

class Game:
    __metaclass__ = GameMetaClass
    class_name = "Game"
    width = 640
    height = 480
    depth = 32
    title = "Glumol"
    fullscreen = False
    use_sdl = False
    allow_resize = False
    first_scene = None
    archive_filename = ''
    
    def __init__(self, filename = ""):
        self.filename = filename
        self.screen = GScreen()
        self.to_call = None
        self.name = "A game"
        self.debug = False
        self.fonts = {}
        self.stop = False
        self.font = None
        
    def register_font(self, font):
        self.fonts[font.__class__.__name__] = font
        if not hasattr(self, "font"): self.font = font
        
    def set_font(self, font):
        try:
            self.font = self.fonts[font.__name__]
        except KeyError:
            print "Font", font, "doesn't exist..."
        except AttributeError:
            print "Game.set_font : invalid font", font
        
    def on_key_down(self, key): pass
    def on_key_up(self, key): pass
    def on_key_down_repeat(self, key): pass
    def on_mouse_button_down(self, key): pass
    def on_mouse_button_up(self, key): pass
    def on_left_button_down(self): pass
    def on_left_button_up(self): pass
    def on_mouse_wheel_up(self): pass
    def on_mouse_wheel_down(self): pass
    def on_mouse_move(self): pass
    def on_right_button_down(self): pass
    def on_right_button_up(self): pass
    def on_middle_button_down(self): pass
    def on_middle_button_up(self): pass
    def on_left_button_down_repeat(self, time): pass
    def on_right_button_down_repeat(self, time): pass
    def on_middle_button_down_repeat(self, time): pass
    def on_main(self): pass
    def on_close(self): pass
    def on_resize(self, width, height): pass
        
    def quit(self):
        pass
        
    def draw(self):
        self.screen.draw()
        if self.to_call:
            to_call = self.to_call
            self.to_call = None
            to_call()
            
    def init(self):
        pass
        
    def run(self):
        self.demo()

def get_game():
    global game
    return game

def set_game(_game):
    wx.GetApp().gns.globals["game"] = _game
    global game
    game = _game
    
