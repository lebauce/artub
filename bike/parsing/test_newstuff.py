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
import os,sys
import unittest
from bike.testutils import *
from bike.parsing.newstuff import getModuleUsingFQN,\
     generateModuleFilenamesInPythonPath, getSourceNodesContainingRegex,\
     generatePackageDependencies
     

class TestGetModuleUsingFQN(BRMTestCase):
    def test_worksForFullPath(self):
        try:
            createPackageStructure("pass","pass")
            self.assertEqual(pkgstructureFile2,
                             getModuleUsingFQN("a.b.bah",[pkgstructureRootDir]).filename)
        finally:
            removePackageStructure()
        
    def test_worksForPackageInitFile(self):
        try:
            createPackageStructure("pass","pass")
            self.assertEqual(getModuleUsingFQN("a.b",[pkgstructureRootDir]).filename,
                             os.path.join(pkgstructureChilddir,"__init__.py"))
        finally:
            removePackageStructure()


class TestGenerateModuleFilenamesInPythonPath(BRMTestCase):
    def test_works(self):
        try:
            createPackageStructure("pass","pass")
            fnames = [f for f in \
                 generateModuleFilenamesInPythonPath(pkgstructureFile2,[])]

            assert os.path.join(pkgstructureBasedir,"__init__.py") in fnames
            assert pkgstructureFile1 in fnames
            assert os.path.join(pkgstructureChilddir,"__init__.py") in fnames
            assert pkgstructureFile2 in fnames
            assert len(fnames) == 5
        finally:
            removePackageStructure()

        

    def test_doesntTraverseIntoNonPackages(self):
        try:
            createPackageStructure("pass","pass")
            nonPkgDir = os.path.join(pkgstructureChilddir,"c")
            newfile = os.path.join(nonPkgDir,"baz.py")
            # N.B. don't put an __init__.py in it, so isnt a package
            os.makedirs(nonPkgDir)
            writeFile(newfile,"pass")
            fnames = [f for f in \
                 generateModuleFilenamesInPythonPath(pkgstructureFile2,[])]
            assert newfile not in fnames
        finally:
            #os.remove(initfile)
            os.remove(newfile)
            os.removedirs(nonPkgDir)
            removePackageStructure()


    def test_doesScanFilesInTheRootDirectory(self):
        try:
            createPackageStructure("pass","pass","pass")
            fnames = [f for f in \
                 generateModuleFilenamesInPythonPath(pkgstructureFile2,[])]
            assert pkgstructureFile0 in fnames
        finally:
            #os.remove(initfile)
            removePackageStructure()

    def test_returnsOtherFilesInSameNonPackageDirectory(self):
        try:
            writeTmpTestFile("")
            newtmpfile = os.path.join(tmproot,"baz.py")
            writeFile(newtmpfile, "")
            fnames = [f for f in \
                      generateModuleFilenamesInPythonPath(tmpfile,[])]
            assert newtmpfile in fnames
        finally:
            os.remove(newtmpfile)
            deleteTmpTestFile()
            


    def test_doesntTraverseIntoNonPackagesUnderRoot(self):
        try:
            os.makedirs(pkgstructureBasedir)
            writeFile(pkgstructureFile1,"pass")
            fnames = [f for f in \
                      generateModuleFilenamesInPythonPath(pkgstructureFile2,[])]
            assert pkgstructureFile1 not in fnames
        finally:
            os.remove(pkgstructureFile1)
            os.removedirs(pkgstructureBasedir)


    def test_doesntGenerateFilenamesMoreThanOnce(self):
        try:
            createPackageStructure("pass","pass")
            newfile = os.path.join(pkgstructureChilddir,"baz.py")
            writeFile(newfile,"pass")
            fnames = [f for f in \
                generateModuleFilenamesInPythonPath(pkgstructureFile2,[])]
            matched = [f for f in fnames if f == newfile]
            self.assertEqual(1, len(matched))
        finally:
            os.remove(newfile)
            removePackageStructure()

class TestGetSourceNodesContainingRegex(BRMTestCase):
    def test_works(self):
        try:
            createPackageStructure("# testregexfoobah","pass")
            srcfiles = [s for s in 
                        getSourceNodesContainingRegex("testregexfoobah",
                                                      pkgstructureFile2,[])]
            self.assertEqual(pkgstructureFile1,srcfiles[0].filename)
        finally:
            removePackageStructure()

