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

# Please don't look at this, it's just horrible

import os, sys
from os.path import join, getsize
from struct import unpack, calcsize
from string import join as string_join

from PIL import Image, ImagePalette

data = None
globals()["data"] = data

kBoxXFlip = 0x08
kBoxYFlip = 0x10
kBoxIgnoreScale	= 0x20
kBoxPlayerOnly = 0x20
kBoxLocked = 0x40
kBoxInvisible = 0x80

scene_name = "myscene"
dir_prefix = ""

try: decompress_scene_zbuffers = int(sys.argv[1])
except: decompress_scene_zbuffers = 1
try: decompress_scene_background = int(sys.argv[2])
except: decompress_scene_background = 1
try: decompress_objects_images = int(sys.argv[3])
except: decompress_objects_images = 1
try: decompress_objects_zbuffers = int(sys.argv[4])
except: decompress_objects_zbuffers = 0

class File:
    def open(self, filename):
        self.file = open(filename, 'rb')
        self.size = getsize(filename)
        self.cursor = 0
        
    def read(self, size):
        self.cursor += size
        return self.file.read(size)
        
    def close(self):
        self.file.close()
        
    def seek_set(self, distance):
        self.file.seek(distance)
        self.cursor = distance
    
    def seek_current(self, distance):
        self.file.seek(distance, 1)
        self.cursor += distance
        
    def get_size(self):
        pos = self.file.tell()
        self.file.seek(0, 2)
        size = self.file.tell()
        self.file.seek(pos)
        return size
        
    def get_cursor(self):
        return self.cursor

    def read_header(file):
        buf = file.read(4)
        name = string_join(unpack('4c', buf), '')
        buf = file.read(4)
        size = unpack('>I', buf)[0]
        return (name, size)


class ScummDisk:
    def __init__(self, file):
        self.file = file
        name, size = file.read_header()
        if name != 'LECF':
            raise "Invalid SCUMM disk found."
            
        name, size = file.read_header()
        if name != 'LOFF':
            raise "Invalid SCUMM disk found."

        self.parse_LOFF()

    def seek_room(self, broom):
        self.file.seek_set(self.room_offsets[broom])
        
    def parse_LOFF(self):
        file = self.file
        buf = file.read(1)
        num_rooms = unpack('B', buf)[0]

        self.room_offsets = [0] * 256
        
        for b in xrange(num_rooms):
            buf = file.read(1)
            broom = unpack('B', buf)[0]
            buf = file.read(4)
            self.room_offsets[broom] = unpack('I', buf)[0]
            
class ScummDirectory:
    def parse(self, v8, data):
        index = 0
        if v8:
            self.nb_items = unpack("I", data[:4])[0]
            index += 4
        else:
            self.nb_items = unpack("H", data[:2])[0]
            index += 2
        
        self.rooms = []
        self.offsets = []
        
        for i in xrange(self.nb_items):
            n = unpack("B", data[index:index + 1])[0]
            self.rooms.append(n)
            index += 1
            
        for i in xrange(self.nb_items):
            n = unpack("I", data[index:index + 4])[0]
            self.offsets.append(n)
            index += 4
    
    def get_item_room(self, index):
        return self.rooms[index]
        
    def get_item_offset(self, index):
        return self.offsets[index]
        
    def get_count(self):
        return self.nb_items
            
