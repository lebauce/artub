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

import sys, os, os.path

startup_path = "startup\\index.html"
test_path = "F:\\Documents and Settings\\bob\\Mes documents\\glumol\\foo2.xml"
recent_file_path = "startup\\recents.html"
directory_sep = "\\"
index_templates_path = "startup\\index_templates.html"

def set_sys_path():
    sys.path.append(os.getcwd())
    sys.path.append(os.path.join(os.getcwd(), "Numeric"))
    sys.path.append(os.path.join(os.getcwd(), "wx-2.8-msw-unicode"))
    sys.path.append(os.path.join(os.getcwd(), "_xmlplus"))
    sys.path.append(os.path.join(os.getcwd(), "PIL"))
    sys.path.append(os.path.join(os.getcwd(), "win32"))
    sys.path.append(os.path.join(os.getcwd(), "win32", "lib"))
