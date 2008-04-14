import wx
import string
from types import *
from propertyeditorcontrols import *
from new import instancemethod
from pypoujol import Animation, Sprite, Scene, global_dict
from log import log
from types import FunctionType, ClassType
from companions import ResourceCompanion, ColorCompanion, AnimationCompanion, \
                       EnumCompanion, PointCompanion, FilenameCompanion, FontCompanion
from gouzi import MethodNotFound
from undoredo import Action
from script import get_full_name
from pypoujol.path import Path
from inspect import isclass

oiLineHeight = 20

class Filename(str): pass

class PropertyRegistry:
    """ Factory to return propery editors from recognisable types
        It does not return property editors for certain design-time types like
        sets, enumerations, booleans, etc.
    """

    def __init__(self):
        self.classRegistry = {}
        self.typeRegistry = { int : IntPropEdit,
                              str : 1,
                              tuple : 2,
                              bool : BoolPropEdit,
                              float : FloatPropEdit,
                              instancemethod : IntPropEdit,
                              FunctionType : EventPropEdit,
                              Path : FilepathConfPropEdit
                              # , Point : PosPropEdit, poujol.Color : ColourConfPropEdit
                            }
                            
        self.companions = { ResourceCompanion : ResourcePropEdit,
                            ColorCompanion : ColourConfPropEdit,
                            AnimationCompanion : AnimationPropEdit,
                            EnumCompanion : EnumPropEdit,
                            PointCompanion : EnumPropEdit,
                            FilenameCompanion : FilepathConfPropEdit,
                            FontCompanion : FontPropEdit }

    def registerClasses(self, propClass, propEditors):
        for propEdit in propEditors:
            self.classRegistry[propClass.__name__] = propEdit

    def registerTypes(self, propType, propEditors):
        for propEdit in propEditors:
            self.typeRegistry[propType] = propEdit

    def factory(self, name, parent, idx, width, value, tipe, script, constraints):
        """
        if isinstance(constraints, ResourceCompanion):
            return ResourcePropEdit(name, parent, idx, width, value, script, constraints)
        elif isinstance(constraints, ColorCompanion):
            return ColourConfPropEdit(name, parent, idx, width, value, script, constraints)
        elif isinstance(constraints, AnimationCompanion):
            return AnimationPropEdit(name, parent, idx, width, value, script)
        elif isinstance(constraints, EnumCompanion):
            return EnumPropEdit(name, parent, idx, width, value, script)
        elif isinstance(constraints, PointCompanion):
            return EnumPropEdit(name, parent, idx, width, value, script)
        elif isinstance(constraints, FilenameCompanion):
            return FilepathConfPropEdit(name, parent, idx, width, value, script)
        elif isinstance(constraints, FontCompanion):
            return FontPropEdit(name, parent, idx, width, value, script)
        """
        comp = self.companions.get(constraints.__class__)
        if comp:
            return comp(name, parent, idx, width, value, script, constraints)
        elif self.typeRegistry.has_key(type(value)):
           return self.typeRegistry[type(value)](name, parent, idx, width, value, script)

class PropertyWrapper:
   def __init__(self, value, name):
      self.value = value
      self.name = name
   def getValue(self):
      return self.value
   def setValue(self, value):
      if type(value) != type(self.value):
         if type(self.value) == str:
            self.value = unicode(value)
            return
         #else:
         #   raise "Value must be of type " + str(type(self.value)) + " Had" + str(type(value)) + "instead."
      pass # self.value = type(self.value)(value)

# XXX Check IEC initialisation not from Display value but from 'valueFromIEC'
class PropertyEditor:
    """ Class associated with a design time identified type,
        it manages the behaviour of a NameValue in the Inspector
    """

    def __init__(self, name, parent, idx, width, value, _1=None , _2=None):
        self.name = name
        self.parent = parent

        self.idx = idx
        self.width = width
        self.editorCtrl = None
        self.style = []
        self.ownerPropEdit = None
        self.expanded = False
        self.initFromComponent()
        self.value = value
        self.script = _1
        self.propWrapper = PropertyWrapper(value, name)

    def initFromComponent(self):
        pass #self.value = self.propWrapper.getValue()
        if self.editorCtrl:
            self.editorCtrl.setValue(self.valueToIECValue())

    def edit(self):
        pass

    def inspectorEdit(self):
        """ Start a property editing operation and opens the inplace editor """
        pass

    def refreshCompCtrl(self):
        if self.obj and hasattr(self.obj, 'Refresh'):
            self.obj.Refresh()

    def validateProp(self, oldVal, newVal):
        pass

    def inspectorPost(self, closeEditor = True):
        """ Post inspector editor control, update ctrl and persist value """
        if self.editorCtrl:
            v = self.getValue()
            cv = self.getCtrlValue()
            # print 'v != cv', v, cv, type(v), type(cv) 
            # Only post changes
            if `v` != `cv`:
                self.validateProp(v, cv)
                self.setCtrlValue(cv, v)
                #self.refreshCompCtrl()
                #self.persistValue(self.valueAsExpr())
                # When sub properties post, update their main properies
                if self.ownerPropEdit: pass
                    #self.companion.updateOwnerFromObj()
                    #self.ownerPropEdit.initFromComponent()

                    # XXX Font's want new objects assigned to them before
                    # XXX they update
                    #if esRecreateProp in self.ownerPropEdit.getStyle():
                    #    v = self.companion.eval(self.ownerPropEdit.valueAsExpr())
                    #    self.ownerPropEdit.setCtrlValue(v, v)

                    #self.ownerPropEdit.persistValue(self.ownerPropEdit.valueAsExpr())
                    #self.ownerPropEdit.refreshCompCtrl()

                """if self.name in self.companion.mutualDepProps:
                    for prop in self.companion.mutualDepProps:
                        if prop != self.name:
                            insp = self.companion.designer.inspector
                            insp.constructorUpdate(prop)
                            insp.propertyUpdate(prop)"""
            if closeEditor and self.editorCtrl:
                self.editorCtrl.destroyControl()
                self.editorCtrl = None
        
        self.change_value()

    def change_value(self):
        # Control is destroyed, can't call self.getValue
        if type(self.value) == ClassType:
            self.companion.change_value(self.name, self.value.__name__)
        else:
            self.companion.change_value(self.name, self.value)
    
    def inspectorCancel(self):
        """ Cancel a property editor operation """
        if self.editorCtrl:
            self.editorCtrl.destroyControl()
            self.editorCtrl = None

    def getStyle(self):
        return self.style

    def getValue(self):
        """ Returns and initialises value for prop editor.
        

        If in edit mode, value should be read from the editor control

        Override if needed.
        """
        if self.editorCtrl:
            self.value = self.editorCtrl.getValue()
        return self.value

    def setValue(self, value):
        """ Initialise the prop editor and if needed the editor control """
        self.value = value
        if self.editorCtrl:
            self.editorCtrl.setValue(self.valueToIECValue())

    def getCtrlValue(self):
        """ Read current prop value from designed object """
        return self.propWrapper.getValue()

    def setCtrlValue(self, oldValue, value):
        """ Update designed object with current prop """
        # If overridden, rem to call check triggers if not calling parent method
        #self.companion.checkTriggers(self.name, oldValue, value)
        self.propWrapper.setValue(value)

    def persistValue(self, value):
        funcName = self.propWrapper.getSetterName()
        self.companion.persistProp(self.name, funcName, value)

    def getDisplayValue(self):
        """ Value that should display when the prop editor is not in edit mode """
        if isclass(self.value): return self.value.__name__
        else: return `self.value`

    def valueAsExpr(self):
        """ Return value as evaluatable source """
        return self.getDisplayValue()

    def getValues(self):
        """ Return list of options """
        return self.values

    def setValues(self, values):
        """ Sets list of options """
        self.values = values

    def valueToIECValue(self):
        """ Return prop value in the form that the form that the editor control expects """
        return self.value

    def setValueFromIECValue(self, value):
        """ Set value from the format that the editor control produces """
        self.value = value

    def setWidth(self, width):
        self.width = width
        if self.editorCtrl:
            self.editorCtrl.setWidth(width)

    def setIdx(self, idx):
        self.idx = idx
        if self.editorCtrl:
            self.editorCtrl.setIdx(idx)

