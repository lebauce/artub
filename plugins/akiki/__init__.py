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

from resourceeditor import CResourceEditor
from propertiesbar.companions import Companion, ResourceCompanion
from project import CProject
from script import CScript, get_function_args
from akikioptions import AkikiOptions
import wx
import sys
import string
from propertiesbar.propertyeditors import Filename
from propertiesbar.propertiesbar_actions import PropertiesBarChangeValue
from pypoujol import Scene, set_game
from gouzi import MethodNotFound
import undoredo
from undoredo import Action
from depplatform import get_image_path
import exceptions

class ProjectCompanion(Companion):
    def __init__(self, akiki, obj):
        Companion.__init__(self, obj)
        self.akiki = akiki
        self.resource = akiki.active_resource
        self.add_variables([ ["first_scene", ResourceCompanion(obj, Scene, as_string = True)] ])
        self.ignore.update(["screen", "to_call"])
        self.functions = [ "on_key_down", "on_key_up", "on_key_down_repeat",
                           "on_mouse_button_down", "on_mouse_button_up",
                           "on_left_button_down", "on_left_button_up" ]

    def change_value(self, name, value):
        if name == "first_scene":
            if value == type(None):
                PropertiesBarChangeValue(self.resource, self.obj, name, None, method = "__init__")
            else:
                PropertiesBarChangeValue(self.resource, self.obj, name, value, method = "__init__")
        else:
            PropertiesBarChangeValue(self.resource, self.obj, name, value)

