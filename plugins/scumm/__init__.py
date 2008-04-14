import wx
from resourceeditor import CPlugin, AddResource
from glumolobject import CGlumolObject
from choosename import choose_a_name
import os
import os.path
import threading

class GaugeDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE, thread=None
            ):

        self.thread = thread
        pre = wx.PreDialog()
        pre.Create(parent, ID, title, pos, size, style)
        self.PostCreate(pre)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.gauge = wx.Gauge(self, -1, 50, (110, 95), (250, 25))
        vbox.Add(self.gauge)
        
        self.SetSizer(vbox)
        vbox.Fit(self)
        self.Bind(wx.EVT_TIMER, self.TimerHandler)
        self.timer = wx.Timer(self)
        self.timer.Start(100)
        
        if thread:
            thread.start()

    def __del__(self):
        self.timer.Stop()

    def TimerHandler(self, event):
        if not self.thread.isAlive():
            self.EndModal(wx.ID_CANCEL)
            return
        self.gauge.Pulse()

class TestDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE
            ):

        pre = wx.PreDialog()
        pre.Create(parent, ID, title, pos, size, style)

        self.PostCreate(pre)

        vbox = wx.BoxSizer(wx.VERTICAL)

        box = wx.BoxSizer(wx.HORIZONTAL)
        self.text = wx.TextCtrl(self, -1, "1")
        box.Add(self.text)
        self.spin = wx.SpinButton(self, -1)
        box.Add(self.spin)

        vbox.Add(box, wx.EXPAND)

        box = wx.BoxSizer(wx.HORIZONTAL)
        ok = wx.Button(self, wx.ID_OK, "Ok")
        box.Add(ok)
        cancel = wx.Button(self, wx.ID_CANCEL, "Cancel")
        box.Add(cancel)

        vbox.Add(box)

        self.SetSizer(vbox)
        vbox.Fit(self)

        self.Bind(wx.EVT_SPIN, self.on_spin, self.spin)

    def on_spin(self, event):
        self.text.SetValue(str(event.GetPosition()))


class ScummImport(CPlugin):
    def __init__(self, *args):
        CPlugin.__init__(self, *args)
        artub = wx.GetApp().frame
        id = artub.mainmenu.FindMenu(_("Tools"))
        menu = artub.mainmenu.GetMenu(id)
        id = wx.NewId()
        menu.Append(id, _("Import scene from a SCUMM game"))
        menu.Enable(id, False)
        wx.EVT_MENU(artub, id, self.on_import)
        artub._enable_menus.append(id)

    def on_import(self, evt):
        dlg = wx.DirDialog(self.artub, _("Choose the root directory of a SCUMM game"))

        if dlg.ShowModal() == wx.ID_OK:
            import scumm
            mngr = scumm.ScummResourceManager(dlg.GetPath())
            dlg = TestDialog(self.artub, -1, _("Choose a scene"))
            dlg.CenterOnScreen()
            dlg.spin.SetRange(1, len(mngr.dir_rooms.rooms))
            dlg.spin.SetValue(0)

            project = self.artub.project

            if dlg.ShowModal() == wx.ID_OK:
                scene_name = choose_a_name("ScummScene")
                path = os.getcwd()
                newdir = os.path.join(project.project_path, scene_name)
                try: os.mkdir(newdir)
                except: pass
                os.chdir(newdir)
                gaugedlg = None
                try:
                    self.running = True
                    def load_scene():
                        scumm.scene_name = scene_name
                        scumm.dir_prefix = scene_name + os.sep
                        roomdata, size = mngr.load_room(int(dlg.text.GetValue()))
                        scumm.data = roomdata
                        room = scumm.LFLF(0, size).room
                        self.running = False
                    t = threading.Thread(target=load_scene)
                    gaugedlg = GaugeDialog(self.artub, -1, _("Importing scumm scene"), thread=t)
                    gaugedlg.CenterOnScreen()
                    gaugedlg.ShowModal()
                    scene = CGlumolObject(project)
                    scene.name = scene_name
                    scene.listing = open("scene.txt").read()
                    AddResource(scene, _("add Scene"), refresh_editor = True)
                                        
                except:
                    raise
                if gaugedlg:
                    gaugedlg.Destroy()
                    del gaugedlg
                os.chdir(path)

            dlg.Destroy()

        dlg.Destroy()

plugin = ScummImport