class FactoryPropEdit(PropertyEditor):
    pass
        
class BITPropEditor(FactoryPropEdit):
    """ Editors for Built-in Python Types """
    def valueToIECValue(self):
        return `self.value`
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx, self.width)
    def getValue(self):
        if self.editorCtrl:
            try:
                value = eval(self.editorCtrl.getValue())
            except Exception, mess:
                wx.LogError('Invalid value: %s' % str(mess))
                raise
            self.value = value
        return self.value

class StrPropEdit(BITPropEditor):
    def valueToIECValue(self):
        return self.value

    def getValue(self):
        return FactoryPropEdit.getValue(self)

    def inspectorPost(self, close = True):
        BITPropEditor.inspectorPost(self, close)

class NamePropEdit(StrPropEdit):
    def __init__(self, name, parent, idx, width, value):
        StrPropEdit.__init__(self, name, parent, idx, width, value)

    identifier = string.letters+string.digits+'_'

    def getValue(self):
        # XXX Currently returning the old value in case of error because
        # XXX an exception here cannot be gracefully handled yet.
        # XXX Specifically closing the frame with the focus on the
        if self.editorCtrl:
            value = self.editorCtrl.getValue()
            if value != self.value:
                if self.companion.designer.objects.has_key(value):
                    wxLogError('Name already used by another control.')
                    return self.value

                if not value:
                    message = 'Invalid name for Python object'
                    wxLogError(message)
                    return self.value

                for c in value:
                    if c not in self.identifier:
                        message = 'Invalid name for Python object'
                        wxLogError(message)
                        return self.value
            self.value = value
        return self.value
                

class ConfPropEdit(PropertyEditor):
    def __init__(self, name, parent, idx, width, value, _1=None , _2=None):
        PropertyEditor.__init__(self, name, parent, idx, width, value, _1, _2)
        #self.setValues(names)

    def getDisplayValue(self):
        return str(self.value)

    def initFromComponent(self):
        pass # self.value = self.getCtrlValue()

    def persistValue(self, value):
        pass

class ContainerConfPropEdit(ConfPropEdit):
    def getStyle(self):
        return [esExpandable]
    def inspectorEdit(self):
        self.editorCtrl = BevelIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)

class StrConfPropEdit(ConfPropEdit):
    def valueToIECValue(self):
 #       return self.value
        return eval(self.value)

    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
            try:
                self.value = self.editorCtrl.getValue()
            except Exception, message:
                self.value = self.getCtrlValue()
                print 'invalid constr prop value', message
        else:
            self.value = self.getCtrlValue()
        return self.value

class PasswdStrConfPropEdit(StrConfPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width, style = wxTE_PASSWORD)
    def getDisplayValue(self):
        return '*'*len(self.value)

class EvalConfPropEdit(ConfPropEdit):
    def valueToIECValue(self):
        return `self.value`

    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, `self.value`)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
            try:
                self.value = eval(self.editorCtrl.getValue(), {})
            except Exception, message:
                self.value = self.getCtrlValue()
                print 'invalid constr prop value', message
        else:
            self.value = self.getCtrlValue()
        return self.value

class EnumConfPropEdit(ConfPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.getValue())
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.value)
##
##    def getValues(self):
##        return self.names

class ColourConfPropEdit(ConfPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = ColorIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx, self.width)

