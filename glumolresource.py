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

class CGlumolResource(object):
   __xmlexclude__ = ["treeitem","ast","_ast","parent"]
    
   def __init__(self, parent = None):
      object.__init__(self)
      self.type = "CGlumolResource"
      self.id = None
      self.name = "Une resource"
      self.filename = ""
      self.fullpathname = ""
      self.node = None
      self.childs = []
      self.modifiers = []
      self.parent = parent
      self.template = False
      
      if parent:
          parent.add(self)
      
   def link_to(self, modifier):
      self.modifiers.append(modifier)
   
   def remove_modifier(self, modifier):
      for i in self.modifiers:
         if i == modifier:
            del i
   
   def relay_modif(self, modifier):
      for i in self.modifiers:
         if i != modifier:
            i.modified_data(modifier)
               
   def is_scripted(self):
      return true

   def before_load(self):
      pass

   def after_save(self):
      pass

   def compile(self):
      pass

   def add(self, child):
      child.parent = self
      self.childs.append(child)

   def remove(self, child):
      self.childs.remove(child)

   def has_children(self):
      try:
         self.childs[0]
         return True
      except:
         return False

   def get_all_childs_of_type(self, tipe):
       l = []
       for i in self.childs:
           if isinstance(i, tipe):
               l.append(i)
           l = l + i.get_all_childs_of_type(tipe)
       return l

   def get_super_parent(self):
      oldparent = self
      parent = self.parent
      while parent != None:
         oldparent = parent
         parent = parent.parent
      return oldparent

   def get_resource_from_id(self):
      pass
   
   def __getitem__(self, item):
       for i in self.childs:
           if i.name == item:
               return i
       return None

   def has_child(self, name):
      item = self.__getitem__(name)
      if item:
         return item
      for i in self.childs:
         item = i.has_child(name)
         if item: return item
      return None
            
   def get_resource_name(self, prefix="New_resource"):
       proj = self.get_super_parent()
       indice = 2
       suffix = ""
       found = False
       while self.has_child(prefix + suffix):
          suffix = "_" + str(indice)
          indice = indice + 1
       return prefix + suffix
      
   def apply(self, f, arg = None):
       f(self, arg)
       for i in self.childs:
           i.apply(f, arg)
           
   def filter_apply(self, f, cond, arg = None):
       if cond and cond(self):
           if arg: f(self, arg)
           else: f(self)
       for i in self.childs:
           i.filter_apply(f, cond, arg)
           
   def clean_up(self):
       for i in self.childs:
           i.clean_up()

                  
class CFolder(CGlumolResource): pass

class VirtualGlumolResource(CGlumolResource):
   def __init__(self, type):
      object.__init__(self)
      CGlumolResource.__init__(self)
      self.type = type
      
   def get_first_non_virtual_parent(self):
       parent = self.parent
       while parent:
           if not isinstance(parent, VirtualGlumolResource):
               return parent
           parent = parent.parent
           
   def get_listing(self):
       parent = self.get_first_non_virtual_parent()
       if parent: return parent.listing
       return ""
       
   def set_listing(self, listing):
       parent = self.get_first_non_virtual_parent()
       if parent: parent.listing = listing
       
   listing = property(get_listing, set_listing)
   
   def get_ast_has_changed(self):
       parent = self.get_first_non_virtual_parent()
       if parent: return parent.ast_has_changed
       return ""
       
   def set_ast_has_changed(self, ast_has_changed):
       parent = self.get_first_non_virtual_parent()
       if parent: parent.ast_has_changed = ast_has_changed
       
   ast_has_changed = property(get_ast_has_changed, set_ast_has_changed)

   def get_listing_has_changed(self):
       parent = self.get_first_non_virtual_parent()
       if parent: return parent.listing_has_changed
       return ""
       
   def set_listing_has_changed(self, listing_has_changed):
       parent = self.get_first_non_virtual_parent()
       if parent: parent.listing_has_changed = listing_has_changed
       
   listing_has_changed = property(get_listing_has_changed, set_listing_has_changed)

   def sync(self):
       parent = self.get_first_non_virtual_parent()
       if parent: return parent.sync()
       
   def topy(self):
       parent = self.get_first_non_virtual_parent()
       if parent: return parent.topy()
       
   def get_class(self, name = ""):
       parent = self.get_first_non_virtual_parent()
       if parent:
            if not name: 
                name = parent.name
            return parent.get_class(name)
        
