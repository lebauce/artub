from OpenGL.GL import *
from screen import get_screen
from time import clock
from game import get_game
from Enum import *
from new import classobj
from animation import Animation, AnimationMetaClass, global_dict
from numpy import array, dot
from math import cos, sin, pi
import wx
matrixmultiply = dot

class SpriteMetaClass(type):
    def __new__(self, name, bases, dct):
        n = type.__new__(self, name, bases, dct)
        autos = []
        for i in dct.keys():
            if isinstance(dct[i], type) and name != self.__class__.__name__:
                dct[i].parent_class = n
                global_dict[dct[i].__name__] = n
            if getattr(dct[i], "auto", None):
                autos.append((dct[i].auto, dct[i]))
        n.__autos__ = autos
        return n
        
    def __init__(self, name, bases, dict):
        super(SpriteMetaClass, self).__init__(name, bases, dict)
        """for i in dict.keys():
            if isinstance(dict[i], type) and name != self.__class__.__name__:
                dict[i].parent_class = name
                global_dict[dict[i].__name__] = name"""
                
"""
class RegionMetaClass(type):
    def __init2__(self, name, bases, dict):
        super(RegionMetaClass, self).__init__(name, bases, dict)
        for i in dict.keys():
            if isinstance(dict[i], type) and name != self.__class__.__name__:
                global_dict[dict[i].__name__] = name
"""

def mkmatrix(rows, cols):
    count = 1
    mx = [ None ] * rows
    for i in range(rows):
        mx[i] = [0] * cols
        for j in range(cols):
            mx[i][j] = count
            count += 1
    return mx

def mmult(rows, cols, m1, m2):
    m3 = [ None ] * rows
    for i in range( rows ):
        m3[i] = [0] * cols
        for j in range( cols ):
            val = 0
            for k in range( cols ):
                val += m1[i][k] * m2[k][j]
            m3[i][j] = val
    return m3
    
# from poujol import Region, Contour, region_type
class Contour:
    def __init__(self, l):
        pass
    
class Rect:
    def __init__(self, left = 0, top = 0, width = 0, height = 0):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        
    def is_inside(self, point):
        return point[0] >= self.left and point[0] <= self.left + self.width and \
               point[1] >= self.top and point[1] <= self.top + self.height
    
class Region:
    __metaclass__ = SpriteMetaClass
    boxes = []
        
    def __init__(self, parent, *extras):
        self.contours = []
        self.active = True
        
    def from_list(self, l): return self
    def to_string(self): pass
    def is_point_in_region(self, x, y): return False
    def set_boxes(self): pass
    def get_bouncing_box(self): return Rect()
    def cut(self): pass
    def __sub__(self, obj): return self
    def on_enter_region(self, sprite): pass
    def on_leave_region(self, sprite): pass
    def on_move_in_region(self, sprite): pass

class region_type(Enum):
    transparent = 0
    walkable = 1
    non_walkable = 2
    
class direction(Enum):
    south = 0
    north = 1
    west = 2
    east = 3
    