class FilepathConfPropEdit(ConfPropEdit):
    def __init__(self, name, parent, idx, width, value, _1=None , _2=None):
        ConfPropEdit.__init__(self, name, parent, idx, width, value, _1, _2)
        self.extensions = _("All files (*.*)")
     
    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        #from wx.FileDlg import FileDialog
        dlg = wx.FileDialog(None, 'Choose the file', '.', '', self.extensions + '|*.*', wx.OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = wx.GetApp().artub_frame.project.get_relative_path(dlg.GetPaths()[0])
                self.editorCtrl.setValue(filename)
                self.inspectorPost(False)
            else:
                if wx.MessageBox('Clear the current property value?',
                      'Clear filepath?', style=wx.ICON_QUESTION | wx.YES_NO) == wx.YES:
                    self.editorCtrl.setValue("''")
                    self.inspectorPost(False)
        finally:
            dlg.Destroy()

class DirpathConfPropEdit(ConfPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        dlg = wxDirDialog(self.parent)#, defaultPath=self.editorCtrl.value)
        try:
            dlg.SetPath(self.companion.eval(self.editorCtrl.value))
            if dlg.ShowModal() == wx.ID_OK:
                self.editorCtrl.setValue(`dlg.GetPath()`)
                self.inspectorPost(False)
            else:
                if wx.MessageBox('Clear the current property value?',
                      'Clear dirpath?', style=wx.ICON_QUESTION | wx.YES_NO) == wx.YES:
                    self.editorCtrl.setValue("''")
                    self.inspectorPost(false)
        finally:
            dlg.Destroy()

class BoolConfPropEdit(ConfPropEdit):
    truths = ['on', 'True', '1']
    def __init__(self, name, parent, idx, width, value, _1=None , _2=None):
        ConfPropEdit.__init__(self, name, parent, idx, width, value, _1, _2)
          
    def getDisplayValue(self):
        return self.valueToIECValue()

    def valueToIECValue(self):
        return string.lower(self.value) in self.truths and 'True' or 'False'

    def inspectorEdit(self):
        self.editorCtrl = CheckBoxIEC(self, self.value in self.truths)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.value)
        
#-------------------------------------------------------------------------------

class OptionedPropEdit(PropertyEditor):
    """ Property editors initialised with options """
    def __init__(self, name, parent, idx, width, value, _1=None , _2=None):
        PropertyEditor.__init__(self, name, parent, idx, width, value, _1, _2)
        #if names:
        #    self.revNames = reverseDict(names)
        #else:
        #    self.revNames = None

class ConstrPropEditFacade:
    def initFromComponent(self):
        self.value = ''
    def getCtrlValue(self):
        return ''
    def getValue(self):
        return ''
    def setValue(self, value):
        self.value = value

class ConstrPropEdit(ConstrPropEditFacade, PropertyEditor):
    def __init__(self, name, parent, idx, width, value, _1=None , _2=None):
        PropertyEditor.__init__(self, name, parent, idx, width, value, _1, _2)
    def initFromComponent(self):
        self.value = self.getValue()
    def valueToIECValue(self):
        return self.value
    def getDisplayValue(self):
        return self.getValue()
    def getCtrlValue(self):
        return self.companion.textConstr.params[ \
          self.companion.constructor()[self.name]]
    def setCtrlValue(self, oldValue, value):
        self.companion.checkTriggers(self.name, oldValue, value)
        if hasattr(self.companion, 'index'):
            self.propWrapper.setValue(self.companion.eval(value), self.companion.index)
        else:
            self.propWrapper.setValue(value)

# Collection id name
class ItemIdConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        val = self.valueToIECValue()
        self.editorCtrl = TextCtrlIEC(self, val)
        self.editorCtrl.createControl(self.parent, val, self.idx, self.width)

    def valueToIECValue(self):
        return self.getDisplayValue()

    def getDisplayValue(self):
        base = self.companion.newWinId('')
        return self.getValue()[len(base):]

    def fixupName(self, name):
        newname = []
        for c in name:
            if c == ' ': c = '_'
            if c in string.digits + string.letters + '_':
                newname.append(c)

        return string.upper(string.join(newname, ''))

    def getValue(self):
        if self.editorCtrl and self.editorCtrl.getValue():
            base = self.companion.newWinId('')
            self.value = base + self.fixupName(self.editorCtrl.getValue())
        else:
            self.value = self.getCtrlValue()
        return self.value

    def valueAsExpr(self):
        return self.getValue()

    def setCtrlValue(self, oldValue, value):
        self.companion.checkTriggers(self.name, oldValue, value)
        self.propWrapper.setValue(value, self.companion.index)

class IntConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl and self.editorCtrl.getValue():
            try:
                anInt = self.companion.eval(self.editorCtrl.getValue())
                if type(anInt) is IntType:
                    self.value = self.editorCtrl.getValue()
                else:
                    self.value = self.getCtrlValue()
            except Exception, message:
                self.value = self.getCtrlValue()
                #print 'invalid constr prop value', message, self.editorCtrl.getValue()
        else:
            self.value = self.getCtrlValue()
        return self.value

class SBFWidthConstrPropEdit(IntConstrPropEdit):
    def getCtrlValue(self):
        return self.companion.GetWidth()

    def setCtrlValue(self, oldValue, value):
        self.companion.SetWidth(value)

    def persistValue(self, value):
        pass

class ClassLinkConstrPropEdit(IntConstrPropEdit): pass

class BitmapPropEditMix:
    extTypeMap = {'.bmp': 'wxBITMAP_TYPE_BMP',
                  '.gif': 'wxBITMAP_TYPE_GIF',
                  '.jpg': 'wxBITMAP_TYPE_JPEG',
                  '.png': 'wxBITMAP_TYPE_PNG'}
    def showImgDlg(self, dir, name):
        if not os.path.isdir(dir):
            wxMessageBox('The given directory is invalid, using current directory.\n(%s)'%dir,
                  'Warning', wxOK | wxICON_EXCLAMATION)
            dir = '.'

        from FileDlg import wxFileDialog
        dlg = wxFileDialog(self.parent, 'Choose an image', dir, name,
              'ImageFiles', wxOPEN)
        try:
            if dlg.ShowModal() == wxID_OK:
                pth = abspth = string.replace(dlg.GetFilePath(), '\\', '/')
                if not Preferences.cgAbsoluteImagePaths:
                    pth = Utils.pathRelativeToModel(pth, self.companion.designer.model)
                return abspth, pth, self.extTypeMap[string.lower(os.path.splitext(pth)[-1])]
            else:
                return '', '', ''
        finally:
            dlg.Destroy()

    def extractPathFromSrc(self, src):
        if src and Utils.startswith(src, 'wxBitmap('):
            filename = src[len('wxBitmap(')+1:]
            pth = filename[:string.rfind(filename, ',')-1]
            if not os.path.isabs(pth):
                mbd = Utils.getModelBaseDir(self.companion.designer.model)
                if mbd: mbd = mbd[7:]
                pth = string.replace(os.path.normpath(os.path.join(mbd, pth)), '\\', '/')
            dir, name = os.path.split(pth)
            if not dir: dir = '.'
            return pth, dir, name
        return '', '.', ''


class BitmapConstrPropEdit(IntConstrPropEdit, BitmapPropEditMix):
    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        dummy, dir, name = self.extractPathFromSrc(self.value)
        abspth, pth, tpe = self.showImgDlg(dir, name)
        if abspth:
            self.value = 'wxBitmap(%s, %s)'%(`pth`, tpe)
            #v = self.getValue()
            #cv = self.getCtrlValue()
            #self.setCtrlValue(cv, v)
            self.persistValue(self.value)
            # manually update ctrl
            self.propWrapper.setValue(wxBitmap(abspth, getattr(wx, tpe)),
                  self.companion.index)
            self.refreshCompCtrl()

    def getValue(self):
        if self.editorCtrl:
            return self.value
        else:
            return self.getCtrlValue()


class EnumConstrPropEdit(IntConstrPropEdit):
    def __init__(self, name, parent, idx, width, value, _1=None , _2=None):
        IntConstrPropEdit.__init__(self, name, parent, idx, width, value, _1, _2)
        self.names = names
    def valueToIECValue(self):
        return self.getValue()
    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.getValue())
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.getValue())
    def getDisplayValue(self):
        return self.valueToIECValue()
    def getValues(self):
        return self.names

class ClassConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        val = self.getValue()
        if self.companion.designer.model.customClasses.has_key(self.value):
            self.editorCtrl = ChoiceIEC(self, val)
            self.editorCtrl.createControl(self.parent, self.idx, self.width)
            self.editorCtrl.setValue(val)
        else:
            self.editorCtrl = BeveledLabelIEC(self, val)
            self.editorCtrl.createControl(self.parent, self.idx, self.width)

    def setCtrlValue(self, oldValue, value):
        #self.companion.checkTriggers(self.name, oldValue, value)
        self.propWrapper.setValue(value)
    def getCtrlValue(self):
        return self.propWrapper.getValue()

    def getValue(self):
        if self.editorCtrl:
            self.value = self.editorCtrl.getValue()
        else:
            self.value = self.getCtrlValue()
        return self.value

    def getValues(self):
        custClss = self.companion.designer.model.customClasses
        MyCls = custClss[self.value]
        vals = []
        for name, Cls in custClss.items():
            if MyCls == Cls:
                vals.append(name)
        vals.remove(MyCls.__name__)
        vals.insert(0, MyCls.__name__)
        return vals




##    def getDisplayValue(self):
##        dv = EnumConstrPropEdit.getDisplayValue(self)
##        print dv
##        return dv

class BoolConstrPropEdit(EnumConstrPropEdit):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, 
                 width, options, names):
        EnumConstrPropEdit.__init__(self, name, parent, companion, rootCompanion, 
                 propWrapper, idx, width, options, ['True', 'False'])

    def inspectorEdit(self):
        self.editorCtrl = CheckBoxIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.value)

