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
     

