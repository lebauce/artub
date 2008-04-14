# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

#!/usr/bin/env python
import unittest
from bike.parsing.fastparserast import *
from fastparser import fastparser
from bike.testutils import *

class TestGetModule(BRMTestCase):
    def test_returnsNoneIfModuleDoesntExist(self):
        assert getModule(tmpfile) == None
        

class TestGetMaskedLines(BRMTestCase):
    def test_doit(self):
        src =trimLines("""
        class foo: #bah
            pass
        """)
        mod = writeSourceAndCreateNode(src).fastparseroot
        lines = mod.getMaskedModuleLines()
        assert lines[0] == "class foo: #***\n"


class TestGetLinesNotIncludingThoseBelongingToChildScopes(BRMTestCase):
    def test_worksForModule(self):
        src =trimLines("""
        class TheClass:
            def theMethod():
                pass
        def foo():
            b = TheClass()
            return b
        a = foo()
        a.theMethod()
        """)
        mod = writeSourceAndCreateNode(src).fastparseroot
        self.assertEqual(''.join(mod.getLinesNotIncludingThoseBelongingToChildScopes()),
                         trimLines("""
                         a = foo()
                         a.theMethod()
                         """))

    def test_worksForModuleWithSingleLineFunctions(self):
        src=trimLines("""
        a = blah()
        def foo(): pass
        b = 1
        """)
        mod = writeSourceAndCreateNode(src).fastparseroot
        lines = mod.getLinesNotIncludingThoseBelongingToChildScopes()
        self.assertEqual(''.join(lines),
                         trimLines("""
                         a = blah()
                         b = 1
                         """))


    def test_worksForSingleLineFunction(self):
        src=trimLines("""
        a = blah()
        def foo(): pass
        b = 1
        """)
        fn = writeSourceAndCreateNode(src).fastparseroot.getChildNodes()[0]
        lines = fn.getLinesNotIncludingThoseBelongingToChildScopes()
        self.assertEqual(''.join(lines),
                         trimLines("""
                         def foo(): pass
                         """))


fnWithEmptyLineInIt = """
class TheClass:
    def theFunction():
        a = foo()

        print 'a'

    # end of function
"""

if __name__ == "__main__":
    unittest.main()
    