class LCCEdgeConstrPropEdit(EnumConstrPropEdit):
    def getCtrlValue(self):
        return self.companion.GetEdge()

    def getValue(self):
        if self.editorCtrl:
            try:
                # Sad to admit, a hack; don't use combo value if it's None
                if self.editorCtrl.getValue():
                    self.value = self.editorCtrl.getValue()
                else:
                    self.value = self.getCtrlValue()
            except Exception, message:
                self.value = self.getCtrlValue()
        else:
            self.value = self.getCtrlValue()
        return self.value

    def setCtrlValue(self, oldValue, value):
        self.companion.SetEdge(value)

    def persistValue(self, value):
        pass

    def getValues(self):
        objName = self.companion.__class__.sourceObjName
        return [self.getCtrlValue()] + \
          map(lambda a, objName=objName: '%s.%s'%(objName, a),
          self.companion.availableItems())

class ObjEnumConstrPropEdit(EnumConstrPropEdit):
    def getValue(self):
        if self.editorCtrl:
            try:
                # Sad to say, a hack; don't use combo value if it's None
                if self.editorCtrl.getValue():
                    self.value = self.editorCtrl.getValue()
                else:
                    self.value = self.getCtrlValue()
            except Exception, message:
                self.value = self.getCtrlValue()
        else:
            self.value = self.getCtrlValue()
        return self.value

    def persistValue(self, value):
        pass

    def getObjects(self):
        return self.companion.designer.getAllObjects().keys()

    def getValues(self):
        vals = self.getObjects()
        try:
            val = self.getValue()
            if val == 'self': vals.remove('self')
            else: vals.remove('self.'+val)
        except: pass
        return vals

class WinEnumConstrPropEdit(ObjEnumConstrPropEdit):
    def setCtrlValue(self, oldValue, value):
        self.companion.SetOtherWin(value)
    def getCtrlValue(self):
        return self.companion.GetOtherWin()
    def getValues(self):
        return ['None'] + ObjEnumConstrPropEdit.getValues(self)

class MenuEnumConstrPropEdit(ObjEnumConstrPropEdit):
    def getValues(self):
        return ['wxMenu()'] + ObjEnumConstrPropEdit.getValues(self)
    def getObjects(self):
        return self.companion.designer.getObjectsOfClass(wxMenu).keys()
    def setCtrlValue(self, oldValue, value):
        self.companion.SetMenu(value)
    def getCtrlValue(self):
        return self.companion.GetMenu()

class SizerEnumConstrPropEdit(ObjEnumConstrPropEdit):
##    def getValues(self):
##        return ['wxMenu()'] + ObjEnumConstrPropEdit.getValues(self)
    def getObjects(self):
        return self.companion.designer.getObjectsOfClass(wxBoxSizer).keys()
##    def setCtrlValue(self, oldValue, value):
##        self.companion.SetMenu(value)
##    def getCtrlValue(self):
##        return self.companion.GetMenu()


class BaseFlagsConstrPropEdit(IntConstrPropEdit):
    def getStyle(self):
        return [esExpandable]

    def getValue(self):
        """ For efficiency override the entire getValue"""
        if self.editorCtrl:
            try:
                anInt = self.companion.eval(self.editorCtrl.getValue())
                if type(anInt) is IntType:
                    self.value = string.join(map(string.strip,
                        string.split(self.editorCtrl.getValue(), '|')), ' | ')
                else:
                    self.value = self.getCtrlValue()
            except Exception, message:
                self.value = self.getCtrlValue()
                print 'invalid constr prop value', message
        else:
            self.value = self.getCtrlValue()
        return self.value

class StyleConstrPropEdit(BaseFlagsConstrPropEdit):
    def getSubCompanion(self):
        from Companions.Companions import WindowStyleDTC
        return WindowStyleDTC

class FlagsConstrPropEdit(BaseFlagsConstrPropEdit):
    def getSubCompanion(self):
        from Companions.Companions import FlagsDTC
        return FlagsDTC

class StrConstrPropEdit(ConstrPropEdit):
    def valueToIECValue(self):
        return self.companion.eval(self.value)

    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
            try:
                aStr = self.editorCtrl.getValue()
                if type(aStr) in StringTypes:
                    self.value = `aStr`
                else:
                    self.value = self.getCtrlValue()
            except Exception, message:
                self.value = self.getCtrlValue()
                print 'invalid constr prop value', message
        else:
            self.value = self.getCtrlValue()
        return self.value

# XXX Check for name conflicts
class NameConstrPropEdit(StrConstrPropEdit):
    def getValue(self):
        if self.editorCtrl:
            value = self.editorCtrl.getValue()
            if type(value) in StringTypes:
                value = `self.editorCtrl.getValue()`
            else:
                value = self.getCtrlValue()

            if value != self.value:
                strVal = self.companion.eval(value)
                if not strVal:
                    message = 'Invalid name for Python object'
                    wxLogError(message)
                    return self.value

                for c in strVal:
                    if c not in string.letters+string.digits+'_':#"\'':
                        message = 'Invalid name for Python object'
                        wxLogError(message)
                        return self.value
                        #raise message

                if self.companion.designer.objects.has_key(value):
                    wxLogError('Name already used by another control.')
                    return self.value
                    #raise 'Name already used by another control.'
            self.value = value
        else:
            self.value = self.getCtrlValue()
        return self.value


    def getCtrlValue(self):
        return `self.companion.name`

    def setCtrlValue(self, oldValue, newValue):
        self.companion.checkTriggers(self.name, 
              self.companion.eval(oldValue), 
              self.companion.eval(newValue))

    def persistValue(self, value):
        pass

class ChoicesConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
            try:
                aList = self.companion.eval(self.editorCtrl.getValue())
                if type(aList) is ListType:
                    self.value = self.editorCtrl.getValue()
                else:
                    self.value = self.getCtrlValue()
            except Exception, message:
                self.value = self.getCtrlValue()
                print 'invalid constr prop value', message
        else:
            self.value = self.getCtrlValue()
        return self.value

class MajorDimensionConstrPropEdit(ConstrPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx,
          self.width)

    def getValue(self):
        if self.editorCtrl:
            try:
                anInt = self.companion.eval(self.editorCtrl.getValue())
                if type(anInt) is IntType:
                    self.value = self.editorCtrl.getValue()
                else:
                    self.value = self.getCtrlValue()
            except Exception, message:
                self.value = self.getCtrlValue()
                print 'invalid constr prop value', message
        else:
            self.value = self.getCtrlValue()
        return self.value

class PropertiesBarChangeEvent(Action):
    def __init__(self, func, fullname, value):
        self.func = func
        self.fullname = fullname
        self.value = value
        Action.__init__(self, self.value + _(" event ") + func.func_name)
        
    def undo(self):
        self.do()
        
    def do(self):
        artub = wx.GetApp().frame
        value = self.value
        fullname = self.fullname
        func = self.func
        if value == "add":
            if artub.active_editor.name == "akiki":
                artub.active_editor.edit_event(func, fullname)
            else:
                artub.pb.dont_select = True
                artub.edit_resource(artub.pb.active_resource, artub.get_editor('akiki'))
                artub.active_editor.edit_event(func, fullname)
                artub.pb.dont_select = False
            self.value = "delete"
            """
            if self.first:
                self.editorCtrl.editorCtrl.Clear()
                for i in self.extraOpts:
                    self.editorCtrl.editorCtrl.Append(i)
                self.editorCtrl.editorCtrl.SetSelection(0)
            """
        elif value == "delete":
            res = artub.pb.active_resource
            c = res.get_class(fullname)
            c.remove_function(func.func_name)
            res.ast_has_changed = True
            res.topy()
            if artub.active_editor.name == "akiki":
                artub.pb.dont_select = True
                artub.edit_resource(res, artub.get_editor('akiki'))
                artub.pb.dont_select = False
            self.value = "add"
        #artub.todos.append(artub.pb.reload())
        """
        self.editorCtrl.editorCtrl.Clear()
        for i in self.extraOpts2:
            self.editorCtrl.editorCtrl.Append(i)
        self.editorCtrl.editorCtrl.SetSelection(0)
        """

