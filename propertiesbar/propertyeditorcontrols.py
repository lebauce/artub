import wx
import string
import sys
import os, os.path
from animation import CAnimation
from newanimation import NewAnimationDialog
import pypoujol.animation
from pypoujol import Animation, get_parent_class
import pypoujol.animation as animation
import wx.lib.imagebrowser as ib
from os.path import realpath, normpath, normcase, exists, join
from depplatform import get_image_path

oiLineHeight = 20

class InspectorEditorControl:
    """ Interface for controls that edit values in the Inspector
        values are stored in the native type of the control       """

    def __init__(self, propEditor, value):
        self.propEditor = propEditor
        self.editorCtrl = None
        self.wID = wx.NewId()
        self.value = value

    def createControl(self):
        if self.editorCtrl: self.editorCtrl.SetFocus()

    def destroyControl(self):
        """ Close an open editor control """
        if self.editorCtrl:
            self.editorCtrl.Destroy()
            self.editorCtrl = None

    def getValue(self):
        """ Read value from editor control """
        return self.value

    def setValue(self, value):
        """ Write value to editor control """
        self.value = value

    # default sizing for controls that span the entire value width
    def setWidth(self, width):
        if self.editorCtrl:
            height = self.editorCtrl.GetSize().y
            self.editorCtrl.SetSize(wx.Size(width -1, height))

    def setIdx(self, idx):
        """ Move the to the given index """
        if self.editorCtrl:
            self.editorCtrl.SetPosition( (-2, idx*oiLineHeight -2) )

    def OnSelect(self, event):
        """ Post the value.

            Bind the event of the control that 'sets' the value to this method
        """
        event.Skip()
        self.propEditor.inspectorPost(False)

class BevelIEC(InspectorEditorControl):
    def destroyControl(self):
        if self.bevelTop:
            self.bevelTop.Destroy()
            self.bevelTop = None
            self.bevelBottom.Destroy()
        InspectorEditorControl.destroyControl(self)

    def createControl(self, parent, idx, sizeX):
        self.bevelTop = wx.Panel(parent, -1,
            (0, idx*oiLineHeight -1), (sizeX, 1))
        self.bevelTop.SetBackgroundColour(wx.BLACK)
        self.bevelBottom = wx.Panel(parent, -1,
            (0, (idx + 1)*oiLineHeight -1), (sizeX, 1))
        self.bevelBottom.SetBackgroundColour(wx.WHITE)

    def setWidth(self, width):
        if self.bevelTop:
            self.bevelTop.SetSize(wx.Size(width, 1))
            self.bevelBottom.SetSize(wx.Size(width, 1))

    def setIdx(self, idx):
        if self.bevelTop:
            self.bevelTop.SetPosition(wx.Point(-2, idx*oiLineHeight -1))
            self.bevelBottom.SetPosition(wx.Point(-2, (idx +1)*oiLineHeight -1))
#        InspectorEditorControl.setIdx(self, idx)

class BeveledLabelIEC(BevelIEC):
    def createControl(self, parent, idx, sizeX):
        BevelIEC.createControl(self, parent, idx, sizeX)
        self.editorCtrl = wx.StaticText(parent, -1, self.value,
            (2, idx*oiLineHeight+2),
            (sizeX, oiLineHeight-3))
        self.editorCtrl.SetForegroundColour(wx.Colour(24, 24, 24)) #Preferences.propValueColour)

