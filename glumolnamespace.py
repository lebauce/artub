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

import sys
from pypoujol import *
from new import instancemethod
from log import log
from behaviour import *
from script import get_full_name

class GlumolNamespace:
    def __init__(self):
        self.globals = dict(globals())
        self.locals = { }
        
    def clear(self):
        # self.globals = dict(globals())
        # self.locals = { }
        pass
        
    def get_value(self, name):
        return self.globals[name]
        
    def call(self, func, args):
        self.locals["func"] = func
        self.locals["args"] = args
        exec "func(*args)" in self.locals, self.locals
        del self.locals["func"]
        del self.locals["args"]
        
    def eval(self, listing):
        return eval(listing, self.globals, self.locals)
        
    def run(self, listing, module = __name__, globs = None, locs = None):
        if not globs:
            globs = self.globals
        if not locs:
            locs = self.globals
        globs["__name__"] = module
        exec listing in globs, locs
        globs["__name__"] = "glumolnamespace"
        
    def getattr(self, name, *defaults):
        attrs = name.split('.')
        try: o = self.globals[attrs[0]]
        except:
            if len(defaults):
              try: o = self.locals[attrs[0]]
              except: o = defaults[0]
            else: o = self.locals[attrs[0]]
        for i in attrs[1:]:
            o = getattr(o, i, None)
        return o
        
    def create_object(self, classe, loc = None, args = tuple() ):
         if loc == None:
             loc = self.locals
         
         loc["classe"] = classe
         loc["args"] = args
         s = "classe(*args)"
         
         self.obj = newobj = eval(s, self.globals, self.locals)
         
         del loc["args"]
         del loc["classe"]
        
         return newobj
             
    def create_from_script(self, script, args = tuple() ):
        self.run(script.listing)
        try:
            classe = self.getattr(script.realname)
            if not classe: raise
        except:
            try:
                classe = self.getattr(script.name)
                if not classe: raise
            except:
                classe = self.getattr(get_full_name(script.name))
        return self.create_object(classe, None, args)
