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

import wx
from configmanager import config
from wx.lib import masked

[wxID_WXPANEL1, wxID_WXPANEL1CHECKBOX1] = map(lambda _init_ctrls: wx.NewId(), range(2))

class BuilderOptionsPage(wx.Panel):
    def _init_ctrls(self, prnt):
        wx.Panel.__init__(self, id=wxID_WXPANEL1, name='', parent=prnt,
              pos=wx.Point(304, 219), size=wx.Size(337, 300),
              style=wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(337, 300))

        proj = self.project
              
        sizer = wx.BoxSizer(wx.VERTICAL)

        import  wx.lib.filebrowsebutton as filebrowse

        self.fbb = filebrowse.FileBrowseButton(self, -1, labelText=_("Icon"))
        self.fbb.SetValue(proj.icon)
        sizer.Add(self.fbb, 0, wx.GROW|wx.ALIGN_CENTRE|wx.ALL, 2)

        self.readme = filebrowse.FileBrowseButton(self, -1, labelText=_("Readme file"))
        self.readme.SetValue(proj.readme_path)
        sizer.Add(self.readme, 0, wx.GROW|wx.ALIGN_CENTRE|wx.ALL, 2)

        self.eula = filebrowse.FileBrowseButton(self, -1, labelText=_("End of user license agreement file"))
        self.eula.SetValue(proj.eula_path)
        sizer.Add(self.eula, 0, wx.GROW|wx.ALIGN_CENTRE|wx.ALL, 2)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, _("Optimization"))
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 2)

        self.optim = wx.ComboBox(self, -1, proj.optimization,
                                 choices=[_("Default"),
                                          _("Debug"),
                                          _("All")])
        box.Add(self.optim, 1, wx.ALIGN_CENTRE|wx.ALL, 2)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2)

        self.upx = wx.CheckBox(self, -1, _("Use upx"))
        self.upx.SetValue(proj.use_upx)
        sizer.Add(self.upx, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        
        self.not_one_file = wx.CheckBox(self, -1, _("Do not create an unique file"))
        self.not_one_file.SetValue(proj.no_single_file)
        sizer.Add(self.not_one_file, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        
        self.display_console = wx.CheckBox(self, -1, _("Display console"))
        self.display_console.SetValue(proj.use_console)
        sizer.Add(self.display_console, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)

        self.tcl_tk = wx.CheckBox(self, -1, _("Use Tcl/Tk"))
        self.tcl_tk.SetValue(proj.use_tk)
        sizer.Add(self.tcl_tk, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)

        box_label = wx.StaticBox( self, -1, _("Executable's informations (Windows only)"))
        buttonbox = wx.StaticBoxSizer( box_label, wx.VERTICAL )
        
        infosizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, _("Product name"))
        infosizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 1)
        self.product_name = wx.TextCtrl(self, -1, proj.product_name)
        infosizer.Add(self.product_name, 1, wx.ALIGN_CENTRE|wx.ALL, 1)
        buttonbox.Add(infosizer, 0, wx.GROW|wx.ALIGN_CENTRE|wx.ALL, 1)
        
        infosizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, _("Company"))
        infosizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 1)
        self.company = wx.TextCtrl(self, -1, proj.company_name)
        infosizer.Add(self.company, 1, wx.ALIGN_CENTRE|wx.ALL, 1)
        buttonbox.Add(infosizer, 0, wx.GROW|wx.ALIGN_CENTRE|wx.ALL, 1)
        
        infosizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, _("Version"))
        infosizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 1)
        proj.product_version = 1.0
        self.version = masked.Ctrl(self, value=proj.product_version, integerWidth=2, fractionWidth=2, controlType=masked.controlTypes.NUMBER)
        infosizer.Add(self.version, 1, wx.ALIGN_CENTRE|wx.ALL, 1)
        buttonbox.Add(infosizer, 0, wx.GROW|wx.ALIGN_CENTRE|wx.ALL, 1)
        
        infosizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, _("Description"))
        infosizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 1)
        self.description = wx.TextCtrl(self, -1, proj.description)
        infosizer.Add(self.description, 1, wx.ALIGN_CENTRE|wx.ALL, 1)
        buttonbox.Add(infosizer, 0, wx.GROW|wx.ALIGN_CENTRE|wx.ALL, 1)
         
        infosizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, _("Copyrights"))
        infosizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 1)
        self.copyrights = wx.TextCtrl(self, -1, proj.copyrights)
        infosizer.Add(self.copyrights, 1, wx.ALIGN_CENTRE|wx.ALL, 1)
        buttonbox.Add(infosizer, 0, wx.GROW|wx.ALIGN_CENTRE|wx.ALL, 1)

        infosizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, _("License"))
        infosizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 1)
        self.license = wx.TextCtrl(self, -1, proj.license)
        infosizer.Add(self.license, 1, wx.ALIGN_CENTRE|wx.ALL, 1)
        buttonbox.Add(infosizer, 0, wx.GROW|wx.ALIGN_CENTRE|wx.ALL, 1)

        sizer.Add(buttonbox, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
        
    def __init__(self, parent, project):
        self.project = project
        self._init_ctrls(parent)
        
    def OnOk(self):
        proj = self.project
        proj.debug = 0
        proj.optimization = self.optim.GetValue()
        proj.company_name = self.company.GetValue()
        proj.description = self.description.GetValue()
        proj.file_version = ""
        proj.copyrights = self.copyrights.GetValue()
        proj.trademark = ""
        proj.product_name = self.product_name.GetValue()
        proj.product_version = self.version.GetValue()
        proj.use_upx = self.upx.GetValue()
        proj.use_console = self.display_console.GetValue()
        proj.no_single_file = self.not_one_file.GetValue()
        proj.use_tk = self.tcl_tk.GetValue()
        proj.icon = self.fbb.GetValue()
        proj.license = self.license.GetValue()
        proj.eula_path = self.eula.GetValue()
        proj.readme_path = self.readme.GetValue()
        print proj.optimization
        print proj.company_name
        print proj.description
        print proj.copyrights
        print proj.product_name
        print proj.product_version
        print proj.use_upx
        print proj.use_console
        print proj.no_single_file
        print proj.use_tk
        print proj.license
        
        

 
