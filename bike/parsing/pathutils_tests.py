# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

"""
Utilities to help with finding python modules, translating module names into filenames etc..
"""
from protest.assertions import *
from protest.test import TestPackageStructure
from pathutils import *

class filenameToModulePathTests:
    ''' Given a python module filename, returns the fully qualified package path.
        e.g. someroot/foo/bah/baz.py ->  foo.bah.baz'''

    def __teardown__(self):
        try:
            self.t.remove()
        except: pass

    def returns_module_name_if_not_in_a_package(self):
        self.t = TestPackageStructure()
        self.t.create_module("foo","pass")
        assert_equal('foo',filenameToModulePath(os.path.join(self.t.rootdir,"foo.py")))

    def returns_nested_package_name_for_module_that_is_in_a_package(self):
        self.t = TestPackageStructure()
        self.t.create_module("a.b.foo","pass")
        assert_equal('a.b.foo',filenameToModulePath(
            os.path.join(self.t.rootdir,"a","b","foo.py")))

    def returns_module_name_if_filename_is_relative_to_dot(self):
        os.mkdir("tmproot")
        os.chdir("tmproot")
        file("tmpfile.py","w+").write("pass")
        try:
            assert_equal('tmpfile',filenameToModulePath("."+os.sep+"tmpfile.py"))
        finally:
            try: _removefile("tmpfile.py")
            except: pass
            os.chdir("..")
            os.rmdir("tmproot")



class getRootDirectoryTests:
    '''
    Given a python module filename, this function returns the directory at the root of the package hierarchy containing the module
    '''
    
    def returns_the_parent_directory_if_file_not_in_package(self):
        try:
            # this doesnt have __init__.py file, so
            # isnt package
            os.makedirs("a")
            _writeFile(os.path.join("a", "foo.py"),"pass")
            dir = getRootDirectory(os.path.join("a", "foo.py"))
            assert dir == "a"
        finally:
            _removefile(os.path.join("a", "foo.py"))
            os.removedirs(os.path.join("a"))

    def returns_the_first_non_package_parent_directory_if_file_in_package(self):
        try:
            os.makedirs(os.path.join("root", "a", "b"))
            _writeFile(os.path.join("root", "a", "__init__.py"), "# ")
            _writeFile(os.path.join("root", "a", "b", "__init__.py"), "# ")
            _writeFile(os.path.join("root", "a", "b", "foo.py"), "pass")
            dir = getRootDirectory(os.path.join("root", "a", "b", "foo.py"))
            assert dir == "root"
        finally:
            _removefile(os.path.join("root", "a", "__init__.py"))
            _removefile(os.path.join("root", "a", "b", "__init__.py"))
            _removefile(os.path.join("root", "a", "b", "foo.py"))
            os.removedirs(os.path.join("root", "a", "b"))

    def returns_the_first_non_package_parent_directory_if_path_is_a_package(self):
        try:
            os.makedirs(os.path.join("root", "a", "b"))
            _writeFile(os.path.join("root", "a", "__init__.py"), "# ")
            _writeFile(os.path.join("root", "a", "b", "__init__.py"), "# ")
            _writeFile(os.path.join("root", "a", "b", "foo.py"), "pass")
            dir = getRootDirectory(os.path.join("root", "a", "b"))
            assert dir == "root"
        finally:
            _removefile(os.path.join("root", "a", "__init__.py"))
            _removefile(os.path.join("root", "a", "b", "__init__.py"))
            _removefile(os.path.join("root", "a", "b", "foo.py"))
            os.removedirs(os.path.join("root", "a", "b"))

    def returns_the_dir_if_dir_is_the_root_directory(self):
        try:
            os.makedirs(os.path.join("root", "a", "b"))
            _writeFile(os.path.join("root", "a", "__init__.py"), "# ")
            _writeFile(os.path.join("root", "a", "b", "__init__.py"), "# ")
            _writeFile(os.path.join("root", "a", "b", "foo.py"), "pass")
            dir = getRootDirectory("root")
            assert dir == "root"
        finally:
            _removefile(os.path.join("root", "a", "__init__.py"))
            _removefile(os.path.join("root", "a", "b", "__init__.py"))
            _removefile(os.path.join("root", "a", "b", "foo.py"))
            os.removedirs(os.path.join("root", "a", "b"))

def _writeFile(path,src):
    file(path,'w+').write(src)

def _removefile(path):
    try: os.remove(path)
    except: pass
