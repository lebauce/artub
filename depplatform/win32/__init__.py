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