class TextCtrlIEC(InspectorEditorControl):
    ugly_hack = True
    
    def createControl(self, parent, value, idx, sizeX, style=wx.TE_PROCESS_ENTER):
        value = self.propEditor.valueToIECValue()
        self.editorCtrl = wx.TextCtrl(parent, self.wID, value,
              (-2, idx*oiLineHeight -2),
              (sizeX, oiLineHeight+3), style = style)
        wx.EVT_TEXT_ENTER(parent, self.wID, self.OnSelect)
        InspectorEditorControl.createControl(self)

        if value:
            self.editorCtrl.SetSelection(0, len(value))
        
        # Ugly hack. It doesn't get focus the very first time
        if TextCtrlIEC.ugly_hack:
            wx.GetApp().frame.pb.Freeze()
            wx.GetApp().frame.pb.nb.SetSelection(1)
            wx.GetApp().frame.pb.nb.SetSelection(0)
            wx.GetApp().frame.pb.Thaw()
            TextCtrlIEC.ugly_hack = False
            
    def getValue(self):
        if self.editorCtrl:
            self.value = self.editorCtrl.GetValue()
        return self.value

    def setValue(self, value):
        self.value = value
        if self.editorCtrl:
            self.editorCtrl.SetValue(value)
            
class ChoiceIEC(InspectorEditorControl):
    def createControl(self, parent, values, idx, sizeX, iec = None):
        self.editorCtrl = wx.Choice(parent, self.wID,
         wx.Point(-2, idx*oiLineHeight -1), wx.Size(sizeX, oiLineHeight+3),
         values)
        wx.EVT_CHOICE(self.editorCtrl, self.wID, self.OnSelect)
        InspectorEditorControl.createControl(self)
        self.iec = None
        
    def getValue(self):
        if self.editorCtrl:
            sel = self.editorCtrl.CurrentSelection
            #if sel != -1: return self.editorCtrl.GetClientData(sel)
            return self.editorCtrl.GetStringSelection()

    def setValue(self, value):
        if self.editorCtrl:
            self.editorCtrl.SetStringSelection(value)
    
    def repopulate(self):
        self.editorCtrl.Clear()
        for val in self.propEditor.getValues():
            self.editorCtrl.Append(val)
    
    def OnSelect(self, evt):
        InspectorEditorControl.OnSelect(self, evt)
        
class ComboIEC(InspectorEditorControl):
    def createControl(self, parent, idx, sizeX):
        self.editorCtrl = wxComboBox(parent, self.wID, self.value,
         wxPoint(-2, idx*Preferences.oiLineHeight -1), wxSize(sizeX, Preferences.oiLineHeight+3),
         self.propEditor.getValues())
        InspectorEditorControl.createControl(self);
    def getValue(self):
        if self.editorCtrl:
            return self.editorCtrl.GetStringSelection()
    def setValue(self, value):
        if self.editorCtrl:
            self.editorCtrl.SetSelection(self.editorCtrl.FindString(value))

class ButtonIEC(BevelIEC):
    btnSize = 18
    def createControl(self, parent, idx, sizeX, editMeth):
        bmp = wx.Image(get_image_path('ellipsis.xpm'), wx.BITMAP_TYPE_XPM).ConvertToBitmap()
        self.editorCtrl = wx.BitmapButton(parent, self.wID, bmp,
          wx.Point(sizeX - self.btnSize - 3, idx*oiLineHeight +1),
          wx.Size(self.btnSize, oiLineHeight-2))
        self.propValLabel = wx.StaticText(parent, -1, str(self.getValue()),
          wx.Point(2, idx*oiLineHeight+2), 
          wx.Size(sizeX - self.btnSize - 6, oiLineHeight-3),
          style=wx.ST_NO_AUTORESIZE)
        wx.EVT_BUTTON(self.editorCtrl, self.wID, editMeth)
        BevelIEC.createControl(self, parent, idx, sizeX)

    def setWidth(self, width):
        if self.editorCtrl:
            self.editorCtrl.SetDimensions(width - self.btnSize - 3, 
              self.editorCtrl.GetPosition().y, self.btnSize, 
              oiLineHeight-2)
            self.propValLabel.SetDimensions(2, 
              self.propValLabel.GetPosition().y, width - self.btnSize - 6, 
              oiLineHeight-3)

        BevelIEC.setWidth(self, width)

    def setIdx(self, idx):
        if self.editorCtrl:
            self.editorCtrl.SetDimensions(self.editorCtrl.GetPosition().x,
              idx*oiLineHeight +2, self.btnSize, 
              oiLineHeight-2)
            self.propValLabel.SetDimensions(
              self.propValLabel.GetPosition().x, 
              idx*oiLineHeight +1, self.propValueLabel.GetSize().x,
              oiLineHeight-3)

        BevelIEC.setIdx(self, idx)

    def setValue(self, value):
        BevelIEC.setValue(self, value)
        self.propValLabel.SetLabel(str(value))

    def destroyControl(self):
        if self.editorCtrl:
            self.propValLabel.Destroy()
            self.propValLabel = None
        BevelIEC.destroyControl(self)

