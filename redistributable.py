import wx
platforms = []

class Redistributable:
    def __init__(self):
        artub = wx.GetApp().artub_frame
        for i in artub.plugins:
            if hasattr(i, "dist_platform"):
                platforms.append(i)
        projmenu = artub.mainmenu.GetMenu(artub.mainmenu.FindMenu(_("Tools")))
        id = wx.NewId()
        projmenu.AppendMenu(id, _("Build redistributable"), self.get_menu(projmenu))
        projmenu.Enable(id, False)
        artub._enable_menus.append(id)
                
    def get_menu(self, parent):
        item = wx.Menu()
        for i in platforms:
            id = wx.NewId()
            item.Append(id, i.dist_platform)
            wx.EVT_MENU(wx.GetApp().artub_frame, id, i.on_build)
        return item
