from glumolresource import VirtualGlumolResource, CGlumolResource
from script import CScript

class CAnimation(CScript):
   def __init__(self, parent = "None"):
      CScript.__init__(self, parent)
      self.type = "CAnimation"
      self.filename = ""

class VirtualAnimation(VirtualGlumolResource, CAnimation):
    def __init__(self):
        CAnimation.__init__(self)
        VirtualGlumolResource.__init__(self, "CAnimation")
