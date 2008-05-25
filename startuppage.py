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

import wx
import os
from os.path import join, exists
import depplatform as platform
import time
import sys
      
class StartupPageBase:
    def __init__(self, artub_frame):
        self.url_handlers = { "new_project" : artub_frame.on_new, \
                              "open_project" : artub_frame.on_open, \
                              "import_template" : self.show_templates_page }
        self.dyn_path = os.path.join(wx.GetApp().artub_path, 'startup', 'dynamic.html')
    
    def get_history_string(self):
        s = ''
        for i in range(self.artub_frame.filehistory.GetNoHistoryFiles()):
            s += '<tr><td height="30"><a href="' + self.artub_frame.filehistory.GetHistoryFile(i)
            s += '">' + self.artub_frame.filehistory.GetHistoryFile(i)
            s += '</a></td><td>'
            try:
                s += time.ctime(os.stat(         \
                    self.artub_frame.filehistory.GetHistoryFile(i))[8])
            except: pass
            s += '</td></tr>'
        if not s:
            s = "<tr><td><i>No recent file</i></td></tr>"
        return s

    def redirect_outputs(self):
        class Buffer:
            def __init__(self):
                self.buffer = ''
            def write(self, s):
                self.buffer += s
        self.oldstdout = sys.stdout
        sys.stdout = Buffer()
        
    def restore_outputs(self):
        if hasattr(self, "oldstdout"):
            buffer = sys.stdout.buffer
            sys.stdout = self.oldstdout
            del self.oldstdout
            return buffer
        return ""
    
    def show(self):
        if self.artub_frame.active_editor:
            self.artub_frame.unactivate_editor(self.artub_frame.active_editor)
        self.artub_frame.nb.SetSelection(0)

    def header(self):
        print """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML>
<HEAD>
<TITLE>Startup</TITLE>
<META http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<LINK href="glumol.css" type=text/css rel=stylesheet>
</HEAD>
<BODY>
<table width="100%" cellspacing="0" class="projects">
<tbody>
"""

    def footer(self):
        print """</tbody>
</table>
</BODY>
</HTML>"""

    def update_template_page(self):
        self.redirect_outputs()
        try:
            self.header()
            def for_each_template(templates):
                for k, i in templates.items():
                    if type(i) == type({}):
                        print '<tr><td><br>'
                        print '<table class="projects" width="100%">'
                        print '<tr class="smalltab"><td>'
                        print k
                        print '</td></tr>'
                        for_each_template(i)
                        print '</td></tr></table>'
                    else:
                        if self.artub_frame.project.has_template(i): continue
                        print '<tr class="project"><td>'
                        if hasattr(i, "html_page"):
                            print '<a href="#' + join(i.path, i.html_page) + '">' + i.name + '</a>'
                            self.url_handlers[join(i.path, i.html_page)] = i.do
                        else:
                            norm = i.name.replace(" ", "")
                            print '<a href="#' + norm + '">' + i.name + '</a>'
                            self.url_handlers[norm] = i.do
                        print '<br><span class="description">' + i.description + '</span>'
                        print '</td></tr>'

            for_each_template(self.artub_frame.templates)
            print "<p>&nbsp;</p>"
            self.footer()
            s = self.restore_outputs().encode('iso-8859-1')
            open(self.dynpath, 'w').write(s)
        except:
            raise
            self.restore_outputs()

    def load_page(self, page):
        self.Navigate(page)
        
