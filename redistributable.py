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
platforms = []

class Redistributable:
    def __init__(self):
        artub = wx.GetApp().artub_frame
        for i in artub.plugins:
            if hasattr(i, "dist_platform"):
                platforms.append(i)
        projmenu = artub.mainmenu.GetMenu(artub.mainmenu.FindMenu(_("Tools")))
        id = wx.NewId()
        projmenu.AppendMenu(id, _("Build redistributable"), self.get_menu(projmenu))
        projmenu.Enable(id, False)
        artub._enable_menus.append(id)
                
    def get_menu(self, parent):
        item = wx.Menu()
        for i in platforms:
            id = wx.NewId()
            item.Append(id, i.dist_platform)
            wx.EVT_MENU(wx.GetApp().artub_frame, id, i.on_build)
        return item
