import wx

[wxID_WXPANEL1] = map(lambda _init_ctrls: wx.NewId(), range(1))

class WoolseyOptions(wx.Panel):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wx.Panel.__init__(self, style=wx.TAB_TRAVERSAL, name='', parent=prnt, pos=wx.DefaultPosition, id=wxID_WXPANEL1, size=wx.Size(200, 100))
        self._init_utils()

    def __init__(self, parent, id):
        self._init_ctrls(parent)
