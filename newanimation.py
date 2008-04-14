import wx
import  wx.lib.filebrowsebutton as filebrowse

class NewAnimationDialog(wx.Dialog):
    def __init__(
            self, parent, ID=-1, title=_("New animation"), size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP):

        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)
        self.this = pre.this

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.text = wx.StaticText(self, -1, "Name")
        sizer2.Add(self.text, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        
        self.name = wx.TextCtrl(self, -1, "")
        sizer2.Add(self.name, 1,  wx.ALIGN_CENTRE | wx.ALL, 5)
        
        sizer.Add(sizer2, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.filename = filebrowse.FileBrowseButton(self, -1, size=(400, -1))
        sizer2.Add(self.filename, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        
        sizer.Add(sizer2, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL)
        
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.ok = wx.Button(self, wx.ID_OK, _("Ok"))
        sizer2.Add(self.ok, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        
        self.cancel = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
        sizer2.Add(self.cancel, 1,  wx.ALIGN_CENTRE | wx.ALL, 5)
        
        sizer.Add(sizer2, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