class ScummResourceManager:
    def __init__(self, gamepath):
        self.disks = []
        self.scumm_disks = []
        self.dir_rooms = ScummDirectory()
        self.dir_costumes = ScummDirectory()
        import glob
        files = glob.glob(join(gamepath, "*.la*"))
        if os.name != "nt":
            files += glob.glob(join(gamepath, "*.LA*"))
        if not files: raise "No file found"
        f = File()
        f.open(files[0])
        self.disks.append(f)
        self.scumm_disks.append(f)
        self.parse_index()
        for i in files[1:]:
            f = File()
            self.disks.append(f)
            f.open(i)
            self.scumm_disks.append(ScummDisk(f))
        
    def do_RNAM(self, size):
        pass
        
    do_MAXS = do_RNAM
    do_DRSC = do_RNAM
    
    def do_DROO(self, size):
        disk = self.disks[0]
        original_cursor = disk.get_cursor();
        data = disk.read(size)
        self.dir_rooms.parse(True, data)
        disk.seek_set(original_cursor)
        
    do_DSCR = do_RNAM
    do_DSOU = do_RNAM

    def do_DCOS(self, size):
        disk = self.disks[0]
        original_cursor = disk.get_cursor();
        data = disk.read(size)
        self.dir_costumes.parse(True, data)
        disk.seek_set(original_cursor)

    do_DCHR = do_RNAM
    do_DOBJ = do_RNAM
    do_AARY = do_RNAM
    do_ANAM = do_RNAM
    
    def get_nb_costumes(self):
        return self.dir_costumes.get_count()

    def parse_index(self):
        cursor = 0
        
        disk = self.disks[0]
        total_size = disk.get_size()
        
        while cursor < total_size:
            name, size = self.disks[0].read_header()
            handler = getattr(self, "do_" + name)
            handler(size - 8)
            # self.disks[0].seek_current(size - 8)
            self.disks[0].read(size - 8)
            cursor += size

    def load_room(self, room):
        bdisk = self.dir_rooms.get_item_room(room)
        self.scumm_disks[bdisk].seek_room(room)
        name, size = self.disks[bdisk].read_header()
        assert name == 'LFLF'
        return self.disks[bdisk].read(size), size

    def load_costume(self, cost):
        broom = self.dir_costumes.get_item_room(cost)
        assert broom != -1
        bdisk = self.dir_rooms.get_item_room(broom)
        assert bdisk != 0
        self.scumm_disks[bdisk].seek_room(broom)
        self.disks[bdisk].seek_current(self.dir_costumes.get_item_offset(cost))
        name, size = self.disks[bdisk].read_header()
        assert name == 'AKOS'
        self.disks[bdisk].seek_current(-8)
        return self.disks[bdisk].read(size)

class Block:
    def get_header(self, index):
        # print "data =", ord(data[index + 0]), "index", index, "data[0:20]", data[0:20]#:index + 4]
        name = string_join(unpack('4c', data[index:index + 4]), '')
        size = unpack('>I', data[index + 4:index + 8])[0]
        return (name, size)

    def get_children(self, index, size):
        s = 0
        childs = []
        print "get_children", size
        while s < size:
            name, s2 = self.get_header(index)
            print "name", name, "size", s2
            s += s2
            if globals().has_key(name):
                handler = globals()[name](index + 8, s2 - 8)
                childs.append(handler)
            index += s2
        print "done"
        self.childs = childs
        
    def get_children_by_type(self, typename):
        objects = []
        for i in self.childs:
                if i.__class__.__name__ == typename:
                    objects.append(i)
        return objects
        
    def repr(self, attrs):
        s = ""
        for i in attrs:
            s += i + ' : ' + str(getattr(self, i)) + '\n'
        return s
        
class RMHD(Block):
    def __init__(self, index, size):
        global data
        dat = unpack("IIIIII", data[index:index + size])
        self.mmucus = dat[0]
        self.width = dat[1]
        self.height = dat[2]
        self.nb_objects = dat[3]
        self.nb_zplanes = dat[4]
        self.transparent_color = dat[5]

class Box: pass
    
class BOXD(Block):
    def __init__(self, index, size):
        n = unpack("I", data[index: index + 4])[0]
        index += 4
        self.boxes = []
        for i in xrange(n):
            dat = unpack("iiiiiiiiIIIII", data[index:index + 52])
            index += 52
            box = Box()
            self.boxes.append(box)
            if (dat[0] == dat[2]) and (dat[1] == dat[3]):
                inc_x, inc_y = 2, 2
            else: inc_x, inc_y = 0, 0
            box.zplane = dat[8]
            box.p1 = (dat[0] - inc_x, dat[1] - inc_y)
            box.p2 = (dat[2] + inc_x, dat[3] - inc_y)
            box.p3 = (dat[4] + inc_x, dat[5] + inc_y)
            box.p4 = (dat[6] - inc_x, dat[7] + inc_y)
            box.flags = dat[9]
            box.scale_slot = dat[10]
            box.scale = dat[11]
    
