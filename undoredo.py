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

from configmanager import config
import wx

undomanager = None

class Action:
    def __init__(self, name, volatil = False, inverted = False):
        self.name = name
        self.volatil = volatil
        self.inverted = inverted
        self.first = True
        undomanager.add_action(self)
        self.first = False
        
    def do(self):
        pass
    
    def undo(self):
        pass
        
class UndoManager:
    def __init__(self):
        global undomanager
        undomanager = self
        self.undos = []
        self.redos = []
        self.grouping = 0
        self.modifs = 0
        self.protected = False
        self.modified = False
        self.menu = None
        try:
            self.max_modifs = int(config["modifs_limit"])
        except:
            self.max_modifs = 10
        self.handlers = [ self.undo, self.redo, self.on_cut, self.on_copy, self.on_paste ]
        
    def on_event(self, evt):
        id = evt.GetId() - self.artub_frame.undoID
        self.handlers[id]()
            
    def on_update_ui(self, evt):
        id = evt.GetId() - self.artub_frame.undoID
        if id == 0:
            if self.can_undo():
                evt.SetText(_("Undo ") + self.undos[-1].name)
            evt.Enable(self.can_undo())
        elif id == 1:
            if self.can_redo():
                evt.SetText(_("Redo ") + self.redos[-1].name)
            evt.Enable(self.can_redo())
    
    def set_modified(self, state = True):
        self.modified = state
    
    def care_of_menu(self, parent):
        self.artub_frame = parent
        wx.EVT_MENU_RANGE(wx.GetApp(), parent.undoID, parent.pasteID, parent.undo)
        wx.EVT_UPDATE_UI_RANGE(wx.GetApp(), parent.undoID, parent.pasteID, parent.undo_update_ui)

    def undo(self):
        self.protect()
        if self.can_undo():
            while True:
                action = self.undos.pop()
                self.modifs -= 1
                if action.inverted:
                    action.do()
                    self.undos.append(action)
                else:
                    action.undo()
                    self.redos.append(action)
                modified = self.is_modified()
                self.set_modified(action.modified_flag)
                action.modified_flag = modified
                if action.member_of_group <= 1:
                    break
        self.unprotect()
    
    def redo(self):
        self.protect()
        if self.can_redo():
            lastmemberofgroup = 0
            while True:
                action = self.redos.pop()
                self.modifs -= 1
                if action.inverted:
                    action.undo()
                    self.redos.append(action)
                else:
                    action.do()
                    self.undos.append(action)
                modified = self.is_modified()
                self.set_modified(action.modified_flag)
                action.modified_flag = modified
                if not self.can_redo() or \
                   action.member_of_group <= 1 or \
                   (action.member_of_group <= lastmemberofgroup):
                    break
                lastmemberofgroup = action.member_of_group;
        self.unprotect()
    
    def on_copy(self):
        if self.artub_frame.active_editor.__class__.__name__ == "Akiki":
            self.artub_frame.active_editor.wnd.Copy()
    
    def on_cut(self):
        if self.artub_frame.active_editor.__class__.__name__ == "Akiki":
            self.artub_frame.active_editor.wnd.Cut()
    
    def on_paste(self):
        if self.artub_frame.active_editor.__class__.__name__ == "Akiki":
            self.artub_frame.active_editor.wnd.Paste()
    
    def add_action(self, action):
        if self.is_protected(): raise "Undomanager protected"
        action.modified_flag = self.is_modified()
        action.do()
        if self.modifs >= self.max_modifs:
            self.undos.pop(0)
        else:
            self.modifs += 1
        action.member_of_group = self.grouping
        if self.is_grouping():
            self.grouping += 1
        self.undos.append(action)
        if len(self.redos):
            self.redos = []
        self.set_modified(True)
            
    def add_actions(self, actions):
        for i in actions:
            self.add_action(i)
    
    def remove_volatils(self):
        pass
    
    def can_undo(self):
        return len(self.undos) != 0
    
    def can_redo(self):
        return len(self.redos) != 0
    
    def delete_all(self):
        self.undos = []
        self.redos = []
        
    def set_modified(self, state):
        self.modified = state
        
    def is_modified(self):
        return self.modified
        
    def remove_volatils(self):
        def is_volatil(i):
            return i.volatil
        self.undos = self.undos.filter(is_volatil)
        self.redos = self.redos.filter(is_volatil)
    
    def reset(self):
        for i in self.undos:
            i.modified_flag = True
        for i in self.redos:
            i.modified_flag = True
        self.set_modified(False)

    def is_grouping(self):
        return self.grouping != 0
        
    def begin_group(self):
        self.grouping = 1
    
    def end_group(self):
        self.grouping = 0

    def saved(self):
        pass
    
    def is_protected(self):
        return self.protected
        
    def protect(self):
        self.protected = True
        
    def unprotect(self):
        self.protected = False

class ChangeProperty(Action):
    def __init__(self, tipe, listing, script, selected_script = None):
        self.type = 0
        self.listing = listing
        self.script = script
        self.selected_script = selected_script

    def do(self):
        pass
        
    def undo(self):
        pass

undo_manager = UndoManager()