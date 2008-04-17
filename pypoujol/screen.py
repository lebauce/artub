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

from OpenGL.GL import *
import _psyco

class GScreen:
    def __init__(self):
        self.children = []
        self.screen = None
        self._alpha = 1.0
        self.alpha = 1.0
        self.z = 0
        
    def draw(self):
        for i in self.children:
            i.draw()
            
    def print_children(self):
        for i in self.children:
            print i

    def remove(self, child):
        self.children.remove(child)

_screen = None
            
class Screen(object):
    def __init__(self):
        self._current_texture = 0
        
    def bind_texture(self, id):
        #if self._current_texture == id:
        #    return
        #else:"""
        glBindTexture(GL_TEXTURE_2D, id)
        self._current_texture = id
    
    _psyco.proxy    
    def fill(self, color):
        glClearColor(*_switch_color(color))
        glClear(GL_COLOR_BUFFER_BIT)

    _psyco.proxy    
    def blit(self, surface, dest):
        glPushMatrix()
        glTranslatef(dest[0], dest[1], 0)
        if surface.rotation != 0.0:
            glRotatef(surface.rotation, 0, 0, 1)
        if surface.scale != 1.0:
            scale = surface.scale
            glScalef(scale,scale,scale)
        surface.render()
        glPopMatrix()
        
_psyco.proxy    
def _switch_color(color):
    nc = []
    for c in color:
        if c == 0:
            nc.append(0.0)
        else:
            nc.append(255.0 / c)
    if len(nc) < 4:
        nc.append(1.0)
    return nc

def set_mode(w,h):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0,w,h,0,1,0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glShadeModel(GL_SMOOTH)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)

    global _screen
    if not _screen:
        _screen = Screen()
    return _screen

def set_screen(screen):
    global _screen
    _screen = screen
    
def get_screen():
    return _screen