class ROOM(Block):
    def __init__(self, index, size):
        #name, size = get_header(data)
        #assert name == 'RMHD'
        print "ROOM.__init__", data[index:index + 4]
        self.get_children(index, size)
        self.header = self.get_children_by_type('RMHD')[0]
        self.objects = self.get_children_by_type('OBIM')
        self.image = self.get_children_by_type('IMAG')[0]
        self.palette = self.get_children_by_type('PALS')[0]
        self.boxes = self.get_children_by_type('BOXD')
        self.zplanes = self.get_children_by_type('ZPLN')
        palette = []
        for i in xrange(768):
            palette.append(self.palette.wrap.data.colors[i])
        global img
        if decompress_scene_background:
            img = Image.new("P", (self.header.width, self.header.height))
            img.putpalette(palette)
            self.image.wrap.data.bstr.decompress(self.header.width, self.header.height)
            img.save("background.png", transparency=self.header.transparent_color)
        n = 0
        
        import sys
        if os.name == "posix":
            sys.path.append("/home/bob/dev/artub")
        else:
            sys.path.append("d:\\glumol\\artub")
        from poujol import Region, Box
        r = Region(None)
        for i in self.boxes[0].boxes:
            if (i.flags & kBoxInvisible): continue
            r2 = Region( \
                [ \
                    Box([i.p1, i.p2, i.p3, i.p4]), \
                ])
            r = r + r2
        l = r.to_list()
        boxstr = ""
        for box in l:
            boxstr += "Box(["
            for p in box:
                boxstr += "(" + str(p[0]) + ", " + str(p[1]) + "), "
            boxstr += "]), "    
        s = ["class " + scene_name + "(Scene):", "", ]
        
        zbuffers_list = []
        n = 0
        for i in self.image.wrap.data.zplanes.wrap.zstrs:
            ns = str(n + 1)
            if decompress_scene_zbuffers:
                img = Image.new("P", (self.header.width, self.header.height))
                img.putpalette(palette)
                i.decompress(self.header.width, self.header.height)
                img.save("background_zbuffer" + ns + ".png")
            s += ["    class ZPlane" + ns + "(ZPlane):",
                  "        class ZPlane" + ns + "_anim(Animation):",
                  "            filenames = [ '" + dir_prefix + "background_zbuffer" + ns + ".png']",
                  "        def __init__(self, parent):",
                  "            ZPlane.__init__(self, parent)",
                  "            self.current_anim = self.ZPlane" + ns + "_anim()", ""]     
            zbuffers_list.append("        self.zbuffer" + ns + " = " + scene_name + \
                                ".ZPlane" + ns + "(self)")
            n = n + 1

        s += ["    class WalkZone1(WalkZone):", \
              "        def __init__(self, parent):", \
              "            WalkZone.__init__(self, parent)", \
              "            " + scene_name + ".WalkZone1.__glumolinit__(self)", \
              "            self.set_boxes()", "",
              "        def __glumolinit__(self):" , \
              "            self.boxes = [" + boxstr + "]", ""]
        objects = []
        for i in self.objects:
            import string
            if len(i.images):
              n = 0
              filenames = ""
              for bmp in i.images:
                filenames += dir_prefix + i.header.name + str(n) + ".png, "
                if decompress_objects_images:
                    img = Image.new("P", (i.header.width, i.header.height))
                    img.putpalette(palette)
                    bmp.wrap.data.bstr.decompress(i.header.width, i.header.height)
                    img.save(i.header.name + str(n) + ".png", transparency=self.header.transparent_color)
                n = n + 1
              filenames = filenames[:-2]
              boxstr = "Box([(%d, %d), (%d, %d), (%d, %d), (%d, %d)])" % \
                          (i.header.x, i.header.y, \
                           i.header.x + i.header.width, i.header.y, \
                           i.header.x + i.header.width, i.header.y + i.header.height, \
                           i.header.x, i.header.y + i.header.height)
              s += ["    class " + i.header.name + "(Object):", \
                    "        class " + i.header.name + "_anim(Animation):", \
                    "            filenames = ['" + filenames + "']", "", \
                    "        def __init__(self, parent):", \
                    "            Object.__init__(self, parent)", \
                    "            self.current_anim = self." + i.header.name + "_anim()", \
                    "            self.x = " + str(i.header.x), \
                    "            self.y = " + str(i.header.y), \
                    "            " + scene_name + "." + i.header.name + ".__glumolinit__(self)", \
                    "            self.set_boxes()", \
                    "        def __glumolinit__(self):", \
                    "            self.boxes = [" + boxstr + "]", ""]
            else:
                s += ["    class " + i.header.name + "(RegionObject):", \
                      "        def __init__(self, parent):", \
                      "            RegionObject.__init__(self, parent)", "" ]
            objects += ["        self._" + i.header.name + " = self." + i.header.name + "(self)"]
    
        s += ["    class myscene_anim(Animation):", \
              "        filenames = ['" + dir_prefix + "background.png']", "", \
              "    def __init__(self, parent):", \
              "        Scene.__init__(self, parent)", \
              "        self.current_anim = self.myscene_anim()", \
              "        self.walkzone1 = self.WalkZone1(self)", ] + objects + \
             ["        self.__glumolinit__()", \
              "    def __glumolinit__(self):", \
              "        super(" + scene_name + ", self).__glumolinit__()"]
        open("scene.txt", "wt").write(string.join(s + zbuffers_list, "\n"))
                
                