class EventPropEdit(OptionedPropEdit):
    """ Property editor to handle design time definition of events """
    
    extraOpts = [_('(show)'), _('(delete)')] # , '(rename)']
    extraOpts2 = [_('(add)')] # , '(rename)']
    scopeOpts = {}
    
    def initFromComponent(self):
        # unlike other propedit getter setters these are methods not funcs
        pass # self.value = self.propWrapper.getValue(self.name)
    
    def valueToIECValue(self):
        v = self.value
        return v

    def inspectorPost(self, closeEditor = True):
        artub = wx.GetApp().frame
        wx.GetApp().editor = self
        sel = artub.pb.events.prevSel
        if self.editorCtrl:
            fullname = get_full_name(self.script.__class__.__name__)
            cv = self.getCtrlValue()
            value = self.editorCtrl.getValue()
            artub = wx.GetApp().frame
            if closeEditor and self.editorCtrl:
                self.editorCtrl.destroyControl()
                self.editorCtrl = None
                return
                
            if value == '(show)':
                if artub.active_editor.name == "akiki":
                    artub.active_editor.edit_event(cv, fullname)
                else:
                    artub.pb.dont_select = True
                    artub.edit_resource(artub.pb.active_resource, artub.get_editor('akiki'))
                    artub.active_editor.edit_event(cv, fullname)
                    artub.pb.dont_select = False

            else:    
                PropertiesBarChangeEvent(cv, fullname, value[1:-1])        
                artub.todos.append(sel.hideEditor)
        
    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.getValues(), self.idx, self.width)
        cv = self.getCtrlValue()
        self.editorCtrl.setValue(str(self.getCtrlValue()))
        self.editorCtrl.editorCtrl.SetSelection(0)

    def setCtrlValue(self, oldValue, value):
        ##        self.companion.checkTriggers(self.name, oldValue, value)
        pass # self.propWrapper.setValue(value, self.name)

    def getDisplayValue(self):
        klass = self.script.__class__
        for parent in klass.__bases__:
            f = getattr(parent, self.value.func_name, None)
            if f and f.im_func is self.value:
                return _('Inherited from ') + parent.__name__
        return "Defined line " + str(self.value.func_code.co_firstlineno) # str(self.valueToIECValue())

    def getValues(self):
        """ Build event list based on currently selected scope for the event """
        # XXX Should ideally do this one day:
        # XXX   Show event's of similar types, e.g. mouse events, cmd events.
        # XXX   Also show events from the code not bound to the frame
        vals = []
        showScope = 'own'
        if self.companion:
            """for evt in self.companion.textEventList:
                if evt.event_name == self.name:
                    showScope = evt.show_scope

                if evt.trigger_meth not in self.extraOpts:
                    try: vals.index(evt.trigger_meth)
                    except ValueError: vals.append(evt.trigger_meth)

            if showScope != 'own':
                # Add evts from other scopes
                # XXX Collection items' events aren't handled correctly
                # XXX designer != CollEditorView
                for comp, ctrl, prnt in self.companion.designer.objects.values():
                    if comp != self.companion and showScope == 'all':
                        #or  showScope == 'same' and comp.__class__ == self.companion.__class__):
                        for evt in comp.textEventList:
                            if evt.trigger_meth not in self.extraOpts:
                                try: vals.index(evt.trigger_meth)
                                except ValueError: vals.append(evt.trigger_meth)"""

        scopeChoices = self.scopeOpts.keys()
        # del scopeChoices[self.scopeOpts.values().index(showScope)]

        try:
            fullname = get_full_name(self.script.__class__.__name__)
            c = self.companion.resource.get_class(fullname)
            c.get_method(self.getCtrlValue().func_name)
            vals.extend(scopeChoices + self.extraOpts)
        except MethodNotFound:
            vals.extend(scopeChoices + self.extraOpts2)
        return vals

    def _repopulateChoice(self, value):
        self.editorCtrl.repopulate()
        self.editorCtrl.setValue(value)

    def getValue(self):
        """ Return current value, or if a special (*) value is selected,
            process it, and return previous 'current value' """
        return self.value.func_code.co_firstlineno #self.value
        if self.editorCtrl:
            oldVal = defVal = self.value
            value = self.editorCtrl.getValue()
            # Event rename
            if value == '(rename)':
                if oldVal == '(delete)':
                    for evt in self.companion.textEventList:
                        if evt.trigger_meth == oldVal:
                            defVal = evt.prev_trigger_meth
                            break

                ted = wxTextEntryDialog(self.parent, 'Enter a new method name:',
                      'Rename event method', defVal)
                try:
                    if ted.ShowModal() == wxID_OK:
                        self.value = ted.GetValue()

                        # XXX All references should be renamed !!!!
                        # XXX Add as method on designer
                        for evt in self.companion.textEventList:
                            if evt.trigger_meth == oldVal:
                                if not evt.prev_trigger_meth:
                                    evt.prev_trigger_meth = oldVal
                                evt.trigger_meth = self.value
                                break
                        self._repopulateChoice(self.value)
                finally:
                    ted.Destroy()
            # Event deletion
            elif value == '(delete)':
                for evt in self.companion.textEventList:
                    if evt.trigger_meth == oldVal:
                        if not evt.prev_trigger_meth:
                            evt.prev_trigger_meth = oldVal
                        break
                self.value = self.editorCtrl.getValue()
            # Event scope change
            elif value in self.scopeOpts.keys():
                # self.value = oldVal
                return self.value
                # self.companion.akiki.edit_event(self.value.func_name)
                #for evt in self.companion.textEventList:
                #    if evt.event_name == self.name:
                #        evt.show_scope = self.scopeOpts[value]
                #        self._repopulateChoice(oldVal)
                #        break
                
            # Normal event selection
            else:
                self.value = self.editorCtrl.getValue()

        return self.value

    def persistValue(self, value):
        self.companion.persistEvt(self.name, value)

class BITPropEditor(FactoryPropEdit):
    """ Editors for Built-in Python Types """
    def valueToIECValue(self):
        return `self.value`
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx, self.width)
    def getValue(self):
        if self.editorCtrl:
            try:
                value = eval(self.editorCtrl.getValue())
            except Exception, mess:
                wx.LogError('Invalid value: %s' % str(mess))
                raise
            self.value = value
        return self.value

class IntPropEdit(BITPropEditor):
    pass

class FloatPropEdit(BITPropEditor):
    def inspectorEdit(self):
        if not self.constraints:
            self.constraints = [1, 2, False, 0.0, 1.0, True, False]
        self.editorCtrl = FloatCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx, self.width, self.constraints)
        
    def getValue(self):
        if self.editorCtrl:
            self.value = self.editorCtrl.getValue()
            return self.value

