# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

#!/usr/bin/env python
import setpath
import unittest
import os
import compiler
from bike.testutils import *
from bike.parsing.load import getSourceNode
from bike.parsing.fastparser import fastparser
from bike.parsing.fastparserast import Module, Class
from common import indexToCoordinates, getScopeForLine, walkLinesContainingStrings, translateSourceCoordsIntoASTNode


class TestGetScopeForLine(BRMTestCase):

    def test_worksWithFunctionScope(self):
        src = trimLines("""
        class a:
            def foo():
                pass
        """)
        node = writeSourceAndCreateNode(src)
        self.assertEqual(getScopeForLine(node,3).name,"foo")

    def test_worksWithModuleScope(self):
        src = trimLines("""
        class TheClass:
            pass
        a = TheClass()
        """)
        node = writeSourceAndCreateNode(src)
        assert isinstance(getScopeForLine(node,3),Module)

    def test_worksWithInlineClass(self):
        src = trimLines("""
        class TheClass: pass""")
        node = writeSourceAndCreateNode(src)
        assert isinstance(getScopeForLine(node,1),Class)


class TestIndexToCoordinates(BRMTestCase):

    def test_worksOnSingleLineString(self):
        src = trimLines('''
        foo bah
        ''')
        x,y = indexToCoordinates(src,src.index("bah"))
        self.assertEqual(x,4)
        self.assertEqual(y,0)
        x,y = indexToCoordinates(src,src.index("foo"))
        self.assertEqual(x,0)
        self.assertEqual(y,0)

    def test_worksOnMultilLineString(self):
        src = trimLines('''
        foo bah
        baz boh
        ''')
        x,y = indexToCoordinates(src,src.index("boh"))
        self.assertEqual(x,4)
        self.assertEqual(y,1)



        


class TestMatchFinder(BRMTestCase):

    def test_visitLambda(self):
        from bike.parsing.load import MatchFinder
        finder = MatchFinder()
        src = '''x = lambda a, b, c=None, d=None: (a + b) and c or d'''
        ast = compiler.parse(src)
        finder.reset(src)
        compiler.walk(ast, finder)


class TestWalkLinesContainingStrings(BRMTestCase):
    def test_walksClasses(self):
        src=trimLines("""
        class TestClass(a,
                        baseclass):
            pass
        """)
        class MyWalker:            
            def visitClass(self, node):
                self.basenames = []
                for name in node.bases:
                    self.basenames.append(name.name)
        
        writeTmpTestFile(src)
        srcnode = getSourceNode(tmpfile)
        walker = MyWalker()
        walkLinesContainingStrings(srcnode.fastparseroot,walker,
                                   ["baseclass"])
        self.assertEqual(["a","baseclass"],walker.basenames)


if __name__ == "__main__":
    unittest.main()