class LFLF(Block):
    def __init__(self, index, size):
        name, size = self.get_header(index)
        assert name == 'ROOM'
        self.room = ROOM(index + 8, size - 8)
    
class AKCI(Block):
    def __init__(self, index):
        size = calcsize("HHhhhh")
        data = unpack("HHhhhh", data[cursor:cursor + size])
        self.wWidth = data[0]
        self.wHeight = data[1]
        self.relX = data[2]
        self.relY = data[3]
        self.movX = data[4]
        self.movY = data[5]

class IMHD(Block):
    def __init__(self, index, size):
        global data
        dat = unpack("32sIIIIIIIIIIII", data[index:index + calcsize("32sIIIIIIIIIIII")])
        self.name = dat[0].rstrip()
        n = len(self.name)
        for i in xrange(n):
            if not ord(dat[0][i]):
                self.name = self.name[:i]
                break
        self.name = self.name.replace('-', '_')
        self.mmucus = dat[3]
        self.nb_images = dat[4]
        self.x = dat[5]
        self.y = dat[6]
        self.width = dat[7]
        self.height = dat[8]
        self.actor_dir = dat[9]
        self.flags = dat[10]
        self.actor_x = dat[11]
        self.actor_y = dat[12]

class APAL(Block):
    def __init__(self, index, size):
        self.colors = unpack("768B", data[index + 8:index + 8 + 768])
        
class PALS(Block):
    def __init__(self, index, size):
        self.wrap = PALSWRAP(index, size - 8)
        #self.decompress(data[16 + self.wrap.offsets[0]:])
    
class BITMAP(Block):
    def __init__(self, index, size):
        pass