class Sprite(object):
    __metaclass__ = SpriteMetaClass
    class_name = "Sprite"
    
    def __init__(self, parent = None):
        self.parent = parent
        self.x = 0
        self.y = 0
        self.z = 1
        self.angle = 0.0
        self.scale = (1.0, 1.0)
        self._current_frame = 0
        self.current_order = 0
        self._current_anim = None
        self.hotspot = (0, 0)
        self.fading = False
        self.fade_time = 0.0
        self.fade_delay = 0.0
        self.set_to_zero = False
        self.last_time = self.update_time = clock()
        self.is_play_loop = True
        self.is_play_backward = False
        self.is_play_pingpong = False
        self.playing = False
        self.delta = 1
        self._alpha = 1.0
        self._Alpha = 1.0
        self.children = []
        self.visible = True
        self.size = (0, 0)
        self.color = (255, 255, 255, 255)
        self.regions = []
        self.track_position = False
        if parent == None:
            if get_game(): get_game().screen.children.append(self)
        else:
            self.alpha = parent.alpha
            parent.children.append(self)
        if hasattr(self, "autos"):
            for j, i in self.autos:
                klass = wx.GetApp().gns.getattr(i)
                if not issubclass(klass, Animation):
                    obj = klass(self)
                    self.__dict__[j] = obj
                    self.children.append(obj)
        p = getattr(self, "animation", None)
        if p: self.current_anim = p()
        else: self._current_anim = None
        
    def __glumolinit__(self): pass
    
    def set_current_anim(self, anim):
        self._current_anim = anim
        if anim:
            if not anim.is_loaded():
                anim.load()
            self.nbframes = anim.nbframes
            if self.nbframes:
                self.size = anim.frames[0][0]
                anim.set_frame(0)
            
    def get_current_anim(self):
        return self._current_anim
        
    current_anim = property(get_current_anim, set_current_anim)
    
    def get_alpha(self):
        return self._Alpha
        
    def update_alpha(self):
        if self.parent:
            self._alpha = self._Alpha * self.parent._alpha
        else:
            self._alpha = self._Alpha
        for i in self.children:
            i.update_alpha()

    def set_alpha(self, value):
        self._Alpha = value
        if hasattr(self, "parent"): self.update_alpha()
        
    alpha = property(get_alpha, set_alpha)

    def set_current_frame(self, index):
        self.current_order = index
        self._current_frame = self.current_anim.orders[index]
        self.current_anim.set_frame(self._current_frame)
        
    def get_current_frame(self):
        return self.current_order
        
    current_frame = property(get_current_frame, set_current_frame)
    
    def set_position(self, tup):
        if type(tup) == type((1,)):
            self.x, self.y = tup
        else:
           self.x, self.y = tup.x, tup.y
        
    def get_position(self):
        return (self.x, self.y)
    
    position = property(get_position, set_position)
    
    def set_color(self, tup):
        if len(tup) < 4:
            tup = tup + (self.alpha * 255,)
        self._color = tup
        
    def get_color(self):
        return self._color
    
    color = property(get_color, set_color)

    def remove(self, child):
        self.children.remove(child)
        
    def render(self):
        glEnable (GL_BLEND)
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        w, h = self.current_anim.size
        glPushMatrix()
        glTranslatef(self.hotspot[0], self.hotspot[1], 0)
        get_screen().bind_texture(self.current_anim._id)
        glColor4f(self._color[0] / 255., self._color[1] / 255., self._color[2] / 255., self._alpha)
        glBegin(GL_QUADS)
        #glTexCoord2f(self._current_frame * 1.0 / self.nbframes, 0.0)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(0, 0)
        #glTexCoord2f((self._current_frame + 1) * 1.0 / self.nbframes, 0.0)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(w, 0)
        glColor4f(self._color[0] / 255., self._color[1] / 255., self._color[2] / 255., self._alpha)
        #glTexCoord2f((self._current_frame + 1)* 1.0 / self.nbframes, 1.0)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(w, h)
        #glTexCoord2f(self._current_frame * 1.0 / self.nbframes, 1.0)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(0, h)
        glEnd()
        #glTranslatef(-self.hotspot[0], -self.hotspot[1], 0)
        glPopMatrix()
        
    def on_before_draw(self): pass
    def on_after_draw(self): pass
    def on_left_button_down(self): pass
    def on_left_button_up(self): pass
    def on_right_button_down(self): pass
    def on_right_button_up(self): pass
    def on_middle_button_down(self): pass
    def on_middle_button_up(self): pass
    def on_mouse_wheel_up(self): pass
    def on_mouse_wheel_down(self): pass
    def on_mouse_move(self): pass
    def on_left_button_down_repeat(self, time): pass
    def on_right_button_down_repeat(self, time): pass
    def on_middle_button_down_repeat(self, time): pass
    def on_frame_changed(self, frame): pass
    
    def on_focus(self, oldobj): pass
    def on_lose_focus(self, newobj): pass

    def draw(self):
        self.update()
        if not self.visible: return
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        if self.angle != 0.0:
            glRotatef(self.angle, 0, 0, 1)
        if type(self.scale) == type( tuple() ):
            glScalef(self.scale[0], self.scale[1], 1.0)
        else:
            glScalef(self.scale, self.scale, self.scale)
        # self.on_before_draw()
        if self.current_anim and self.current_anim.nbframes > 0: 
            self.render()
        # self.on_after_draw()

        # stencil_test = wx.GetApp().artub_frame.active_editor.stencil_test

        for i in self.children:
            i.draw()

        """
        stencil_test2 = wx.GetApp().artub_frame.active_editor.stencil_test
        if not stencil_test and stencil_test2:
            #glDisable(GL_STENCIL_TEST)
            wx.GetApp().artub_frame.active_editor.stencil_test = False
        """
        
        glPopMatrix()
    
    def fade_out(self, delay):
        dec = self.alpha * 255
        if dec == 0.0: return
        self.fade_time = 0
        self.fading = True
        self.fade_delay = delay / dec
        self.fade_incr = 1 / -dec

    def fade_in(self, delay):
        dec = (1 - self.alpha) * 255
        if dec == 0.0: return
        self.fade_time = 0
        self.fading = True
        self.fade_delay = delay / dec
        self.fade_incr = 1 / dec
        
    def center(self):
        pass

    def update(self):
        c = clock()
        time_elapsed = (c - self.last_time)
        self.last_time = c
        
        fade_time = self.fade_time
        
        if self.set_to_zero:
            fade_time = 0
            self.set_to_zero = 0
        else:
            fade_time = fade_time + time_elapsed

        while self.fading and fade_time >= self.fade_delay:
            fade_time -= self.fade_delay
            self.alpha = self.alpha + self.fade_incr
            if self.alpha < 0:
                self.alpha = 0.0
                self.fading = False
            elif self.alpha > 1:
                self.alpha = 1.0
                self.fading = False
                
        if not self.playing: return

        total_frames = len(self.current_anim.delays)
        total_orders = len(self.current_anim.orders)
        current_frame = self.current_frame 
        current_order = self.current_order
        framedelay = self.current_anim.delays[current_order] / 1000.
        update_time = self.update_time + time_elapsed
        delta = self.delta
        
        if framedelay == 0:
            framedelay = 10
        
        while update_time > framedelay:
            update_time -= framedelay;
            current_order = current_order + delta

            if current_order >= total_frames or current_order < 0:
                if not self.is_play_loop:
                    if self.is_play_backward:
                        delta_frame = -1
                    else:
                        delta_frame = 1
                    if delta_frame != delta or not self.is_play_pingpong:
                        self.on_animation_finished()
                        return

                if self.is_play_pingpong:
                    delta = -delta
                    if delta > 0:
                        current_order = 1
                    else:
                        current_order = total_frames - 2
                else:
                    if self.is_play_backward:
                        current_order = total_frames - 1
                    else:
                        current_order = 0

            self.current_frame = self.current_anim.orders[current_order]

            p = self.current_anim.hotspots[current_order]
                
        self.current_order = current_order
        self.update_time = update_time
        self.fade_time = fade_time
        
    def client_to_screen(self, point):
        angle = self.angle
        centre = (0, 0)
        offset = self.position
        scal = self.scale
        cosa = cos(angle * pi / 180.);
        sina = sin(angle * pi / 180.);
        rot = array(((cosa, -sina, centre[0] * (1 - cosa) + centre[1] * sina),
                     (sina, cosa, centre[1] * (1 - cosa) - centre[0] * sina),
                     (0, 0, 1)))
              
        scale = array(((scal[0], 0, 0),
                       (0, scal[1], 0),
                       (0, 0, 1)))

        trans = array(((1, 0, offset[0]),
                       (0, 1, offset[1]),
                       (0, 0, 1)))

        p = array((point[0], point[1], 1))
        r = matrixmultiply(matrixmultiply(matrixmultiply(rot, scale), trans), p)
        return (r[0], r[1])
        
    def screen_to_client(self, point):
        angle = self.angle
        centre = (0, 0)
        offset = self.position
        if type(self.scale) == type(()):
            scal = (self.scale[0], self.scale[1])
        else:
            scal = (self.scale, self.scale)
        cosa = cos(-angle * pi / 180.);
        sina = sin(-angle * pi / 180.);
        centre = (0, 0)
        rot = array(((cosa, -sina, centre[0] * (1 - cosa) + centre[1] * sina),
                     (sina, cosa, centre[1] * (1 - cosa) - centre[0] * sina),
                     (0, 0, 1)))
              
        scale = array(((1 / scal[0], 0, 0),
                       (0, 1 / scal[1], 0),
                       (0, 0, 1)))

        trans = array(((1, 0, -offset[0]),
                       (0, 1, -offset[1]),
                       (0, 0, 1)))

        p = array((point[0], point[1], 1))
        r = matrixmultiply(matrixmultiply(matrixmultiply(rot, scale), trans), p)
        return (r[0], r[1])

    def on_timer(self):
        self.thread = Timer(self.current_anim.times[self.current_order] / 1000, self.on_timer)
        self.thread.start()
        
    def start(self):
        
        self.playing = True
        self.update_time = 0

    def stop(self):
        self.playing = False
        
    def sort_z(self):
        def z_comp(a, b):
            if a.z < b.z: return -1
            elif a.z > b.z: return 1
            else: return 0
        self.children.sort(z_comp)
        
    def print_children(self):
        for i in self.children:
            print i
            
    def glumolinit(self):
        if hasattr(self, "__glumolinited__"): return
        bases = type(self).__mro__
        for b in bases:
            if b.__dict__.has_key("__glumolinit__"):
                b.__glumolinit__(self)
        self.__glumolinited__ = True
        
    def __glumolinit__(self):
        pass

