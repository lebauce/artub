import wx
from depplatform import get_image_path
import platform
import inspect
from compiler import parse
import compiler.ast as ast
from script import is_derived_from
from wx.lib.mixins.listctrl import CheckListCtrlMixin

if platform.system() != 'Darwin':
    class CheckedListCtrl(wx.ListCtrl):
        def __init__(self, parent, id, pt, sz, style):
            wx.ListCtrl.__init__(self, parent, id, pt, sz, style | wx.LC_REPORT)
            self.m_imageList = wx.ImageList(16, 16, True)
    
            self.m_imageList.Add(wx.Bitmap(get_image_path("unchecked.bmp"), wx.BITMAP_TYPE_BMP))
            self.m_imageList.Add(wx.Bitmap(get_image_path("checked.bmp"), wx.BITMAP_TYPE_BMP))

            self.SetImageList(self.m_imageList, wx.IMAGE_LIST_SMALL)

            info = wx.ListItem()
            info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_FORMAT
            info.m_format = 0
            info.m_text = _("Behaviour")
            self.InsertColumnInfo(0, info)
            self.SetColumnWidth(0, 200)

            wx.EVT_LEFT_DCLICK(self, self.OnMouseEvent)
    
        def OnMouseEvent(self, event):
            item, flags = self.HitTest(event.GetPosition())
            print "caca",item, flags, event.GetPosition()
            if item > -1 and (flags & wx.LIST_HITTEST_ONITEMICON) and self.GetItem(item).GetImage() != -1:
                self.Check(item, not self.IsChecked(item))
                self.on_checked(item, not self.IsChecked(item))
            else:
                event.Skip()

        def on_checked(self, item, state):
            if state:
                self.remove_behavior(item)
            else:
                self.add_behavior(item)
            
        def IsChecked(self, item):
            return self.GetItem(item).m_image == 1

        def remove_checkbox(self, item):
            self.SetItemImage(item, -1, -1)
        
        def Check(self, item, checked):
            if checked:
                self.SetItemImage(item, 1, -1)
            else:
                self.SetItemImage(item, 0, -1)
                
else:
    class CheckedListCtrl(wx.ListCtrl, CheckListCtrlMixin):
        def __init__(self, parent, id, pt, sz, style):
            wx.ListCtrl.__init__(self, parent, id, pt, sz, style | wx.LC_REPORT)
            CheckListCtrlMixin.__init__(self)
            
            info = wx.ListItem()
            info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_FORMAT
            info.m_format = 0
            info.m_text = _("Behaviour")
            self.InsertColumnInfo(0, info)
            self.SetColumnWidth(0, 200)
            self.ignore_on_check_item = False

            self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

        def OnItemActivated(self, evt):
            self.ToggleItem(evt.m_itemIndex)
    
        def OnCheckItem(self, index, flag):
            if not self.ignore_on_check_item and self.GetItemBackgroundColour(index) != wx.Color(226, 226, 220):
                if flag:
                    self.add_behavior(index)
                else:
                    self.remove_behavior(index)
        
        def remove_checkbox(self, item):
            self.SetItemImage(item, -1, -1)
                    
        def Check(self, item, checked):
            self.CheckItem(item, checked)
                
class BehaviorsWindow(CheckedListCtrl):
    def __init__(self, parent, id = -1, pt = wx.DefaultPosition, sz = wx.DefaultSize, style = 0):
        CheckedListCtrl.__init__(self, parent, id, pt, sz, style=style)
        self.ignore_base_classes = { "object" : None, "BehaviourFoo" : None, "Behaviour" : None }
    
    def add_behavior_listitem(self, behavior, index = -1):
        if index == -1: index = self.GetItemCount()
        self.InsertImageStringItem(index, behavior.__name__, 0)
            
    def set_inspector(self, cm):
        allready_added = {}
        obj = cm.obj
        resource = cm.resource
        self.resource = resource
        self.obj = obj
        mro = inspect.getmro(obj.__class__)
        self.DeleteAllItems()
        behaviour = wx.GetApp().gns.getattr("Behaviour")
        self.ignore_on_check_item = True
        n = 0
        for i in mro[1:]:
            if allready_added.has_key(i.__name__) or \
               self.ignore_base_classes.has_key(i.__name__):
                continue
            allready_added[i.__name__] = None
            if not is_derived_from(i, behaviour):
                self.add_behavior_listitem(i, n)
                self.remove_checkbox(n)
                self.SetItemBackgroundColour(n, wx.Color(226, 226, 220))
                n += 1
            else:
                self.add_behavior_listitem(i, self.GetItemCount())
                self.Check(self.GetItemCount() - 1, True)

        self.ignore_on_check_item = False
        import behaviour
        for i in behaviour.behaviours:
            j = wx.GetApp().gns.getattr(i)
            if hasattr(j, "apply_on"):
                if type(j.apply_on) == type(''):
                    try:
                        c = wx.GetApp().gns.getattr(j.apply_on)
                    except KeyError:
                        continue
                else:
                    c = j.apply_on
            else:
                c = None
            if not c or is_derived_from(obj.__class__, c) and \
               not self.ignore_base_classes.has_key(j.__name__):
                if not allready_added.has_key(j.__name__):
                    self.add_behavior_listitem(j)
                    allready_added[j.__name__] = None
            
    def remove_behavior(self, behavior):
        name = self.GetItemText(behavior)
        c = self.resource.get_class(self.obj.__class__.__name__)
        n = 0
        # Remove base class
        for b in c.ast.bases:
            if b.name == name:
                del c.ast.bases[n]
                break
            n = n + 1
        # Remove constructor
        n = 0
        cons = c.get_method("__init__")
        for i in cons.ast.code.nodes:
            if isinstance(i, ast.Discard):
                if isinstance(i.expr, ast.CallFunc):
                    if isinstance(i.expr.node, ast.Getattr) and \
                      i.expr.node.attrname == '__init__' and \
                      i.expr.node.expr.name == name:
                          del cons.ast.code.nodes[n]
                          break
            n = n + 1
        self.resource.ast_has_changed = True
        self.update()
        
    def update(self):
        artub = wx.GetApp().frame
        if artub.active_editor:
            artub.active_editor.update(True)
            artub.active_editor.update(False)
        else:
            artub.edit_resource(self.resource)
    
    def add_behavior(self, behavior):
        name = self.GetItemText(behavior)
        c = self.resource.get_class(self.obj.__class__.__name__)
        # Add base class
        c.ast.bases.insert(0, ast.Name(name))
        # Add constructor
        cons = c.get_method("__init__")
        l = name + ".__init__(self)"
        AST = parse(l)
        cons.ast.code.nodes.insert(0, AST.node.nodes[0])
        self.resource.ast_has_changed = True
        self.update()


