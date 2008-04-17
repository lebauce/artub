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

from poujol.poujol import *
import os
from new import instancemethod
import string

def chdir(path):
    try: os.mkdir(path)
    except: pass
    oldpass = os.getcwd()
    os.chdir(path)
    return oldpass
        
def gen_html(name, obj):
    buf = '<html><body><font face="Verdana">'
    if 0: # type(obj) == instancemethod:
        func = obj
        print name, dir(func)
        l = list(func.func_code.co_varnames)
        l2 = list(func.func_code.co_names)
        for i in l2[1:]:
            if i in l: l.remove(i)
        n = len(l)
        if func.func_defaults:
            n = n - len(func.func_defaults)
        j = 0
        args = ""
        for i in l:
            if j: args += ", "
            args += i 
            if j >= n:
                args += " = ", func.func_defaults[j - n]
            j = j + 1
        buf += name + '(' + args + ')'
        
    doc_list = []
    if type(obj) != instancemethod:
        doc_list.append(name) 
    doc_list += obj.__doc__.split("\n")
    if len(doc_list) >= 2 and doc_list[1].startswith("Event"):
        del doc_list[1]
    doc_list[0] = '<font color="blue"><b>' + doc_list[0] + "</b></font>"
    buf += string.join(doc_list, "<br>")
    buf += "</font></body></html>"
    return buf
    
def show_class_doc(classe):
    path = chdir(classe.__name__)
    print "Class " , classe.__name__
    print classe.__doc__
    print
    for i in classe.__dict__:
        obj = getattr(classe, i)
        if not i.startswith("__") and hasattr(obj, "__doc__") and obj.__doc__:
            open(i + ".html", "w").write(gen_html(i, obj))
    os.chdir(path)
    
chdir("docs")

show_class_doc(Game)
show_class_doc(Sprite)
show_class_doc(Region)
show_class_doc(Font)
