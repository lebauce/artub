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

from _poujol import *
from Enum import Enum
from stackless import *
import time
import types
from path import Path
import math
import sys

if sys.platform == 'darwin':
    ESCAPE = 19
    SPACE = 22
else:
    SPACE = 32
    ESCAPE = 27

sleepingTasklets = []

game = None
ego = None

SpriteOld = Sprite
del Sprite

def sleep(delay):
    chan = channel() 
    sleepingTasklets.append([(time.time() + delay),chan])
    sleepingTasklets.sort()
    chan.receive()

class direction(Enum):
    south = 0
    north = 1
    west = 2
    east = 3
    
def _remove(self, obj):
    i = (len(self.children) - 1) 
    while i >= 0:
        if self.children[i] == obj:
            del self.children[i]
        i = i - 1

Screen.remove = _remove

def py_print_children(self, nbspaces = 0, regions = True):
    if nbspaces: print " " * nbspaces, self
    else:
        print self
    if hasattr(self, "regions"):
        n = len(self.regions)
        i = 0
        if n:
            print " " * nbspaces + "    " * 2, str(n), "regions :"
        while i < n:
            print " " * nbspaces + "    " * 2, self.regions[i]
            i = i + 1
    if hasattr(self, "walk_zones"):
        n = len(self.walk_zones)
        i = 0
        if n:
            print " " * nbspaces + "    " * 2, str(n), "walkzones :"
        while i < n:
            print " " * nbspaces + "    " * 2, self.walk_zones[i]
            i = i + 1
    i = 0
    n = len(self.children)
    while i < n:
        if hasattr(self.children[i], "z"):
            print "%4d" % self.children[i].z,
        self.children[i].py_print_children(nbspaces + 4)
        i = i + 1

def remove_child(obj, child):
    n = len(obj.children) - 1
    while n >= 0:
        if obj.children[n] == child:
            del obj.children[n]
            return
        n = n - 1

def change_scene(newscene, entrypoint = None):
    if game.changing_scene: return
    game.changing_scene = True
    n = len(game.scene.children) - 1
    game.scene.on_leave()
    game.scene.fade_out(1.0)
    while game.scene.alpha > 0:
        schedule()
    if type(newscene) in [type(''), type(u'')]:
        scene = eval(newscene)(game.screen)
    else:
        scene = newscene(game.screen)
    scene.alpha = 0.0
    scene.on_enter(entrypoint)
    scene.children.append(ego)
    scene.fade_in(1.0)
    ego.parent = scene
    ego.position = ego.position
    while n >= 0:
        del game.scene.children[n]
        n = n - 1
    remove_child(game.screen, game.scene)
    game.scene = scene
    while scene.alpha < 0.99:
        schedule()
    game.changing_scene = False

Screen.print_children = py_print_children
Screen.py_print_children = py_print_children

BoostPythonMetaclass = Game.__class__

class Timer:
    def __init__(self, delay, action, args):
        self.action = action
        self.delay = delay
        self.args = args
        self.repeat = True

    def start(self):
        tasklet(self.do)()

    def do(self):
        while self.repeat:
            sleep(self.delay)
            self.action(*self.args)
            
class mmetaclass(BoostPythonMetaclass):
        def __init__(self, name, bases, dict):
            """for b in bases:
                if type(b) not in (self, type):
                    pass
                    #for k,v in dict.items():
                    #    setattr(b,k,v)"""
            return type.__init__(self, name, bases, dict)
            if hasattr(t, "width"):
                print >> sys.__stderr__, "Vuve Glumol"
            return t

