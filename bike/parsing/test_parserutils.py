# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

import unittest
from parserutils import *
from bike.testutils import *

def runOverPath(path):
    import compiler
    from parser import ParserError
    from bike.parsing.load import getFilesForName
    files = getFilesForName(path)
    for fname in files:
        print fname
        src = file(fname).read()
        #print src
        src = maskStringsAndRemoveComments(src)

        for logicalline in splitLogicalLines(src):
            #print "logicalline=",logicalline    
            logicalline = logicalline.strip()
            logicalline = makeLineParseable(logicalline)
            try:
                compiler.parse(logicalline)
            except ParserError:
                print "ParserError on logicalline:",logicalline
            except:
                log.exception("caught exception")
                

explicitlyContinuedLineWithComment = """
z = a + b + \  # comment
  c + d
pass
"""

implicitlyContinuedLine = """
z = a + b + (
  c + d)
pass
"""


implicitlyContinuedLine2 = """
z = a + b + ( c + [d
  + e]
  + f)   # comment
pass
"""

multilineComment = """
''' this is an mlc
so is this
'''
pass
"""

if __name__ == "__main__":
    from bike import logging
    logging.init()
    log = logging.getLogger("bike")
    log.setLevel(logging.INFO)
    
    # add soak tests to end of test
    class Z_SoakTest(BRMTestCase):
        def test_linesRunThroughPythonParser(self):
            print ""
            #print splitLogicalLines(file('/usr/local/lib/python2.2/aifc.py').read())
            #runOverPath('/usr/local/lib/python2.2/test/badsyntax_nocaret.py')
            runOverPath('/usr/local/lib/python2.2/')
    unittest.main()
