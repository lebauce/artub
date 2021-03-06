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
import configmanager as config
from wx.lib import masked

[wxID_WXPANEL1, wxID_WXPANEL1CHECKBOX1] = map(lambda _init_ctrls: wx.NewId(), range(2))

class DistCEOptions(wx.Panel):
    def _init_ctrls(self, prnt):
        wx.Panel.__init__(self, id=wxID_WXPANEL1, name='', parent=prnt,
              pos=wx.DefaultPosition, size=wx.Size(337, 600),
              style=wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(337, 450))

        proj = wx.GetApp().artub_frame.project
              
        sizer = wx.BoxSizer(wx.VERTICAL)

        import  wx.lib.filebrowsebutton as filebrowse

        self.fbb = filebrowse.FileBrowseButton(self, -1, labelText=_("CABWIZ.EXE full path"))
        try: cabwiz_path = config.config["cabwiz_path"]
        except IndexError: cabwiz_path = ""
        self.fbb.SetValue(cabwiz_path)
        sizer.Add(self.fbb, 1, wx.GROW|wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL, 5)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)
        
    def __init__(self, parent, id):
        self._init_ctrls(parent)
        
    def OnOk(self):
        config.config["cabwiz_path"] = self.fbb.GetValue()
 