class AnimationPropEdit(FactoryPropEdit):
    """ Editors for Built-in Python Types """
    def valueToIECValue(self):
        return `self.value`
        
    def inspectorEdit(self):
        self.editorCtrl = AnimationIEC(self, get_parent_class(self.value.__class__))
        self.editorCtrl.resource = self.script
        self.editorCtrl.createControl(self.parent, get_parent_class(self.value.__class__), self.idx, self.width)
        
    def getDisplayValue(self):
        try: return self.value.__class__.__name__
        except: return self.value.__name__
        
    def getValue(self):
        if self.editorCtrl:
            try:
                value = self.editorCtrl.getValue() # wx.GetApp().gns.eval(self.editorCtrl.getValue())
            except Exception, mess:
                wx.LogError('Invalid value: %s' % str(mess))
                raise
            if value == "None":
                return "None"
            self.value = wx.GetApp().gns.eval(value + '()')
            return value
        return ""
        
    def GetSubCompanion(self):
        return (1, 2)

def is_derived_from(c, b):
    try:
        for i in c.__bases__:
            if b == i: return True
            if is_derived_from(i, b): return True
        return None
    except: pass # Not a class ?
    
class ResourcePropEdit(FactoryPropEdit):
    """ Editors for Built-in Python Types """
    def valueToIECValue(self):
        return `self.value`

    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.value)
        gns = wx.GetApp().gns
        l = []
        l2 = []
        n = 0
        sel = 0
        gns = wx.GetApp().gns
        klass = gns.getattr(self.constraints.classe.__name__)
        if self.constraints.classe.__name__ == "Scene":
            d = gns.globals
        else:
            d = global_dict
        #if self.constraints.context:
        #    d = getattr(self.constraints.obj, self.constraints.context).__dict__
        for i, v in d.items():
            if i == "Scene": continue
            if self.value:
                if type(self.value) in [type(''), type(u'')]:
                    if self.value == i:
                        sel = len(l)
                elif i == self.value.__name__:
                    sel = len(l)
            try:
                #if self.constraints.context:
                #    context = getattr(self.constraints.obj, self.constraints.context)
                #    full = gns.getattr(get_full_name(context.__name__) + '.' + i)
                #else:
                full = gns.getattr(get_full_name(i))
                if isclass(full) and issubclass(full, klass):
                    l.append(i)
                    l2.append(full)
            except: raise
            n = n + 1
        self.editorCtrl.createControl(self.parent, l, self.idx, self.width)
        self.editorCtrl.editorCtrl.Insert('None', 0)
        self.editorCtrl.editorCtrl.SetSelection(sel + 1)
        l2.insert(0, NoneType)
        n = 0
        for i in l2:
            self.editorCtrl.editorCtrl.SetClientData(n, i)
            n += 1

    def getValue(self):
        if self.editorCtrl:
            try:
                value = self.editorCtrl.getValue()
                sel = self.editorCtrl.editorCtrl.GetSelection()
                if sel != -1: value = self.editorCtrl.editorCtrl.GetClientData(sel)
            except Exception, mess:
                wx.LogError('Invalid value: %s' % str(mess))
                raise
            self.value = value
            return value
        return ""

    def GetSubCompanion(self):
        return (1, 2)
        
class StrPropEdit(BITPropEditor):
    def valueToIECValue(self):
        return self.value

    def getValue(self):
        return FactoryPropEdit.getValue(self)

    def change_value(self):
        self.companion.change_value(self.name, self.value)

# The following is a work in progress for having a string editor dlg that
# also handles gettext formatted strings
#
# The current problem is that for normal string properties, the property
# refers to a string object, not to the source reference, iow _() is not a string
##    def inspectorEdit(self):
##        self.editorCtrl = TextCtrlButtonIEC(self, self.value)
##        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)
##    def edit(self, event):
##        import StringPropEditorDlg
##        dlg = StringPropEditorDlg.create(self.parent, repr(self.value))
##        try:
##            if dlg.ShowModal() == wxID_OK:
##                self.inspectorPost(false)
##                pass
##        finally:
##            dlg.Destroy()


class NamePropEdit(StrPropEdit):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, options, names):
        StrPropEdit.__init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width)

    identifier = string.letters+string.digits+'_'

    def getValue(self):
        # XXX Currently returning the old value in case of error because
        # XXX an exception here cannot be gracefully handled yet.
        # XXX Specifically closing the frame with the focus on the
        if self.editorCtrl:
            value = self.editorCtrl.getValue()
            if value != self.value:
                if self.companion.designer.objects.has_key(value):
                    wxLogError('Name already used by another control.')
                    return self.value

                if not value:
                    message = 'Invalid name for Python object'
                    wxLogError(message)
                    return self.value

                for c in value:
                    if c not in self.identifier:
                        message = 'Invalid name for Python object'
                        wxLogError(message)
                        return self.value
            self.value = value
        return self.value

class TuplePropEdit(BITPropEditor):
    pass

class BoolPropEdit(OptionedPropEdit):
    def valueToIECValue(self):
        v = self.value
        if type(v) == IntType:
            return self.getValues()[v]
        else: return `v`
    def inspectorEdit(self):
        self.editorCtrl = CheckBoxIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.getValues()[self.value])
    def getDisplayValue(self):
        return self.valueToIECValue()
    def getValues(self):
        return ['False', 'True']
    def getValue(self):
        if self.editorCtrl:
            # trick to convert boolean string to integer
            v = self.editorCtrl.getValue()
            self.value = bool(self.getValues().index(self.editorCtrl.getValue()))
        return self.value

class EnumPropEdit(OptionedPropEdit):
    def valueToIECValue(self):
        #if self.revNames:
        #    try:
        #        return self.revNames[self.value]
        #    except KeyError:
        #        return `self.value`
        #else: OptionedPropEdit.getDisplayValue(self)
        return str(self.value)
    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.value)
        m = self.constraints.obj.__members__
        try: m.remove('__module__')
        except: pass
        self.editorCtrl.createControl(self.parent, m, self.idx, self.width)
        s = str(self.value).split('.')
        self.enum = s[0]
        self.setValue(s[-1])
        
    def getDisplayValue(self):
        return self.valueToIECValue()
    def getValues(self):
        vals = self.names.keys()
        try:
            name = self.revNames[self.value]
        except KeyError:
            name = `self.value`
        if name not in vals:
            vals.append(name)
        return vals
    def setValue(self, value):
        self.value = value
        self.editorCtrl.setValue(value)
        #if self.editorCtrl:
        #    try:
        #        self.editorCtrl.setValue(self.revNames[value])
        #    except KeyError:
        #        self.editorCtrl.setValue(`value`)
    def getValue(self):
        if self.editorCtrl:
            self.value = self.enum + '.' + self.editorCtrl.getValue()
            #try:
            #    self.value = self.names[strVal]
            #except KeyError:
            #    self.value = self.companion.eval(strVal)

        return self.value
# SetPropEdit

# Property editors for classes
class ClassPropEdit(FactoryPropEdit):
    def getDisplayValue(self):
        return '('+self.value.__class__.__name__+')'
    def getStyle(self):
        return [esExpandable]

class ClassLinkPropEdit(OptionedPropEdit):
    defaults = {'None': None}
    linkClass = None
    def getStyle(self):
        return []
    def valueToIECValue(self):
        for k, v in self.defaults.items():
            if self.value == v:
                return k

        objs = self.companion.designer.getObjectsOfClass(self.linkClass)
        for objName in objs.keys():
            if `objs[objName]` == `self.value`:
                return objName
        # Ok lets try again ;\
