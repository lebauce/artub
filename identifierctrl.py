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

import string
import wx
import wx.lib.masked as masked

class IdentifierCtrl(masked.TextCtrl):
    def __init__(self, parent = None, id = -1, value = "", pos = wx.DefaultPosition, 
                 size = wx.DefaultSize, style = 0, validator = wx.DefaultValidator,
                 name = wx.TextCtrlNameStr):
        masked.TextCtrl.__init__(self, parent, id, value,
                                 mask         = "CN{31}", # "C{1}N{63}",
                                 excludeChars = " ",
                                 formatcodes  = "F_",
                                 # formatcodes  = "C>",
                                 includeChars = "_",
                                 validRegex   = "^[a-zA-Z_][a-zA-Z_0-9]*",
                                 validRange   = '',
                                 choices      = '',
                                 validRequired = True,
                                 choiceRequired = True,
                                 defaultValue = '',
                                 demo         = True,
                                 name         = 'identifier',
                                 stopFieldChangeIfInvalid = True,
                                 useFixedWidthFont = False)
                                 
    def GetValue(self):
        return masked.TextCtrl.GetValue(self).strip()
