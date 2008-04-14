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
import compiler
import os

from bike.testutils import *

from pathutils import getPathOfModuleOrPackage
from pathutils import *
import pathutils as loadmodule
from protest.assertions import *

class TestGetFilesForName(BRMTestCase):
    def testGetFilesForName_recursivelyReturnsFilesInBreadthFirstOrder(self):
        createPackageStructure("pass", "pass")

        files = getFilesForName(pkgstructureBasedir)
        for f in files:
            assert f in \
                  [os.path.join(pkgstructureBasedir, '__init__.py'), 
                    os.path.join(pkgstructureBasedir, 'foo.py'), 
                    os.path.join(pkgstructureChilddir, '__init__.py'), 
                    os.path.join(pkgstructureChilddir, 'bah.py')]

    def testGetFilesForName_globsStars(self):
        createPackageStructure("pass", "pass")
        assert getFilesForName(os.path.join(pkgstructureBasedir, "fo*")) == [os.path.join(pkgstructureBasedir, 'foo.py')]
        removePackageStructure()

    def testGetFilesForName_doesntListFilesWithDotAtFront(self):
        writeFile(os.path.join(".foobah.py"),"")
        files = getFilesForName("a")
        assert_equal([],files)
        




class getPackageBaseDirectory(BRMTestCase):
    def test_returnsBasePackageIfFileInPackageHierarchy(self):
        try:
            createPackageStructure("","")
            dir = loadmodule.getPackageBaseDirectory(pkgstructureFile2)
            assert_equal(pkgstructureBasedir, dir)
        finally:
            removePackageStructure()

    def test_returnsFileDirectoryIfFileNotInPackage(self):
        try:
            createPackageStructure("","")
            dir = loadmodule.getPackageBaseDirectory(pkgstructureFile0)
            assert_equal(pkgstructureRootDir, dir)
        finally:
            removePackageStructure()


class TestGetPathOfModuleOrPackage(BRMTestCase):
    def test_worksForFullPath(self):
        try:
            createPackageStructure("pass","pass")
            import sys
            assert_equal(getPathOfModuleOrPackage("a.b.bah",
                                                      [pkgstructureRootDir]),
                             pkgstructureFile2)
        finally:
            removePackageStructure()



if __name__ == "__main__":
    unittest.main()
