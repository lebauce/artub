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

from sprite import Sprite
from OpenGL.GL import *
import wx

class ZPlane(Sprite):
    def render(self):
        glClearStencil(0)
        glEnable(GL_STENCIL_TEST)
        glStencilFunc(GL_ALWAYS, 1, 255)
        glStencilOp(GL_REPLACE, GL_REPLACE, GL_REPLACE)
        glDisable(GL_DEPTH_TEST)
        glColorMask(0,0,0,0)
        Sprite.render(self)
        glColorMask(1,1,1,1)
        glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
        glStencilFunc(GL_EQUAL, 1, 0)
        
        
