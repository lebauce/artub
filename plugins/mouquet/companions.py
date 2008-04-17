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

from resourceeditor import *
from pypoujol import Point
from propertiesbar.companions import Companion, AdvancedCompanion, FilenameCompanion, FontCompanion, ColorCompanion
from propertiesbar.propertiesbar_actions import PropertiesBarChangeValue
from os.path import join, basename

class foo(object):
    def __init__(self, obj, anim, index):
        self.obj = obj
        self.anim = anim
        self.index = index
            
    def set_move_offset_x(self, offset):
        self.anim.move_offsets[self.index].x = offset
        
    def get_move_offset_x(self):
        return self.anim.move_offsets[self.index].x
    
    def set_move_offset_y(self, offset):
        self.anim.move_offsets[self.index].y = offset
    
    def get_move_offset_y(self):
        return self.anim.move_offsets[self.index].y

    def set_hotspot_x(self, offset):
        self.anim.hotspots[self.index].x = offset
    
    def get_hotspot_x(self):
        return self.anim.hotspots[self.index].x
    
    def set_hotspot_y(self, offset):
        self.anim.hotspots[self.index].y = offset
    
    def get_hotspot_y(self):
        return self.anim.hotspots[self.index].y
            
    def set_delay(self, delay):
        self.anim.delays[self.index] = delay
    
    def get_delay(self):
        return self.anim.delays[self.index]
    
    def set_frame(self, frame):
        self.anim.orders[self.index] = frame
        self.obj.current_frame = self.index
    
    def get_frame(self):
        return self.anim.orders[self.index]

    move_offset_x = property(get_move_offset_x, set_move_offset_x)
    move_offset_y = property(get_move_offset_y, set_move_offset_y)
    hotspot_x = property(get_hotspot_x, set_hotspot_x)
    hotspot_y = property(get_hotspot_y, set_hotspot_y)
    delay = property(get_delay, set_delay)
    frame = property(get_frame, set_frame)


class MouquetCompanion(Companion):
    def __init__(self, mouquet, obj):
        Companion.__init__(self, obj.current_anim)
        self.sprite = obj
        self.obj = obj.current_anim
        self.mouquet = mouquet
        self.resource = mouquet.active_resource
        self.add_variables([ ["filename", FilenameCompanion()], "nbframes", "virtual_frames"])
        self.ignore = [ "data" ]
        
    def change_value(self, name, value):
        try:
            if name == "filename":
                self.resource.filename = value
                self.obj.filename = value
                self.obj.nbframes = 1
                self.obj.virtual_frames = 1
                self.mouquet.change_script()
            elif name == "nbframes":
                Companion.change_value(self, name, value)
                self.sprite.current_anim = self.obj
                self.resource.change_global_property(name, str(value))
                self.obj.frame_width = self.obj.size[0] / value
            elif name == "virtual_frames":
                v = value
                if v > self.obj.virtual_frames:
                    v = v - self.obj.virtual_frames
                    self.obj.orders.extend([0] * v)
                    self.obj.delays.extend([0] * v)
                    for i in xrange(v):
                        self.obj.move_offsets.append(Point(0, 0))
                        self.obj.hotspots.append(Point(0, 0))
                elif v < self.obj.virtual_frames:
                    self.obj.orders = self.obj.orders[:v]
                    self.obj.delays = self.obj.delays[:v]
                    self.obj.move_offsets = self.obj.move_offsets[:v]
                    self.obj.hotspots = self.obj.hotspots[:v]
                Companion.change_value(self, name, value)
                self.resource.change_global_property(name, str(value))
                self.mouquet.populate_frame_list(self.obj)
            else:
                Companion.change_value(self, name, value)
                self.resource.change_global_property(name, str(value))
        except: pass
            
class MouquetVirtualFrameCompanion(Companion):
    def __init__(self, resource, obj, index):
        Companion.__init__(self, None)

        self.resource = resource
        self.obj = foo(obj, obj.current_anim, index)
        obj = obj.current_anim
        self.anim = obj
        self.obj.delay = obj.delays[index]
        self.obj.move_offset_x = obj.move_offsets[index].x
        self.obj.move_offset_y = obj.move_offsets[index].y
        self.obj.hotspot_x = obj.hotspots[index][0]
        self.obj.hotspot_y = obj.hotspots[index][1]
        self.variables = [ "delay", "frame", "move_offset_x", "move_offset_y", "hotspot_x", "hotspot_y" ]
        self.ignore = [ "data" ]

    def change_value(self, name, value):
        setattr(self.obj, name, value)

class Frame:
    def __init__(self, txt):
        self.filename = txt
        
class MouquetFrameCompanion(Companion):
    def __init__(self, mouquet, obj, index):
        Companion.__init__(self, obj)
        self.mouquet = mouquet
        self.obj = Frame(str(obj.current_anim.filenames[index]))
        self.anim = obj.current_anim
        self.index = index
        self.variables = [ ["filename", FilenameCompanion()] ]
    
    def change_value(self, name, value):
        project = wx.GetApp().frame.project
        if self.anim.filenames[self.index] not in [value, project.get_relative_path(value), basename(value)]:
            value = project.ask_to_import(value)
            self.anim.filenames[self.index] = value
            self.mouquet.update(True)
            self.mouquet.update(False)
            self.mouquet.to_select = self.index

class MouquetFontCompanion(AdvancedCompanion):
    def __init__(self, mouquet, obj, resource):
        self.mouquet = mouquet
        AdvancedCompanion.__init__(self, obj, resource)
        self.add_variables([ ["font_face", FontCompanion()], ["color", ColorCompanion(obj, None)] ])
    
    def get_font_filename(self, font):
        from sysfont import match_font
        return match_font(font.GetFaceName(), font.GetWeight() == wx.FONTWEIGHT_BOLD, font.GetStyle() == wx.FONTSTYLE_ITALIC)

    def build_font_image(self, fontname, font, paletted = False):
        if paletted: mode = "P"
        else: mode = "RGBA"
        import Image, ImageDraw
        img = Image.new(mode, font.getsize(self.obj.letters))
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), self.obj.letters, font=font)
        font_path = join(wx.GetApp().frame.project.project_path, "fonts")
        try: os.mkdir(font_path)
        except: pass
        img.save(join(font_path, fontname + ".png"))
        
    def change_value(self, name, value):
        if name == "font_face":
            if type(value) in (str, unicode): return
            sizes = []
            import ImageFont
            fontname = value.GetFaceName()
            filename = self.get_font_filename(value)
            if filename[-4:].upper() in ('.TTF', '.OTF',) or filename[-6:].upper() == '.DFONT':
                font = ImageFont.truetype(filename, value.GetPointSize())
            else:
                font = ImageFont.load(filename, value.GetPointSize())
            for c in self.obj.letters:
                sizes.append(font.getsize(c)[0])
            self.resource.sync()
            self.build_font_image(fontname, font, False)
            PropertiesBarChangeValue(self.resource, self.obj, "font_face",
                                     (("widths", tuple(sizes)),
                                     ("filename", join("fonts", str(fontname) + '.png')),
                                     ("font_face", fontname)), multiple = True, update_now = True)
        elif name in ("color", "scale", "alpha"):
            setattr(self.mouquet.sprite, name, value)
            AdvancedCompanion.change_value(self, name, value)
        else:
            AdvancedCompanion.change_value(self, name, value)
