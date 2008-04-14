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
from path import Path
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
            elif type(self.value) == unicode:
                self.value = value
            else:
                raise "Value must be of type " + str(type(self.value)) + " Had" + str(type(value)) + "instead."
        pass # self.value = type(self.value)(value)

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
            # Only post changes
            if `v` != `cv`:
                self.validateProp(v, cv)
                self.setCtrlValue(cv, v)

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

class StrConfPropEdit(ConfPropEdit):
    def valueToIECValue(self):
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

class EnumConfPropEdit(ConfPropEdit):
    def inspectorEdit(self):
        self.editorCtrl = ChoiceIEC(self, self.getValue())
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.value)

#    def getValues(self):
#        return self.names

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

"""
class BoolConstrPropEdit(EnumConstrPropEdit):
    def __init__(self, name, parent, companion, rootCompanion, propWrapper, idx, 
                 width, options, names):
        EnumConstrPropEdit.__init__(self, name, parent, companion, rootCompanion, 
                 propWrapper, idx, width, options, ['True', 'False'])

    def inspectorEdit(self):
        self.editorCtrl = CheckBoxIEC(self, self.value)
        self.editorCtrl.createControl(self.parent, self.idx, self.width)
        self.editorCtrl.setValue(self.value)
"""

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
        # artub.todos.append(artub.pb.reload())
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
        scopeChoices = self.scopeOpts.keys()

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
        return self.value.func_code.co_firstlineno
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
            elif value == '(delete)':
                for evt in self.companion.textEventList:
                    if evt.trigger_meth == oldVal:
                        if not evt.prev_trigger_meth:
                            evt.prev_trigger_meth = oldVal
                        break
                self.value = self.editorCtrl.getValue()
            elif value in self.scopeOpts.keys():
                return self.value
                
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

class FontPropEdit(PropertyEditor):
    def getDisplayValue(self):
        return str(self.value)

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
    ('Class', Filename, [FilepathConfPropEdit])
]

try:
    registeredTypes.append( ('Type', UnicodeType, [StrPropEdit]) )
except:
    # 1.5.2
    pass
