from script import CScript
from glumolresource import VirtualGlumolResource

class CGlumolObject(CScript):
   def __init__(self, parent = None):
      CScript.__init__(self, parent = parent)
      self.type = "CGlumolObject"

class VirtualGlumolObject(VirtualGlumolResource, CGlumolObject):
    def __init__(self):
        VirtualGlumolResource.__init__(self, "CGlumolObject")
        CGlumolObject.__init__(self)
