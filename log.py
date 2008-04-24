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

import wx
import sys

_log = None
oldstdout = None

class ArtubLog(wx.PyLog):
    def __init__(self, textCtrl=None, logTime=0):
        wx.PyLog.__init__(self)
        self.tc = textCtrl
        self.logTime = logTime
        global _log
        _log = self

    def DoLogString(self, message, timeStamp = None):
        if self.tc:
            message = message.strip()
            if message:
                self.tc.AppendText(message + "\n")
        else:
            print message

    def write(self, message):
       # print message
       # wx.LogMessage(message)
       self.DoLogString(message)

    def redirect_outputs(self):
        self.oldstdout = sys.stdout
        sys.stdout = self
        
    def restore_outputs(self):
        sys.stdout = self.oldstdout

_log = ArtubLog()
wx.Log_SetActiveTarget(_log)

def set_text_ctrl(textCtrl):
    _log.tc = textCtrl
    _log.redirect_outputs()

def log(*args):
    global _log
    s = ""
    for i in args:
        s = s + str(i) + ' '
    _log.write(s)

output = log

