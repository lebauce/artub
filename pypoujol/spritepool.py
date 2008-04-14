import Image
from os.path import join, basename, isabs
from screen import get_screen
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
