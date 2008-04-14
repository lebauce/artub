import string
import wx
import wx.lib.masked as masked

class IdentifierCtrl(masked.TextCtrl):
    def __init__(self, parent = None, id = -1, value = "", pos = wx.DefaultPosition, 
                 size = wx.DefaultSize, style = 0, validator = wx.DefaultValidator,
                 name = wx.TextCtrlNameStr):
        masked.TextCtrl.__init__(self, parent, id, value,
                                 mask         = "", #"C{1}N{63}",
                                 excludeChars = "",
                                 formatcodes  = "C>",
                                 includeChars = "_",
                                 validRegex   = "^[a-zA-Z_][a-zA-Z_0-9]*",
                                 validRange   = '',
                                 choices      = '',
                                 choiceRequired = True,
                                 defaultValue = '',
                                 demo         = True,
                                 name         = 'identifier',
                                 useFixedWidthFont = False)
                                 
    def GetValue(self):
        return masked.TextCtrl.GetValue(self).strip()