class Box:
    def __init__(self, points = []):
        self.points = points

def _from_list(self, l): return Region(None)

class WalkZone(Region):
    def __init__(self, parent):
        Region.__init__(self, parent)

class ForbiddenZone(WalkZone):
    def __init__(self, parent):
        WalkZone.__init__(self, parent)
        self.type = region_type.non_walkable

class EntryPoint(Region):
    north = 0
    east = 1
    west = 2
    
    def __init__(self, parent):
        Region.__init__(self, parent)
        self.default = False
        self.direction = EntryPoint.north
        if hasattr(parent, "entry_points"):
            parent.entry_points.append(self)
    
class PoujolLightZone(Region):
    def __init__(self, parent):
        Region.__init__(self, parent)
        self.color = (1.0, 1.0, 1.0)
        self.alpha = 1.0
        
LightZone = PoujolLightZone

class PoujolScaleZone(Region):
    def __init__(self, parent):
        Region.__init__(self, parent)
        self.regions = []
        self.type = region_type.transparent
        self.bottom_factor = 0.5
        self.top_factor = 0.3
    
ScaleZone = PoujolScaleZone

class PoujolChangeSceneZone(Region):
    north = 0
    east = 1
    west = 2
    def __init__(self, parent):
        Region.__init__(self, parent)
        self.to_scene = None
        self.regions = []
        self.entry_point = None
        self.cursor_direction = self.north
        
ChangeSceneZone = PoujolChangeSceneZone

class Object(Region, Sprite):
    def __init__(self, parent):
        Region.__init__(self, parent)
        Sprite.__init__(self, parent)

class RegionObject(Region, Sprite):
    def __init__(self, parent):
        Region.__init__(self, parent)
        Sprite.__init__(self, parent)
        self.description = ''
            
    def on_take(self):
        pass
        
    def on_look_at(self):
        pass

def auto_init(f):
    def __init__(self, parent):
        if not hasattr(self, "__inited__"):
            self.__inited__ = True
            super(self.__class__, self).__init__(parent)
            f(self, parent)
            self.glumolinit()
        else:
            f(self, parent)
    return __init__
    
def auto_glumolinit(f):
    def __init__(self, *args):
        f(self, *args)
        self.glumolinit()
    return __init__
