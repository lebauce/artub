import wx
from propertiesbar.companions import Companion, ResourceCompanion
from resourceeditor import AutoTemplate, Template
from os.path import join
from glumolobject import CGlumolObject
from standardcharacter import SeparateHeadTemplate, BasicCharacter, StandardCharacter, MainCharacterTemplate
from inventorytemplate import InventoryTemplate
from monkey2 import Monkey2InterfaceTemplate
from cmi import CMIInterfaceTemplate

class ClassicDoorTemplate(AutoTemplate):
    name = "Door template"
    description = "A standard door"
    section = "Object/Door"
    resource_name = "Door"
    needed_classes = ["Object"]
    listing = """class Door(Object):
    def __init__(self, parent):
        Object.__init__(self, parent)
        #self.open_anim = None
        #self.close_anim = None
        self.opened = False

    def open(self):
        #self.current_anim = self.open_anim 
        self.frame = 1
        self.x = 166 
        self.y = 136 
        self.opened = True
        
    def close(self):
        #self.current_anim = self.close_anim 
        self.frame = 0
        self.x = 101 
        self.y = 138 
        self.opened = False 
            
    def open_or_close(self):
        if self.opened:
            self.close()
        else:
            self.open()
            
    def on_hand(self):
        self.open_or_close()
"""

class BasicSceneTemplate(AutoTemplate):
    name = "A basic scene"
    description = "A basic scene"
    section = "Scenes"
    resource_name = "Scene"
    listing = """class Scene(Sprite, Pathfinder):
    def __init__(self, parent):
        self.music_filename = ""
        Sprite.__init__(self, parent)
        Pathfinder.__init__(self)
        self.walk_zones = []
        self.entry_points = []
        
    def __glumolinit__(self):
        pass
        
    def start_music(self):
        if self.music_filename:
            self.music = Sound(self.music_filename)
            self.music.play()
            
    def on_left_button_down(self):
        ego.walk_to(game.mouse_position.x - self.position.x, game.mouse_position.y - self.position.y)

    def on_enter(self, entrypoint = None):
        self.start_music()
        if not entrypoint:
            for i in self.entry_points:
                if isinstance(i, EntryPoint):
                    if i.default:
                        entrypoint = i
                        break
            if not entrypoint: return
        if len(entrypoint.boxes) and len(entrypoint.boxes[0].points):
            ego.position = entrypoint.boxes[0].points[0]

    def on_leave(self):
        if hasattr(self, "music"):
            self.music.stop()
            del self.music

    def on_after_draw(self):
        if not getattr(self, "draw_boxes", None): return
        for zone in self.walk_zones:
            for box in zone.boxes:
                ip = 0
                n = len(box.points)
                for point in box.points:
                      game.screen.draw_line(Point(point[0] + self.position.x, point[1]), Point(box.points[(ip + 1) % n][0] + self.position.x, box.points[(ip + 1) % n][1]), Color(255, 0, 0))
                      ip += 1

    def find_path(self, p1, p2):
        Pathfinder.find_path(self, Point_(
            int(p1[0]), int(p1[1])), Point_(int(p2[0]), int(p2[1])))
        l = []
        i, n = 1, len(self.waypoints)
        while i < n:
            l.append(self.waypoints[i])
            i = i + 1
        return l
        
    def find_path(self, p1, p2):
        if not hasattr(self, "pathfinder_inited"):
            self.pathfinder_inited = True
            i = 0
            n = len(self.walk_zones)
            while i < n:
                self.add_region(self.walk_zones[i])
                i = i + 1
        Pathfinder.find_path(self, Point_(
            int(p1[0]), int(p1[1])), Point_(int(p2[0]), int(p2[1])))
        l = []
        i = 0
        n = len(self.waypoints) - 1
        while n >= 0:
            l.append(self.waypoints[n])
            n = n - 1
        return l


"""

class AutomaticDoorTemplate(Template):
    name = "Automatic door template"
    description = "Automatic door"
    section = "Object/Door"
    # html_page = "audoor.html"
    
    def do(self, evt):
        pass

class FollowingCharacter(Template):
    name = "A following character"
    description = "A character that follows the main character"
    section = "Characters"
    html_page = "following_ego.html"
    
    def do(self, evt):
        print "FollowingCharacter DO"
        evt.Cancel = False

class ScaleZoneTemplate(Template):
    name = "Scaling zone"
    description = "An area that will scale the object inside."
    section = "Zones"

    def do(self, evt):
        pass

