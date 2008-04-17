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

import wx.py.shell
import images
from depplatform import get_image_path

STEP_ID, NEXT_ID, RETURN_ID, CONTINUE_ID, GO_TO_CURSOR_ID, DEBUG_STOP_ID = range(11, 17)

class DebugBar(wx.ToolBar):
    name = _('Debug bar')
    def __init__(self, parent=None, id=-1, title = _("Debug"),
                 pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_HORIZONTAL,
                 name = "debugbar", value = None):
        
        wx.ToolBar.__init__(self, parent, id, pos, size, style)
        self.artub = wx.GetApp().frame

        self.SetToolBitmapSize(wx.Size(16, 16))
        bmp = wx.Bitmap(get_image_path("breakpoint.xpm"))
        self.AddSimpleTool(self.artub.breakID, bmp, _("Toggle breakpoint"), _("Toggle breakpoint"))
        bmp = wx.Bitmap(get_image_path("go.xpm"))
        self.AddSimpleTool(self.artub.runprojectID, bmp, _("Go"), _("Go"))
        self.EnableTool(self.artub.runprojectID, False)
        bmp = wx.Bitmap(get_image_path("step.xpm"))
        self.AddSimpleTool(STEP_ID, bmp, _("Step"), _("Step"))
        bmp = wx.Bitmap(get_image_path("next.xpm"))
        self.AddSimpleTool(NEXT_ID, bmp, _("Next"), _("Next"))
        bmp = wx.Bitmap(get_image_path("return.xpm"))
        self.AddSimpleTool(RETURN_ID, bmp, _("Return"), _("Return"))
        self.AddSimpleTool(CONTINUE_ID, bmp, _("Continue"), _("Continue"))
        bmp = wx.Bitmap(get_image_path("gotocursor.xpm"))
        self.AddSimpleTool(GO_TO_CURSOR_ID, bmp, _("Go to cursor"), _("Go to cursor"))
        # bmp = wx.Bitmap(get_image_path("pause.png"))
        # self.AddSimpleTool(PAUSE_ID, bmp, _("Pause"), _("Pause"))
        bmp = wx.Bitmap(get_image_path("debugstop.xpm"))
        self.AddSimpleTool(DEBUG_STOP_ID, bmp, _("Stop"), _("Stop"))
        self.Bind(wx.EVT_TOOL, self.on_toggle_breakpoint, id=self.artub.breakID)
        self.Bind(wx.EVT_TOOL, self.artub.on_debug_run, id=self.artub.runprojectID)
        self.Bind(wx.EVT_TOOL, self.on_step, id=STEP_ID)
        self.Bind(wx.EVT_TOOL, self.on_next, id=NEXT_ID)
        self.Bind(wx.EVT_TOOL, self.on_return, id=RETURN_ID)
        self.Bind(wx.EVT_TOOL, self.on_continue, id=CONTINUE_ID)
        self.Bind(wx.EVT_TOOL, self.on_go_to_cursor, id=GO_TO_CURSOR_ID)
        # self.Bind(wx.EVT_TOOL, self.on_pause, id=PAUSE_ID)
        self.Bind(wx.EVT_TOOL, self.on_stop, id=DEBUG_STOP_ID)
        
        self.set_debugging(self.artub.debugging)
        
        self.Realize()

    def set_debug_running(self):
        self.EnableTool(9, False)
        self.EnableTool(STEP_ID, False)
        self.EnableTool(NEXT_ID, False)
        self.EnableTool(RETURN_ID, False)
        self.EnableTool(CONTINUE_ID, False)
        if self.artub.active_editor:
            self.EnableTool(GO_TO_CURSOR_ID, self.artub.active_editor.name == "akiki")
        else:
            self.EnableTool(GO_TO_CURSOR_ID, False)
        # self.EnableTool(PAUSE_ID, False)
        self.EnableTool(DEBUG_STOP_ID, True)

    def set_debugging(self, state):
        self.EnableTool(STEP_ID, state)
        self.EnableTool(NEXT_ID, state)
        self.EnableTool(RETURN_ID, state)
        self.EnableTool(CONTINUE_ID, state)
        if self.artub.active_editor:
            self.EnableTool(GO_TO_CURSOR_ID, self.artub.active_editor.name == "akiki")
        else:
            self.EnableTool(GO_TO_CURSOR_ID, False)
        # self.EnableTool(PAUSE_ID, state)
        self.EnableTool(DEBUG_STOP_ID, state)
            
    def on_update_ui(self, evt):
        if self.artub.debugging:
            pass
        else:
            pass
            
    def on_step(self, evt):
        self.artub.debugger.on_step()
        
    def on_next(self, evt):
        self.artub.debugger.on_next()
        
    def on_return(self, evt):
        self.artub.debugger.on_return()

    def on_continue(self, evt):
        self.artub.debugger.on_continue()
        
    def on_stop(self, evt):
        self.artub.debugger.on_stop()
        
    def on_go_to_cursor(self, evt):
        self.artub.debugger.on_go_to_cursor()
        
    def on_pause(self, evt):
        pass
    
    def enable_breakpoints(self, state):
        self.EnableTool(10, state)
        
    def enable_go(self, state):
        self.EnableTool(self.artub.runprojectID, state)
        
    def on_toggle_breakpoint(self, evt):
        if self.artub.active_editor and \
           self.artub.active_editor.name == "akiki":
            self.artub.active_editor.on_toggle_breakpoint(evt)
            
    def on_close_window(self, event):
        self.manager.toggle_bar(self.menu_id)