class TextCtrlButtonIEC(BevelIEC):
    def createControl(self, parent, value, idx, sizeX, editMeth = None):
        bmp = wx.Bitmap('images/ellipsis.xpm')
        value = self.propEditor.valueToIECValue()
        self.wID2 = wx.NewId()
        self.editorCtrl = [
              wx.TextCtrl(parent, self.wID, value,
               (-2, idx*oiLineHeight -2),
               (sizeX - 18, oiLineHeight+3)),#, style = style),
              wx.BitmapButton(parent, self.wID2, bmp,
               (sizeX - 18 -3, idx*oiLineHeight +1),
               (18, oiLineHeight-2))]
        EVT_BUTTON(self.editorCtrl[1], self.wID2, editMeth)

        if value:
            self.editorCtrl[0].SetSelection(0, len(value))

        BevelIEC.createControl(self, parent, idx, sizeX)

    def destroyControl(self):
        """ Close an open editor control """
        if self.editorCtrl:
            #self.editorCtrl.GetParent().SetFocus()
            for ec in self.editorCtrl:
                ec.Destroy()
            self.editorCtrl = None
        if self.bevelTop:
            self.bevelTop.Destroy()
            self.bevelTop = None
            self.bevelBottom.Destroy()
            self.bevelBottom = None

    # default sizing for controls that span the entire value width
    def setWidth(self, width):
        if self.editorCtrl:
            self.editorCtrl[0].SetSize(wxSize(width -18,
                  self.editorCtrl[0].GetSize().y))
            self.editorCtrl[1].SetDimensions(width - 18 -3,
                  self.editorCtrl[1].GetPosition().y, 18,
                  Preferences.oiLineHeight-2)

        BevelIEC.setWidth(self, width)

    def setIdx(self, idx):
        """ Move the to the given index """
        if self.editorCtrl:
            for ec in self.editorCtrl:
                ec.SetPosition(ec.GetPosition().x, idx*Preferences.oiLineHeight -2)
        BevelIEC.setIdx(self, idx)

    def getValue(self):
        if self.editorCtrl:
            self.value = self.editorCtrl[0].GetValue()
        return self.value

    def setValue(self, value):
        self.value = value
        if self.editorCtrl:
            self.editorCtrl[0].SetValue(value)

class CheckBoxIEC2(InspectorEditorControl):
    def createControl(self, parent, idx, sizeX):
        self.editorCtrl = wxWindow(parent, wxNewId(),
         style = wxTAB_TRAVERSAL | wxSUNKEN_BORDER)
        self.editorCtrl.SetDimensions(-2, idx*Preferences.oiLineHeight-2,
         sizeX, Preferences.oiLineHeight+3)

        self.checkBox = wxCheckBox(self.editorCtrl, self.wID, 'False', (2, 1))
        EVT_CHECKBOX(self.editorCtrl, self.wID, self.OnSelect)
        def OnWinSize(evt, win=self.checkBox):
            win.SetSize(evt.GetSize())
        EVT_SIZE(self.editorCtrl, OnWinSize)

        InspectorEditorControl.createControl(self)

    truefalseMap = {True: 'True', False: 'False'}
    def getValue(self):
        if self.editorCtrl:
            return self.truefalseMap[self.editorCtrl.GetValue()]
    def setValue(self, value):
        if self.editorCtrl:
            self.editorCtrl.SetLabel(value)
            self.editorCtrl.SetValue(self.truefalseMap[True] == value)

    def OnSelect(self, event):
        if event.IsChecked():
            self.setValue(self.truefalseMap[event.IsChecked()])

        InspectorEditorControl.OnSelect(self, event)