class LightZoneTemplate(Template):
    name = "Light zone"
    description = "The object inside this area will appear like it was under a colored light."
    section = "Zones"

    def do(self, evt):
        pass

class SamnmaxInterfaceTemplate(Template):
    name = "Samnmax interface"
    description = "The Samnmax interface"
    section = "Interfaces"

    def do(self, evt):
        pass

class PickableTemplate(AutoTemplate):
    name = "Pickable"
    description = "Make an object pickable"
    section = "Behaviours"
    resource_name = "Pickable"
    listing = """class Pickable(Behaviour):
    apply_on = "Object"
    onlyone = False
    
    def __init__(self):
        self.inventory_sprite = None 
        self.pickable = True 
        
    def on_before_pick(self):
        pass 
        
    def on_after_pick(self):
        pass 
        
    def take(self):
        self.on_before_pick()
        if self.pickable:
            inventory.add(self)
            self.on_after_pick()
"""

class AssembleWithTemplate(AutoTemplate):
    name = "Assemble with"
    description = "Makes an object be able to be assembled with an other object"
    section = "Behaviours"
    resource_name = "AssembleWith"
    listing = """class AssembleWith(Behaviour):
    apply_on = "Object"
    def __init__(self):
        self.with_object = None # Scene1.Brosse
        self.result_object = None # BalaisBrosse
        self.add_to_inventory = True
        
    def on_result(self):
        pass
        
    def assemble(self):
        self.new_obj = self.result_object()
        if self.on_result(): return
        inventory.remove(self)
        inventory.remove(self.with_object)
        if self.add_to_inventory:
            inventory.add(self.new_obj)
"""

    class AssembleWithCompanion(Companion):
        def __init__(self, obj, resource = None):
            import pypoujol
            Companion.__init__(self, obj, resource)
            obj_class = wx.GetApp().gns.getattr("Object")
            self.add_variables([["result_object", ResourceCompanion(obj, obj_class)],
                                ["with_object", ResourceCompanion(obj, obj_class)]])

    def get_companions(self):
        return { "AssembleWith" : self.AssembleWithCompanion }

class CanWalkTemplate(AutoTemplate):
    name = "Can walk"
    description = "Allow an ego to walk"
    section = "Behaviours/Characters"
    resource_name = "CanWalk"
    listing = """class CanWalk(Behaviour):
    apply_on = "Character"

    class EgoWest(Animation): pass
    class EgoNorthWest(Animation): pass
    class EgoNorthEast(Animation): pass
    class EgoEast(Animation): pass
    class EgoSouth(Animation): pass
    class EgoNorth(Animation): pass
    class EgoSouthEast(Animation): pass
    class EgoSouthWest(Animation): pass
    class EgoStanding(Animation): pass
    
    def walk_thread(self, x, y):
        if self.position.x == x and self.position.y == y: return
        self.walking = True 
        self.origin = Point(self.position) 
        self.get_move_offset(x, y)
        dir = self.get_walk_direction(x, y) 
        print 'dir = ', dir, self.walk_faces[dir]
        self.current_anim = self.walk_faces[dir] 
        self.from_ = dir 
        self.playing = True 
        for i in self.walk_faces:
            i.move_offsets[:] = [Point(0, 0)] * i.virtual_frames 
            
        self.playing = False 
        if self.direction < 0:
            pass 
            
        frame = self.current_frame 
        '(old_xold_y,,) = (self.position.x,self.position.y) '
        while  not self.quit and self.walking:
            self.current_frame = ((self.current_frame + 1) % self.current_anim.virtual_frames) 
            if abs(self.move_x) > abs(self.move_y):
                if self.direction == 1:
                    if self.position.x > x:
                        break
                else:
                    if self.position.x < x:
                        break 
                
                self.position += Point(self.inc_x * (self.scale[0] + 0.099999999999999992), self.inc_y * (self.scale[1] + 0.10000000000000001))
                
            else:
                if self.direction == 1:
                    if self.position.y > self.step:
                        break                    
                else:
                    if self.position.y < self.step:
                        break 
                        
                self.position += Point(self.inc_x * (self.scale[0] + 0.099999999999999992), self.inc_y * (self.scale[1] + 0.10000000000000001))
                
            sleep(0.050000000000000003)
            
        self.walking = False 
        self.playing = False
        self.current_frame = 0
        self.position = Point(x, y)

    def walk_to(self, x, y, callback=None):
        if x == self.position.x and y == self.position.x:
            return None
            
        scene = game.scene 
        print 'finding_path from', self.position.x, self.position.y, 'to', x, y
        path = game.scene.find_path((self.position.x,self.position.y), (x,y)) 
        print 'found', path
        for waypoint in path:
            argz = waypoint 
            self.turn_to(*waypoint)
            self.add_task(self.walk_thread, waypoint)

    def walk(self, x, y):
        pass
        
    def stop(self):
        self.walking = False
        self.current_frame = 0 

"""

