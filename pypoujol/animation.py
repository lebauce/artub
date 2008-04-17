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
from OpenGL.GLU import gluBuild2DMipmaps, gluUnProject
from OpenGL.GLUT import *
from spritepool import SpritePool
from os import getcwd
from os.path import join
import wx
from screen import get_screen

class Color(list):
    def __init__(self, r, g, b, a = 255):
        self.append(r)
        self.append(g)
        self.append(b)
        self.append(a)
        
class Point:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def __getitem__(self, index):
        if index == 0: return self.x
        else: return self.y
        
    def __setitem__(self, index, value):
        if index == 0: self.x = value
        else: self.y = value
        
anim_classes = {}
parent_sprite = []
global_dict = {}

class AnimationMetaClass(type):
    def __new__(self, name, bases, dct):
        n = type.__new__(self, name, bases, dct)
        ignore = False
        if wx.GetApp():
            Behaviour = wx.GetApp().gns.getattr("Behaviour")
            for i in bases:
                if i == Behaviour or issubclass(i, Behaviour):
                    ignore = True
            if not ignore and name != "Animation" and dct.has_key("filenames"):
                item = (name, dct["filenames"], n)
                if not anim_classes.has_key(name):
                    anim_classes[name] = item
        return n
        
class Animation(object):
    __metaclass__ = AnimationMetaClass
    filenames = []
    nb_frames = 0
    nbframes = 0
    virtual_frames = 0
    delays = []
    hotspots = []
    orders = []
    move_offsets = []
    pool = SpritePool()
        
    def __del__(self):
        pass # glDeleteTextures([self._id])

    def load(self):
        if self.loaded: return
        self._size, self._data, self.__id, mode = self.pool.load_image(self.name)
        glBindTexture(self._id)
        get_screen().bind_texture(self._id)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR_MIPMAP_NEAREST)
        if mode == GL_RGB:
            # Only this function works...
            gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, self._size[0], self._size[1], GL_RGBA, GL_UNSIGNED_BYTE, self.data)
            # glTexImage2D(GL_TEXTURE_2D, 1, 1, size[0], size[1], 0, GL_COLOR_INDEX, GL_UNSIGNED_BYTE, data)
            # gluBuild2DMipmaps(GL_TEXTURE_2D, 4, size[0], size[1], GL_COLOR_INDEX, GL_UNSIGNED_BYTE, data)
        else:
            gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, size[0], size[1], GL_RGBA, GL_UNSIGNED_BYTE, self.data)
        self.frame_width = self._size[0] / self.nbframes
        self.loaded = True
        for i in xrange(self.nbframes):
            self.frames.append((self.size, self.data, self._id))
    
    def is_loaded(self): return self.loaded
    
    def add_frame(self, filename, color = None):
        self.filenames.append(filename)
        self.nbframes += 1
        self.nb_frames += 1
        
    def build(self):
        if self.loaded: return
        frames = []
        for i in self.filenames:
            size, data, _id, mode = self.pool.load_image(i)
            frames.append((size, data, _id))
            get_screen().bind_texture(_id)
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR_MIPMAP_NEAREST)
            if mode == GL_RGB:
                gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, size[0], size[1], GL_RGBA, GL_UNSIGNED_BYTE, data)
                #glTexImage2D(GL_TEXTURE_2D, 1, 1, size[0], size[1], 0, GL_COLOR_INDEX, GL_UNSIGNED_BYTE, data)
                #gluBuild2DMipmaps(GL_TEXTURE_2D, 4, size[0], size[1], GL_COLOR_INDEX, GL_UNSIGNED_BYTE, data)
            else:
                gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, size[0], size[1], GL_RGBA, GL_UNSIGNED_BYTE, data)
        self.loaded = True
        self.frames = frames
        self.nbframes = len(self.filenames)
        self.nb_frames = len(self.filenames)
        
        for i in xrange(self.virtual_frames - len(self.orders)):
            if self.nb_frames:
                self.orders.append(i % self.nb_frames)
            else:
                self.orders.append(0)

        for i in xrange(self.virtual_frames - len(self.delays)):
            self.delays.append(100)

        for i in xrange(self.virtual_frames - len(self.hotspots)):
            self.hotspots.append(Point(0, 0))

        for i in xrange(self.virtual_frames - len(self.move_offsets)):
            self.move_offsets.append(Point(0, 0))
            
    def set_frame(self, frame):
        self.size, self.data, self._id = self.frames[frame]
        
    def __init__(self):
        self.frames = []
        self.loaded = False

        self.nbframes = len(self.filenames)
        self.nb_frames = self.nbframes

        self.build()

        if not self.virtual_frames:
            self.virtual_frames = self.nb_frames

        if self.nbframes:
            self.size, self._id, self._data = self.frames[0]
        else:
            self.size = (50, 50)
            self._id = 0
            self._data = None
        
        for i in xrange(self.virtual_frames - len(self.orders)):
            self.orders.append(i % self.nb_frames)
        for i in xrange(self.virtual_frames - len(self.hotspots)):
            self.hotspots.append(Point(0, 0))
        for i in xrange(self.virtual_frames - len(self.move_offsets)):
            self.move_offsets.append(Point(0, 0))
                
    def draw(self):
        pass
    
    def get_size(self):
        self.load()
        return self._size
    
    def set_size(self, size):
        self._size = size
        
    def get_id(self):
        self.load()
        return self.__id
    
    def set_id(self, id):
        self.__id = id
        
    def get_data(self):
        self.load()
        return self._data
    
    def set_data(self, data):
        self._data = data
        
    def get_frame_width(self):
        self.load()
        return self._frame_width
    
    def set_frame_width(self, frame_width):
        self._frame_width = frame_width
        
    _id = property(get_id, set_id)
    data = property(get_data, set_data)
    size = property(get_size, set_size)
    
class NoImage(Animation):
    filenames = [join(join(getcwd(), "images"), "noimage.png")]
    nbframes = 1
    virtual_frames = 1
    def __init__(self):
        Animation.__init__(self)
        self.__glumolinit__()
    def __glumolinit__(self):
        self.orders = [ 0 ]
    
        
