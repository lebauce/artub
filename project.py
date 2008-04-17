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

from xmlmarshall.xmlmarshaller import marshal, unmarshal
from script import CScript
from dialogue import *
from log import log
from os.path import normpath, normcase
import string
import os
import wx
import sys
from bike.refactor.rename import rename
from bike.transformer.save import save

class CProject(CScript):
   def __init__(self):
      CScript.__init__(self)
      self.project_filename = ""
      self.glumol_path = ""
      self.project_path = ""
      self.normname = ""
      self.icon = ""
      self.icon_filename = ""
      self.debug = False
      self.optimization = _("None")
      self.company_name = ""
      self.company_name = ""
      self.description = ""
      self.file_version = 1.0
      self.copyrights = ""
      self.trademark = ""
      self.product_name = ""
      self.product_version = 1.0
      self.license = ""
      self.use_upx = False
      self.use_console = True
      self.no_single_file = False
      self.use_tk = False
      self.eula_path = ""
      self.readme_path = ""
      self.templates = []
      self.type = "CProject"
      self.autos = {}

   def has_template(self, template):
       return template.name in self.templates
       
   def add_template(self, template):
       self.templates.append(template)
       
   def load2(self, filename):
      self.doc = minidom.parse(filename)
      self.node = self.doc.documentElement

   def load(self, filename):
      s = open(filename, 'r').read()
      self = loads(s)

   def save(self, filename=""):
      if not filename:
         filename = self.filename 
      
      def foo(s, arg):
          if(isinstance(s, CScript)):
              s.listing # To be sure listing's up to date

      self.apply(foo)
      open(filename, "w").write(marshal(self, prettyPrint=True))
           
   def exec_all_scripts(self):
       def exec_all_scripts_aux(resource, template):
           log = ""
           for i in resource.childs:
               i.parent = resource
               try:
                   if isinstance(i, CScript) and i.template == template:
                       log = log + i.exec_listing()
                       i.listing_has_changed = True
                       i.ast_has_changed = False
               except:
                   log = log + exec_all_scripts_aux(i, template)
                   raise
                   continue
               log = log + exec_all_scripts_aux(i, template)
           return log
       try:
           log = exec_all_scripts_aux(self, True)
           log = exec_all_scripts_aux(self, False)
           self.listing_has_changed = True
           self.ast_has_changed = False
           self.exec_listing()
       except:
           print "They were errors during loading of scripts"
           sys.excepthook(*sys.exc_info())
           
   def get_output_filename(self):
      return self.name + ".glu"

   def compile(self, filename=""):
      if filename == '':
         filename = self.get_output_filename()

   def rename_class(self, oldname, newname):
        import string
        class FullListing: 
            def __init__(self):
                self.listing = []
                self.lines = []
        full = FullListing()
        def concat_listing(res, full):
            if hasattr(res, "listing"):
                full.lines.append(len(full.listing))
                full.listing += res.listing.split('\n')
                
        self.apply(concat_listing, full)
        full.listing = string.join(full.listing, '\n')
        full.lines.append(-1)
        
        import re
        import tempfile
        import os.path
        filename = os.path.join(tempfile.gettempdir(), "refactortemp.py")
        open(filename, 'w').write(full.listing)
        lines = full.listing.split('\n')
        line = 1
        for l in lines:
            match = re.compile('class (\s)*(' + oldname + ')[^a-zA-Z_]').search(l)
            if match:
                rename(filename, line, match.start(2), newname)
                save()
                full.listing = open(filename).read().split('\n')
                def restore_listing(res, full):
                    if hasattr(res, "listing"):
                        res.listing = string.join(full.listing[full.lines[0]:full.lines[1]], '\n') + '\n'
                        res.listing_has_changed = True
                        del full.lines[0]
                self.apply(restore_listing, full)
                break
            line += 1
        os.remove(filename)
        self.exec_all_scripts()

   def get_relative_path(self, filename):
      project_path = normpath(normcase(self.project_path))
      filename = normpath(normcase(filename))
      ind = filename.find(project_path + os.sep)
      if ind != -1:
          filename = filename[ind + len(project_path) + 1:]
      return filename
      
   def ask_to_import(self, filename):
        filename = self.get_relative_path(filename)
        import os.path
        if os.path.isabs(filename):
            dlg = wx.MessageDialog(wx.GetApp().frame,
                            _("Do you want this image to be copied into your project's folder ?"),
                            _("Copy image into project's folder"),
                            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            ret = dlg.ShowModal()
            if ret == wx.ID_YES:
                import shutil
                shutil.copy(filename, self.project_path)
                filename = os.path.basename(filename)
            dlg.Destroy()
        return filename

def load_project(filename):
    import propertiesbar.companions as companions
    s = open(filename, 'r')
    project = unmarshal(s.read())
    project.filename = filename
    project.project_path = os.path.dirname(filename)
    return project