##        if hasattr(self.value, 'GetId'):
##            for objName in objs.keys():
##                if objs[objName].GetId() == self.value.GetId():
##                    return objName
        #print 'ClassLinkPropEdit: ', self.value, 'not found'
        return `None`
    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.setValue(self.value)
    def getDisplayValue(self):
        return self.valueToIECValue()
    def getValues(self):
        defs = self.defaults.keys()
        defs.sort()
        return defs + self.companion.designer.getObjectsOfClass(self.linkClass).keys()
    def setValue(self, value):
        self.value = value
        if self.editorCtrl:
            self.editorCtrl.setValue(self.valueToIECValue())
    def getValue(self):
        if self.editorCtrl:
            strVal = self.editorCtrl.getValue()
            if self.defaults.has_key(strVal):
                self.value = self.defaults[strVal]
            else:
                objs = self.companion.designer.getObjectsOfClass(self.linkClass)
                self.value = objs[strVal]

        return self.value

class WindowClassLinkPropEdit(ClassLinkPropEdit):
    pass #linkClass = wx.WindowPtr

class WindowClassLinkWithParentPropEdit(WindowClassLinkPropEdit):
    pass #linkClass = wx.WindowPtr
    def getValues(self):
        return ['None'] + self.companion.designer.getObjectsOfClassWithParent(self.linkClass, self.companion.name).keys()

class StatusBarClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wx.StatusBar

class ToolBarClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wx.ToolBar

class MenuBarClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wx.MenuBar

class ImageListClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wx.ImageList

class SizerClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wx.BoxSizer

class ButtonClassLinkPropEdit(ClassLinkPropEdit):
    linkClass = wx.Button

class CursorClassLinkPropEdit(ClassLinkPropEdit):
    defaults = {'None': wx.NullCursor, 'wxSTANDARD_CURSOR': wx.STANDARD_CURSOR,
                'wxHOURGLASS_CURSOR': wx.HOURGLASS_CURSOR,
                'wxCROSS_CURSOR': wx.CROSS_CURSOR}
    pass #linkClass = wx.CursorPtr
##    def getValues(self):
##        vals = ClassLinkPropEdit.getValues(self)
##        return vals + ['wxSTANDARD_CURSOR', 'wxHOURGLASS_CURSOR', 'wxCROSS_CURSOR']

class ListCtrlImageListClassLinkPropEdit(ImageListClassLinkPropEdit):
    listTypeMap = {wx.IMAGE_LIST_SMALL : 'wxIMAGE_LIST_SMALL',
                   wx.IMAGE_LIST_NORMAL: 'wxIMAGE_LIST_NORMAL'}
    def valueToIECValue(self):
        if self.value[0] is None: return `None`
        objs = self.companion.designer.getObjectsOfClass(self.linkClass)
        for objName in objs.keys():
            if `objs[objName]` == `self.value[0]`:
                return objName
        print 'ClassLinkPropEdit: ', self.value[0], 'not found'
        return `None`

    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.valueToIECValue())
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.valueToIECValue())
#        self.setValue(self.value[0])

    def getValue(self):
        if self.editorCtrl:
            strVal = self.editorCtrl.getValue()
            if strVal == `None`:
                self.value = (None, self.value[1])
            else:
                objs = self.companion.designer.getObjectsOfClass(self.linkClass)
                self.value = (objs[strVal], self.value[1])
        return self.value

    def valueAsExpr(self):
        return '%s, %s'%(self.valueToIECValue(), self.listTypeMap[self.value[1]])

class ColPropEdit(ClassPropEdit):
    def getStyle(self):
        return [esExpandable]

    def getSubCompanion(self):
        from Companions.Companions import ColourDTC
        return ColourDTC

    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        data = wxColourData()
        data.SetColour(self.value)
        data.SetChooseFull(true)
        dlg = wxColourDialog(self.parent, data)
        try:
            if dlg.ShowModal() == wxID_OK:
                self.value = dlg.GetColourData().GetColour()
                self.inspectorPost(false)
                self.editorCtrl.setValue(self.value)
                #self.propWrapper.setValue(self.value)
                #self.obj.Refresh()
        finally:
            dlg.Destroy()

    def getValue(self):
        return self.value#wxColour(self.value.Red(), self.value.Green(), self.value.Blue())

    def valueAsExpr(self):
        return 'wxColour(%d, %d, %d)'%(self.value.Red(), self.value.Green(), self.value.Blue())

class SizePropEdit(ClassPropEdit):
    def getDisplayValue(self):
        return self.valueToIECValue()
    def valueToIECValue(self):
        return `self.value`
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.valueToIECValue())
        self.editorCtrl.createControl(self.parent, self.valueToIECValue(), self.idx, self.width)
    def getValue(self):
        if self.editorCtrl:
            try:
                s = self.editorCtrl.getValue()
                s = s[s.index('(') + 1:-1].split(',')
                tuplePos = (int(s[0]), int(s[1]))
            except Exception, mess:
                Utils.ShowErrorMessage(self.parent, 'Invalid value', mess)
                raise
            self.value = wx.Size(tuplePos[0], tuplePos[1])
        return self.value
    def valueAsExpr(self):
        return 'wx.Size(%d, %d)'%(self.value.x, self.value.y)
    def getSubCompanion(self):
        from Companions.Companions import SizeDTC
        return SizeDTC

class PosPropEdit(ClassPropEdit):
    def getDisplayValue(self):
        return self.valueToIECValue()
    def valueToIECValue(self):
        return `self.value`
    def inspectorEdit(self):
        self.editorCtrl = TextCtrlIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.value, self.idx, self.width)
    def getValue(self):
        if self.editorCtrl:
            try:
                tuplePos = self.companion.eval(self.editorCtrl.getValue())
            except Exception, mess:
                Utils.ShowErrorMessage(self.parent, 'Invalid value', mess)
                raise
            self.value = wxPoint(tuplePos[0], tuplePos[1])
        return self.value
    def valueAsExpr(self):
        return 'wxPoint(%d, %d)'%(self.value.x, self.value.y)
    def getSubCompanion(self):
        return ( ("x", self.value.x), ("y", self.value.y) )


class FontPropEdit(ClassPropEdit):
    def __init2__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, _1=None , _2=None):
        ClassPropEdit.__init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width)
        #import Enumerations
        #self.fontFamily = reverseDict(Enumerations.fontFamilyNames)
        #self.fontStyle = reverseDict(Enumerations.fontStyleNames)
        #self.fontWeight = reverseDict(Enumerations.fontWeightNames)

    def getStyle2(self):
        return ClassPropEdit.getStyle(self) + [esDialog, esReadOnly, esRecreateProp]

    def getDisplayValue(self):
        return str(self.value)
        
    def getSubCompanion(self):
        from Companions.Companions import FontDTC
        return FontDTC

    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def getValue(self):
        return self.value

    def edit(self, event):
        font = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                       wx.FONTWEIGHT_NORMAL, False, self.value) 
        data = wx.FontData()
        data.SetInitialFont(font)
        dlg = wx.FontDialog(self.parent, data)
        # dlg.GetFontData().SetInitialFont(self.value)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.value = dlg.GetFontData().GetChosenFont()
                self.inspectorPost(False)
        finally:
            dlg.Destroy()
            self.editorCtrl.setValue(self.value)
    def valueAsExpr(self):
        # XXX Duplication with sub property editors
        fnt = self.value
        return 'wxFont(%d, %s, %s, %s, %s, %s)'%(\
            fnt.GetPointSize(),
            self.fontFamily[fnt.GetFamily()],
            self.fontStyle[fnt.GetStyle()],
            self.fontWeight[fnt.GetWeight()],
            fnt.GetUnderlined() and 'True' or 'False',
            `fnt.GetFaceName()`)