class CheckBoxIEC(BevelIEC):
    def createControl(self, parent, idx, sizeX):
        self.editorCtrl = wx.CheckBox(parent, self.wID, 'False',
            (2, idx*oiLineHeight+1),
            (sizeX, oiLineHeight-2) )
        wx.EVT_CHECKBOX(self.editorCtrl, self.wID, self.OnSelect)

        BevelIEC.createControl(self, parent, idx, sizeX)

    truefalseMap = {True: 'True', False: 'False'}
    def getValue(self):
        if self.editorCtrl:
            return self.truefalseMap[self.editorCtrl.GetValue()]
        else:
            return self.value
    def setValue(self, value):
        if self.editorCtrl:
            self.editorCtrl.SetLabel(value)
            self.editorCtrl.SetValue(
                string.lower(self.truefalseMap[True]) == string.lower(value))

    def setIdx(self, idx):
        if self.editorCtrl:
            self.editorCtrl.SetDimensions(2, idx*Preferences.oiLineHeight +1,
            self.editorCtrl.GetSize().x, Preferences.oiLineHeight-2)
        BevelIEC.setIdx(self, idx)
        # InspectorEditorControl.setIdx(self, idx)

    def OnSelect(self, event):
        self.setValue(self.truefalseMap[event.IsChecked()])

        BevelIEC.OnSelect(self, event)

import  wx.lib.popupctl as  pop
import  wx.calendar     as  cal

thumbnail_size = 64

