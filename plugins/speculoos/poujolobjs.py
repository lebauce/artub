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

import pypoujol
from OpenGL.GL import *
from box import POINT_WIDTH

class RegionPoint(pypoujol.Sprite):
    def __init__(self, parent = None, frames = 1, virtual_frames = -1):
        pypoujol.Sprite.__init__(self, parent)
        self.x = 0
        self.y = 0
        self.color = (1.0, 1.0, 1.0, 1.0)
        self.visible = True

    def draw(self):
        if not self.visible: return
        glDisable(GL_TEXTURE_2D)
        glPushMatrix()
        glLoadIdentity()
        glBegin(GL_QUADS)
        x, y, w, h = self.x, self.y, POINT_WIDTH, POINT_WIDTH
        glColor4f(*self.color)
        glVertex2f(x - w / 2, y - h / 2)
        glColor4f(*self.color)
        glVertex2f(x + w / 2, y - h / 2)
        glColor4f(*self.color)
        glVertex2f(x + w / 2, y + h / 2)
        glColor4f(*self.color)
        glVertex2f(x - w / 2, y + h / 2)
        glEnd()
        glPopMatrix()
        glEnable(GL_TEXTURE_2D)

class Contour(pypoujol.Sprite):
    def __init__(self, parent = None, frames = 1, virtual_frames = -1, loop = False, hotspot = (0, 0)):
        pypoujol.Sprite.__init__(self, parent)
        self.hotspot = hotspot
        self.box = None
        self.color = (1.0, 1.0, 1.0, 1.0)
        self.visible = True
        self.gpoints = []
        self.loop = loop

    def draw(self):
        if not self.box or not self.visible or len(self.box.points) < 2: return
        glDisable(GL_TEXTURE_2D)
        glTranslatef(self.hotspot[0], self.hotspot[1], 0)
        if self.loop:
            glBegin(GL_LINE_LOOP)
        else:
            glBegin(GL_LINE_STRIP)
        glColor4f(*self.color)
        if self.box:
            for i in self.box.points:
                glVertex2f(i[0], i[1])
        glEnd()
        glEnable(GL_TEXTURE_2D)

    def set_box(self, box):
        self.box = box
