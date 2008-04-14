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
        
        
