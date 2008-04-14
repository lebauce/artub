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

    def DoLogString(self, message, timeStamp):
        if self.logTime:
            message = time.strftime("%Xl",
                                    time.localtime(timeStamp)) + ": " + message
        if self.tc:
            self.tc.AppendText(message)

    def write(self, message):
        print message # wx.LogMessage(message)

    def redirect_outputs(self):
        self.oldstdout = sys.stdout
        sys.stdout = self
        
    def restore_outputs(self):
        sys.stdout = self.oldstdout

_log = ArtubLog()
wx.Log_SetActiveTarget(_log)

def set_text_ctrl(self, textCtrl):
    _log.tc = textCtrl
    _log.redirect_outputs()

def log(*args):
    global _log
    s = ""
    for i in args:
        s = s + str(i) + ' '
    _log.write(s)

output = log

