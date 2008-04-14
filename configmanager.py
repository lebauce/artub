import wx
from log import log

class ConfigManager:
    def __init__(self):
        log("Loading configuration")
        self.config = wx.FileConfig("artub", "bnc", "artub.conf")
        
    def __getitem__(self, key):
        if type(key) != str:
            raise KeyError
        if not self.config.Exists(key):
            raise IndexError
        try:
           val = self.config.Read(key)
        except:
           return ''
        return val
    
    def __setitem__(self, key, item):
        if type(key) != str:
            raise KeyError
        self.config.Write(key, str(item))
    
config = ConfigManager()       