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
from configmanager import config
import wx.aui as PyAUI

class ToolbarManager:
    def __init__(self, artub_frame):
        self.artub_frame = artub_frame
        self.toolbars = []
        
    def create_toolbar(self, toolbar, args = None, keywords = {}, infos = None, window_attr_name = None):
        if not infos:
            infos = PyAUI.PaneInfo().ToolbarPane().Left().GripperTop().TopDockable(False).BottomDockable(False).DestroyOnClose(False)
        try:
            s = self.artub_frame.config.Read(toolbar.__name__)
            x, y, cx, cy, state, floating, direction, pos, row, layer, dock_proportion = s.split('|')
            state = int(state) != 0
        except:
            x = wx.DefaultPosition.x
            y = wx.DefaultPosition.y
            cx = wx.DefaultSize.x
            cy = wx.DefaultSize.y
            state = True 
            floating = False
            direction = PyAUI.AUI_DOCK_LEFT
            pos = 0
            row = 0
            layer = 0
            dock_proportion = 0
        if int(floating):
            infos = infos.Float()
            infos = infos.FloatingPosition(wx.Point(int(x), int(y))). \
                        FloatingSize(wx.Size(int(cx), int(cy))). \
                        Row(int(row)). \
                        Layer(int(layer)). \
                        Direction(int(direction))
            infos.dock_proportion = int(dock_proportion)
        infos = infos.Position(int(pos)).Show(state)
        try:
            self.artub_frame.Freeze()
            if not args:
                tb = toolbar(parent = self.artub_frame, pos = wx.Point(int(x), int(y)), size = wx.Size(int(cx), int(cy)), id = -1)
                if window_attr_name:
                    tb = getattr(tb, window_attr_name)
            else:
                keywords["parent"] = self.artub_frame
                keywords["size"] = wx.Size(int(cx), int(cy))
                keywords["pos"] = wx.Point(int(x), int(y))
                tb = toolbar(*args, **keywords)
                if window_attr_name:
                    tb = getattr(tb, window_attr_name)
                
            self.artub_frame._mgr.AddPane(tb, infos)
            tt = [tb, toolbar, (args, keywords, infos, window_attr_name)]
            try: tb.SetTitle(self.get_bar_name(tt))
            except: tb.SetName(self.get_bar_name(tt))
            tb.Raise()
            tb.manager = self
            self.artub_frame.config.Read(toolbar.__name__)
            self.toolbars.append(tt)
            pane = self.artub_frame._mgr.GetPane(tb)
            if state:
                tb.Show(False)
                pane.Show()
            else:
                tb.Show(True)
                pane.Show(False)
            self.artub_frame._mgr.Update()
            try: self.artub_frame.Thaw()
            except: pass # Because of a strange behaviour on Windows
        except:
            raise
            self.artub_frame.Thaw()        
            return tb
        return tb

    def remove_toolbar(self, toolbar):
        n = 0
        for i in self.toolbars:
            if i[0] == toolbar:
                self.artub_frame._mgr.DetachPane(toolbar)
                toolbar.Destroy()
                del self.toolbars[n]
                break
            n = n + 1
            
    def care_of_exit(self):
        self.save()
            
    def get_bar(self, name):
        for i in self.toolbars:
            if name == self.get_bar_name(i):
                return i[0]

    def get_bar_by_id(self, id):
        for i in self.toolbars:
            if i[0].menu_id == id:
                return i[0]

    def get_bar_name(self, i):
        try:
            return i[0].name
        except:
            return i[1].__name__
    
    def care_of_menu(self, menu):
        self.menu = menu
        for i in self.toolbars:
            index = wx.NewId()
            i[0].menu_id = index
            name = self.get_bar_name(i)
            menu.Append(index, name, _("Shows ") + name, wx.ITEM_CHECK)
            try:
                state = config[i[1].__name__].split('|')[4]
            except:
                state = '0'
            if state == '1':
                menu.Check(index, True)
            wx.EVT_MENU(self.artub_frame, index, self.artub_frame.on_window_toggle_bar)

    def show_toolbar(self, toolbar, state):
        pane = self.artub_frame._mgr.GetPane(toolbar)
        pane.Show(state)
        self.artub_frame._mgr.Update()
        
    def on_close_toolbar(self, toolbar):
        for i in self.toolbars:
            if i[0] is toolbar:
                self.toggle_bar(toolbar.menu_id)
                
    def toggle_bar(self, id):
        for i in self.toolbars:
            if i[0].menu_id == id:
                pane = self.artub_frame._mgr.GetPane(i[0])
                state = not pane.IsShown()
                if state:
                    pane.Show()
                else:
                    pane.Hide()
                self.artub_frame._mgr.Update()
                self.menu.Check(i[0].menu_id, state)
                return
    
    def save_toolbar(self, i):
        tb = i[0]
        pane = self.artub_frame._mgr.GetPane(tb)
        s = str(pane.floating_pos.x) + '|' + str(pane.floating_pos.y) + \
             '|' + str(pane.floating_size.width) + \
             '|' + str(pane.floating_size.height) + \
             '|' + str(1 - (not pane.IsShown())) + \
             '|' + str(int(pane.IsFloating())) + \
             '|' + str(int(pane.dock_direction)) + \
             '|' + str(int(pane.dock_pos)) + \
             '|' + str(int(pane.dock_row)) + \
             '|' + str(int(pane.dock_layer)) + \
             '|' + str(int(pane.dock_proportion))
        self.artub_frame.config.Write(i[1].__name__, s)
        
    def save(self):
        for i in self.toolbars: self.save_toolbar(i)
        self.artub_frame.config.Flush(True)
            

    