from os.path import join

import sys

try:
   s = "from %s import *" % sys.platform
   exec s
except:
   raise "Unknown platform", sys.platform
   
set_sys_path()
import wx
    
def get_image_path(filename):
    return join(wx.GetApp().artub_path, 'images', filename)
