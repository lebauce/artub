import wx
import wx.lib.flatnotebook as fnb

def create(parent):
    return OptionsWindow(parent)

[wxID_WXOPTIONSDIALOG, wxID_WXOPTIONSNOTEBOOK, wxID_WXDIALOG1BUTTON1, wxID_WXDIALOG1BUTTON2
] = map(lambda _init_ctrls: wx.NewId(), range(4))

[wxID_WXPANEL1] = map(lambda _init_ctrls: wx.NewId(), range(1))

class OptionsWindow(wx.Dialog):
    def __init__(self, parent):
        self.parent = parent
        self.pages = []
        
        wx.Dialog.__init__(self, id=wxID_WXOPTIONSDIALOG, name='', parent=parent,
              pos=wx.DefaultPosition, size=wx.Size(500, 400),
              style=wx.DEFAULT_DIALOG_STYLE, title=_("Options"))

        self.SetExtraStyle(wx.DIALOG_EX_METAL)
        sizer2 = wx.StdDialogButtonSizer()

        self.okbutton = wx.Button(id=wx.ID_OK, label=_("Ok"),
              parent=self, style=0)
        
        wx.EVT_BUTTON(self.okbutton, wx.ID_OK, self.OnOk)

        self.cancelbutton = wx.Button(id=wx.ID_CANCEL, label=_("Cancel"),
              parent=self, style=0)

        self.notebook = fnb.FlatNotebook(id=wxID_WXOPTIONSNOTEBOOK,
              name='notebook1', parent=self, style=fnb.FNB_NO_X_BUTTON)

        self.create_plugins_pages()
        
        sizer = self.sizer
        
        sizer2.Add(self.okbutton, 0, wx.ALIGN_CENTRE | wx.ALL)
        sizer2.Add(self.cancelbutton, 0, wx.ALIGN_CENTRE | wx.ALL)
        sizer.Add(sizer2, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER | wx.ALL, 5)
        
        self.notebook.SetSelection(0)
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.SetAutoLayout(True)
        self.CenterOnScreen()
        

    def create_plugins_pages(self):
        from artuboptions import ArtubOptions
        page = ArtubOptions(self.notebook, -1)
        self.pages.append(page)
        self.notebook.AddPage(page, _("Options"))
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.notebook.SetMinSize(wx.Size(400, 250))
        sizer.Add(self.notebook, 0, wx.ALL, 10)
        for editor in self.parent.editors + self.parent.plugins:
            if not hasattr(editor, "options"): continue
            try:
                pageobj, title = editor.options
                if pageobj:
                    page = pageobj(self.notebook, -1)
                    self.pages.append(page)
                    self.notebook.AddPage(page, title)
            except:
                raise
                wx.LogMessage("Can't create option page for plugin " + editor.__name__)
        self.sizer = sizer

        
    def OnOk(self, event):
        for i in self.pages:
           if hasattr(i, "OnOk"):
              i.OnOk()
        event.Skip()
        