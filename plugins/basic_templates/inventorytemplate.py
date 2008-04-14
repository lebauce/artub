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