class TestGenerateModuleFilenamesInPythonPath2(BRMTestCase):
    def test_getsAllFilenamesInSameHierarchyAsContextFile(self):
        try:
            createPackageStructure("","")
            fnames = [f for f in
                      generateModuleFilenamesInPythonPath(pkgstructureFile1,[])]
            self.assert_(pkgstructureFile0 in fnames)
            self.assert_(pkgstructureFile1 in fnames)
            self.assert_(pkgstructureFile2 in fnames)
        finally:
            removePackageStructure()

    def test_getsFilenamesInSubPackagesIfCtxFilenameIsInTheRoot(self):
        try:
            createPackageStructure("","")
            fnames = [f for f in
                      generateModuleFilenamesInPythonPath(pkgstructureFile0,[])]
            self.assert_(pkgstructureFile1 in fnames)
            self.assert_(pkgstructureFile2 in fnames)
        finally:
            removePackageStructure()

    def test_doesntTraverseOtherPackagesOffOfTheRoot(self):
        try:
            createPackageStructure("","")
            os.makedirs(os.path.join(pkgstructureRootDir, "c"))
            writeFile(os.path.join(pkgstructureRootDir, "c", "__init__.py"), "# ")
            bazfile = os.path.join(pkgstructureRootDir, "c", "baz.py")
            writeFile(bazfile, "pass")
            fnames = [f for f in
                      generateModuleFilenamesInPythonPath(pkgstructureFile1,[])]
            self.assert_(pkgstructureFile0 in fnames)
            self.assert_(pkgstructureFile1 in fnames)
            self.assert_(pkgstructureFile2 in fnames)
            self.assert_(bazfile not in fnames)
        finally:
            os.remove(os.path.join(pkgstructureRootDir, "c", "baz.py"))
            os.remove(os.path.join(pkgstructureRootDir, "c", "__init__.py"))
            os.removedirs(os.path.join(pkgstructureRootDir, "c"))
            removePackageStructure()


class TestGetPackageDependencies(BRMTestCase):

    def test_followsImportModule(self):
        try:
            createPackageStructure("","import c.bing")
            createSecondPackageStructure("")
            dependencies = [d for d in
                            generatePackageDependencies(pkgstructureFile2,
                                                        [pkgstructureRootDir])]
            self.assertEqual([pkgstructureBasedir2],dependencies)
        finally:
            removeSecondPackageStructure()
            removePackageStructure()


    def test_followsFromImportPackage(self):
        try:
            createPackageStructure("","import c")
            createSecondPackageStructure("")
            dependencies = [d for d in
                            generatePackageDependencies(pkgstructureFile2,
                                                        [pkgstructureRootDir])]
            self.assertEqual([pkgstructureBasedir2],dependencies)
        finally:
            removeSecondPackageStructure()
            removePackageStructure()



    def test_followsFromImportStar(self):
        try:
            createPackageStructure("","from c import *")
            createSecondPackageStructure("")
            dependencies = [d for d in
                            generatePackageDependencies(pkgstructureFile2,
                                                        [pkgstructureRootDir])]
            self.assertEqual([pkgstructureBasedir2],dependencies)
        finally:
            removeSecondPackageStructure()
            removePackageStructure()

    def test_followsFromImportModule(self):
        try:
            createPackageStructure("","from c import bing")
            createSecondPackageStructure("")
            dependencies = [d for d in
                            generatePackageDependencies(pkgstructureFile2,
                                                        [pkgstructureRootDir])]
            self.assertEqual([pkgstructureBasedir2],dependencies)
        finally:
            removeSecondPackageStructure()
            removePackageStructure()


    def test_doesntBreakIfImportIsInAMultilineString(self):
        try:
            createPackageStructure("",trimLines("""
            '''
            from aoeuaoeu import aocxaoieicxoe
            '''
            """))
            createSecondPackageStructure("")
            dependencies = [d for d in
                            generatePackageDependencies(pkgstructureFile2,
                                                        [pkgstructureRootDir])]
            self.assertEqual([],dependencies)
        finally:
            removeSecondPackageStructure()
            removePackageStructure()

    def test_doesntBreakIfImportIsCommented(self):
        try:
            createPackageStructure("","#from aoeuaoeu import aocxaoieicxoe")
            createSecondPackageStructure("")
            dependencies = [d for d in
                            generatePackageDependencies(pkgstructureFile2,
                                                        [pkgstructureRootDir])]
            self.assertEqual([],dependencies)
        finally:
            removeSecondPackageStructure()
            removePackageStructure()


    def test_doesntBreakIfCantFindImport(self):
        try:
            createPackageStructure("","from aoeuaoeu import aocxaoieicxoe")
            createSecondPackageStructure("")
            dependencies = [d for d in
                            generatePackageDependencies(pkgstructureFile2,
                                                        [pkgstructureRootDir])]
            self.assertEqual([],dependencies)
        finally:
            removeSecondPackageStructure()
            removePackageStructure()


    def test_doesntIncludeCurrentPackage(self):
        try:
            createPackageStructure("","import a.foo")
            createSecondPackageStructure("")
            dependencies = [d for d in
                            generatePackageDependencies(pkgstructureFile2,
                                                        [pkgstructureRootDir])]
            self.assertEqual([],dependencies)
        finally:
            removeSecondPackageStructure()
            removePackageStructure()




if __name__ == "__main__":
    unittest.main()
