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
from wx import glcanvas
from OpenGL.GL import *
from screen import set_mode
from new import instancemethod
from animation import Animation

def _OnIdle(self, event):
    self.parent.Refresh()
    event.Skip()

space_width = 640 + 3000
space_height = 480 + 3000

class ClanlibCanvas:
    def __init__(self, parent, game, size = wx.DefaultSize):
        self.canvas = None
        for i in wx.GetApp().artub_frame.alive_editors:
            if hasattr(i, "canvas"):
                self.canvas = glcanvas.GLCanvasWithContext(parent, i.canvas.GetContext(), -1, size=size, style = wx.ALWAYS_SHOW_SB | wx.VSCROLL | wx.HSCROLL)
                break
        if not self.canvas:
            Animation.pool.clear()
            self.canvas = glcanvas.GLCanvas(parent, -1, \
                              size = size, style = wx.ALWAYS_SHOW_SB | wx.VSCROLL | wx.HSCROLL, \
                              attribList = [glcanvas.WX_GL_RGBA, \
                                            glcanvas.WX_GL_DOUBLEBUFFER, \
                                            glcanvas.WX_GL_STENCIL_SIZE, 8])
        
        self.parent = parent
        self.init = False
        # initial mouse position
        self.lastx = self.x = 30
        self.lasty = self.y = 30
        wx.EVT_ERASE_BACKGROUND(self.canvas, self.OnEraseBackground)
        self.canvas.Bind(wx.EVT_PAINT, self.OnPaint)
        self.canvas.Bind(wx.EVT_IDLE, self.OnIdle)
        self.game = game
        
        import platform
        if platform.system() == 'Darwin':
            self.mac = True
        
    def Refresh(self): self.canvas.Refresh()
    
    def OnIdle(self, event):
        self.parent.Refresh()
        event.Skip()
        
    def OnEraseBackground(self, event):
        pass # Do nothing, to avoid flashing on MSW.

    def OnDraw(self):
        size = self.canvas.GetClientSize()
        if hasattr(self, "mac"):
            glViewport(-self.canvas.GetScrollPos(wx.HORIZONTAL), self.canvas.GetScrollPos(wx.VERTICAL), size.width, size.height)
            self.game.screen.screen = set_mode(size.width, size.height)
        else:
            glViewport(-self.canvas.GetScrollPos(wx.HORIZONTAL), size.height - space_height + self.canvas.GetScrollPos(wx.VERTICAL), space_width, space_height) #size.width, size.height)
            self.game.screen.screen = set_mode(space_width, space_height)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT);
        
        self.game.draw()
        self.canvas.SwapBuffers()
        
    def OnPaint(self, event):
        dc = wx.PaintDC(self.canvas)
        self.canvas.SetCurrent()
        self.OnDraw()
        event.Skip()
