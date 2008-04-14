# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

"""
Finds the definition of a variable
"""
from protest.assertions import *
from protest.test import TestPackageStructure
from textwrap import dedent
from findDefinition import findDefinitionByCoords

class FindDefinitionByCoordsTests:

    def __init__(self):
        self.t = TestPackageStructure()
    
    def __teardown__(self):
        try: self.t.remove()
        except: pass


    def test_findsClassRef(self):
        todo()
        src=dedent("""
        class TheClass:
            pass
        a = TheClass()
        """)
        createSourceNodeAt(src,"mymodule")
        defn = findDefinitionByCoords(os.path.abspath("mymodule.py"),3,6,[])
        assert defn.filename == os.path.abspath("mymodule.py")
        assert defn.lineno == 1
        assert defn.colno == 6
        assert defn.confidence == 100


    def finds_a_module_from_an_import(self):
        src = dedent("""
        import foo
        """)        
        srcfile= self.t.create_module("mymodule",src)
        foofile= self.t.create_module("foo","pass")
        defn = findDefinitionByCoords(srcfile,2,7,[])
        assert_equal(foofile,defn.filename)
        assert_equal(0,defn.lineno)
        assert_equal(0,defn.colno)
        assert_equal(100,defn.confidence)


    def finds_a_module_from_an_fromstar(self):
        src = dedent("""
        from foo import *
        """)        
        srcfile= self.t.create_module("mymodule",src)
        foofile= self.t.create_module("foo","pass")
        defn = findDefinitionByCoords(srcfile,2,5,[])
        assert_equal(foofile,defn.filename)
        assert_equal(0,defn.lineno)
        assert_equal(0,defn.colno)
        assert_equal(100,defn.confidence)


    def finds_a_module_from_a_name(self):
        src = dedent("""
        import foo
        foo
        """)        
        srcfile= self.t.create_module("mymodule",src)
        foofile= self.t.create_module("foo","pass")
        defn = findDefinitionByCoords(srcfile,3,0,[])
        assert_equal(foofile,defn.filename)
        assert_equal(0,defn.lineno)
        assert_equal(0,defn.colno)
        assert_equal(100,defn.confidence)

    def finds_a_module_from_a_getattr(self):
        src = dedent("""
        import bah.foo
        bah.foo
        """)        
        srcfile= self.t.create_module("mymodule",src)
        foofile= self.t.create_module("bah.foo","pass")
        defn = findDefinitionByCoords(srcfile,3,4,[])
        assert_equal(foofile,defn.filename)
        assert_equal(0,defn.lineno)
        assert_equal(0,defn.colno)
        assert_equal(100,defn.confidence)
