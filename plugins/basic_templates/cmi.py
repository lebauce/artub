from resourceeditor import Template
from glumolobject import CGlumolObject
from os.path import join
import os
import wx

class CMIInterfaceTemplate(Template):
    name = "CMI & Fullthrottle like interface"
    description = "Interface like Curse of Monkey Island (Monkey Island III)."
    section = "Interfaces"

    def do(self, evt):
        project = self.artub.project

        resource = CGlumolObject(project)
        resource.template = True
        resource.name = "CMIObject"
        resource.listing = """class CMIObject:
    pass
"""
        self.artub.add_template(resource)

        resource = CGlumolObject(project)
        resource.template = True
        resource.name = "Object"
        resource.listing = """class Object(RegionObject, CMIObject, Pickable):
    pass
"""
        self.artub.add_template(resource)

        resource = CGlumolObject(project)
        #resource.template = True
        resource.name = "Interface"
        from string import Template
        resource.listing = Template("""class Interface(Sprite):
    class InterfaceBitmap(Animation):
        filenames = ['${images_path}interface.png'] 
        nbframes = 1 
        virtual_frames = 1 
        def __init__(self):
            Animation.__init__(self)
            self.__glumolinit__()
            
        def __glumolinit__(self):
            pass 
            self.delays[:] = [1] 
            self.orders[:] = [0] 
            self.hotspots[:] = [Point(142, 155)] 
            self.move_offsets[:] = [Point(0, 0)] 
            
        
    class HandBitmap(Animation):
        filenames = ['${images_path}hand1.png','${images_path}hand2.png'] 
        nbframes = 2 
        virtual_frames = 2 
        def __glumolinit__(self):
            pass 
            self.delays[:] = [1,1] 
            self.orders[:] = [0,1] 
            self.hotspots[:] = [Point(0, 0),Point(0, 0)] 
            self.move_offsets[:] = [Point(0, 0),Point(0, 0)] 
            
        
    class LookBitmap(Animation):
        filenames = ['${images_path}eyes1.png','${images_path}eyes2.png'] 
        nbframes = 2 
        virtual_frames = 2 
        def __glumolinit__(self):
            pass 
            self.delays[:] = [1,1] 
            self.orders[:] = [0,1] 
            self.hotspots[:] = [Point(0, 0),Point(0, 0)] 
            self.move_offsets[:] = [Point(0, 0),Point(0, 0)] 
            
        
    def __init__(self, parent):
        Sprite.__init__(self, parent)
        self.__glumolinit__()
        
    def __glumolinit__(self):
        self.current_anim = Interface.InterfaceBitmap() 
        self.look = Interface.lookRegionObject(self) 
        self.use = Interface.useRegionObject(self) 
        self.alpha = 0.0 
        self.boxes = [] 
        self.position = (200,200) 
        self.scale = 0.29999999999999999 
        self.z = 100000 
        self.track_position = False 
        
    def popup(self, obj):
        self.current_object = obj 
        self.z = 100000 
        game.scene.sort()
        print self.alpha,  not self.alpha, obj.position.x, obj.position.y, self.current_anim.hotspots[0].x, self.current_anim.hotspots[0].y
        if  not self.alpha:
            self.position = Point(game.input.mouse_position.x, game.input.mouse_position.y) 
            self.fade_in(0.5)
            
        
    def on_lose_focus(self, newobj):
        print 'lose focus'
        if  not newobj in self.children:
            self.fade_out(0.5)
            
        
    class lookRegionObject(RegionObject):
        def __init__(self, parent):
            RegionObject.__init__(self, parent)
            self.__glumolinit__()
            
        def __glumolinit__(self):
            self.to_scene = None 
            self.current_anim = Interface.LookBitmap() 
            self.position = Point(107, 82) 
            self.playing = False 
            self.boxes = [] 
            
        def on_focus(self, oldobj):
            self.current_frame = 1 
            
        def on_lose_focus(self, newobj):
            self.current_frame = 0 
            
        def on_left_button_down(self):
            self.parent.fade_out(0.5)
            game.ego.look_at(self.parent.current_object)
            
        
    class useRegionObject(RegionObject):
        def __init__(self, parent):
            RegionObject.__init__(self, parent)
            self.__glumolinit__()
            
        def __glumolinit__(self):
            self.to_scene = None 
            self.current_anim = Interface.HandBitmap() 
            self.position = Point(16, 76) 
            self.playing = False 
            self.boxes = [] 
            
        def on_focus(self, oldobj):
            self.current_frame = 1 
            
        def on_lose_focus(self, newobj):
            self.current_frame = 0 
            
        def on_left_button_down(self):
            self.parent.fade_out(0.5)
            print self.parent
            game.ego.use(self.parent.current_object)
            
        
    class talkRegionObject(RegionObject):
        def __init__(self, parent):
            RegionObject.__init__(self, parent)
            self.__glumolinit__()
            
        def __glumolinit__(self):
            self.to_scene = None 
            
""").substitute(images_path=repr(join(wx.GetApp().artub_path, "plugins", "basic_templates") + os.sep)[1:-1])

        project.add_template(self.name)
        self.artub.add_template(resource)

    
