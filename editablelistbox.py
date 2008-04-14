import wx
from depplatform import get_image_path

wxID_ELB_DELETE = wx.ID_HIGHEST + 1
wxID_ELB_NEW = wx.ID_HIGHEST + 2
wxID_ELB_UP = wx.ID_HIGHEST + 3
wxID_ELB_DOWN = wx.ID_HIGHEST + 4
wxID_ELB_EDIT = wx.ID_HIGHEST + 5
wxID_ELD_LISTCTRL = wx.ID_HIGHEST + 6

wxEL_ALLOW_NEW         = 0x0100
wxEL_ALLOW_EDIT        = 0x0200
wxEL_ALLOW_DELETE      = 0x0400
wxEL_ALLOW_UPDOWN      = 0x0800
wxEL_SHOW_TEXT         = 0x1000

BTN_BORDER = 4

class CheckedListCtrl(wx.ListCtrl):
    def __init__(self, parent, id, pt, sz, style):
        wx.ListCtrl.__init__(self, parent, id, pt, sz, style | wx.LC_REPORT)
        self.m_imageList = wx.ImageList(16, 16, True)

        self.InsertColumn(0, u"Value", wx.LIST_FORMAT_LEFT, 80)

        wx.EVT_LEFT_DOWN(self, self.OnMouseEvent)
    
    def OnMouseEvent(self, event):
        if event.LeftDown():
            item, flags = self.HitTest(event.GetPosition())
            if item > -1 and (flags & wx.LIST_HITTEST_ONITEMICON):
                self.SetChecked(item, not self.IsChecked(item))
            else:
                event.Skip()
        else:
            event.Skip()

    def IsChecked(self, item):
        return self.GetItem(item).m_image == 1

    def SetChecked(self, item, checked):
        if checked:
            self.SetItemImage(item, 1, -1)
        else:
            self.SetItemImage(item, 0, -1)

class CleverListCtrl(CheckedListCtrl):
    def __init__(self, parent,
                  id = -1,
                  pos = wx.DefaultPosition,
                  size = wx.DefaultSize,
                  style = wx.LC_ICON,
                  validator = wx.DefaultValidator,
                  name = u"listctrl"):
        CheckedListCtrl.__init__(self, parent, id, pos, size, style)
        self.CreateColumns()
        wx.EVT_SIZE(self, self.OnSize)

    def CreateColumns(self):
        self.InsertColumn(0, u"item")
        self.SizeColumns()

    def SizeColumns(self):
         w = self.GetSize().x
#ifdef __WXMSW__
         # w -= wxSystemSettings::GetMetric(wxSYS_VSCROLL_X) + 6;
#else
         w -= 2 * wx.SystemSettings_GetMetric(wx.SYS_VSCROLL_X)
#endif
         self.SetColumnWidth(0, w)

    def OnSize(self, event):
        self.SizeColumns()
        event.Skip()