if wx.Platform == '__WXMSW__':
    import wx.lib.iewin as iewin
    class StartupPage(StartupPageBase, iewin.IEHtmlWindow):
        def __init__(self, parent, id, artub_frame):
            self.artub_frame = artub_frame
            StartupPageBase.__init__(self, artub_frame)
            iewin.IEHtmlWindow.__init__(self, parent, id, style = wx.NO_FULL_REPAINT_ON_RESIZE)
            iewin.EVT_BeforeNavigate2(parent, -1, self.OnBeforeNavigate2)
            iewin.EVT_DocumentComplete(parent, -1, self.OnDocumentComplete)
            self.times = 0
            self.ignore_before_navigate = False
            self.must_go_back = False
            
        def update_recent_files(self):
            self.redirect_outputs()
            try:
                self.header()
                print """<tr class="smalltab">
    <td width="50%" height="30">Name</td>
    <td width="50%">Modified</td>
    </tr>"""
                path = os.getcwd()
                os.chdir(os.path.dirname(platform.startup_path))
                no_recent_files = True
                n = self.artub_frame.filehistory.GetNoHistoryFiles()
                for i in range(n):
                    try:
                        s = '<tr class="project"><td height="30"><a href="' + self.artub_frame.filehistory.GetHistoryFile(i)
                        s += '">' + self.artub_frame.filehistory.GetHistoryFile(i)
                        s += '</a></td><td>' + time.ctime(os.stat(         \
                                self.artub_frame.filehistory.GetHistoryFile(i))[8]) + '</td></tr>'
                        print s
                        no_recent_files = True
                    except:
                        pass
                if not n:
                    print "<tr><td><i>No recent file</i></td></tr>"
                self.footer()
                open('recents.html', 'w').write(self.restore_outputs())
                self.ignore_before_navigate = True
                self.load_page(os.path.join(wx.GetApp().artub_path, platform.startup_path))
                self.ignore_before_navigate = False
                os.chdir(path)
            except:
                self.restore_outputs()
                os.chdir(path)
                raise
                

        def OnDocumentComplete(self, evt):
            # print "OnDocumentComplete", self.must_go_back, evt.URL
            if self.must_go_back:
                self.must_go_back = False
                self.ignore_before_navigate = True
                self.load_page(os.getcwd() + '\\' + platform.startup_path)
        
        def OnBeforeNavigate2(self, evt):
            if evt.URL.startswith("http"):
                evt.Skip()
            else:
                url = evt.URL
                index = url.find('#')
                if index != -1:
                    command = url[index + 1:]
                    evt.Cancel = True
                    self.url_handlers[command](evt)
                    self.update_template_page()
                    self.load_page(os.path.join(wx.GetApp().artub_path, 'startup', 'index_templates.html'))
                elif url.endswith('.glu'):
                    self.artub_frame.open_project(evt.URL)
                    evt.Cancel = True
            evt.Skip()

        def LoadFile(self, page):
            self.ignore_before_navigate = True
            self.load_page(os.path.join(wx.GetApp().artub_path, page))

        def show_templates_page(self, evt = None):
            self.update_template_page()
            self.load_page(os.path.join(wx.GetApp().artub_path, platform.index_templates_path))
            self.show()

elif wx.Platform == '__WXMAC__':
    import wx.webkit as webkit
    class StartupPage(StartupPageBase, webkit.WebKitCtrl):
        def __init__(self, parent, id, artub_frame):
            self.artub_frame = artub_frame
            StartupPageBase.__init__(self, artub_frame)
            webkit.WebKitCtrl.__init__(self, parent, id, style = wx.NO_FULL_REPAINT_ON_RESIZE)
            webkit.EVT_WEBKIT_BEFORE_LOAD(parent, self.on_before_navigate)
            
        def update_recent_files(self):
            self.redirect_outputs()
            try:
                self.header()
                print """<tr class="smalltab">
    <td width="50%" height="30">Name</td>
    <td width="50%">Modified</td>
    </tr>"""
                path = os.getcwd()
                os.chdir(os.path.dirname(platform.startup_path))
                no_recent_files = True
                n = self.artub_frame.filehistory.GetNoHistoryFiles()
                for i in range(n):
                    try:
                        s = '<tr class="project"><td height="30"><a href="' + self.artub_frame.filehistory.GetHistoryFile(i)
                        s += '">' + self.artub_frame.filehistory.GetHistoryFile(i)
                        s += '</a></td><td>' + time.ctime(os.stat(         \
                                self.artub_frame.filehistory.GetHistoryFile(i))[8]) + '</td></tr>'
                        print s
                        no_recent_files = True
                    except:
                        pass
                if not n:
                    print "<tr><td><i>No recent file</i></td></tr>"
                self.footer()
                open('recents.html', 'w').write(self.restore_outputs())
                self.ignore_before_navigate = True
                self.load_page(os.path.join(wx.GetApp().artub_path, platform.startup_path))
                self.ignore_before_navigate = False
                os.chdir(path)
            except:
                self.restore_outputs()
                os.chdir(path)
                raise

        def on_before_navigate(self, evt):
            if evt.URL.startswith("http"):
                evt.Skip()
            else:
                url = evt.URL
                index = url.find('#')
                if index != -1:
                    command = url[index + 1:]
                    self.url_handlers[command](evt)
                    # self.show_templates_page()
                elif url.endswith('.glu'):
                    self.artub_frame.open_project(evt.URL[7:])
            evt.Skip()

        def load_page(self, filename):
          self.SetPageSource(open(filename).read(), 'file://' + filename)

        def LoadFile(self, page):
            self.ignore_before_navigate = True
            self.load_page(os.path.join(wx.GetApp().artub_path, page))

        def show_templates_page(self, evt = None):
            self.update_template_page()
            self.load_page(os.path.join(wx.GetApp().artub_path, platform.index_templates_path))
            self.show()
