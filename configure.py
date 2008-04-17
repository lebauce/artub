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

import tempfile
import shutil
import os
import sys
import dircache
import pprint
import py_compile
import UserList
import compiler
import locale
import optparse
import difflib
import code
import inspect
import keyword
import gettext, urlparse, urllib2, types
import pickle
import threading
sys.path.append(os.path.join(os.getcwd(), "builder", "Installer"))
os.chdir(os.path.join(os.getcwd(), "builder", "Installer"))
sys.argv[0] = os.path.join(os.getcwd(), os.path.basename(sys.argv[0]))
exec open("Configure.py")
print os.getcwd()

import Configure