class AnimationPanel(wx.Panel):
    class ThumbnailCache:
        def __init__(self):
            self.cache = {}
            
        def get_thumbnail(self, filename):
            filename = join(wx.GetApp().frame.project.project_path, filename)
            if not exists(filename):
                return None
            if self.cache.has_key(filename):
                return self.cache[filename]
            img = wx.Image(filename)
            w, h = img.GetWidth(), img.GetHeight()
            if w > h:
                h *= thumbnail_size / float(w)
                w = thumbnail_size
            else:
                w *= thumbnail_size / float(h)
                h = thumbnail_size
                
            img.Rescale(w, h)
            bmp = wx.BitmapFromImage(img)
            self.cache[filename] = bmp
            return bmp
    
    cache = ThumbnailCache()
    
    def __init__(self, parent, iec, poz):
        wx.Panel.__init__(self, parent, pos = poz)
        self.parent = parent
        self.iec = iec

        n = len(pypoujol.animation.anim_classes.values()) + 2
        self.SetSize((thumbnail_size * 4 + 40, (n / 4) * thumbnail_size + 104))
        parent.SetSize((thumbnail_size * 4 + 40, (n / 4) * thumbnail_size + 104))
        
    def create_buttons(self):
        def is_derived_from(c, b):
            try:
                for i in c.__bases__:
                    if b == i: return True
                    if is_derived_from(i, b): return True
                return None
            except: pass # Not a class ?

        if sys.platform == "darwin": pos = (20, 20)
        else: pos = (20, 20)
        cancel = wx.Button(self, 30, "Cancel\n", pos = pos, size = (thumbnail_size, thumbnail_size))
        cancel.Bind(wx.EVT_BUTTON, self.on_cancel_button)
        n = 1
        pos = ((n % 4) * thumbnail_size + 20, (n / 4) * thumbnail_size + 20)
        nonebutton = wx.Button(self, -1, "None\n", pos = pos, size = (thumbnail_size, thumbnail_size))
        nonebutton.Bind(wx.EVT_BUTTON, self.on_none_button)
        n += 1
        newanimbutton = wx.Button(self, -1, "From file\n",
            pos = ((n % 4) * thumbnail_size + 20,
                   (n / 4) * thumbnail_size + 20),
            size = (thumbnail_size, thumbnail_size))
        newanimbutton.Bind(wx.EVT_BUTTON, self.on_new_anim_button)
        n += 1
        self.buttons = []

        for i, filename, j in pypoujol.animation.anim_classes.values():
            if (not filename) or (not filename[0]): continue
            filename = filename[0]
            bmp = self.cache.get_thumbnail(filename)
            if not bmp: continue
            b = wx.BitmapButton(self, 30 + n, bmp, ((n % 4) * thumbnail_size + 20, (n / 4) * thumbnail_size + 20), (thumbnail_size, thumbnail_size))
            self.buttons.append(b)
            try:
                parent_class = get_parent_class(j)
                b.image = parent_class
                b.Bind(wx.EVT_BUTTON, self.on_button)
                n = n + 1
            except: pass

    def on_cancel_button(self, evt):
        self.iec.editorCtrl.PopDown()
        
    def on_none_button(self, evt):
        self.iec.editorCtrl.SetValue("None")
        self.iec.editorCtrl.PopDown()

    def on_new_anim_button(self, evt):
        self.iec.editorCtrl.PopDown()
        
        newanimdlg = NewAnimationDialog(wx.GetApp().frame, -1, size = (500, 400),
                                        style = wx.DEFAULT_DIALOG_STYLE)
        newanimdlg.CenterOnScreen()
        newanimdlg.name.SetValue(self.iec.resource.__class__.__name__ + "_anim")
        val = newanimdlg.ShowModal()
    
        if val == wx.ID_OK:
            project = wx.GetApp().frame.project
            res = wx.GetApp().frame.pb.active_resource
            res.sync()
            name = newanimdlg.name.GetValue()
            filename = project.ask_to_import(newanimdlg.filename.GetValue())
            
            if filename.endswith('.psd'):
                from PythonMagick import Image
                img = Image(str(filename))
                base = str(filename[:-4]) + '.png'
                import tempfile
                import os.path
                import os
                import exceptions
                import glob
                
                tempdir = tempfile.gettempdir()
                infos = img.get_layer_names()
                infos = infos.split('\n')
                layers = []
                for i in infos:
                    n, x, y = i.split('|')
                    x = int(x)
                    y = int(y)
                    layers.append((n, x, y))
                tempdir = tempdir + '/psd_outputs'
                try: os.mkdir(tempdir)
                except exceptions.OSError: 
                    for i in glob.glob(tempdir + '/*'):
                        os.remove(i)
                
                img.write_files(tempdir + '/' + os.path.basename(base))
                dlg = ib.ImageDialog(self, tempdir)
                dlg.Centre() 

                if dlg.ShowModal() == wx.ID_OK:
                    import shutil
                    filename = wx.GetApp().frame.project.project_path + '/' + os.path.basename(dlg.GetFile())
                    shutil.copyfile(dlg.GetFile(), filename)
                    
                else:
                    self.iec.editorCtrl.PopDown()
                    newanimdlg.Destroy()
                    return

                for i in glob.glob(tempdir + '/*'):
                    os.remove(i)
                os.rmdir(tempdir)
            
            filename = filename.replace('\\', '\\\\')
            nom = get_parent_class(self.iec.resource.__class__)
            classe = res.get_class(nom)
            c = classe.add_class(name, ["Animation"], [
                           "filenames = [u'" + filename + "']\n"])
            res.ast_has_changed = True
            res.topy()
            wx.GetApp().gns.run(res.listing)
            wx.GetApp().artub_frame.update_treeitem(res)
            self.iec.editorCtrl.SetValue(nom + '.' + name)
            import os
            if os.name != "posix":
                self.iec.editorCtrl.PopDown()
            self.iec.propEditor.inspectorPost(False)
            
        newanimdlg.Destroy()
        
    def on_button(self, evt):
        self.iec.editorCtrl.SetValue(evt.GetEventObject().image)
        self.iec.editorCtrl.PopDown()
        self.iec.propEditor.inspectorPost(False)
        evt.Skip()
        
    
