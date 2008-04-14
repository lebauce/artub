# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

"""
API for loading python source into BRM abstract objects
"""
from protest.assertions import *
from protest.test import TestPackageStructure
from load import *
from textwrap import dedent
class getSourceNodeTests:
    pass

class SourceFileTests:
    """
    Encapsulates a python source file
    """

    def can_be_created_from_a_string(self):
        src = "pass"
        s = SourceFile.createFromString("somefile.py","a.b.somefile",src)
        assert isinstance(s,SourceFile)

    def holds_the_fastparser_abstract_syntax_tree_for_the_module(self):
        from bike.parsing.fastparserast import Module
        src = "pass"
        s = SourceFile.createFromString("somefile.py","a.b.somefile",src)
        assert isinstance(s.fastparseroot,Module)


    def can_translate_sourcecoords_into_an_ast_node(self):
        src = dedent('''
        from foo import bar, baz
        ''')[1:]
        s = SourceFile.createFromString("mymodule.py","mymodule",src)
        node = s.translateCoordsToASTNode(1, 17)
        assert node.name == 'bar'

    def can_translate_sourcecoords_into_an_ast_node2(self):
        src = dedent("""
        def foo(x,
                y,
                z):
            return x*y*z
        """)[1:]
        s = SourceFile.createFromString("mymodule.py","mymodule",src)
        node = s.translateCoordsToASTNode(3,8)
        assert node.name == 'z'


    def can_translate_sourcecoords_to_a_from_element_into_an_ast_node(self):
        src = dedent("""
        from foo.baz import bah
        """)[1:]
        s = SourceFile.createFromString("mymodule.py","mymodule",src)
        node = s.translateCoordsToASTNode(1,9)
        assert node.modname == 'foo.baz'


    def can_translate_coords_to_a_from_element_into_an_ast_node2(self):
        src = dedent("""
        from foo.baz import bah
        """)[1:]
        s = SourceFile.createFromString("mymodule.py","mymodule",src)
        node = s.translateCoordsToASTNode(1,20)
        assert node.name == 'bah'


    def can_translate_coords_to_a_fromstar_element_into_an_ast_node2(self):
        src = dedent("""
        from foo import *
        """)[1:]
        s = SourceFile.createFromString("mymodule.py","mymodule",src)
        node = s.translateCoordsToASTNode(1,5)
        assert node.modname == 'foo'

        
class resolveAutoloadFilenameTests:
    """ decides whether to load an autosave file rather than the original.
    Allows editors to perform queries on files that haven't been properly saved
    yet."""
    def returns_filename_if_file_is_newer_than_autosave(self):
        self.t = TestPackageStructure()
        fname = self.t.create_module("foo","pass")
        autosavefile = os.path.join(self.t.rootdir,"#foo.py#")
        file(os.path.join(self.t.rootdir,"#foo.py#"),"w+").write("")
        os.utime(autosavefile,(0,0))
        assert_equal(fname, resolveAutoloadFilename(fname))

    def returns_autosave_file_if_present_and_newer(self):
        self.t = TestPackageStructure()
        fname = self.t.create_module("foo","pass")
        autosavefile = os.path.join(self.t.rootdir,"#foo.py#")
        file(os.path.join(self.t.rootdir,"#foo.py#"),"w+").write("")
        os.utime(fname,(0,0))
        assert_equal(autosavefile, resolveAutoloadFilename(fname))
        
    def returns_filename_if_autosave_file_doesnt_exist(self):
        self.t = TestPackageStructure()
        fname = self.t.create_module("foo","pass")
        assert_equal(fname, resolveAutoloadFilename(fname))

    def __teardown__(self):
        try: self.t.remove()
        except: pass
 