class BSTR(Block):
    def __init__(self, index, size):
        name, size = self.get_header(index)
        self.index = index
        #assert name == "BSTR"
        self.wrap = BSTRWRAP(index, size)

    def decompress(self, dstPitch, height):
        index = self.index
        n = 0
        for i in self.wrap.offsets:
            code = ord(data[index + 8 + i])
            if code <= 10:
                if code == 1:
                    self._unkDecode7(index + 8 + i, n, dstPitch, height)
            else:
                code /= 10;
                if code == 1:
                    self._strip_basic_v(index + 8 + i, n, dstPitch, height)
                elif code == 2:
                    self._strip_basic_h(index + 8 + i, n, dstPitch, height)
                elif code == 10:
                    self._decompress(index + 8 + i, n, dstPitch, height)
                elif code == 12:
                    self._decompress(index + 8 + i, n, dstPitch, height)
                else:
                    raise "Unknown compression code " + str(code)
            n += 1

    def _unkDecode7(self, index, n, dstPitch, height):
        src = index
        x = n * 8
        y = 0
        while height:
            for i in xrange(8):
                img.putpixel((x, y), ord(data[src + i]))
            y += 1
            src += 8
            height -= 1
            
    def _strip_basic_v(self, index, n, dstPitch, height):
        src = index
        code = ord(data[src])
        src += 1
        _decomp_shr = code % 10
        _decomp_mask = 0xFF >> (8 - _decomp_shr)
        color = ord(data[src])
        #print "strip code", code, height * dstPitch - 1, height, dstPitch
        #print "shr", _decomp_shr, "mask", _decomp_mask, "code", code, "color", color
        src += 1
        bits = ord(data[src])
        src += 1
        cl = 8
        inc = -1
        transpCheck = False
        dst = 8 * n
        _vertStripNextInc = height * dstPitch - 1
        x = 8
        while True:
            h = height
            while True:
                if cl <= 8:
                    bits |= (ord(data[src]) << cl)
                    src += 1
                    cl += 8
                if not transpCheck or color != _transparentColor:
                    img.putpixel((dst % dstPitch, dst / dstPitch), color) # *dst = _roomPalette[color] + _paletteMod
                dst += dstPitch

                cl -= 1
                bit = bits & 1
                bits >>= 1
                if not bit: pass
                else:
                    cl -= 1
                    bit = bits & 1
                    bits >>= 1
                    if not bit:
                        if cl <= 8:
                            bits |= (ord(data[src]) << cl)
                            src += 1
                            cl += 8
                        color = bits & _decomp_mask
                        bits >>= _decomp_shr
                        cl -= _decomp_shr
                        inc = -1
                    else:
                        cl -= 1
                        bit = bits & 1
                        bits >>= 1
                        if not bit:
                            color += inc
                        else:
                            inc = -inc
                            color += inc
                h -= 1
                if not h: break
            dst -= _vertStripNextInc
            x -= 1
            if not x: break

    def _decompress(self, index, n, dstPitch, height):
        transpCheck = False
        def z(data, r):
            for i in xrange(r):
                print ord(data[i]),
        #print "data =",
        #z(data, 10)
        #print
        src = index
        code = ord(data[src])
        src += 1
        _decomp_shr = code % 10
        _decomp_mask = 0xFF >> (8 - _decomp_shr)
        code /= 10;
        color = ord(data[src])
        #print "shr", _decomp_shr, "mask", _decomp_mask, "code", code, "color", color
        src += 1
        bits = ord(data[src])
        src += 1
        cl = 8
        _x = 8 * n
        _y = 0
        #dstPitch = 640
        paletted = True
        while True:
            x = 8
            while True:
                if cl <= 8:
                    bits |= (ord(data[src]) << cl)
                    src += 1
                    cl += 8
                    
                #if (!transpCheck || color != _transparentColor)
                #print "AFFICHE PIXEL", color #~*dst = _roomPalette[color] + _paletteMod;
                img.putpixel((_x, _y), color)
                _x += 1

                while True:
                    cl -= 1
                    bit = bits & 1
                    bits >>= 1
                    if not bit: pass
                    else:
                        cl -= 1
                        bit = bits & 1
                        bits >>= 1
                        if not bit:
                            if cl <= 8:
                                bits |= (ord(data[src]) << cl)
                                src += 1
                                cl += 8
                            color = bits & _decomp_mask
                            bits >>= _decomp_shr
                            cl -= _decomp_shr
                        else:
                            incm = (bits & 7) - 4
                            cl -= 3
                            bits >>= 3
                            if incm:
                                color += incm
                            else:
                                if cl <= 8:
                                    bits |= (ord(data[src]) << cl)
                                    src += 1
                                    cl += 8
                                reps = bits & 0xFF;
                                while True:
                                    x -= 1
                                    if not x:
                                        x = 8
                                        _x = n * 8
                                        _y += 1
                                        height -= 1
                                        if not height:
                                            return img
                                    if not transpCheck or color != _transparentColor:
                                        img.putpixel((_x, _y), color)
                                        # print "AFFICHE PIXEL", color #*dst = _roomPalette[color] + _paletteMod
                                        _x += 1
                                        #dst += 1
                                    reps -= 1
                                    if not reps:
                                        break
                                bits >>= 8
                                bits |= ord(data[src]) << (cl - 8)
                                src += 1
                                continue
                    break
                x -= 1
                if not x: break
            _x = n * 8
            _y += 1
            height -= 1
            if not height: break
        return img