class AnchorPropEdit(OptionedPropEdit):
    def getStyle(self):
        return [esExpandable]

    def getSubCompanion(self):
        from Companions.Companions import AnchorsDTC
        return AnchorsDTC

    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def edit(self, event):
        if self.expanded:
            wxMessageBox('Anchors can not be reset while the property is expanded',
                  'Anchors')
        else:
            if self.companion.anchorSettings:
                message = 'Remove anchors?'
            else:
                message = 'Define default Anchors?'

            dlg = wxMessageDialog(self.parent, message,
                              'Anchors', wxYES_NO | wxICON_QUESTION)
            try:
                if dlg.ShowModal() == wxID_YES:
                    if self.companion.anchorSettings:
                        self.companion.removeAnchors()
                        self.propWrapper.setValue(self.getValue())
                    else:
                        self.companion.defaultAnchors()
                        self.inspectorPost(false)
            finally:
                dlg.Destroy()

    def getValue(self):
        return self.companion.GetAnchors(self.companion)

    def getDisplayValue(self):
        if self.companion.anchorSettings:
            l, t, r, b = self.companion.anchorSettings
            set = []
            if l: set.append('left')
            if t: set.append('top')
            if r: set.append('right')
            if b: set.append('bottom')
            return '('+string.join(set, ', ')+')'
        else:
            return 'None'

    def valueAsExpr(self):
        if self.companion.anchorSettings:
            l, t, r, b = self.companion.anchorSettings
            return 'LayoutAnchors(self.%s, %s, %s, %s, %s)'%(self.companion.name,
                l and 'True' or 'False', t and 'True' or 'False',
                r and 'True' or 'False', b and 'True' or 'False')

import  wx.lib.popupctl as  pop

class BitmapPropEdit(PropertyEditor, BitmapPropEditMix):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, options = None, names = None):
        PropertyEditor.__init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width)

##    def getStyle(self):
##        return ClassPropEdit.getStyle(self) + [esDialog, esReadOnly]

    def getDisplayValue(self):
        return '(wxBitmapPtr)'

    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)
        constrs = self.companion.constructor()
        if constrs.has_key(self.name):
            constr = self.companion.textConstr.params[constrs[self.name]]
        else:
            constr = self.companion.persistedPropVal(self.name, self.propWrapper.getSetterName())

        self.bmpPath, dir, name = self.extractPathFromSrc(constr)

    def edit(self, event):
        if self.bmpPath:
            dir, name = os.path.split(self.bmpPath)
        else:
            dir, name = '.', ''

        abspth, pth, tpe = self.showImgDlg(dir, name)
        if abspth:
            self.value = wxBitmap(abspth, getattr(wx, tpe))
            self.bmpPath = pth
            self.inspectorPost(false)

    def getValue(self):
        return self.value

    def valueAsExpr(self):
        if self.bmpPath:
            return 'wxBitmap(%s, %s)'%(`self.bmpPath`,
                    self.extTypeMap[string.lower(os.path.splitext(self.bmpPath)[-1])])
        else:
            return 'wxNullBitmap'

class SashVisiblePropEdit(BoolPropEdit):
    sashEdgeMap = {wx.SASH_LEFT: 'wxSASH_LEFT', wx.SASH_TOP: 'wxSASH_TOP',
                   wx.SASH_RIGHT: 'wxSASH_RIGHT', wx.SASH_BOTTOM: 'wxSASH_BOTTOM'}
    def valueToIECValue(self):
        v = self.value[1]
        if type(v) == IntType:
            return self.getValues()[v]
        else: return `v`
    def inspectorEdit(self):
        self.editorCtrl = CheckBoxIEC(self, self.value[1])
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.getValues()[self.value[1]])
##    def getDisplayValue(self):
##        return self.valueToIECValue()
##    def getValues(self):
##        return ['false', 'true']
    def getValue(self):
        if self.editorCtrl:
            # trick to convert boolean string to integer
            v = self.editorCtrl.getValue()
            self.value = (self.value[0], self.getValues().index(self.editorCtrl.getValue()))
        return self.value
    def valueAsExpr(self):
        return '%s, %s'%(self.sashEdgeMap[self.value[0]],
                         self.value[1] and 'True' or 'False')

class CollectionPropEdit(PropertyEditor):
    """ Class associated with a design time identified type,
        it manages the behaviour of a NameValue in the Inspector
    """

    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width, names, options):
        PropertyEditor.__init__(self, name, parent, companion, rootCompanion, propWrapper, idx, width)

    def inspectorEdit(self):
        self.editorCtrl = ButtonIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width, self.edit)

    def inspectorPost(self, closeEditor = True):
        """ Code persistance taken over by companion because collection
            transactions live longer than properties
        """
        if self.editorCtrl and closeEditor:
            self.editorCtrl.destroyControl()
            self.editorCtrl = None
            self.refreshCompCtrl()

    def getDisplayValue(self):
        return '(%s)'%self.name

    def valueAsExpr(self):
        return self.getDisplayValue()

    def edit(self, event):
        self.companion.designer.showCollectionEditor(\
          self.companion.name, self.name)

class ListColumnsColPropEdit(CollectionPropEdit): pass
class AcceleratorEntriesColPropEdit(CollectionPropEdit): pass
class MenuBarColPropEdit(CollectionPropEdit): pass
class MenuColPropEdit(CollectionPropEdit): pass
class ImagesColPropEdit(CollectionPropEdit): pass
class NotebookPagesColPropEdit(CollectionPropEdit): pass

# Property editor registration

def registerEditors(reg):
    for theType, theClass, editors in registeredTypes:
        if theType == 'Type':
            reg.registerTypes(theClass, editors)
        elif theType == 'Class':
            reg.registerClasses(theClass, editors)

registeredTypes = [\
    ('Type', IntType, [IntPropEdit]),
    ('Type', StringType, [StrPropEdit]), # [FilepathConfPropEdit]), 
    ('Type', TupleType, [TuplePropEdit]),
    ('Class', wx.Size, [SizePropEdit]),
    #('Class', wx.SizePtr, [SizePropEdit]),
    ('Class', wx.Point, [PosPropEdit]),
    #('Class', wx.PointPtr, [PosPropEdit]),
    #('Class', wx.FontPtr, [FontPropEdit]),
    #('Class', wx.ColourPtr, [ColPropEdit]),
    #('Class', wx.BitmapPtr, [BitmapPropEdit]),
    ('Class', wx.Validator, [ClassLinkPropEdit]),
    ('Class', Filename, [FilepathConfPropEdit])
]

try:
    registeredTypes.append( ('Type', UnicodeType, [StrPropEdit]) )
except:
    # 1.5.2
    pass
