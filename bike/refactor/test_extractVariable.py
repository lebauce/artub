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
from bike.testutils import *
from bike.refactor.extractVariable import coords, extractLocalVariable
from bike.transformer.save import getQueuedFileContents


class TestExtractLocalVariable(BRMTestCase):
    def test_worksOnSimpleCase(self):
        srcBefore=trimLines("""
        def foo():
            print 3 + 2
        """)
        srcAfter=trimLines("""
        def foo():
            a = 3 + 2
            print a
        """)
        writeFile(tmpfile,srcBefore)
        extractLocalVariable(tmpfile,coords(2,10),coords(2,15),'a')
        self.assertEqual(srcAfter,getQueuedFileContents(tmpfile))

    def test_worksIfCoordsTheWrongWayRound(self):
        srcBefore=trimLines("""
        def foo():
            print 3 + 2
        """)
        srcAfter=trimLines("""
        def foo():
            a = 3 + 2
            print a
        """)
        writeFile(tmpfile,srcBefore)
        extractLocalVariable(tmpfile,coords(2,15),coords(2,10),'a')
        self.assertEqual(srcAfter,getQueuedFileContents(tmpfile))

        
if __name__ == "__main__":
    unittest.main()


