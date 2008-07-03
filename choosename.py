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
from script import get_full_name
from identifierctrl import IdentifierCtrl

class ChooseNameDialog(wx.Dialog):
    def __init__(
            self, name, parent = None, ID=-1, title=_("Choose a name"), size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP, unique = False):

        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        self.this = pre.this

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.text = wx.StaticText(self, -1, _("Name"))
        sizer2.Add(self.text, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        
        self.name = IdentifierCtrl(self, -1, name, size = (200, 20))
        sizer2.Add(self.name, 1,  wx.ALIGN_CENTRE | wx.ALL, 5)
        #self.name.SetValue(name)
        self.name.SetSelection(-1, -1)
        
        sizer.Add(sizer2, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.ok = wx.Button(self, wx.ID_OK, _("Ok"))
        self.ok.SetDefault()
        sizer2.Add(self.ok, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        
        self.cancel = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
        sizer2.Add(self.cancel, 1,  wx.ALIGN_CENTRE | wx.ALL, 5)
        
        sizer.Add(sizer2, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)
        
        self.unique = unique
        self.failed = False
                
        wx.EVT_BUTTON(self, wx.ID_OK, self.on_ok)
        
    def on_ok(self, evt):
        self.failed = self.unique and wx.GetApp().gns.getattr(get_full_name(self.name.GetValue()), None)
        evt.Skip(True)
        
def choose_a_name(name = _("New_object"), unique = True):
    while True:
        dlg = ChooseNameDialog(name, unique = unique)
        dlg.Centre()

        res = dlg.ShowModal()
        name = dlg.name.GetValue()
        dlg.Destroy()
        if res != wx.ID_OK and not dlg.failed:
            return ""
        if not dlg.failed:
            break
        else:
            dlg2 = wx.MessageDialog(None, _("An object (") + get_full_name(dlg.name.GetValue()) + _(") already has this name"),
            _("Please choose an other name"), wx.OK | wx.ICON_ERROR)
            dlg2.ShowModal()
            dlg2.Destroy()
            
    return name.rstrip()
