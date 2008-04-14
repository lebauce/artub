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