GameOld = Game
class Game(GameOld, object):
    __metaclass__2 = mmetaclass
    width = 640
    height = 480
    depth = 32
    title = "Glumol"
    fullscreen = False
    use_sdl = False
    allow_resize = False

    def __init__(self, *args):
        width = self.width
        height = self.height
        fullscreen = self.fullscreen
        title = self.title
        use_sdl = self.use_sdl
        del Game.width
        del Game.height
        del Game.fullscreen
        del Game.title
        del Game.use_sdl
        """
        try: del self.__class__.width
        except: pass
        try: del self.__class__.height
        except: pass
        try: del self.__class__.fullscreen
        except: pass
        try: del self.__class__.use_sdl
        except: pass
        try: del self.__class__.title
        except: pass
        """
        GameOld.__init__(self, fullscreen, width, height, \
                         self.depth, title, use_sdl, self.allow_resize)
        global game
        #print >> sys.__stderr__, "Setting global variable game"
        game = self
        self.commands = []
        self.stop = False
        self.fonts = {}
        self.font = None
        self.changing_scene = False
        self._paused = False

    def register_font(self, font):
        self.fonts[font.__class__.__name__] = font
        if not self.font: self.font = font
        
    def set_pause(self, state):
        print "set_pause", state
        if self._paused != state:
            self._paused = state
            if state:
                print "while", self._paused
                while self._paused:
                    #print "update"
                    self.update()
        
    def is_paused(self):
        return self._paused
    
    paused = property(is_paused, set_pause)
    
    def pause(self): self.paused = True

    def resume(self): self.paused = False
        
    def start_cutscene(self):
        self.cutscene = True
        self.inputs_disabled = True

    def end_cutscene(self):
        self.cutscene = False
        self.inputs_disabled = False
        
    def set_font(self, font):
        oldfont = self.font
        try:
            if type(font) is str: self.font = self.fonts[font]
            else: self.font = self.fonts[font.__name__]
        except IndexError:
            print >> sys.__stderr__, "Font", font, "doesn't exist..."
        except AttributeError:
            print >> sys.__stderr__, "Game.set_font : invalid font", font
        return oldfont
            
    def __del2__(self):
        n = len(self.screen.children) - 1
        while n >= 0:
            del self.screen.children[n].parent
            del self.screen.children[n]
            n = n - 1

    def draw(self):
        while not self.stop:
            currentTasklet = getcurrent()
            try:
                self.update()
            except:
                sys.excepthook(*sys.exc_info())
            schedule()

        self.popo = False
        schedule()

    def exit(self):
        self.stop = True

    def run(self):
        self.on_main()

    def on_main(self):
        global game
        global scene
        global ego
        global sleepingTasklets
        self.popo = True 
        try:
            if not hasattr(self, "scene"):
                self.scene = None
                
            draw = tasklet(self.draw)() 
            while self.popo:
                  currentTime = time.time() 
                  while len(sleepingTasklets):
                      (ETA,channel,) = sleepingTasklets[0] 
                      if ETA > currentTime:
                          break 
                          
                      del sleepingTasklets[0]
                      tasklet(channel.send)(True)
                      
                  schedule()
                  if self.commands:
                      self.really_process_line(self.commands[0])
                      del self.commands[0]

        except:
            draw = None 
            game.__dict__ = {}  
            game.stop = True 
            game = None 
            scene = None 
            ego = None 
            raise 
            
        
        for (ETA,channel,) in sleepingTasklets:
            tasklet(channel.send)(True)
            
        sleepingTasklets = [] 
        schedule()
        del draw
        game.__dict__ = {}  
        game.stop = True 
        game = None 
        scene = None 
        try:
            del ego
        except: pass
            
class Children:
    def __init__(self, sprite):
        self.sprite = sprite
        self.childs = []
        
    def append(self, obj):
        self.childs.append(obj)
        self.sprite.add_children(obj)
        
class Sprite(SpriteOld):
    __doc__ = SpriteOld.__doc__
    
    def __glumolinit__(self):
        pass
    
    def __init__(self, parent, a1 = None, a2 = None, a3 = None):
        scale = self.__class__.__dict__.get("scale", None)
        if scale:
            del self.__class__.scale

        if (not a1) and (not a2) and (not a3):
            SpriteOld.__init__(self, parent)
        else:
            SpriteOld.__init__(self, parent, a1, a2, a3)
        
        if isinstance(parent, Sprite):
            # print >> sys.__stderr__, "set parent", parent
            self.parent = parent
        
        if scale:
            self.scale = scale
            
        self.z = self.z
        p = getattr(self, "animation", None)
        if p: self.current_anim = p()
            
        if parent:
            if len(parent.children):
                self.z = parent.children[-1].z + 10
            parent.children.append(self)
        
    remove = _remove
    py_print_children = py_print_children

    def set_parent(self, parent):
        return
        if self.parent:
            self.parent.remove(self)
        self.__dict__["parent"] = parent
        self.set_parent(parent)
        if parent:
            parent.children.append(self)
        
    def _get_parent(self):
        return self.get_parent()
    
    def glumolinit(self):
        if hasattr(self, "__glumolinited__"): return
        bases = type(self).__mro__
        for b in bases:
            if b.__dict__.has_key("__glumolinit__"):
                b.__glumolinit__(self)
        self.__glumolinited__ = True
                
AnimationOld = Animation
del Animation