class EditableListBox(wx.Panel):
    def __init__(self, parent, id, label, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wxEL_ALLOW_NEW | wxEL_ALLOW_EDIT | wxEL_ALLOW_DELETE | wxEL_ALLOW_UPDOWN, name = "editablelistbox"):
        wx.Panel.__init__(self, parent, id, pos, size, wx.TAB_TRAVERSAL, name)
        self.m_bEdit = self.m_bNew = self.m_bDel = self.m_bUp = m_bDown = None
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.subp = wx.Panel(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        subsizer = wx.BoxSizer(wx.HORIZONTAL)
        if style & wxEL_SHOW_TEXT:
            subsizer.Add(wx.StaticText(self.subp, -1, label), 1, wx.ALIGN_CENTRE_VERTICAL | wx.LEFT, 4)
        else:
            subsizer.Add(wx.StaticText(self.subp, -1, ""), 1, wx.ALIGN_CENTRE_VERTICAL | wx.LEFT, 4)

        self.m_style = style
        self.m_selection = 0
        
        # Si ca deconne sous Windows, voir le fichier original
        if style & wxEL_ALLOW_EDIT:
            self.m_bEdit = wx.BitmapButton(self.subp, wxID_ELB_EDIT, wx.Bitmap(get_image_path("edit.xpm"), wx.BITMAP_TYPE_XPM))
            subsizer.Add(self.m_bEdit, 0, wx.ALIGN_CENTRE_VERTICAL | wx.TOP | wx.BOTTOM, BTN_BORDER)
            wx.EVT_BUTTON(self.m_bEdit, wxID_ELB_EDIT, self.OnEditItem)

        if style & wxEL_ALLOW_NEW:
            self.m_bNew = wx.BitmapButton(self.subp, wxID_ELB_NEW, wx.Bitmap(get_image_path("new.xpm"), wx.BITMAP_TYPE_XPM))
            subsizer.Add(self.m_bNew, 0, wx.ALIGN_CENTRE_VERTICAL | wx.TOP | wx.BOTTOM, BTN_BORDER)
            wx.EVT_BUTTON(self.m_bNew, wxID_ELB_NEW, self.OnNewItem)

        if style & wxEL_ALLOW_DELETE:
            self.m_bDel = wx.BitmapButton(self.subp, wxID_ELB_DELETE, wx.Bitmap(get_image_path("delete.xpm"), wx.BITMAP_TYPE_XPM))
            subsizer.Add(self.m_bDel, 0, wx.ALIGN_CENTRE_VERTICAL | wx.TOP | wx.BOTTOM, BTN_BORDER)
            wx.EVT_BUTTON(self.m_bDel, wxID_ELB_DELETE, self.OnDelItem)

        if style & wxEL_ALLOW_UPDOWN:
            self.m_bUp = wx.BitmapButton(self.subp, wxID_ELB_UP, wx.Bitmap(get_image_path("up.xpm"), wx.BITMAP_TYPE_XPM))
            subsizer.Add(self.m_bUp, 0, wx.ALIGN_CENTRE_VERTICAL | wx.TOP | wx.BOTTOM, BTN_BORDER)
        
            self.m_bDown = wx.BitmapButton(self.subp, wxID_ELB_DOWN, wx.Bitmap(get_image_path("down.xpm"), wx.BITMAP_TYPE_XPM))
            subsizer.Add(self.m_bDown, 0, wx.ALIGN_CENTRE_VERTICAL | wx.TOP | wx.BOTTOM, BTN_BORDER)
            wx.EVT_BUTTON(self.m_bUp, wxID_ELB_UP, self.OnUpItem)
            wx.EVT_BUTTON(self.m_bDown, wxID_ELB_DOWN, self.OnDownItem)

        self.subp.SetAutoLayout(True)
        self.subp.SetSizer(subsizer)
        self.subsizer = subsizer
        subsizer.Fit(self.subp)

        sizer.Add(self.subp, 0, wx.EXPAND)

        class MyPanel(wx.Panel):
            def OnSize(self, event):
                w,h = self.GetClientSizeTuple()
                self.list.SetDimensions(0, 0, w, h)
                
            def __init__(self, parent):
                wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)
                self.Bind(wx.EVT_SIZE, self.OnSize)
        
        p = MyPanel(self)
        
        st = wx.LC_REPORT | wx.LC_NO_HEADER | wx.LC_SINGLE_SEL | wx.SUNKEN_BORDER
        
        if style & wxEL_ALLOW_EDIT:
            st |= wx.LC_EDIT_LABELS

        self.m_listCtrl = CleverListCtrl(p, wxID_ELD_LISTCTRL,
                                    wx.DefaultPosition, wx.DefaultSize, st)

        self.SetStrings([])

        p.list = self.m_listCtrl
        sizer.Add(p, 1, wx.EXPAND)

        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()

        wx.EVT_LIST_ITEM_SELECTED(self.m_listCtrl, wxID_ELD_LISTCTRL, self.OnItemSelected)
        wx.EVT_LIST_END_LABEL_EDIT(self.m_listCtrl, wxID_ELD_LISTCTRL, self.OnEndLabelEdit)
        
    def SetStrings(self, strings):
        self.m_listCtrl.DeleteAllItems()
        n = 0
        for i in strings:
            self.m_listCtrl.InsertStringItem(n, i)
            n = n + 1
        self.m_listCtrl.InsertStringItem(len(strings), u"")

    def GetStrings(self):
        strings = []

        for i in xrange(m_listCtrl.GetItemCount() - 1):
            strings.append(self.m_listCtrl.GetItemText(i))

    def GetListCtrl(self): return self.m_listCtrl
    def GetDelButton(self): return self.m_bDel
    def GetNewButton(self): return self.m_bNew
    def GetUpButton(self): return self.m_bUp
    def GetDownButton(self): return self.m_bDown
    def GetEditButton(self): return self.m_bEdit


    def OnItemSelected(self, event):
        self.m_selection = event.GetIndex()
        if self.m_style & wxEL_ALLOW_UPDOWN:
            self.m_bUp.Enable(self.m_selection != 0 and self.m_selection < self.m_listCtrl.GetItemCount() - 1)
            self.m_bDown.Enable(self.m_selection < self.m_listCtrl.GetItemCount() - 2)
        if self.m_style & wxEL_ALLOW_EDIT:
            self.m_bEdit.Enable(self.m_selection < self.m_listCtrl.GetItemCount() - 1)
        if self.m_style & wxEL_ALLOW_DELETE:
            self.m_bDel.Enable(self.m_selection < self.m_listCtrl.GetItemCount() - 1)

    def OnNewItem(self, event):
        self.m_listCtrl.SetItemState(self.m_listCtrl.GetItemCount() - 1,
                             wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
        self.m_listCtrl.EditLabel(self.m_selection)

    def OnEndLabelEdit(self, event):
        if event.GetText():
            self.m_listCtrl.SetItemImage(event.GetIndex(), 0)
        if event.GetIndex() == self.m_listCtrl.GetItemCount() - 1 and (event.GetText() or self.m_listCtrl.GetItemText(event.GetIndex())):
            self.m_listCtrl.InsertStringItem(self.m_listCtrl.GetItemCount(), u"")

    def OnDelItem(self, event):
        self.m_listCtrl.DeleteItem(self.m_selection)
        if self.m_selection:
            self.m_listCtrl.SetItemState(max(0, self.m_selection - 1),
                                         wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

    def OnEditItem(self, event):
        self.m_listCtrl.EditLabel(self.m_selection)

    def OnUpItem(self, event):
        t1 = self.m_listCtrl.GetItemText(self.m_selection - 1)
        t2 = self.m_listCtrl.GetItemText(self.m_selection)
        self.m_listCtrl.SetItemText(self.m_selection - 1, t2)
        self.m_listCtrl.SetItemText(self.m_selection, t1)
        self.m_listCtrl.SetItemState(self.m_selection - 1,
                             wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

    def OnDownItem(self, event):
        t1 = self.m_listCtrl.GetItemText(self.m_selection + 1)
        t2 = self.m_listCtrl.GetItemText(self.m_selection)
        self.m_listCtrl.SetItemText(self.m_selection + 1, t2)
        self.m_listCtrl.SetItemText(self.m_selection, t1)
        self.m_listCtrl.SetItemState(self.m_selection + 1,
                             wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