class ZBUFFER:
    def __init__(self, index, size):
        pass # print ord(data[0]), ord(data[1]), size
        
class ZBUFFERWRAP(Block):
    def __init__(self, index, size):
        name, size = self.get_header(index)
        assert name == "WRAP"
        name, size = self.get_header(index + 8)
        assert name == "OFFS"
        l = (size - 8) / 4
        offsets = unpack(str(l) + "I", data[index + 16:index + 16 + 4 * l])
        #name, size = self.get_header(data, 8 + offsets[0])
        #for i in xrange(l):
        #    self.data = ZBUFFER(index, size, 8 + offsets[i])
        self.offsets = offsets
        print "len offsets", len(self.offsets)
        
class ZSTR(Block):
    def __init__(self, index, size):
        name, size = self.get_header(index)
        self.wrap = ZBUFFERWRAP(index + 8, size - 8)
        self.index = index

    def decompress(self, width, height):
        index = self.index
        n = 0
        for i in self.wrap.offsets:
            code = ord(data[index + 16 + i])
            #print "_decompress", index, self.wrap.offsets, index + 16 + i
            self._decompress(index + 16 + i, width, height, n)
            n += 1
            
    def _decompress(self, index, width, height, n):
        print "_decompress"
        _numStrips = 0
        pixels = 0
        src = index
        dst = 0
        y = 0
        _x = n * 8
        while height:
            b = ord(data[src])
            #print "b=", b
            src += 1
            if (b & 0x80):
                b &= 0x7F
                c = ord(data[src])
                src += 1
                while b and height:
                    #img.putpixel((x, y), c)
                    #print c, 
                    # pixel *dst = c
                    #x += 1
                    x = n * 8
                    for i in (128, 64, 32, 16, 8, 4, 2, 1): #(1, 2, 4, 8, 16, 32, 64, 128):
                      try:
                        #print x, y, c & i
                        if c & i:
                            img.putpixel((pixels % 8 + _x, pixels / 8), 0)
                            pixels += 1
                        else:
                            img.putpixel((pixels % 8 + _x, pixels / 8), 255)
                            pixels += 1
                        x += 1
                      except:
                        print "X, Y", x, y
                        raise
                    #dst += 1
                    #dst += _numStrips
                    #y = y + 1
                    height -= 1
                    b -= 1
            else:
                #b -= 1
                while b and height:
                    x = n * 8
                    c = ord(data[src])
                    for i in (128, 64, 32, 16, 8, 4, 2, 1): #(1, 2, 4, 8, 16, 32, 64, 128):
                        #print x, y
                        if c & i:
                            #raise str(x) + " " + str(y)
                            img.putpixel((pixels % 8 + _x, pixels / 8), 0)
                            pixels += 1
                        else:
                            img.putpixel((pixels % 8 + _x, pixels / 8), 255)
                            pixels += 1
                        x += 1
                    # putpixel 
                    #print "pixel", ord(data[src])
                    src += 1
                    # dst += 1
                    #dst += _numStrips
                    height -= 1
                    y = y + 1
                    b -= 1
        print "wrote", pixels, "pixels"        

class ZSTRWRAP(Block):
    def __init__(self, index, size):
        name, size = self.get_header(index)
        assert name == "WRAP"
        name, size = self.get_header(index + 8)
        assert name == "OFFS"
        l = (size - 8) / 4
        print "offsets", str(l), data[index + 16:index + 16 + 4 * l]
        offsets = unpack(str(l) + "I", data[index + 16:index + 16 + 4 * l])
        name, size = self.get_header(index + 8 + offsets[0])
        self.zstrs = []
        for i in xrange(l):
            self.zstrs.append(ZSTR(index + 8 + offsets[i], size))
        self.offsets = offsets

class ZPLN(Block):
    def __init__(self, index, size):
        print "size =", size, "data =", ord(data[index + 0]), ord(data[index + 1])
        self.wrap = ZSTRWRAP(index, size)
        
class SMAP(Block):
    def __init__(self, index, _size):
        name, size = self.get_header(index)
        #assert name == "SMAP"
        #self.bstr = BSTR(data[8:], size - 8)
        #print "SMAP", size, 
        #self.zplanes = ZPLN(data[size], _size - 8 - size)
        self.get_children(index + 8, size - 8)
        self.bstr = self.get_children_by_type("BSTR")[0]
        self.zplanes = self.get_children_by_type("ZPLN")[0]
        