try:
    from wx import stc
    from StyledTextCtrl_2 import PythonSTC
    class AkikiWindow(PythonSTC):
        def __init__(self, parent, ID):
            PythonSTC.__init__(self, parent, ID)
            self.SetEdgeMode(stc.STC_EDGE_NONE)
            self.SetSelBackground(True, wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT))
            self.SetSelForeground(True, wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))
            self.SetModEventMask(stc.STC_MOD_INSERTTEXT | stc.STC_MOD_DELETETEXT)
            self.Bind(wx.stc.EVT_STC_MODIFIED, self.on_code_modified)
            self.Bind(wx.stc.EVT_STC_UPDATEUI, self.on_change)
            self.bmp = wx.Bitmap(get_image_path("breakpoint2.png"))
            self.SetMarginMask(1, 0x0ff)
            self.MarkerDefineBitmap(6, self.bmp)
            self.bmp = wx.Bitmap(get_image_path("cursor2.png"))
            self.MarkerDefineBitmap(5, self.bmp)
            self.ignore_code_modified = False
            self.finddata = wx.FindReplaceData()
            self.Bind(wx.EVT_FIND, self.on_find)
            self.Bind(wx.EVT_FIND_REPLACE, self.on_replace)
            self.Bind(wx.EVT_FIND_REPLACE_ALL, self.on_replace_all)
        
        def on_replace_all(self, event):
            end = self.GetLastPosition()
            start = self.GetSelection()[1]
            findstring = self.finddata.GetFindString()
            loc = self.FindText(self.GetSelection()[1], end, findstring)
            n = 0
            if loc == -1:
                dlg = wx.MessageDialog(self, _('Find String Not Found'),
                              _('Find String Not Found'),
                              wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            else:
                while loc != -1:
                    n = n + 1
                    self.SetSelection(loc, loc + len(findstring))
                    self.ReplaceSelection(self.finddata.GetReplaceString())
                    loc = self.FindText(self.GetSelection()[1], end, findstring)
                dlg = wx.MessageDialog(self, str(n) + _(' occurences replaced'),
                              _('Replace done'),
                              wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                
        def on_replace(self, event):
            end = self.GetLastPosition()
            start = self.GetSelection()[1]
            findstring = self.finddata.GetFindString()
            loc = self.FindText(self.GetSelection()[1], end, findstring)
            if loc == -1:
                dlg = wx.MessageDialog(self, _('Find String Not Found'),
                              _('Find String Not Found'),
                              wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            if self.finddlg:
                self.finddlg.SetFocus()
            self.ShowPosition(loc)
            self.SetSelection(loc, loc + len(findstring))
            self.ReplaceSelection(self.finddata.GetReplaceString())
            
        def on_show_find(self, event):
            self.finddlg = wx.FindReplaceDialog(self, self.finddata, _("Find / Replace"), wx.FR_REPLACEDIALOG)
            self.finddlg.Show(True)
            
        def on_find_next(self, event):
            if self.finddata.GetFindString():
                self.on_find(event)
            else:
                self.on_show_find(event)
                
        def on_find(self, event):
            end = self.GetLastPosition()
            start = self.GetSelection()[1]
            findstring = self.finddata.GetFindString().lower()
            loc = self.FindText(self.GetSelection()[1], end, findstring)
            if loc == -1 and start != 0:
                # string not found, start at beginning
                start = 0
                loc = self.FindText(0, start, findstring)
            if loc == -1:
                dlg = wx.MessageDialog(self, _('Find String Not Found'),
                              _('Find String Not Found'),
                              wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            if self.finddlg:
                if loc == -1:
                    self.finddlg.SetFocus()
                    return
                else:
                    self.finddlg.Destroy()
                    self.finddlg = None
            self.ShowPosition(loc)
            self.SetSelection(loc, loc + len(findstring))

        def on_change(self, evt):
            pos = self.GetCurrentPos()
            line = self.LineFromPosition(pos)
            pos = pos - self.PositionFromLine(line)
            wx.GetApp().frame.statusbar.SetStatusText(_("Line ") + str(line + 1) + _(", column ") + str(pos + 1))
            
        def on_code_modified(self, evt):
            if self.ignore_code_modified:
                return

            modif = evt.GetLength()
            if modif == 2 and evt.GetText() == "\r\n":
                modif = 1

            if self.backspace:
                modif = -1
                self.backspace = False
                
            class TextAdd(Action):
                def __init__(self, name):
                    Action.__init__(self, name)
                    self.modif = modif
                    
                def do(this):
                    self.ignore_code_modified = True
                    self.Redo()
                    self.ignore_code_modified = False
                    
                def undo(this):
                    self.ignore_code_modified = True
                    self.Undo()
                    self.ignore_code_modified = False
            
            last_action = None
            add_action = False
            if undoredo.undomanager.undos:
                last_action = undoredo.undomanager.undos[-1]
                if not last_action.name == "change text":
                    add_action = True
                else:
                    if modif not in [1, -1]:
                        add_action = True
                    else:
                        if last_action.modif not in [1, -1]:
                            add_action = True
                        if modif != last_action.modif:
                            add_action = True
            else:
                add_action = True
            if self.cut_paste:
                add_action = False
                self.cut_paste = False
            if add_action:
                TextAdd(_("change text"))
                    
        def Clear(self):
            self.ClearAll()

        def SetInsertionPoint(self, pos):
            self.SetCurrentPos(pos)

        def ShowPosition(self, pos):
            self.GotoPos(pos)

        def GetLastPosition(self):
            return self.GetLength()

        def GetRange(self, start, end):
            return self.GetTextRange(start, end)

        def GetSelection(self):
            return self.GetAnchor(), self.GetCurrentPos()

        def SetSelection(self, start, end):
            self.SetSelectionStart(start)
            self.SetSelectionEnd(end)
            
except ImportError:
    class AkikiWindow(wx.TextCtrl):
        def __init__(self, parent, ID):
            wx.TextCtrl.__init__(self, parent, ID, style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL | wx.TE_RICH2 | wx.TE_NOHIDESEL)

class Akiki(CResourceEditor):
    known_resources = [ CProject, CScript ]
    options = ( AkikiOptions, "Akiki options" )
    name = "akiki"
    
    def __init__(self):
        CResourceEditor.__init__(self)
    
    def set_listing(self, l):
        self.wnd.ignore_code_modified = True
        self.wnd.SetText(l)
        self.wnd.EmptyUndoBuffer()
        self.wnd.SetSavePoint()
        self.wnd.ignore_code_modified = False
        
    def on_toggle_breakpoint(self, evt):
        line = self.wnd.LineFromPosition(self.wnd.GetCurrentPos())
        marker = self.wnd.MarkerGet(line)
        
        if marker & (1 << 6):
            for k, v in self.active_resource.breakpoints.items():
                if line == v.line: # line == self.wnd.MarkerLineFromHandle(k):
                    self.active_resource.remove_breakpoint(k)
                    self.wnd.MarkerDelete(line, 6)
        else:
            id = self.wnd.MarkerAdd(line, 6)
            self.active_resource.add_breakpoint(id, line, id)
        if self.artub.debugging:
            self.artub.debugger.set_break(self.active_resource, line)
    
    def on_find(self, event):
        self.wnd.on_show_find(event)
        
    def on_find_next(self, event):
        self.wnd.on_find_next(event)
        
    def go_to_line(self, line):
        self.wnd.ScrollToLine(max(line - 10, 0))
        
    def remove_debug_cursor(self, line):
        self.wnd.MarkerDelete(line, 5)
        self.set_breakpoints()
        
    def get_current_line(self):
        return self.wnd.LineFromPosition(self.wnd.GetCurrentPos())

    def set_debug_cursor(self, line):
        self.wnd.MarkerDelete(line, 6)
        self.wnd.MarkerAdd(line, 5)
        self.go_to_line(line)

    def create_window(self, resource, parent_window):
        self.parent = parent_window
        self.wnd = AkikiWindow(parent_window, -1)
        return (self.wnd, resource.name + " (code)")

    def set_breakpoints(self):
        for k, bp in self.active_resource.breakpoints.items():
            if bp.enabled:
                bp.handle = self.wnd.MarkerAdd(bp.line, 6)
            else:
                bp.handle = self.wnd.MarkerAdd(bp.line, 7)

    def update(self, save=True):
        if save:
            if not self.wnd.GetModify(): return
            self.active_resource.last_position = self.wnd.GetAnchor()
            self.active_resource.listing = self.wnd.GetTextRange(0, self.wnd.GetLastPosition())
            try:
                self.active_resource.exec_listing()
            except (exceptions.IndentationError, exceptions.SyntaxError), excpt:
                tb = sys.exc_info()[2]
                dlg = wx.MessageDialog(self.artub,
                                       _("There is an error in your code at line ") + \
                                       str(sys.exc_info()[1].lineno),
                                       _("Error"),
                                       wx.OK)
                self.go_to_line(sys.exc_info()[1].lineno)
                dlg.ShowModal()
                dlg.Destroy()
                self.wnd.Raise()
                return -1
            except:
                sys.excepthook(*sys.exc_info())
                tb = sys.exc_info()[2]
                while tb.tb_next:
                    tb = tb.tb_next
                f = tb.tb_frame
                dlg = wx.MessageDialog(self.artub,
                                       _("There is an error in your code at line ") + \
                                       str(tb.tb_lineno), #str(sys.exc_info()[1].lineno)),
                                       _("Error"),
                                       wx.OK)
                self.go_to_line(tb.tb_lineno)
                dlg.ShowModal()
                dlg.Destroy()
                self.wnd.Raise()
                return -1
            for k, bp in self.active_resource.breakpoints.items():
                line = self.wnd.MarkerLineFromHandle(bp.handle)
                if line != -1:
                    bp.line = line
                else:
                    del self.active_resource.breakpoints[k]
        else:
            if not self.active_resource.listing and sys.platform == 'darwin':
                self.active_resource.listing = "\n"
            self.set_listing(self.active_resource.listing)
            self.active_resource.sync()
            if isinstance(self.active_resource, CProject):
                try:
                    obj = wx.GetApp().gns.create_from_script(self.active_resource)
                    set_game(obj)
                    obj.filename = Filename(obj.filename)
                    inspector = ProjectCompanion(self, obj)
                    self.artub.pb.set_inspector(inspector)
                except:
                    print "There were syntax errors in your listing"
                    sys.excepthook(*sys.exc_info())
            #else:
            #    self.artub.pb.set_inspector(None)
                
            self.set_breakpoints()
            if hasattr(self.active_resource, "debug_cursor"):
                self.wnd.MarkerAdd(self.active_resource.debug_cursor)

    def edit_event(self, func, name):
        self.wnd.EnsureCaretVisible()
        c = self.active_resource.get_class(name)
        try:
            m = c.get_method(func.func_name)
            self.go_to_line(m.ast.lineno)
            pos = self.wnd.PositionFromLine(m.ast.lineno)
            self.wnd.SetSelection(pos, pos)
        except MethodNotFound:
            args = get_function_args(func)    
            f = c.add_function("def "+ func.func_name + "(" + args + "): pass")
            self.active_resource.ast_has_changed = True
            self.set_listing(self.active_resource.listing)
            c = self.active_resource.get_class(name)
            m = c.get_method(func.func_name)
            self.go_to_line(m.ast.lineno)
            pos = self.wnd.PositionFromLine(m.ast.lineno)
            pos = self.wnd.FindText(pos, self.wnd.GetTextLength(), "pass")
            if pos != -1: self.wnd.SetSelection(pos, pos + 4)
        self.wnd.SetFocus()
        
    def close_window(self):
        self.parent.remove_page(self.wnd)
    
    def modified_data(self, obj, attr, value):
        script = self.active_resource
        lines = script.listing.split('\n')
        lineno = -1
        linenb = 0
        for i in lines:
            line = i.replace(' ', '')
            if line.find('self.' + attr + '=') != -1:
                index = i.find('=') + 1
                index2 = index
                if type(value) == type('') or type(value) == type(u''):
                    s = "'" + str(value) + "'"
                else:
                    s = str(value)
                lines[linenb] = i.replace(i[index:], s)
                break
            linenb = linenb + 1
        self.active_resource.listing = string.join(lines, '\n')
        self.set_listing(self.active_resource.listing)
    
    def get_popup_menu(self, resource):
        artub = self.artub
        menu = wx.Menu()
        new = wx.Menu()
        new.AppendMenu(wx.NewId(), "New scene",
                    artub.get_templates_menu(
                    callback = self.artub.on_new_class,
                    section = "Scene", prefix = ""))
        new.AppendMenu(wx.NewId(), "New sprite",
                artub.get_templates_menu(
                callback = self.artub.on_new_class,
                section = "Sprite", prefix = ""))
        new.Append(artub.new_anim_id, _("New animation"), _("New animation"))
        wx.EVT_MENU(new, artub.new_anim_id, artub.on_new_animation)
        new.Append(artub.new_font_id, _("New font"), _("New font"))
        wx.EVT_MENU(new, artub.new_font_id, artub.on_new_font)
        new.Append(artub.new_script_id, _("New script"), _("New script"))
        wx.EVT_MENU(new, artub.new_script_id, artub.on_new_script)
        new.Append(artub.new_dialog_id, _("New dialog"), _("New dialog"))
        wx.EVT_MENU(new, artub.new_dialog_id, artub.on_new_dialog)
        menu.AppendMenu(-1, "New", new) 
        menu.Append(artub.propID, _("Properties"), _("Properties"))
        
        return menu

editor = Akiki