class Animation(AnimationOld):
    transparent_color = None
    def __init__(self):
        orders = self.__class__.__dict__.get("orders", None)
        if orders:
            del self.__class__.orders

        hotspots = self.__class__.__dict__.get("hotspots", None)
        if hotspots:
            del self.__class__.hotspots

        move_offsets = self.__class__.__dict__.get("move_offsets", None)
        if move_offsets:
            del self.__class__.move_offsets

        delays = self.__class__.__dict__.get("delays", None)
        if delays:
            del self.__class__.delays

        AnimationOld.__init__(self, delays, orders, hotspots, move_offsets)
        for f in self.filenames:
            if self.transparent_color:
                self.add_frame(f, self.transparent_color)
            else:
                self.add_frame(f, Color(0, 0, 0))
        self.build()

    def add_frame(self, frame, color):
        AnimationOld.add_frame(self, str(frame), color)
    
class Plane(Sprite):
    def __init__(self, parent):
        Sprite.__init__(self, parent)
        self.transparent = True

class Scene(Sprite, Pathfinder):
    def __init__(self, parent):
        Sprite.__init__(self, parent)
        Pathfinder.__init__(self)
        self.walk_zones = []
    
    def on_enter(self, entrypoint = None):
        pass
        
    def find_path(self, p1, p2):
        print "Scene.find_path", self, p1, p2, self.regions
        Pathfinder.find_path(self, Point_(
            int(p1[0]), int(p1[1])), Point_(int(p2[0]), int(p2[1])))
        l = []
        i, n = 1, len(self.waypoints)
        while i < n:
            l.append(self.waypoints[i])
            i = i + 1
        return l
                
poujolRegion = Region

class Box:
    def __init__(self, points = []):
        self.points = points

class Region(poujolRegion):
    __getstate_manages_dict__ = 1
    boxes = []
    
    def __getstate__(self):
        return (self.parent,)
    
    def __setstate__(self, state):
        self.parent = state[0]
    
    def __getinitargs__(self):
        return (self.parent, )
    
    def __init__(self, parent, *extras):
        poujolRegion.__init__(self, *extras)
        if type(parent) == type([]):
            self.boxes = parent
            self.from_list(parent)
        self.active = True
        
    def __glumolinit__(self): pass

    def from_list(self, l):
        for i in l:
            c = Contour(i.points) 
            self.contours.append(c)
        center = self.get_center()
        self.center = (center.x, center.y)
        
    def set_boxes(self):
        print "set_boxes", self, len(self.contours), hasattr(self, "regions"), self.boxes
        if len(self.contours): return
        for i in self.boxes:
            c = Contour(i.points) 
            print "adding contour", c
            self.contours.append(c)
        print self.to_string()
        center = self.get_center()
        self.center = (center.x, center.y)
        if hasattr(self, "regions"): self.regions.append(self)

class WalkZone(Region):
    def __init__(self, parent):
        Region.__init__(self, parent)
        self.type = region_type.walkable 
        if parent and hasattr(parent, "walk_zones"):
            print "adding to walkzones"
            parent.walk_zones.append(self)
        if parent and hasattr(parent, "regions"):
            print "adding to regions"
            parent.regions.append(self)
        self.set_boxes()

class ForbiddenZone(WalkZone):
    def __init__(self, parent):
        WalkZone.__init__(self, parent)
        self.type = region_type.non_walkable
        
PoujolWalkZone = WalkZone

class LightZone(Region):
    def __init__(self, parent):
        Region.__init__(self, parent)
        self.oldcolor = (255, 255, 255, 255)
        self.color = (255, 0, 255, 255)
        self.alpha = 1.0
        parent.regions.append(self)
        self.set_boxes()

    def on_enter_region(self, obj):
        self.oldcolor = obj.color 
        self.color = (self.color[0], self.color[1], self.color[2], int(self.alpha * 255))
        obj.color = self.color 

    def on_leave_region(self, obj):
        obj.color = self.oldcolor 

PoujolLightZone = LightZone

class EntryPoint(Region):
    def __init__(self, parent):
        Region.__init__(self, parent)
        self.default = False
        self.direction = 0
        if hasattr(parent, "entry_points"):
            parent.entry_points.append(self)
        
PoujolEntryPoint = EntryPoint

class ChangeSceneZone(Sprite, Region):
    def __init__(self, parent):
        Sprite.__init__(self, parent)
        poujolRegion.__init__(self)
        self.active = True
        self.to_scene = None
        parent.regions.append(self)
        self.entry_point = None
        self.set_boxes()
        
    def on_enter_region(self, sprite):
        if self.to_scene: tasklet(change_scene)(self.to_scene, self.entry_point)

PoujolChangeSceneZone = ChangeSceneZone

class ScaleZone(Sprite, Region):
    def __init__(self, parent):
        Sprite.__init__(self, parent)
        Region.__init__(self, parent)
        self.bottom_factor = 0.5
        self.top_factor = 0.3
        self.type = region_type.transparent
        parent.regions.append(self)
        self.set_boxes()

    def on_move_in_region(self, obj):
        rect = self.get_bouncing_box() 
        f = (self.bottom_factor - self.top_factor) / (rect.bottom - rect.top) 
        f2 = (self.top_factor + (ego.position.y - rect.top) * f) 
        ego.scale = (f2,f2) 
    
