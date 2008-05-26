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

import os
from os.path import join
from resourceeditor import CPlugin
from project import CProject
from glumolfont import CGlumolFont
from script import CScript, get_class_code, make_class_name, make_variable_name
from glumolobject import CGlumolObject
from identifierctrl import IdentifierCtrl
import wx

class BasicGameDialog(wx.Dialog):
    def __init__(
            self, parent = None, ID = -1, title = _("More informations are needed"), size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE   
            ):

        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)
        self.this = pre.this

        sizer = wx.BoxSizer(wx.VERTICAL)
        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, _("Main character's name :"))
        box.Add(label, 0, wx.GROW | wx.ALL, 2)

        self.ego_name = IdentifierCtrl(self, -1, "", size=(80,-1))
        self.ego_name.SetHelpText(_("Main character's name :"))
        box.Add(self.ego_name, 1, wx.GROW | wx.ALL, 2)

        sizer.AddSizer(box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, _("First scene's name :"))
        box.Add(label, 0, wx.GROW|wx.ALL, 2)

        self.scene_name = IdentifierCtrl(self, -1, "", size=(80,-1))
        self.scene_name.SetHelpText(_("First scene's name"))
        box.Add(self.scene_name, 1, wx.GROW|wx.ALL, 2)

        sizer.AddSizer(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 3)

        box = wx.BoxSizer(wx.HORIZONTAL)

        btn = wx.Button(self, wx.ID_OK, _("Ok"))
        btn.SetDefault()
        box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        wx.EVT_BUTTON(self, wx.ID_OK, self.OnOK)

        btn = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
        box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

    def OnOK(self, event):
        if self.scene_name.GetValue() and self.ego_name.GetValue():
            self.EndModal(wx.ID_OK)

class StdTemplates(CPlugin):
    def __init__(self):
        pass
        
    def instanciate_template(self, filename, matches = { }):
        f = open(filename, "r")
        listing = f.read()
        for i in matches.keys():
            listing = listing.replace("%%" + i, matches[i])
        return listing
               
    def get_new_templates(self):
        return ( (_("Monkey Island 2 style"),
                  _("Provides a verb interface like in the Monkey Island 2 game")),
                 (_("Curse of Monkey Island style"),
                  _("Provides a popup interface with 3 actions (look, use, talk), like in the Curse of Monkey Island game")),
                 (_("Empty game"),
                  _("An empty game")))
        
    def create_project(self, templ, name, folder):
        proj = CProject()
        wx.GetApp().artub_frame.project = proj
        proj.name = name
        proj.project_path = folder
        proj.normname = name

        templ_name = templ[0]
        
        if templ_name == "Empty game":
            from string import Template
            proj.listing = Template(open(join("plugins", "stdtemplates", "empty_game.tpl")).read()) \
                               .substitute(name=name, first_scene="None", images_path=repr(join(wx.GetApp().artub_path, "images") + os.sep)[1:-1])
            font = CGlumolFont(proj)
            font.parent = proj
            font.name = "StandardFont"
            font.listing = Template(open(join("plugins", "stdtemplates", "standardfont.tpl")).read()) \
                               .substitute(font_path=repr(join(wx.GetApp().artub_path, "plugins", "stdtemplates") + os.sep)[1:-1])
            print proj.listing
            proj.change_property("font", "StandardFont()")
            proj.topy()
        else:
            dlg = BasicGameDialog()
            dlg.CenterOnScreen()
            dlg.ShowModal()
            ego_name = dlg.ego_name.GetValue()
            scene_name = make_class_name(dlg.scene_name.GetValue())
            dlg.Destroy()
            
            from string import Template
            proj.listing = Template(open(join("plugins", "stdtemplates", "empty_game.tpl")).read()) \
                               .substitute(name=name, first_scene=scene_name,
                                           images_path=repr(join(wx.GetApp().artub_path, "images") + os.sep)[1:-1])
            if templ_name == "Curse of Monkey Island style":
                t = ( "Pickable", "Assemble with", "Do something periodically", "CMI & Fullthrottle like interface", \
                      "Door template", "Automatic door template", "Scaling zone", "Light zone", \
                      "Can walk", "Can talk", "Can turn", "Basic character", "Chain animations", \
                      "Camera follow", "A character", ("Main character", (ego_name,)), \
                      "A basic scene", "WithMusic", "Roll over", "Text" )
            else:
                t = ( "Pickable", "Assemble with", "Do something periodically", "Verb interface", \
                      "Door template", "Automatic door template", "Scaling zone", "Light zone", \
                      "Can walk", "Can talk", "Can turn", "Basic character", "Chain animations", \
                      "Camera follow", "A character", ("Main character", (ego_name,)), \
                      "A basic scene", "WithMusic", "Roll over", "Text" )
                
            tl = wx.GetApp().artub_frame.get_template_list()
            for j in t:
                f = False
                if type(j) is tuple:
                    j, args = j
                else:
                    args = (None,)
                for i in tl:
                    if i[1].name == j:
                        i[1].do(*args)
                        f = True
                if not f:
                    raise "Cannot find " + j
            scene = CGlumolObject(proj)
            scene.parent = proj
            scene.name = scene_name
            base_classes = ["Scene", "WithMusic"]
            code = ["    def __init__(self, parent):\n",
                    "        Scene.__init__(self, parent)\n",
                    "        WithMusic.__init__(self)\n",
                    "        self.__glumolinit__()\n",
                    "    def __glumolinit__(self):\n",
                    "        pass"]
            scene.add_class(scene_name, base_classes = base_classes, body = code) # get_class_code(base_classes))
            scene.ast_has_changed = True
            ego = self.artub.on_new_class("Ego", make_class_name(ego_name), proj, True, False)
            proj.change_property(make_variable_name(ego_name),
                                 make_class_name(ego_name) + "(self.scene)")
            proj.change_property("interface", "Interface(self.screen)")
            
            font = CGlumolFont(proj)
            font.parent = proj
            font.name = "StandardFont"
            font.listing = Template(open(join("plugins", "stdtemplates", "standardfont.tpl")).read()) \
                               .substitute(font_path=repr(join(wx.GetApp().artub_path, "plugins", "stdtemplates") + os.sep)[1:-1])
            proj.change_property("font", "StandardFont()")

            proj.topy()
            
        return proj
        
plugin = StdTemplates
