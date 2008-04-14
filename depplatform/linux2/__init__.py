import sys

startup_path = "startup/index_default.html"
startup_path_mozilla = "startup/index.html"
test_path = "/home/bob/glumol/foo2.xml"
directory_sep = "/"
index_templates_path = "startup/index_templates_default.html"

def set_sys_path():
    sys.path.append('/usr/lib/python2.4/site-packages')
    sys.path.append('/usr/lib/python2.4/site-packages/wx-2.6-gtk2-unicode')
    sys.path.append('/usr/lib/python2.4/site-packages/PIL')