class CanTalkTemplate(AutoTemplate):
    name = "Can talk"
    description = "Give the ability to a character to walk"
    section = "Behaviours/Characters"
    resource_name = "CanTalk"
    listing = """class CanTalk(Behaviour):
    apply_on = "Character"
    
    def get_speech_place(self, size):
        pass 
        
    def get_speech_time(self, sentence):
        return (len(sentence) * 0.10000000000000001 + 2)
        
    def say_thread(self, sentence):
        self.speaking = True 
        print 'say_thread'
        sprite = Text(sentence, 250, 200) 
        self.sentences.append(sprite)
        self.head.current_anim = self.head.talk_anim[self.to] 
        if self.from_ in [0,7,3]:
            self.head.scale = (-abs(self.scale[0]),self.scale[1]) 
            
        print self.head.current_anim, self.from_
        self.head.playing = True 
        self.hotspot = self.current_anim.hotspots[0] 
        sentence = self.sentences[-1] 
        sentence.visible = True 
        sleep((len(sentence.text) * 0.050000000000000003 + 0.29999999999999999))
        self.playing = False 
        del self.sentences[-1]
        game.screen.remove(sentence)
        self.speaking = False 
        self.head.playing = False 
        
    def say(self, sentence, callback=None):
        self.add_task(self.stand, (), None)
        self.add_task(self.say_thread, tuple([sentence]), callback)
        self.add_task(self.stand, (), None)
        
"""

class CanTurnTemplate(AutoTemplate):
    name = "Can turn"
    description = "Give the ability to a character to turn"
    section = "Behaviours/Characters"
    resource_name = "CanTurn"
    listing = """class CanTurn(Behaviour):
    apply_on = "Character"
    def turn_to(self, x, y, callback=None):
        self.add_task(self.turn, (x,y), callback)

    def turn(self, x, y):
        self.to = self.get_walk_direction(x, y) 
        print self.to, self.from_
        if self.to == self.from_:
            self.is_turning = False 
            return None
            
        if abs((self.from_ - self.to)) > 4:
            if self.from_ > self.to:
                self.turn_inc = 1 
                
            else:
                self.turn_inc = -1 
                
            
        else:
            if self.from_ > self.to:
                self.turn_inc = -1 
                
            else:
                self.turn_inc = 1 
                
            
        print 'je tourne :', self.from_, self.to, self.turn_inc
        self.playing = False 
        while self.from_ != self.to:
            self.from_ = ((self.from_ + self.turn_inc) % 8) 
            if self.from_ < 0:
                self.from_ = 7 
                
            print 'state', self.from_, self.walk_faces[self.from_]
            self.head.visible = False 
            self.current_anim = self.walk_faces[self.from_] 
            self.playing = False 
            print self.current_anim, self.walk_faces[self.from_]
            self.current_frame = 0 
            schedule()
            'time.sleep(0.05000000000000001)'
            
        self.hotspot = self.current_anim.hotspots[self.current_order] 
        print 'fini de tourner'
        self.is_turning = False 
"""

class CameraFollowTemplate(AutoTemplate):
    name = _("Camera follow")
    description = _("Make the camera follow a character or an object")
    section = "Behaviours/Scenes"
    resource_name = "CameraFollow"
    listing = """class CameraFollow(Behaviour):
    apply_on = "Scene"
    
    def __init__(self):
        Behaviour.__init__(self)
        self.follow_obj = 1 

    def on_before_draw(self):
        if self.follow_obj:
            if self.follow_obj == 1:
                self.follow_obj = ego 
                
            p = (self.follow_obj.position.x - game.width / 2) 
            p = min((self.size[0] - game.width), max(0, p)) 
            self.position = (-p,0) 
"""
    
class ChainAnimationTemplate(AutoTemplate):
    name = "Chain animations"
    description = "Make the character chain animations"
    section = "Behaviours/Characters"
    resource_name = "ChainAnimation"
    listing = """class ChainAnimation(Behaviour):
    pass
"""
    