class BSTRWRAP(Block):
    def __init__(self, index, size):
        name, size = self.get_header(index)
        assert name == "WRAP"
        name, size = self.get_header(index + 8)
        assert name == "OFFS"
        l = (size - 8) / 4
        offsets = unpack(str(l) + "I", data[index + 16:index + 16 + 4 * l])
        name, size = self.get_header(index + 8 + offsets[0])
        self.data = BITMAP(index + 8 + offsets[0], size)
        self.offsets = offsets

class PALSWRAP(Block):
    def __init__(self, index, size):
        name, size = self.get_header(index)
        assert name == "WRAP"
        l = 1 # l = (size - 8) / 4
        offsets = unpack(str(l) + "I", data[index + 16:index + 16 + 4 * l])
        name, size = self.get_header(index + 8 + offsets[0])
        self.data = APAL(index + 8 + offsets[0], size)
        self.offsets = offsets

class SMAPWRAP(Block):
    def __init__(self, index, size):
        name, size = self.get_header(index)
        assert name == "WRAP"
        l = 1 # l = (size - 8) / 4
        offsets = unpack(str(l) + "I", data[index + 16:index + 16 + 4 * l])
        name, size = self.get_header(index + 8 + offsets[0])
        self.data = SMAP(index + 8 + offsets[0], size)
        self.offsets = offsets
        #for i in offsets:
        #    print "offset", i, l
        #    name, size = self.get_header(data, i)
        #    assert name == "SMAP"
        #    self.smaps.append(SMAP(data[i:], size))

class IMAG(Block):
    def __init__(self, index, size):
        self.wrap = SMAPWRAP(index, size - 8)
    
class OBIM(Block):
    def __init__(self, index, size):
        self.get_children(index, size)
        self.header = self.get_children_by_type('IMHD')[0]
        self.images = self.get_children_by_type('IMAG')
        
    def __str__(self):
        return self.header.repr(["nb_images", "x", "y", "width", "height", "actor_dir", "name" ])
        
class AKHD(Block):
    def __init__(self, data, cursor):
        size = calcsize("HBBHHH")
        data = unpack("HBBHHH", data[cursor:cursor + size])
        self.unk1 = data[0]
        self.flags = data[1]
        self.unk2 = data[2]
        self.nb_anims = data[3]
        self.nb_frames = data[4]
        self.codec = data[5]

#class AKCI:
#    def __init__(self, data, cursor):
#        size = calcsize("IH")
#        data = unpack("IH", data[cursor:cursor + size])
    
class AKOF:
    def __init__(self, data, cursor):
        size = calcsize("IH")
        data = unpack("IH", data[cursor:cursor + size])
        self.dwAKCD = data[0]
        self.wAKCI = data[1]

