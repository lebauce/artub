import wx
from depplatform import get_image_path
import wx.lib.flatnotebook as fnb

class ArtubNotebook(fnb.FlatNotebook):
    def __init__(self, parent, id, size, style=wx.CLIP_CHILDREN | fnb.FNB_X_ON_TAB | fnb.FNB_NODRAG):
        fnb.FlatNotebook.__init__(self, parent, id, style=style)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGING, self.on_page_changed)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.on_close_page)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSED, self.on_closed_page)

        self.pages = []
        self.artub_frame = parent
        
    def on_left_button_down(self, evt):
       tup = self.HitTest(evt.GetPosition())
       if tup and tup[1] == wx.NB_HITTEST_ONICON:
           editor = self.artub_frame.get_editor_from_page(tup[0])
           self.artub_frame.close_editor(editor)
           sel = self.GetSelection()
           if sel:
               self.SetSelection(sel)
       evt.Skip()
    
    def on_page_changed(self, event):
        try:
            if self.dont_select:
               del self.dont_select
               event.Skip()
               return
        except: pass
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection() 
        page = self.GetPage(new)
        editor = self.artub_frame.get_editor_from_page(new)
        skip = True
        if editor:
            try: skip = not self.artub_frame.edit_resource(editor.active_resource, editor.editor_class, change_page = False)                
            except:
                raise
                skip = False
            self.artub_frame.set_dying(True)
            if hasattr(editor.active_resource, "treeitem"):
                self.artub_frame.tree.SelectItem(editor.active_resource.treeitem)
            self.artub_frame.set_dying(False)
        else:
            self.artub_frame.active_editor = None
        event.Skip() # May cause bugs...

    def on_closed_page(self, event):
        event.SetSelection(event.GetSelection() - 1)
        event.SetOldSelection(event.GetSelection())
        self.on_page_changed(event)
            
    def on_close_page(self, event):
        if event.GetSelection():
            new = event.GetSelection()
            editor = self.artub_frame.get_editor_from_page(new)
            if editor: self.artub_frame.close_editor(editor, close_page = False)
            event.Skip()
        else:
            event.Veto()