class DoSomethingPeriodicallyTemplate(AutoTemplate):
    name = "Do something periodically"
    description = "Do something periodically"
    section = "Behaviours"
    resource_name = "DoSomethingPeriodically"
    listing = """class DoSomethingPeriodically(Behaviour):
    def __init__(self):
        self.delay = 0
        self.repeat = True

    def __glumolinit__(self):
        self.set_timer()
        
    def on_do_something(self, game):
        pass

    def set_timer(self):
        if self.delay and not game.stop:
            Timer(self.delay, self.on_do_something, (game,)).start()
"""

class RollOverTemplate(AutoTemplate):
    name = "Roll over"
    description = _("Change the image of the sprite when the mouse cursor is on it")
    section = "Behaviours"
    resource_name = "RollOver"
    listing = """class RollOver(Behaviour):
    apply_on = "Sprite"
    
    def __init__(self):
        pass
        
    def on_focus(self, oldobj):
        self.frame = 1
        
    def on_lose_focus(self, newobj):
        self.frame = 0
"""

class TextTemplate(AutoTemplate):
    name = "Text"
    description = _("A sprite that displays text")
    section = "Sprite"
    resource_name = "Text"
    listing = """class Text(Sprite):
    def __init__(self, parent, text = "", position = (0, 0), size = None,
                         color = Color(255, 255, 255, 255), font = None):
        if not parent:
            parent = game.screen 
        Sprite.__init__(self, parent)
        self.text = str(text) 
        if not size and game.font:
            self.size = game.font.get_size(text)
        self.Color = color 
        self.font = font
        
    def remove(self):
        pass 
        
    def on_after_draw(self):
        if self.font: game.set_font(self.font)
        draw_text(str(self.text), (self.position.x, self.position.y), Size(self.size), self.Color)
        self.visible = True 
"""
    
class ShadowTemplate(AutoTemplate):
    name = "Shadow"
    description = _("Shadow")
    section = "Zones/Lights"
    resource_name = "Shadow"
    listing = """class Shadow(LightZone):
    brightness = 50

    def on_enter_region(self, obj):
        self.oldcolor = obj.color
        c = int(255 / 100. * self.brightness)
        obj.color = (c, c, c, int(obj.alpha * 255))

    def on_leave_region(self, obj):
        obj.color = (self.oldcolor.r, self.oldcolor.g, self.oldcolor.b, int(obj.alpha * 255))
"""

class ButtonTemplate(AutoTemplate):
    name = "Button"
    description = _("Make the sprite act as a button")
    section = "Behaviours"
    resource_name = "SpriteButton"
    check_classes = ["RollOver"] # html_page = "classicdoor.html"
    listing = """class SpriteButton(RollOver):
    apply_on = "Sprite"
    
    def on_left_button_down(self):
        self.on_clicked()
        
    def on_clicked(self): pass
"""

class SceneWithMusicTemplate(AutoTemplate):
    name = "WithMusic"
    description = _("The scene can play a single music")
    section = "Behaviours"
    resource_name = "WithMusic"
    listing = """class WithMusic(Behaviour):
    apply_on = "Scene"

    def __init__(self):
        self.music_filename = Path('')

    def get_music_filename(self):
        return self._music_filename

    def set_music_filename(self, filename):
        self._music_filename = Path(filename)

    music_filename = property(get_music_filename, set_music_filename)
"""

templates = [ClassicDoorTemplate, \
             AutomaticDoorTemplate, \
             BasicCharacter, \
             StandardCharacter, \
             SeparateHeadTemplate, \
             MainCharacterTemplate, \
             FollowingCharacter, \
             ScaleZoneTemplate, \
             LightZoneTemplate, \
             CMIInterfaceTemplate, \
             Monkey2InterfaceTemplate, \
             SamnmaxInterfaceTemplate, \
             InventoryTemplate, \
             DoSomethingPeriodicallyTemplate, \
             PickableTemplate, \
             AssembleWithTemplate, \
             CanWalkTemplate, \
             CanTalkTemplate, \
             CanTurnTemplate, \
             ChainAnimationTemplate, \
             CameraFollowTemplate, \
             BasicSceneTemplate, \
             RollOverTemplate, \
             ButtonTemplate, \
             TextTemplate, \
             ShadowTemplate, \
             SceneWithMusicTemplate]