else:
  try:
    from wx.mozilla import *
    class StartupPage(StartupPageBase, MozillaBrowser):
        def __init__(self, parent, id, artub_frame):
            StartupPageBase.__init__(self, artub_frame)
            MozillaBrowser.__init__(self, parent, id,
                                      style = wx.NO_FULL_REPAINT_ON_RESIZE)
            EVT_MOZILLA_BEFORE_LOAD(self, id, self.on_before_load)
            EVT_MOZILLA_URL_CHANGED(self, id, self.on_update_url)
            EVT_MOZILLA_RIGHT_CLICK(self, id, self.on_right_click)
            
            self.artub_frame = artub_frame
            
        def on_update_url(self, evt):
            evt.GetURL = evt.GetNewURL
            self.on_before_load(evt)
            
        def on_before_load(self, evt):
            url = evt.GetURL()
            if url.startswith("http"):
                pass
            else:
                # if self.back_or_forward: return
                index = url.find('#')
                if index != -1:
                    command = url[index + 1:]
                    self.url_handlers[command](evt)
                    evt.SetNewURL(url[:index])
                    self.GoBack()
                    evt.Skip()
                elif not url.endswith('.html'):
                    url = url[7:]
                    self.artub_frame.open_project(url)
                    evt.Skip()
            
        def go_back(self, evt):
            self.GoBack()
            
        def go_forward(self, evt):
            self.back_or_forward = True
            self.GoForward()
            
        def on_right_click(self, evt):
            class ContextMenu(wx.Menu):
                def __init__(this):
                    wx.Menu.__init__(this)
                    
                    propID = wx.NewId()
                    this.Append(propID, _("Back"), _("Back"))
                    wx.EVT_MENU(this, propID, self.go_back)
            
                    propID = wx.NewId()
                    this.Append(propID, _("Forward"), _("Forward"))
                    wx.EVT_MENU(this, propID, self.go_forward)
                    
            self.artub_frame.nb.PopupMenu(ContextMenu(), evt.GetPosition())
        
        def update_recent_files(self):
            s = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML>
<HEAD>
<TITLE>Startup</TITLE>
<META http-equiv="Content-Type" content="text/html; charset=utf-8">
<LINK href="glumol.css" type=text/css rel=stylesheet>
</HEAD>
<BODY>
<table width="100%" cellspacing="0" class="projects">
<tbody>
<tr class="smalltab">
<td width="50%" height="30">Name</td>
<td width="50%">Modified</td>
</tr>"""
            path = os.getcwd()
            os.chdir(os.path.dirname(platform.startup_path))
            for i in range(self.artub_frame.filehistory.GetNoHistoryFiles()):
                s += '<tr class="project"><td height="30"><a href="' + self.artub_frame.filehistory.GetHistoryFile(i)
                s += '">' + self.artub_frame.filehistory.GetHistoryFile(i)
                s += '</a></td><td>' + time.ctime(os.stat(         \
                        self.artub_frame.filehistory.GetHistoryFile(i))[8]) + '</td></tr>'
            if not s:
                s = "<tr><td><i>No recent file</i></td></tr>"
            s += """</tbody>
</table>
</BODY>
</HTML>"""
            open('recents.html', 'w').write(s)
            os.chdir(path)
            self.ignore_before_navigate = True
            self.load_page(join(os.getcwd(), platform.startup_path_mozilla))
            self.ignore_before_navigate = False
            
        def load_page(self, page):
            self.LoadURL("file://" + page)
  
        def show_templates_page(self, evt = None):
            self.update_template_page()
            templates = open(self.dyn_path).read()
            open(self.dyn_path, "w").write(
                open(platform.startup_path).read().replace(
                    '<templates>',
                    templates
                )
            )
            self.load_page(self.dyn_path)
            self.show()

        def header(self):
            pass

        def footer(self):
            pass

  except:
    import wx.html
    class StartupPage(StartupPageBase, wx.html.HtmlWindow):
        def __init__(self, parent, id, artub_frame):
            self.artub_frame = artub_frame
            StartupPageBase.__init__(self, artub_frame)
            wx.html.HtmlWindow.__init__(self, parent, id, style = wx.NO_FULL_REPAINT_ON_RESIZE)
    
        def update_recent_files(self):
            path = os.getcwd()
            os.chdir(os.path.dirname(platform.startup_path))
            page = open(os.path.basename(platform.startup_path), 'r').read()
            s = self.get_history_string()
            self.SetPage(page.replace("<recentfiles>", s))
            os.chdir(path)
            
        def OnLinkClicked(self, linkinfo):
            href = linkinfo.GetHref()
            if href == "#new_project":
                self.artub_frame.on_new(None)
            elif href == "#open_project":
                self.artub_frame.on_open(None)
            else:
                if href[0] == '#':
                    self.url_handlers[href[1:]](linkinfo)
                    self.show_templates_page()
                else:
                    self.artub_frame.open_project(href)
        
        def load_page(self, filename):
          print open(filename).read()
          self.SetPage(open(filename).read())
          
        def show_templates_page(self, evt = None):
            self.update_template_page()
            startup_path = join(wx.GetApp().artub_path, 'startup')
            templates = open(self.dyn_path).read()
            open(self.dyn_path, "w").write(
                open(platform.index_templates_path).read().replace(
                    '<templates>',
                    templates
                )
            )
            self.load_page(self.dyn_path)
            self.show()