PoujolScaleZone = ScaleZone

class RegionObject(Sprite, Region):
    def __init__(self, parent, *args):
        Sprite.__init__(self, parent)
        poujolRegion.__init__(self, *args)
        #self.boxes = []
        self.active = True

class Behaviour(object):
    def __init__(self):
        pass

class ZPlane(Sprite):
    def __init__(self, parent):
        Sprite.__init__(self, parent)
        self.zbuffer = True

FontOld = Font
del Font

class Font(FontOld):
    def __init__(self, letters, filename, widths):
        FontOld.__init__(self, str(letters), str(filename), widths)
        game.register_font(self)

def draw_text(text, pos, maxsize = (0, 0), color = Color(255, 255, 255, 255)):
    game.font.draw(text, pos[0], pos[1], Size(*maxsize), color)

def get_size(text, maxsize = Size(0, 0)):
    return game.font.get_size(text, maxsize)

SoundBuffer = Sound
class Sound(SoundBuffer):
    echo_buffer = 32 * 1024
    invert_echo_buffer = 64 * 1024
    
    def __init__(self, filename, *args):
        print "Sound.__init__", self, filename
        SoundBuffer.__init__(self, str(filename), *args)
        self.session = SoundBuffer.prepare(self)#play(self)
        self.__dict__["echo"] = 0.0
        self.__dict__["invert_echo"] = False
    
    def __del__(self):
        if self.session.playing:
            self.session.stop()
        if hasattr(self, "echo_filter"):
            self.session.remove_filter(self.echo_filter)
        if hasattr(self, "fade_filter"):
            self.session.remove_filter(self.fade_filter)
        if hasattr(self, "invert_echo_filter"):
            self.session.remove_filter(self.invert_echo_filter)
            
    def play(self):
        self.session.play()

    def stop(self):
        self.session.stop()
        self.restart()
        
    def pause(self):
        self.session.stop()
    
    def restart(self):
        self.session.position = 0

    def get_echo(self):
        return self.__dict__["echo"]
        
    def set_echo(self, echo):
        if self.echo:
            self.session.remove_filter(self.echo_filter)
            self.echo_filter = None
        if echo:
            self.echo_filter = EchoFilter(Sound.echo_buffer, echo)
            self.session.add_filter(self.echo_filter, False)
        self.__dict__["echo"] = echo

    echo = property(get_echo, set_echo)
    
    def get_invert_echo(self):
        return self.__dict__["invert_echo"]
        
    def set_invert_echo(self, invert_echo):
        if self.invert_echo:
            self.session.remove_filter(self.invert_echo_filter)
            self.invert_echo_filter = None
        if invert_echo:
            self.invert_echo_filter = EchoFilter(Sound.invert_echo_buffer)
            self.session.add_filter(self.invert_echo_filter, False)
        self.__dict__["invert_echo"] = invert_echo

    invert_echo = property(get_invert_echo, set_invert_echo)

    def fade_to_volume(self, volume, duration):
        if hasattr(self, "fade_filter"):
            self.session.remove_filter(self.fade_filter)
        self.fade_filter = FadeFilter(self.volume)
        self.session.volume = 1.0
        self.session.add_filter(self.fade_filter, False)
        self.fade_filter.fade_to_volume(volume, duration)

    def get_volume(self):
        if hasattr(self, "fade_filter"):
            return self.fade_filter.volume
        else:
            return self.session.volume
        
    def set_volume(self, volume):
        if hasattr(self, "fade_filter"):
            self.fade_filter.volume = volume
        else:
            self.session.volume = volume
        
    volume = property(get_volume, set_volume)

    def is_playing(self):
        return self.session.playing
        
    def set_playing(self, state):
        if state:
            self.session.play()
        else:
            self.session.stop()
            
    playing = property(is_playing, set_playing)
    
    def set_looping(self, state):
        self.session.set_looping(state)
        
    def get_looping(self):
        return self.session.get_looping()
        
    loop = property(get_looping, set_looping)
    
    def get_pan(self):
        return self.session.pan
        
    def set_pan(self, pan):
        self.session.pan = pan
            
    pan = property(get_pan, set_pan)

def play_sound(sound):
    def play_sound_task(sound):
        if type(sound) == str:
            s = Sound(sound)
            s.play()
            while s.playing:
                sleep(1)
    tasklet(play_sound_task)(sound)

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

def NoImage(*args): return None
