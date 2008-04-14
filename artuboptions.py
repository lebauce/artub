import wx
from configmanager import config

[wxID_WXPANEL1, wxID_WXPANEL1CHECKBOX1] = map(lambda _init_ctrls: wx.NewId(), range(2))

class ArtubOptions(wx.Panel):
    def _init_ctrls(self, prnt):
        wx.Panel.__init__(self, id = wxID_WXPANEL1, name = '', parent = prnt,
                          pos = wx.Point(0, 0), size = wx.Size(337, 500),
                          style = wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(337, 150))

        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.checkBox1 = wx.CheckBox(id = wxID_WXPANEL1CHECKBOX1,
              label=_("Load last project at startup"), name = "",
              parent = self, pos = wx.Point(24,
              32), size = wx.Size(270, 23), style = 0)
        sizer.Add(self.checkBox1, 0, wx.ALL, 10)

        import glob
        import os.path
        import wx.lib.langlistctrl as langlistctrl
        langs = glob.glob(os.path.join(wx.GetApp().artub_path, "locale", "*"))
        only = []
        for lang in langs:
            l = os.path.basename(lang)
            if os.path.isdir(lang):
                only.append(wx.Locale.FindLanguageInfo(l).Language)
        self.langlist = langlistctrl.LanguageListCtrl(self, -1, 
              filter=langlistctrl.LC_ONLY, only=only, select = wx.LANGUAGE_DEFAULT, size = wx.Size(270, 100))
        sizer.Add(self.langlist, 0, wx.ALL, 10)

        self.SetSizer(sizer)
        sizer.Fit(self)
              
        try:
            self.checkBox1.SetValue(config["auto_load"] == 'True')
        except IndexError: self.checkBox1.SetValue(False)

    def __init__(self, parent, id):
        self._init_ctrls(parent)
        
    def OnOk(self):
        config["auto_load"] = self.checkBox1.IsChecked()
