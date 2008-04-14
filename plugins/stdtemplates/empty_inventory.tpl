class InventoryAnim(Animation):
    def __init__(self):
        Animation.__init__(self, "plugins\\stdtemplates\\inventory.png", 1, 1)

class ArrowUp(Sprite):
    def __init__(self, parent):
        Sprite.__init__(self, parent)
        self.current_anim = Animation("plugins\\stdtemplates\\fleche.tga", 2)
        self.x = 0
        self.y = 200
        self.z = 300
        
class ArrowDown(Sprite):
    def __init__(self, parent):
        Sprite.__init__(self, parent)
        self.current_anim = Animation("plugins\\stdtemplates\\fleche2.tga", 2)
        self.x = 100
        self.y = 200
        self.z = 200
        
class Inventory(Sprite):
    def __init__(self, parent):
        Sprite.__init__(self, parent)
        self.angle = 0
        self.line = 0
        self.width = 683
        self.height = 483
        self.nb_lines = 3
        self.items_by_line = 5
        self.item_width = 70
        self.item_height = 70
        self.vertical_space = 10
        self.horizontal_space = 10
        self.offset_x = 96
        self.offset_y = 180
        self.objects = []
        self.selection = None
        self.current_page = 0
        self.x = 20
        self.rotation_hotspot = Point(335., 237.)
        return
        self.alpha = 0.0

    def __glumolinit__(self):
        self.current_anim = InventoryAnim()
        self.arrow_down = ArrowDown(self)
        self.arrow_up = ArrowUp(self)
        self.children.append(self.arrow_down)
        #self.children.append(self.arrow_up)
        #self.children.append(self.arrow_down)
        #self.children.append(self.arrow_up)

    def on_left_button_down(self):
        game.input.mouse_sprite = None
        self.selection = None
        
    def add_object(self, obj):
      item = InventoryItem(self, obj)
      self.objects.append(item)
      self.sort_objects(len(self.objects) - 1)
      item.visible = True
      r = item.size.cx
      item.scale = max(self.item_width, self.item_height) / max(item.size.cx, item.size.cy)
      
    def on_focus2(self):
        pass #print "on_focus"

    def remove_object(self, obj):
      item = self.get_item_from_object(obj)
      if item:
         print "removing", item[0], item[1]
         self.objects.remove(item[0])
         print "removed"
         self.sort_objects(item[1])
         
    def show_next_page(self):
        self.current_page = self.current_page + 1
        self.sort_objects(self.current_page * self.nb_lines * self.items_by_line)
        
    def show_prev_page(self):
        self.current_page = self.current_page - 1
        if self.current_page < 0:
            self.current_page = 0
        self.sort_objects(self.current_page * self.nb_lines * self.items_by_line)
        
    def sort_objects(self, ifrom):
      print "sort"
      slice = self.objects[ifrom:]
      IFrom = ifrom
      maxitems = self.nb_lines * self.items_by_line
      for obj in slice:
         if ifrom >= maxitems:
             break
         pos = self.get_item_position(ifrom)
         obj.position = Point(pos[0], pos[1])
         obj.index = ifrom
         obj.visible = True
         ifrom = ifrom + 1
      slice = self.objects[ifrom:]
      for i in slice:
          i.visible = False

    def get_item_line(self, i):
      return i / self.items_by_line
 
    def get_item_position(self, i):
      return [(i % self.items_by_line) * (self.item_width + self.horizontal_space) + self.offset_x, (i / self.items_by_line) * (self.item_height + self.vertical_space) + self.offset_y]
         
    def get_item_from_object(self, obj):
      index = 0
      for i in self.objects:
         if i.obj == obj:
            return (i, index)
         index = index + 1
      return None

    def care_of_up_and_down(self):
      if self.line > 0:
         self.uparrow.visible = True
      else:
         self.uparrow.visible = False
      if self.get_item_line(len(self.objects)) > self.line + self.nb_lines:
         self.downarrow.visible = True
      else:
         self.downarrow.visible = False

    def on_before_draw(self):
        pass #self.angle = (self.angle + 1) % 360
        
    def update_fade(self):
        print "update_fade"
        i = 0
        sleep = self.delay / 255
        while i < 1:
            #j = 0
            #while j < 3000:
            #    j = j + 1
            #time.sleep(0.0)#self.delay / 255)
            self.alpha = i
            i = i + 0.0003921568627450980392156862745098
        #self.fade_thread.ended = True
        #self.fade_thread.terminate()
        print "thread ended"
        
    def fade_in2(self, delay):
        self.visible = True
        self.alpha = 0.0
        self.delay = 1
        l = ( 0 )
        self.fade_thread = Thread(self.update_fade, ())
        self.fade_thread.ended = False
        self.fade_thread.start()
        i = 0
        #while not self.fade_thread.ended:
        #    print "waiting"
        #self.fade_thread = 
        #thread.start_new_thread(self.update_fade, ()) #threading.Thread(None, self.update_fade)
        #self.fade_thread.start()
        print "thread started"
        
    """ BEGINEVENTLIST """
    def on_focus(self):
        print "inventory on_focus", self.alpha, self.visible
        
    def on_lose_focus(self, newobj):
        print "inventory on_lose_focus", newobj, self.arrow_down, newobj.size.cx, self.arrow_down.current_anim, self.arrow_up.current_anim, self.arrow_up.size.cx, newobj.current_anim
        if newobj in self.children:
            print "keep the focus", str(newobj.current_anim)
            return
        self.fade_out(1)
