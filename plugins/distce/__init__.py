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

if os.name in ['nt', 'posix']:
    import wx
    from resourceeditor import CRedistributablePlugin
    from distceoptions import DistCEOptions
    
    import configmanager as config
    
    class DistCE(CRedistributablePlugin):
        dist_platform = "Windows CE"
        options = ( DistCEOptions, "Windows CE" )
        
        def build(self, project):
            import tempfile
            import os
            import os.path
            import shutil
            f = tempfile.NamedTemporaryFile("w+t", suffix = ".inf")
            p = f.name
            del f
            f = open(p, "w+t")
            path = self.path
            s = str(open(os.path.join(path, "dist.inf"), "rt").read())
            s = s.replace("__NAME__", project.name)
            s = s.replace("__PROVIDER__", project.company_name)
            s = s.replace("__PATH__", path)
            f.write(s)
            try: cabwiz_path = config.config["cabwiz_path"]
            except: cabwiz_path = ""
            if not os.path.exists(cabwiz_path):
                wx.MessageDialog(wx.GetApp().artub_frame,
                                _("Cannot find CABWIZ.EXE"),
                                _("Error"),
                                wx.OK)
                return
            f.close()
            os.system('"' + cabwiz_path + '" ' + f.name)
            os.remove(f.name)
            p = os.path.basename(f.name)
            s = str(open(os.path.join(path, "dist.ini"), "rt").read())
            s = s.replace("__NAME__", project.name)
            s = s.replace("__VERSION__", str(project.product_version))
            s = s.replace("__DESCRIPTION__", project.description)
            basename = os.path.splitext(f.name)[0]
            s = s.replace("__FILENAME__", basename)
            f = tempfile.NamedTemporaryFile("rt", suffix = ".ini")
            p = f.name
            del f
            f = open(p, "w+t")
            f.write(s)
            
            cwd = os.getcwd()
            temp_dir = os.path.dirname(f.name)
            os.chdir(temp_dir)
            if project.readme_path and os.path.exists(project.readme_path):
                shutil.copyfile(project.readme_path, "readme.txt")
            else:
                open("readme.txt", "wt").write("\n")
            if project.eula_path and os.path.exists(project.eula_path):
                shutil.copyfile(project.eula_path, "eula.txt")
            else:
                open("eula.txt", "wt").write("\n")
            ezsetup_path = os.path.join(path, "ezsetup.exe")
            exe_file = project.name + ".exe"
            cmd_line = ezsetup_path + " -l english -i " + f.name + \
                    " -r readme.txt -e eula.txt -o " + \
                    exe_file
            f.close()
            os.system(cmd_line)
            os.remove(f.name)
            p = os.path.join(project.project_path, "dist", "wince")
            try: os.makedirs(p)
            except: pass
            shutil.move(exe_file, p)
            shutil.move(basename + ".CAB", os.path.join(p, project.normname + ".cab"))
            os.chdir(cwd)
            
    plugin = DistCE
    
