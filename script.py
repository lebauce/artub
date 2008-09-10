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

from glumolresource import CGlumolResource
import string
import sys
import os
import wx
from gouzi import Manipulator
import pypoujol

_debug = False

class Breakpoint:
    def __init__(self, line = None, enabled = None, handle = None):
        self.enabled = enabled
        self.line = line
        self.handle = handle
        
def get_object_name(self):
        s = repr(self)
        start = index = s.rfind('.') + 1
        try:
            while s[index] != ' ':
               index = index + 1
            return s[start:index + 1]
        except:
            return s[start:-1]

def emit_script(self):
    listing = ''
    for i in self.variables:
        if i == 'listeners': continue
        if i == 'variables': continue
        if i[0:2] == '__': continue
        t = getattr(self, i)
        T = type(t)
        if T == type(u'') or T == type(''):
            listing += 'self.' + i + " = '" + t.replace('\\', '\\\\') + "'\n"
        elif T == type([]):
            listing += 'self.' + i + " = ["
            for j in t:
                listing += get_object_name(j) + ', '
            listing += ']\n'
        else:
            listing += 'self.' + i + ' = ' + repr(t) + '\n'
    return listing

class CScript(CGlumolResource, Manipulator):
   __xmlexclude__ = ["treeitem","ast","_ast","parent", "autos"]

   script_start = 1
   script_end = 2
   function_start = 3
   function_end = 4

   def __init__(self, listing = '', parent = None):
      CGlumolResource.__init__(self, parent)
      self.type = "CScript"
      self.iter = 0
      self.use_utf8_encoding = 0
      self.breakpoints = {}
      self.__dict__["listing"] = listing
      self.listing_has_changed = True
      self.ast_has_changed = False
      Manipulator.__init__(self, self)
      self.script_desc = None
      
   def clean_up(self):
       if hasattr(self, "ast"):
           self.ast = None
       self.listing = str(self.listing)
       CGlumolResource.clean_up(self)
         
   def breakpoint_at_line(self, line):
       try: return self.breakpoints[line]
       except: return None
       
   def remove_breakpoint(self, id):
       del self.breakpoints[id]
       
   def add_breakpoint(self, id, line, condition = None):
       bp = self.breakpoints[id] = Breakpoint(line, True, id)
       return bp

   def split(self):
       start = 0
       end = 0
       self.lines = []
       self.lengths = []
       try:
         while True:
           if self.listing[end] == '\n':
               self.lines.append(self.listing[start:end])
               self.lengths.append(end - start)
               start = end = end + 1
           else:
               end = end + 1
       except: pass
       try:
           self.listing[start + 1]
           self.lines.append(self.listing[start:])
           self.lengths.append(start - end)
       except: pass
    
   def get_class(self, class_name = ""):
      if not class_name: class_name = self.name
      if hasattr(self, "realname"):
          c = self.parent.get_class()
          return c.get_class(self.name)
      else:
          return Manipulator.get_class(self, class_name)
      
   def topy(self):
      if self.ast_has_changed:
          try:
              obj = wx.GetApp().gns.getattr(get_full_name(self.name))
              if hasattr(obj, '__autos__'):
                  project = wx.GetApp().artub_frame.project
                  _autos = project.autos.get(self.name, [])
                  same = len(_autos) == len(obj.__autos__)
                  def get_name(c):
                      if type(c) in (str, unicode): return c
                      else: return c.__name__
                  if same:
                      n = 0
                      for j, i in _autos:
                          if get_name(i) != get_name(obj.__autos__[n][0]) or \
                             j != obj.__autos__[n][1]:
                              same = False
                              break
                          n += 1
                  if not same:
                      s = '['
                      n = 0
                      for j, i in obj.__autos__:
                          if n: s += ", ('" + j + "', '" + get_full_name(get_name(i)) + "')"
                          else: s += "('" + j + "', '" + get_full_name(get_name(i)) + "')"
                          n = 1
                      s += ']'
                      project.autos[self.name] = obj.__autos__
                      self.change_global_property("autos", s)
          except:
              pass
          self.ast_has_changed = False
          if _debug: log("TOPY")
          self.__dict__["listing"] = Manipulator.topy(self)
          self.listing_has_changed = True
   
   def sync(self):
      if self.ast_has_changed:
          self.topy()
          if _debug: log("Warning.", self, "sync method was called before topy.")
      if self.listing_has_changed:
          if _debug: log("SYNC")
          try:
              Manipulator.sync(self, self)
          except:
              log("Error in script", self.listing)
          self.listing_has_changed = False
          self.ast_has_changed = False
          
   def change_property_no_sync(self, name, value, class_name = "", method = None):
      if not class_name: class_name = self.name
      c = self.get_class(class_name)
      c.set_property(name, value, method = method)
      self.ast_has_changed = True
   
   change_property = change_property_no_sync
      
   def get_listing(self):
       if self.ast_has_changed:
           self.topy()
           self.ast_has_changed = False
       return self.__dict__["listing"]
       
   def set_listing(self, l):
       self.listing_has_changed = True
       self.__dict__["listing"] = l

   def get_ast(self):
       if self.listing_has_changed:
           self.sync()
       return self._ast
       
   def set_ast(self, ast):
       self._ast = ast
       
   listing = property(get_listing, set_listing)
   ast = property(get_ast, set_ast)
   
   def change_global_property_no_sync(self, name, value, class_name = ""):
      if not class_name: class_name = self.name
      c = self.get_class(class_name)
      c.set_global_property(name, value)
      self.ast_has_changed = True
   
   def change_global_list_property_no_sync(self, name, value, class_name = ""):
      if not class_name: class_name = self.name
      c = self.get_class(class_name)
      c.set_global_property(name, value)
      self.ast_has_changed = True

   change_global_property = change_global_property_no_sync

   def join(self):
      self.listing = string.join(self.lines, '\n')
      
   def exec_listing(self):
       wx.GetApp().gns.run(self.listing, self.name)
       return ''
   
   def create_from_script(self, glob = None):
      loc = {}
      try:
         if glob:
            exec self.listing in glob, glob
            classe = glob[self.name]
            return self.create_object(classe, loc)
         else:
            exec self.listing in globals(), loc
            try:
                classe = loc[self.name]
            except:
                classe = globals()[self.name]
            return self.create_object(classe, loc)
      except:
         raise
         
