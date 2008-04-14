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
from bike import testdata
from rename import rename
from bike.testutils import *

class TestRenameTemporary(BRMTestCase):
    def test_renamesDefaultArgument(self):
        src=trimLines("""
        a = 'hello'
        def amethod(a=a):
            pass
        """)
        srcAfter=trimLines("""
        b = 'hello'
        def amethod(a=b):
            pass
        """)
        src = self.helper(src,"",1,0,"b")
        self.assertEqual(srcAfter,src)
        

    def test_renamesSimpleReferencesGivenAssignment(self):
        src=trimLines("""
        def foo():
            a = 3
            print a
        """)
        srcAfter=trimLines("""
        def foo():
            b = 3
            print b
        """)
        src = self.helper(src,"",2,4,"b")
        self.assertEqual(srcAfter,src)

    def test_renamesKeywordParameterInSignature(self):
        src=trimLines("""
        def foo(a=None):
            bar(a=a)
        """)
        srcAfter=trimLines("""
        def foo(b=None):
            bar(a=b)
        """)
        src = self.helper(src,"",1,8,"b")
        self.assertEqual(srcAfter,src)

    def test_renamesKeywordParameterInBody(self):
        src=trimLines("""
        def foo(a=None):
            bar(a=a)
        """)
        srcAfter=trimLines("""
        def foo(b=None):
            bar(a=b)
        """)
        src = self.helper(src,"",2,10,"b")
        self.assertEqual(srcAfter,src)

    def test_renamesClassVariable(self):
        src=trimLines("""
        class Foo:
            A = 0
            def bar():
                return self.A
        print Foo.A
        print Foo().A
        """)
        srcAfter=trimLines("""
        class Foo:
            B = 0
            def bar():
                return self.B
        print Foo.B
        print Foo().B
        """)
        src = self.helper(src,"",2,4,"B")
        self.assertEqual(srcAfter,src)

    def helper(self, src, classsrc, line, col, newname):
        try:
            createPackageStructure(src,classsrc)
            rename(pkgstructureFile1,line,col,newname)
            # modify me once save is moved
            #return readFile(filename)
            from bike.transformer.save import outputqueue
            return outputqueue[pkgstructureFile1]
        finally:
            removePackageStructure()
if __name__ == "__main__":
    unittest.main()
