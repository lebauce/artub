from glumolresource import CGlumolResource
from script import CScript

class CDialogue(CScript):
   def __init__(self):
      CScript.__init__(self)
      self.type = "Dialogue"
      self.filename = ""