CScript.emit_script = emit_script

def guess_free_name(name):
   i = 1
   while True:
      try:
         s = name + repr(i)
         exec s
         i = i + 1
      except:
         return s
         
def get_function_args(func, nodefaults = False):
    n = func.func_code.co_argcount
    l = func.func_code.co_varnames[0:n]
    if func.func_defaults:
        n = n - len(func.func_defaults)
    j = 0
    args = ""
    for i in l:
        if j: args += ", "
        args += i 
        if not nodefaults and j >= n:
            args += " = " + `func.func_defaults[j - n]`
        j = j + 1
    return args
        
def is_derived_from(c, b):
    if not issubclass(c, b):
        if hasattr(c, "__class__"):
            return issubclass(c.__class__, b)
    else: return True

def get_full_name(name):
    fullname = name
    while pypoujol.global_dict.has_key(name):
        v = pypoujol.global_dict[name]
        if hasattr(v, "__name__"):
            name = pypoujol.global_dict[name].__name__
        else:
            name = pypoujol.global_dict[name]
        fullname = name + '.' + fullname
    return fullname

def get_class_code(klass):
    if type(klass) == str:
        base_classes = [wx.GetApp().gns.getattr(klass)]
    elif type(klass) == list:
        base_classes = [wx.GetApp().gns.getattr(i) for i in klass]
    else:
        base_classes = [klass]
    if base_classes:
        for klass in base_classes:
            args = get_function_args(klass.__init__)
            args2 = get_function_args(klass.__init__, nodefaults=True)
            if args.endswith(", extras"):
                code = [ "def __init__(" + args[:-7] + "*extras):" ]
                code += [ "    " + klass.__name__ + ".__init__(" + args2[:-7] + "*extras)" ]
            else:
                code = [ "def __init__(" + args + "):" ]
                code += [ "    " + klass.__name__ + ".__init__(" + args2 + ")" ]
        code += ["    self.__glumolinit__()",
            "def __glumolinit__(self):",
            "    super(" + klass.__name__ + ", self).__glumolinit__()" ]
    else:
        code = ["pass"]
    return code

def make_class_name(name):
    return name[0].upper() + name[1:]

def make_variable_name(name):
    return name[0].lower() + name[1:]
