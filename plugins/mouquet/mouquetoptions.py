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

[wxID_WXPANEL1] = map(lambda _init_ctrls: wx.NewId(), range(1))

class MouquetOptions(wx.Panel):
    def _init_utils(self):
        pass

    def _init_ctrls(self, prnt):
        wx.Panel.__init__(self, style=wx.TAB_TRAVERSAL, name='', parent=prnt, pos=wx.DefaultPosition, id=wxID_WXPANEL1, size=wx.Size(200, 100))
        self._init_utils()

    def __init__(self, parent, id):
        self._init_ctrls(parent)
