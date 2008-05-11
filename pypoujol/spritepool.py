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

import Image
from os.path import join, basename, isabs
from screen import get_screen
import numpy.numarray
from OpenGL.GL import glTexParameteri, glGenTextures, GL_TEXTURE_2D, \
                      GL_TEXTURE_MAG_FILTER, GL_LINEAR, GL_TEXTURE_MIN_FILTER, \
                      GL_LINEAR_MIPMAP_NEAREST, GL_RGB, GL_RGBA, GL_UNSIGNED_BYTE, \
                      glTexImage2D, GL_RGBA16, glEnable, GL_COLOR_INDEX
                      
from OpenGL.GLU import gluBuild2DMipmaps, gluUnProject
from wx import GetApp

class SpritePool:
    def __init__(self):
        self.items = {}
        
    def clear(self):
        self.items = {}
        
    def load_image(self, filename):
        if not isabs(filename):
            filename = join(GetApp().frame.project.project_path, filename)
        try:
            f = open(filename)
            f.seek(0, 2)
            filesize = f.tell()
            f.close()
        except:
            filesize = -1
        k = self.items.get(filename)
        if k:
            if k[4] == filesize:
                return k[:4]
        try:
            image = Image.open(filename)
        except:
            raise
            image = Image.open(join(GetApp().artub_path, "images", "cannotopen.png"))

        if image.mode == 'P':
            image = image.convert('RGB')
            mode = GL_RGB
        elif image.mode == 'RGB':
            mode = GL_RGB
        else:
            mode = GL_RGBA

        if mode == GL_RGB:
            image = image.convert('RGBA')

        size = image.size
        data = image.tostring()
        _id = glGenTextures(1)
        self.items[filename] = (size, data, _id, mode, filesize)
        return size, data, _id, mode
