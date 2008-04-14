from project import CProject
import sys
import os
import os.path
from os import makedirs
import wx
from depplatform import get_image_path
import string
from choosename import IdentifierCtrl
import re

class NewProject:
    def new_project(self, parent):
        win = NewDialog(wx.GetApp().frame, -1, _("New"), size=(350, 200), style = wx.DEFAULT_DIALOG_STYLE)
        win.CenterOnScreen()
        val = win.ShowModal()
    
        if val == wx.ID_OK:
            item = win.list.GetNextItem(-1,
                                     wx.LIST_NEXT_ALL,
                                     wx.LIST_STATE_SELECTED)
            t = win.templates[item]
            normname = win.normname.GetValue().strip()
            folder = os.path.join(win.folder, normname)
            project = t[0].create_project(t[1], str(normname), folder)
            project.name = win.name.GetValue()
            project.filename = os.path.join(folder, str(normname) + ".glu")
        else:
            project = None
            
        win.Destroy()
        return project
        
Newproject = NewProject()

class NewDialog(wx.Dialog):
    def dbbCallback(self, evt):
        self.folder = evt.GetString()
    
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE
            ):

        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)
        self.this = pre.this

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.il = wx.ImageList(32, 32)

        self.idx1 = self.il.Add(wx.Bitmap(get_image_path("bike.png"), wx.BITMAP_TYPE_PNG))
        self.idx1 = self.il.Add(wx.Bitmap(get_image_path("drum.png"), wx.BITMAP_TYPE_PNG))
        self.idx1 = self.il.Add(wx.Bitmap(get_image_path("isidoor.xpm"), wx.BITMAP_TYPE_XPM))
        
        self.list = wx.ListCtrl(self, wx.NewId(),
                                 size = wx.Size(400, 120),
                                 style = wx.LC_ICON | wx.SUNKEN_BORDER | wx.LC_NO_HEADER)

        self.list.SetImageList(self.il, wx.IMAGE_LIST_NORMAL)
        sizer.Add(self.list, 2, wx.ALL|wx.GROW, 5)
        index = 0
        self.templates = []
        for plugin in wx.GetApp().frame.plugins:
            if hasattr(plugin, "get_new_templates"):
                for templ in plugin.get_new_templates():
                    self.list.InsertImageStringItem(index, templ[0], index)
                    self.templates.append( (plugin, templ) )
                    index = index + 1
                    
        wx.EVT_LIST_ITEM_SELECTED(self.list, self.list.GetId(), self.on_change_selection)

        self.description = wx.TextCtrl(self, wx.NewId(), style = wx.TE_MULTILINE | wx.TE_READONLY, size=(100, 60))
        sizer.Add(self.description, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 3)
                
        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, _("Name :"))
        label.SetHelpText(_("The full name of your game"))
        box.Add(label, 0, wx.GROW|wx.ALL, 2)

        self.name = wx.TextCtrl(self, -1, "", size=(80,-1))
        self.name.SetHelpText(_("The full name of your game"))
        wx.EVT_KILL_FOCUS(self.name, self.on_kill_focus)
        box.Add(self.name, 1, wx.GROW|wx.ALL, 2)

        sizer.AddSizer(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 3)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, _("Short name :"))
        label.SetHelpText(_("Will be used to name files"))
        box.Add(label, 0, wx.GROW|wx.ALL, 2)

        self.normname = IdentifierCtrl(self, -1, "", size=(80,-1))
        self.normname.SetHelpText(_("Will be used to name files"))
        box.Add(self.normname, 1, wx.GROW|wx.ALL, 2)

        sizer.AddSizer(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 3)

        box = wx.BoxSizer(wx.HORIZONTAL)

        import  wx.lib.filebrowsebutton as filebrowse
        self.dbb = filebrowse.DirBrowseButton(self, -1, changeCallback = self.dbbCallback)

        import os
        if os.name == "nt":
            import winshell
            self.folder = winshell.my_documents ()
        else:
            self.folder = os.path.expanduser('~')
        self.dbb.SetValue(self.folder)

        box.Add(self.dbb, 2, wx.GROW|wx.ALL, 2)
        
        sizer.AddSizer(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 3)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        box = wx.StdDialogButtonSizer()

        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        btn = wx.Button(self, wx.ID_OK, _("Ok"))
        btn.SetDefault()
        box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        wx.EVT_BUTTON(self, wx.ID_OK, self.OnOK)

        btn = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
        box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0,  wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)

        item = self.list.GetNextItem(-1,
                                     wx.LIST_NEXT_ALL)
        if item != -1:
            self.list.SetItemState(item, -1,
                                     wx.LIST_STATE_SELECTED)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

    def on_change_selection(self, evt):
        self.description.SetValue(self.templates[evt.GetIndex()][1][1])
        
    def OnOK(self, event):
        self.guess_normname()
        if not os.path.exists(self.folder):
            dlg = wx.MessageDialog(self,
                _("The specified folder does not exist"),
                _("Invalid folder"), wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            normname = self.normname.GetValue().strip()
            if self.name.GetValue().strip() and normname and self.folder:
                folder = os.path.join(self.folder, normname)
                if os.path.exists(folder):
                    dlg = wx.MessageDialog(self,
                        _("The directory already exists. Do you want to continue ?"),
                        _("Warning"), wx.YES | wx.NO)
                    if dlg.ShowModal() == wx.ID_YES:
                        self.EndModal(wx.ID_OK)
                    dlg.Destroy()
                else:
                    try:
                        os.makedirs(folder)
                        self.EndModal(wx.ID_OK)
                    except:
                        dlg = wx.MessageDialog(self, _("Cannot create directory ") + folder, _("Error"))
                        dlg.ShowModal()
                        dlg.Destroy()

    def guess_normname(self):
        if not self.normname.GetValue():
            s = ""
            for i in self.name.GetValue():
                if re.match("[a-zA-Z_0-9]", i):
                    s += i
            self.normname.SetValue(s)

    def on_kill_focus(self, evt):
        self.guess_normname()
                    
def new_project(parent):
    return Newproject.new_project(parent)
    
