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
import os
from os.path import join
import wx

class Monkey2InterfaceTemplate(Template):
    name = "Verb interface"
    description = "Interface like many adventure games (Monkey Island I & II, Dott, ...)."
    section = "Interfaces"

    def do(self, evt, **args):
        project = self.artub.project

        resource = CGlumolObject(project)
        resource.template = True
        resource.name = "MI2Object"
        resource.listing = """class MI2Object(Behaviour):
    def on_focus(self, oldobj):
        game.cursor.playing = True 
        game.interface.set_object(self)
        super(MI2Object, self).on_focus(oldobj)
        
    def on_look(self):
        if self.walk_point:
            ego.walk_to(self.walk_point.x, self.walk_point.y)
            
        ego.say(self.description)
        
    def on_hand(self):
        if self.walk_point:
            ego.walk_to(self.walk_point.x, self.walk_point.y)
                    
    def on_lose_focus(self, newobj):
        game.cursor.playing = False 
        game.cursor.current_frame = 0 
        game.interface.set_object(None)
        super(MI2Object, self).on_lose_focus(newobj)
        
    def on_walk(self):
        if self.walk_point:
            ego.walk_to(self.walk_point.x, self.walk_point.y)
                    
    def on_left_button_down(self):
        action = game.interface.action 
        d = {'Walk to' : self.on_walk , 'Look at' : self.on_look}  
        d[action]()
        game.interface.set_default_action()
"""
        self.artub.add_template(resource)
        
        resource = CGlumolObject(project)
        resource.template = True
        resource.name = "Object"
        if self.check_classes(["Pickable"]):
            return
        resource.listing = """class Object(MI2Object, RegionObject, Pickable):
    def __init__(self, parent):
        RegionObject.__init__(self, parent)
        Pickable.__init__(self)
        MI2Object.__init__(self)
        self.center = (0,0) 
        self.name = 'an object' 
        self.description = 'Great !' 
        self.walk_point = None 
        self.z = -100 
"""
        self.artub.add_template(resource)

        resource = CGlumolObject(project)
        resource.template = True
        resource.name = "InterfaceItem"
        resource.listing = """class InterfaceItem(Sprite):
    def __init__(self, parent):
        Sprite.__init__(self, parent)
        self.action = 'Action' 
        self.combined_action = False 
        
    def on_focus(self, oldobj):
        self.current_frame = 1 
        
    def on_lose_focus(self, newobj):
        self.current_frame = 0 
        
    def on_left_button_down(self):
        self.parent.on_button_click(self)
"""
        self.artub.add_template(resource)
        
        resource = CGlumolObject(project)
        #resource.template = True
        resource.name = "Interface"
        from string import Template
        resource.listing = Template("""class Interface(Sprite):
    def __init__(self, parent):
        Sprite.__init__(self, parent)
        self.__glumolinit__()
        self.default_action = 'Walk to' 
        self.action = self.default_action 
        self.obj = None
        
    def __glumolinit__(self):
        self.position = (0,game.height - 84) 
        self.open_button = Interface.open_buttonObject(self) 
        self.size = (234,84) 
        self.close_button = Interface.close_buttonObject(self) 
        self.look_button = Interface.look_buttonObject(self) 
        self.give_button = Interface.give_buttonObject(self) 
        self.pull_button = Interface.pull_buttonObject(self) 
        self.talk_button = Interface.talk_buttonObject(self) 
        self.take_button = Interface.take_buttonObject(self) 
        self.use_button = Interface.use_buttonObject(self) 
        self.push_button = Interface.push_buttonObject(self) 
        self.textzone = Interface.textzoneObject(self) 
        
    def on_button_click(self, button):
        self.action = button.action 
        self.textzone.update_text()
        
    def set_default_action(self):
        self.action = self.default_action 
        self.textzone.update_text()
        
    def set_object(self, obj):
        self.obj = obj 
        self.textzone.update_text()
        
    class open_buttonObject(InterfaceItem):
        class OpenAnim(Animation):
            filenames = ['${images_path}open.png','${images_path}open2.png'] 
            nbframes = 2 
            virtual_frames = 2 
            
        def __init__(self, parent):
            InterfaceItem.__init__(self, parent)
            self.__glumolinit__()
            
        def __glumolinit__(self):
            self.to_scene = None 
            self.boxes = [] 
            self.current_anim = self.OpenAnim() 
            self.position = (78,28) 
            self.action = 'Open' 
            
        
    class close_buttonObject(InterfaceItem):
        def __init__(self, parent):
            InterfaceItem.__init__(self, parent)
            self.__glumolinit__()
            
        def __glumolinit__(self):
            self.to_scene = None 
            self.boxes = [] 
            self.current_anim = Interface.close_buttonObject.CloseAnim() 
            self.position = (78,56) 
            self.action = 'Close' 
            
        class CloseAnim(Animation):
            filenames = ['${images_path}close.png','${images_path}close2.png'] 
            nbframes = 2 
            virtual_frames = 2 
            def __init__(self):
                Animation.__init__(self)
                
            
        
    class look_buttonObject(InterfaceItem):
        def __init__(self, parent):
            InterfaceItem.__init__(self, parent)
            self.__glumolinit__()
            
        def __glumolinit__(self):
            self.to_scene = None 
            self.boxes = [] 
            self.current_anim = Interface.look_buttonObject.LookAnim() 
            self.position = (156,0) 
            self.action = 'Look at' 
            
        class LookAnim(Animation):
            filenames = ['${images_path}look.png','${images_path}look2.png'] 
            nbframes = 2 
            virtual_frames = 2 
            def __init__(self):
                Animation.__init__(self)
                
            
        
    class give_buttonObject(InterfaceItem):
        def __init__(self, parent):
            InterfaceItem.__init__(self, parent)
            self.__glumolinit__()
            
        def __glumolinit__(self):
            self.to_scene = None 
            self.boxes = [] 
            self.current_anim = Interface.give_buttonObject.GiveAnim() 
            self.position = (0,28) 
            self.action = 'Give' 
            
        class GiveAnim(Animation):
            filenames = ['${images_path}give.png','${images_path}give2.png'] 
            nbframes = 2 
            virtual_frames = 2 
            def __init__(self):
                Animation.__init__(self)
                
            
        
    class pull_buttonObject(InterfaceItem):
        def __init__(self, parent):
            InterfaceItem.__init__(self, parent)
            self.__glumolinit__()
            
        def __glumolinit__(self):
            self.to_scene = None 
            self.boxes = [] 
            self.current_anim = Interface.pull_buttonObject.PullAnim() 
            self.position = (156,56) 
            self.action = 'Pull' 
            
        class PullAnim(Animation):
            filenames = ['${images_path}pull.png','${images_path}pull2.png'] 
            nbframes = 2 
            virtual_frames = 2 
            def __init__(self):
                Animation.__init__(self)
                
            
        
    class talk_buttonObject(InterfaceItem):
        def __init__(self, parent):
            InterfaceItem.__init__(self, parent)
            self.__glumolinit__()
            
        def __glumolinit__(self):
            self.to_scene = None 
            self.boxes = [] 
            self.current_anim = Interface.talk_buttonObject.TalkAnim() 
            self.position = (78,0) 
            self.action = 'Talk' 
            
        class TalkAnim(Animation):
            filenames = ['${images_path}talk.png','${images_path}talk2.png'] 
            nbframes = 2 
            virtual_frames = 2 
            def __init__(self):
                Animation.__init__(self)
                
            
        
    class take_buttonObject(InterfaceItem):
        def __init__(self, parent):
            InterfaceItem.__init__(self, parent)
            self.__glumolinit__()
            
        def __glumolinit__(self):
            self.to_scene = None 
            self.boxes = [] 
            self.current_anim = Interface.take_buttonObject.TakeAnim() 
            self.position = (156,28) 
            self.action = 'Talk' 
            self.obj = None 
            
        class TakeAnim(Animation):
            filenames = ['${images_path}take.png','${images_path}take2.png'] 
            nbframes = 2 
            virtual_frames = 2 
            def __init__(self):
                Animation.__init__(self)
                
            
        
    class use_buttonObject(InterfaceItem):
        def __init__(self, parent):
            InterfaceItem.__init__(self, parent)
            self.__glumolinit__()
            
        def __glumolinit__(self):
            self.to_scene = None 
            self.boxes = [] 
            self.current_anim = Interface.use_buttonObject.UseAnim() 
            self.action = 'Use' 
            
        class UseAnim(Animation):
            filenames = ['${images_path}use.png','${images_path}use2.png'] 
            nbframes = 2 
            virtual_frames = 2 
            def __init__(self):
                Animation.__init__(self)
                
            
        
    class push_buttonObject(InterfaceItem):
        def __init__(self, parent):
            InterfaceItem.__init__(self, parent)
            self.__glumolinit__()
            
        def __glumolinit__(self):
            self.to_scene = None 
            self.current_anim = Interface.push_buttonObject.PushAnim() 
            self.position = (0,56) 
            self.boxes = [] 
            self.action = 'Push' 
            
        class PushAnim(Animation):
            filenames = ['${images_path}push.png','${images_path}push2.png'] 
            nbframes = 2 
            virtual_frames = 2 
            def __init__(self):
                Animation.__init__(self)
                
            
        
    class textzoneObject(Sprite):
        def __init__(self, parent):
            Sprite.__init__(self, parent)
            self.__glumolinit__()
            self.set_boxes()
            self.text = '' 
            self.Color = Color(255, 255, 255, 255) 
            self.transparent = True
            
        def update_text(self):
            if self.parent.obj:
                self.text = ((self.parent.action + ' ') + self.parent.obj.name) 
                
            else:
                self.text = self.parent.action 
                
            
        def on_after_draw(self):
            draw_text(self.text, (self.position.x, game.height - 108), (300, 300), self.Color)
            
        def __glumolinit__(self):
            self.to_scene = None 
            self.size = (640,20) 
            self.boxes = [] 
            self.position = (0,-20) 
""").substitute(images_path=repr(join(wx.GetApp().artub_path, "plugins", "basic_templates", "dott") + os.sep)[1:-1])

        self.artub.add_template(resource)
        self.artub.add_template(resource)
        project.add_template(self.name)