class Akos:
    def __init__(self, data):
        self.data = data
        name = string_join(unpack('4c', data[0:4]), '')
        size = unpack('>I', data[4:8])[0]
        assert name == 'AKOS'
        cursor = 8
        
        while cursor < size:
            name = string_join(unpack('4c', data[cursor:cursor + 4]), '')
            size2 = unpack('>I', data[cursor + 4:cursor + 8])[0]
                
            cursor += 8

            handler = getattr(self, "do_" + name)
            handler(data, size2, cursor)

            cursor += size2 - 8

    def load_frame(self, index):
        if index > self.AKHD.nb_frames:
            raise "Attempted to load non-existent frame"
            
        self.pcurrent_AKCD = self.pAKCD + self.AKOF[index].dwAKCD
        self.pcurrent_AKCI = self.pAKCI + self.AKOF[index].wAKCI
        self.current_AKCI = AKCI(self.data, self.pcurrent_AKCI)
        self.current_frame = index
        
    def codec1(self):
        paletted = False
        
        if self.nb_colors == 32:
            iShift = 3
            bMask  = 0x7
        elif self.nb_colors == 64:
            iShift = 2
            bMask  = 0x3
        else:
            iShift = 4;
            bMask  = 0xF

        curX = 0
        wWidth = self.current_AKCI.wWidth
        wHeight = self.current_AKCI.wHeight
        h = wHeight
        dest = []
        
        for i in xrange(wWidth):
            for j in xrange(wHeight):
                dest.append(0)
        
        cursor = self.pcurrent_AKCD
        data = self.data
        dest_index = 0
        
        from PIL import Image, ImagePalette

        if paletted:
            img = Image.new("P", (wWidth, wHeight))
        else:
            img = Image.new("RGBA", (wWidth, wHeight))
        
        palette = []
        for i in xrange(768):
            palette.append(ord(data[self.pRGBS + i]))
        
        if paletted:
            img.putpalette(palette)
        
        while True:
            bCode = ord(data[cursor])
            cursor += 1
            bColor = bCode >> iShift;
            bRep = bCode & bMask
            
            if not bRep:
                bRep = ord(data[cursor])
                cursor += 1

            b = 0
            while b < bRep:
                if paletted:
                    img.putpixel((wWidth - 1, h - wHeight), bColor)
                else:
                    color = (palette[bColor * 3], palette[bColor * 3 + 1], palette[bColor * 3 + 2])
                    if not bColor:
                        color = (0, 0, 0, 0)
                    if bColor in (4, 11):
                        color = (0, 0, 0, 80)
                    img.putpixel((wWidth - 1, h - wHeight), color) # color)

                # dest[dest_index] = bColor
                dest_index += self.current_AKCI.wWidth
                    
                wHeight -= 1
                if not wHeight:
                    wHeight = self.current_AKCI.wHeight
                    curX += 1
                    dest_index = curX
                        
                    wWidth -= 1
                    if not wWidth:
                        img.save("D:\\popo.png")
                        return
                b = b + 1

    def save_frame(self, filename):
        codec = self.AKHD.codec
        if codec == 1:
            self.codec1()
        elif codec == 5:
            pass
        elif codec == 6:
            pass
        else: raise "Unknown codec"
            
    def do_AKHD(self, data, size, cursor):
        self.pAKHD = cursor
        self.AKHD = AKHD(data, cursor)
        
    def do_AKPL(self, data, size, cursor):
        self.nb_colors = size - 8
        self.pAKPL = cursor
        
    def do_RGBS(self, data, size, cursor):
        self.pRGBS = cursor

    def do_AKSQ(self, data, size, cursor):
        self.pAKSQ = cursor

    def do_AKCH(self, data, size, cursor):
        self.pAKCH = cursor

    def do_AKOF(self, data, size, cursor):
        self.pAKOF = cursor
        self.AKOF = []
        n = (size - 8) / 6
        for i in xrange(n):
            self.AKOF.append(AKOF(data, cursor + i * 6))

    def do_AKCI(self, data, size, cursor):
        self.pAKCI = cursor

    def do_AKCD(self, data, size, cursor):
        self.pAKCD = cursor

class AkosBrowser:
    def __init__(self, gamepath, gamename):
        self.gamepath = gamepath
        self.gamename = gamename
        self.resourcemanager = ScummResourceManager(gamepath, gamename)
        
    def load_costume(self, cost):
        if cost > self.resourcemanager.get_nb_costumes():
            raise "Costume out of range"
            
        self.current_cost = cost
        self.loaded = False
        
        self.costdata = self.resourcemanager.load_costume(cost)
        
        self.akos = Akos(self.costdata)
        self.akos.load_frame(0)
        
    def save_frame(self, filename):
        self.akos.save_frame(filename)
        
        
"""
akos = AkosBrowser('E:\\', 'COMI')
akos.load_costume(2)
akos.akos.load_frame(650)
akos.save_frame('D:\\popo.png')
"""

def export_room_to_glumol(room, gamepath):
    mgr = ScummResourceManager(gamepath)
    print "load_room"
    roomdata, size = mgr.load_room(room)
    global data
    data = roomdata
    room = LFLF(0, size).room
    for i in room.objects:
        print i
    return room

if __name__ == "__main__":
  if os.name == "posix": #os.chdir("/home/bob/dev/grab")    
    export_room_to_glumol(15, '/media/cdrecorder')
  else:
    export_room_to_glumol(15, 'E:\\')
    
# CMI
# Room 14 : fort