from    wx.lib import masked
import  wx.lib.colourselect as  csel

class FloatCtrlIEC(InspectorEditorControl):
    def createControl(self, parent, value, idx, sizeX, constraints):
        self.editorCtrl = masked.NumCtrl(
                                parent, pos=(-2, idx*oiLineHeight-2),
                                size=(sizeX, oiLineHeight+3), value=value,
                                integerWidth=constraints[0],
                                fractionWidth=constraints[1], allowNegative=constraints[2],
                                min=constraints[3], max=constraints[4],
                                limited=constraints[5], autoSize=constraints[6])
    
    def getValue(self):
        self.value = self.editorCtrl.GetValue()
        return self.value
    
class ColorIEC(InspectorEditorControl):
    def createControl(self, parent, value, idx, sizeX, style=wx.TE_PROCESS_ENTER):
        # r = value[0] * 255
        # g = value[1] * 255
        # b = value[2] * 255
        r = value[0]
        g = value[1]
        b = value[2]
        self.parent = parent
        self.sizeX = sizeX
        self.idx = idx
        s = "(%d, %d, %d)" % (r, g, b)
        self.editorCtrl = csel.ColourSelect(parent, 2000, s, wx.Color(r, g, b),
                                            size=(sizeX, oiLineHeight+3),
                                            pos=(-2, idx*oiLineHeight-2))
        self.editorCtrl.Bind(csel.EVT_COLOURSELECT, self.on_select_color, id=2000)
                                            
    def getValue(self):
        self.value = self.editorCtrl.GetValue()
        self.value = (self.value.Red(), self.value.Green(), self.value.Blue())
        # self.value = (self.value.Red() / 255., self.value.Green() / 255., self.value.Blue() / 255.)
        return self.value

    def on_select_color(self, evt):
        value = evt.GetValue()
        self.editorCtrl.Destroy()
        s = "(%d, %d, %d)" % (value[0], value[1], value[2])
        self.editorCtrl = csel.ColourSelect(self.parent, 2000, s, wx.Color(value[0], value[1], value[2]),
                                            size=(self.sizeX, oiLineHeight+3),
                                            pos=(-2, self.idx*oiLineHeight-2))
        self.editorCtrl.Refresh()
        self.propEditor.inspectorPost(False)
                
class AnimationIEC(InspectorEditorControl):
    def createControl(self, parent, value, idx, sizeX, style=wx.TE_PROCESS_ENTER):
        self.editorCtrl = pop.PopupControl(parent, -1, pos = (0,0), size = (sizeX,oiLineHeight))
        self.win = wx.Window(self.editorCtrl, wx.NewId(),
         style = wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER, size = (-1, -1)) # (200,200))
        self.win.Show(False)
        self.editorCtrl.SetDimensions(-2, idx*oiLineHeight-2,
         sizeX, oiLineHeight+3)

        self.cal = AnimationPanel(self.win, self, (0,0))
        self.cal.resource = self.resource
        
        self.editorCtrl.SetValue(value)
        self.editorCtrl.SetPopupContent(self.win)
        InspectorEditorControl.createControl(self)
        self.cal.create_buttons()

        wx.EVT_KILL_FOCUS(self.cal, self.on_left_button_down)

    def on_left_button_down(self, evt):
        # self.editorCtrl.PopDown()
        evt.Skip()
        
    def getValue(self):
        if self.editorCtrl:
            return self.editorCtrl.GetValue()
            
    def setValue(self, value):
        if self.editorCtrl:
            self.editorCtrl.SetLabel(value)
            self.editorCtrl.SetValue(self.truefalseMap[True] == value)

    def OnSelect(self, event):
        if event.IsChecked():
            self.setValue(self.truefalseMap[event.IsChecked()])

        InspectorEditorControl.OnSelect(self, event)
