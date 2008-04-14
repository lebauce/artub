import wx

def create(parent):
    return OptionsWindow(parent)

[wxID_WXOPTIONSDIALOG, wxID_WXOPTIONSNOTEBOOK, wxID_WXDIALOG1BUTTON1, wxID_WXDIALOG1BUTTON2
] = map(lambda _init_ctrls: wx.NewId(), range(4))

class ProjectProperties(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, id=wxID_WXOPTIONSDIALOG, name='', parent=parent,
                           pos=wx.Point(256, 167), size=wx.Size(385, 330),
                           style=wx.DEFAULT_DIALOG_STYLE, title=_("Options"))
        self.artub = parent
        self.notebook = wx.Notebook(id=wxID_WXOPTIONSNOTEBOOK, name='notebook1',
                                    parent=self, pos=wx.Point(8, 8), style=0)
        self.create_plugins_pages()
        self.CenterOnScreen()
        
    def create_plugins_pages(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        from builder.optionspage import BuilderOptionsPage
        page = BuilderOptionsPage(self.notebook, wx.GetApp().artub_frame.project)
        self.builder_page = page
        self.notebook.AddPage(page, _("Builder"))
        sizer.Add(self.notebook, 0, wx.ALL, 5)
        
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        okbutton = wx.Button(id=wx.ID_OK, label=_("Ok"),
                             name='button1', parent=self, style=0)

        wx.EVT_BUTTON(okbutton, wx.ID_OK, self.OnOk)

        cancelbutton = wx.Button(id=wx.ID_CANCEL, label=_("Cancel"),
                                 name='button2', parent=self, style=0)

        sizer2.Add(okbutton, 0, wx.ALIGN_CENTER)
        sizer2.Add(cancelbutton, 0, wx.ALIGN_CENTER)
        sizer.Add(sizer2, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER | wx.ALL, 10)
        self.SetSizer(sizer)
        sizer.Fit(self)
        
    def OnOk(self, evt):
        self.builder_page.OnOk()
        evt.Skip()
