#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.


import setpath
import unittest
import os

from bike import testdata
from bike.query.findDefinition import findAllPossibleDefinitionsByCoords, findDefinitionByCoords
from bike.query.getTypeOf import getTypeOf,resolveImportedModuleOrPackage
from bike.parsing.newstuff import getModuleUsingFQN
from bike.testutils import *
        
class TestFindDefinitionByCoords(BRMTestCase):

    def test_findsClassRef(self):
        src=trimLines("""
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

    def tests_findsMethodRef(self):
        src=trimLines("""
        class TheClass:
            def theMethod(self):
                pass
        a = TheClass()
        a.theMethod()
        """)

        createSourceNodeAt(src,"mymodule")
        defn = findDefinitionByCoords(os.path.abspath("mymodule.py"),5,3,[])
        assert defn.filename == os.path.abspath("mymodule.py")
        assert defn.lineno == 2
        assert defn.colno == 8
        assert defn.confidence == 100
        

    def test_returnsOtherMethodsWithSameName(self):
        src=trimLines("""
        class TheClass:
            def theMethod(self):
                pass
        a = SomeOtherClass()
        a.theMethod()
        """)

        createSourceNodeAt(src,"mymodule")
        defn = findAllPossibleDefinitionsByCoords(os.path.abspath("mymodule.py"),5,3,[]).next()
        assert defn.filename == os.path.abspath("mymodule.py")
        assert defn.lineno == 2
        assert defn.colno == 8
        assert defn.confidence == 50




    def test_findsTemporaryDefinition(self):
        src=trimLines("""
        a = 3
        b = a + 1
        """)
        createSourceNodeAt(src,"mymodule")
        defn = findDefinitionByCoords(os.path.abspath("mymodule.py"),2,4,[])
        assert defn.filename == os.path.abspath("mymodule.py")
        assert defn.lineno == 1
        assert defn.colno == 0
        assert defn.confidence == 100

    def test_findsArgumentDefinition(self):
        src=trimLines("""
        def someFunction(a):
            b = a + 1
        """)
        createSourceNodeAt(src,"mymodule")
        defn = findDefinitionByCoords(os.path.abspath("mymodule.py"),2,8,[])
        assert defn.filename == os.path.abspath("mymodule.py")
        assert defn.lineno == 1
        assert defn.colno == 17
        assert defn.confidence == 100

    def test_findsClassInstanceDefinition(self):
        src=trimLines("""
        class TheClass():
            pass
        a = TheClass()
        print a
        """)
        createSourceNodeAt(src,"mymodule")
        defn = findDefinitionByCoords(os.path.abspath("mymodule.py"),4,6,[])
        assert defn.filename == os.path.abspath("mymodule.py")
        assert defn.lineno == 3
        assert defn.colno == 0
        assert defn.confidence == 100

    def test_findsDefinitionInParentScope(self):
        src=trimLines("""
        a = 3
        def foo(self):
            b = a + 1
        """)
        createSourceNodeAt(src,"mymodule")
        defn = findDefinitionByCoords(os.path.abspath("mymodule.py"),3,8,[])
        assert defn.filename == os.path.abspath("mymodule.py")
        assert defn.lineno == 1
        assert defn.colno == 0
        assert defn.confidence == 100

    def test_findsDefinitionWithinFunction(self):
        src=trimLines("""
        def foo(yadda):
            a = someFunction()
            print a
        """)
        createSourceNodeAt(src,"mymodule")
        defn = findDefinitionByCoords(os.path.abspath("mymodule.py"),3,10,[])
        assert defn.filename == os.path.abspath("mymodule.py")
        assert defn.lineno == 2
        assert defn.colno == 4
        assert defn.confidence == 100
        

    def test_findsDefinitionFromSubsequentAssignment(self):
        src=trimLines("""
        def foo(yadda):
            a = 3
            print a
            a = 5
        """)
        createSourceNodeAt(src,"mymodule")
        defn = findDefinitionByCoords(os.path.abspath("mymodule.py"),4,4,[])
        assert defn.filename == os.path.abspath("mymodule.py")
        assert defn.lineno == 2
        assert defn.colno == 4
        assert defn.confidence == 100

    def test_findsDefinitionFromDefinition(self):
        src=trimLines("""
        def foo(yadda):
            a = 3
            print a
            a = 5
        """)
        createSourceNodeAt(src,"mymodule")
        defn = findDefinitionByCoords(os.path.abspath("mymodule.py"),4,4,[])
        assert defn.filename == os.path.abspath("mymodule.py")
        assert defn.lineno == 2
        assert defn.colno == 4
        assert defn.confidence == 100


    def test_findsClassRefUsingFromImportStatement(self):
        src=trimLines("""
        from a.b.bah import TheClass
        """)
        classsrc=trimLines("""
        class TheClass:
            pass
        """)
        root = createSourceNodeAt(src,"a.foo")
        root = createSourceNodeAt(classsrc, "a.b.bah")
        module = getModuleUsingFQN("a.foo",[pkgstructureRootDir])
        filename = os.path.abspath(os.path.join("a","foo.py"))        
        defn = findDefinitionByCoords(filename,1,21,[])
        assert defn.filename == os.path.abspath(os.path.join("a","b","bah.py"))
        assert defn.lineno == 1
        assert defn.colno == 6
        assert defn.confidence == 100


    def test_findsVariableRefUsingFromImportStatement(self):
        importsrc=trimLines("""
        from a.b.bah import mytext
        print mytext
        """)
        src=trimLines("""
        mytext = 'hello'
        """)
        root = createSourceNodeAt(importsrc,"a.foo")
        root = createSourceNodeAt(src, "a.b.bah")
        filename = os.path.abspath(os.path.join("a","foo.py"))        
        defn = findDefinitionByCoords(filename,2,6,[])
        assert defn.filename == os.path.abspath(os.path.join("a","b","bah.py"))
        assert defn.lineno == 1
        assert defn.colno == 0
        assert defn.confidence == 100


    def test_findsVariableRefUsingImportStatement(self):
        importsrc=trimLines("""
        import a.b.bah
        print a.b.bah.mytext
        """)
        src=trimLines("""
        mytext = 'hello'
        """)
        root = createSourceNodeAt(importsrc,"a.foo")
        root = createSourceNodeAt(src, "a.b.bah")
        filename = os.path.abspath(os.path.join("a","foo.py"))        
        defn = findDefinitionByCoords(filename,2,14,[])
        assert defn.filename == os.path.abspath(os.path.join("a","b","bah.py"))
        assert defn.lineno == 1
        assert defn.colno == 0
        assert defn.confidence == 100


    def test_findsVariableRefUsingFromImportStarStatement(self):
        importsrc=trimLines("""
        from a.b.bah import *
        print mytext
        """)
        src=trimLines("""
        mytext = 'hello'
        """)
        createSourceNodeAt(importsrc,"a.foo")
        createSourceNodeAt(src, "a.b.bah")
        filename = os.path.abspath(os.path.join("a","foo.py"))
        defn = findDefinitionByCoords(filename,2,6,[])
        assert defn.filename == os.path.abspath(os.path.join("a","b","bah.py"))
        assert defn.lineno == 1
        assert defn.colno == 0
        assert defn.confidence == 100

    def test_findsVariableRefUsingFromPackageImportModuleStatement(self):
        importsrc=trimLines("""
        from a.b import bah
        print bah.mytext
        """)
        src=trimLines("""
        mytext = 'hello'
        """)
        root = createSourceNodeAt(importsrc,"a.b.foo")
        root = createSourceNodeAt(src, "a.b.bah")
        filename = os.path.abspath(os.path.join("a","b","foo.py"))        
        defn = findDefinitionByCoords(filename,2,10,[])
        assert defn.filename == os.path.abspath(os.path.join("a","b","bah.py"))
        assert defn.lineno == 1
        assert defn.colno == 0
        assert defn.confidence == 100

    def test_findsImportedVariableRefInAFunctionArg(self):
        importsrc=trimLines("""
        from a.b import bah
        someFunction(bah.mytext)
        """)
        src=trimLines("""
        mytext = 'hello'
        """)
        root = createSourceNodeAt(importsrc,"a.b.foo")
        root = createSourceNodeAt(src, "a.b.bah")
        filename = os.path.abspath(os.path.join("a","b","foo.py"))        
        defn = findDefinitionByCoords(filename,2,17,[])
        assert defn.filename == os.path.abspath(os.path.join("a","b","bah.py"))
        assert defn.lineno == 1
        assert defn.colno == 0
        assert defn.confidence == 100


    def test_findsVariableRefUsingFromImportStatementInFunction(self):
        importsrc=trimLines("""
        def foo():
            from a.b.bah import mytext
            print mytext
        """)
        src=trimLines("""
        mytext = 'hello'
        """)
        root = createSourceNodeAt(importsrc,"a.foo")
        root = createSourceNodeAt(src, "a.b.bah")
        filename = os.path.abspath(os.path.join("a","foo.py"))        
        defn = findDefinitionByCoords(filename,3,10,[])
        assert defn.filename == os.path.abspath(os.path.join("a","b","bah.py"))
        assert defn.lineno == 1
        assert defn.colno == 0
        assert defn.confidence == 100

    def test_findsVariableRefByImportingModule(self):
        importsrc=trimLines("""
        import a.b.bah
        print a.b.bah.mytext
        """)
        src=trimLines("""
        mytext = 'hello'
        """)
        createSourceNodeAt(importsrc,"a.foo")
        createSourceNodeAt(src,"a.b.bah")
        defn = findDefinitionByCoords(pkgstructureFile1,2,14,[])
        assert defn.filename == pkgstructureFile2
        assert defn.lineno == 1
        assert defn.colno == 0
        assert defn.confidence == 100


    def test_findsVariableRefByImportingModuleWithFrom(self):
        importsrc=trimLines("""
        from a.b import bah
        someFunction(bah.mytext)
        """)
        src=trimLines("""
        mytext = 'hello'
        """)
        createSourceNodeAt(importsrc,"a.foo")
        createSourceNodeAt(src,"a.b.bah")
        defn = findDefinitionByCoords(pkgstructureFile1,2,17,[])
        assert defn.filename == pkgstructureFile2
        assert defn.lineno == 1
        assert defn.colno == 0
        assert defn.confidence == 100



    def test_doesntfindVariableRefOfUnimportedModule(self):
        importsrc=trimLines("""
        # a.b.bah not imported
        print a.b.bah.mytext
        """)
        src=trimLines("""
        mytext = 'hello'
        """)
        root = createSourceNodeAt(importsrc,"a.b.foo")
        root = createSourceNodeAt(src, "a.b.bah")
        filename = os.path.abspath(os.path.join("a","b","foo.py"))        
        defn = findDefinitionByCoords(filename,2,14,[])
        self.assertEqual(None,defn)

    def test_findsVariableImportedViaChildThingy(self):
        importsrc=trimLines("""
        import a
        print a.b.bah.mytext
        """)
        src=trimLines("""
        mytext = 'hello'
        """)
        root = createSourceNodeAt(importsrc,"a.b.foo")
        root = createSourceNodeAt(src, "a.b.bah")
        filename = os.path.abspath(os.path.join("a","b","foo.py"))        
        defn = findDefinitionByCoords(filename,2,14,[])
        self.assertEqual(pkgstructureFile2,defn.filename)
        self.assertEqual(1,defn.lineno)
        self.assertEqual(0,defn.colno)

    def test_findsSelfAttributeDefinition(self):
        src=trimLines("""
        class MyClass:
           def __init__(self):
               self.a = 'hello'
           def myMethod(self):
               print self.a
        """)
        root = createSourceNodeAt(src,"mymodule")
        filename = os.path.abspath("mymodule.py")
        defn = findDefinitionByCoords(filename,5,18)
        assert defn.filename == os.path.abspath("mymodule.py")
        assert defn.lineno == 3
        assert defn.colno == 12
        assert defn.confidence == 100

    def test_findsSelfAttributeDefinitionFromSamePlace(self):
        src=trimLines("""
        class MyClass:
           def __init__(self):
               self.a = 'hello'
           def myMethod(self):
               print self.a
        """)
        root = createSourceNodeAt(src,"mymodule")
        filename = os.path.abspath("mymodule.py")
        defn = findDefinitionByCoords(filename,3,12,[])
        assert defn.filename == os.path.abspath("mymodule.py")
        assert defn.lineno == 3
        assert defn.colno == 12
        assert defn.confidence == 100


    def test_findsSelfAttributeDefinition(self):
        src=trimLines("""
        class MyClass:
            def someOtherFn(self):
                pass
            def load(self, source):
                # fastparser ast
                self.fastparseroot = fastparser(source,self.modulename)
        """)
        root = createSourceNodeAt(src,"mymodule")
        filename = os.path.abspath("mymodule.py")
        defn = findDefinitionByCoords(filename,6,14,[])
        assert defn.filename == os.path.abspath("mymodule.py")
        assert defn.lineno == 6
        assert defn.colno == 13
        assert defn.confidence == 100


    def test_findsDefnOfInnerClass(self):
        src = trimLines("""
        class TheClass:
            class TheClass:
                pass
        a = TheClass.TheClass()
        """)
        root = createSourceNodeAt(src,"mymodule")
        filename = os.path.abspath("mymodule.py")
        defn = findDefinitionByCoords(filename,4,14,[])
        assert defn.filename == os.path.abspath("mymodule.py")
        assert defn.lineno == 2
        assert defn.colno == 10
        assert defn.confidence == 100

    def test_findsDefnOfOuterClass(self):
        src = trimLines("""
        class TheClass:
            class TheClass:
                pass
        a = TheClass.TheClass()
        """)
        root = createSourceNodeAt(src,"mymodule")
        filename = os.path.abspath("mymodule.py")
        defn = findDefinitionByCoords(filename,4,4,[])
        assert defn.filename == os.path.abspath("mymodule.py")
        assert defn.lineno == 1
        assert defn.colno == 6
        assert defn.confidence == 100


    def test_findsDefnOfFunctionNamedSameAsMethod(self):
        src = trimLines("""
        def theFunction():
            pass
        
        class TheClass:
            def theFunction(self):
                theFunction()
        """)
        root = createSourceNodeAt(src,"mymodule")
        filename = os.path.abspath("mymodule.py")
        defn = findDefinitionByCoords(filename,6,8,[])
        assert defn.filename == os.path.abspath("mymodule.py")
        assert defn.lineno == 1
        assert defn.colno == 4
        assert defn.confidence == 100


    def test_findsClassDeclaredIn__init__Module(self):
        importsrc=trimLines("""
        class TheClass:
            pass
        """)
        src=trimLines("""
        from a import TheClass
        c = TheClass()
        """)

        root = createSourceNodeAt(importsrc,"a.__init__")
        root = createSourceNodeAt(src, "mymodule")
        filename = os.path.abspath("mymodule.py")
        defn = findDefinitionByCoords(filename,2,6,[])
        assert defn.filename == os.path.abspath(os.path.join("a",
                                                                "__init__.py"))
        assert defn.lineno == 1
        assert defn.colno == 6
        assert defn.confidence == 100


    def test_findsClassDefinitionWhenHasNestedClassOfSameName(self):
        src = trimLines("""
        class TheClass:
            class TheClass:
                pass
        """)        
        root = createSourceNodeAt(src, "mymodule")
        defn = findDefinitionByCoords("mymodule.py",1,6,[])
        self.assertEqual(defn.filename,os.path.join(tmproot,"mymodule.py"))
        self.assertEqual(defn.lineno,1)
        self.assertEqual(defn.colno,6)
        self.assertEqual(defn.confidence,100)

    def test_findsDefinitionOfKeywordArgUsageAsItself(self):
        src = trimLines("""
        def foo(a=None):
            bar(a=a)
        """)        
        root = createSourceNodeAt(src, "mymodule")
        defn = findDefinitionByCoords("mymodule.py",2,8,[])
        self.assertEqual(defn.filename,os.path.join(tmproot,"mymodule.py"))
        self.assertEqual(defn.lineno,2)
        self.assertEqual(defn.colno,8)
        self.assertEqual(defn.confidence,100)
        


    def test_findsDefinitionOfDefaultArgument(self):
        src=trimLines("""
        a = 'hello'
        def amethod(a=a):
            pass
        """)
        root = createSourceNodeAt(src, "mymodule")
        defn = findDefinitionByCoords("mymodule.py",2,14,[])
        self.assertEqual(defn.filename,os.path.join(tmproot,"mymodule.py"))
        self.assertEqual(defn.lineno,1)
        self.assertEqual(defn.colno,0)
        self.assertEqual(defn.confidence,100)
        

    def test_findsArgumentDefinitionFromItself(self):
        src=trimLines("""
        def someFunction(a):
            pass
        """)
        createSourceNodeAt(src,"mymodule")
        defn = findDefinitionByCoords(os.path.abspath("mymodule.py"),1,17,[])
        assert defn.filename == os.path.abspath("mymodule.py")
        assert defn.lineno == 1
        assert defn.colno == 17
        assert defn.confidence == 100


    def test_findsMethodInBaseClass(self):
        src=trimLines("""
        class a:
            def foo(self): pass

        class b(a):
            pass
        
        inst = b()
        inst.foo()
        """)
        createSourceNodeAt(src,"mymodule")
        defn = findDefinitionByCoords(os.path.abspath("mymodule.py"),8,5,[])
        assert defn.filename == os.path.abspath("mymodule.py")
        assert defn.lineno == 2
        assert defn.colno == 8
        assert defn.confidence == 100



    def findsDefnOfFunctionGivenItself(self):
        src=trimLines("""
        def myfunction():
            pass
        """)
        root = createSourceNodeAt(src, "mymodule")
        defn = findDefinitionByCoords("mymodule.py",1,6,[])
        self.assertEqual(defn.filename,os.path.join(tmproot,"mymodule.py"))
        self.assertEqual(defn.lineno,1)
        self.assertEqual(defn.colno,4)
        self.assertEqual(defn.confidence,100)
        



class TestFindDefinitionUsingFiles(BRMTestCase):
    def test_findsASimpleDefinitionUsingFiles(self):
        src=trimLines("""
        class TheClass:
            pass
        a = TheClass()
        """)
        writeTmpTestFile(src)
        defn = findDefinitionByCoords(tmpfile,3,6,[])
        assert defn.filename == tmpfile
        assert defn.lineno == 1
        assert defn.colno == 6
        assert defn.confidence == 100


    def test_findsDefinitionInAnotherModuleUsingFiles(self):
        src=trimLines("""
        from a.b.bah import TheClass
        """)
        classsrc=trimLines("""
        class TheClass:
            pass
        """)
        createSourceNodeAt(src,"a.foo")
        createSourceNodeAt(classsrc,"a.b.bah")
        defn = findDefinitionByCoords(pkgstructureFile1,1,21,[])
        assert defn.filename == pkgstructureFile2
        assert defn.lineno == 1
        assert defn.colno == 6
        assert defn.confidence == 100



    def test_findsDefinitionInAnotherRelativeModuleUsingFiles(self):
        src=trimLines("""
        from b.bah import TheClass
        """)
        classsrc=trimLines("""
        class TheClass:
            pass
        """)
        createSourceNodeAt(src,"a.foo")
        createSourceNodeAt(classsrc,"a.b.bah")
        defn = findDefinitionByCoords(pkgstructureFile1,1,21,[])
        assert defn.filename == pkgstructureFile2
        assert defn.lineno == 1
        assert defn.colno == 6
        assert defn.confidence == 100

    def test_findsMethodDefinitionInAnotherModuleUsingFiles(self):
        src=trimLines("""
        from b.bah import TheClass
        a = TheClass()
        a.theMethod()
        """)
        classsrc=trimLines("""
        class TheClass:
            def theMethod(self):
                pass
        """)
        createSourceNodeAt(src,"a.foo")
        createSourceNodeAt(classsrc,"a.b.bah")
        defn = findDefinitionByCoords(pkgstructureFile1,3,2,[])
        assert defn.filename == pkgstructureFile2
        assert defn.lineno == 2
        assert defn.colno == 8
        assert defn.confidence == 100

    def test_findsDefinitonOfMethodWhenUseIsOnAMultiLine(self):
        classsrc=trimLines("""
        class TheClass:
            def theMethod(self):
                pass
        """)
        src=trimLines("""
        from b.bah import TheClass
        a = TheClass()
        i,j = (32,
               a.theMethod())  # <--- find me!
        something=somethingelse
        """)
        createSourceNodeAt(src,"a.foo")
        createSourceNodeAt(classsrc,"a.b.bah")
        defn = findDefinitionByCoords(pkgstructureFile1,4,9,[])
        assert defn.filename == pkgstructureFile2
        assert defn.lineno == 2
        assert defn.colno == 8
        assert defn.confidence == 100


    def test_findsDefinitionWhenUseIsOnAMultilineAndNextLineBalancesBrace(self):
        classsrc=trimLines("""
        class TheClass:
            def theMethod(self):
                pass
        """)
        src=trimLines("""
        from b.bah import TheClass
        c = TheClass()
        f1, f2 = (c.func1, 
                c.theMethod)
        f1, f2 = (c.func1, 
                c.theMethod)
        """)
        createSourceNodeAt(src,"a.foo")
        createSourceNodeAt(classsrc,"a.b.bah")
        defn = findDefinitionByCoords(pkgstructureFile1,4,10,[])
        self.assertEqual(pkgstructureFile2,defn.filename)
        self.assertEqual(2,defn.lineno)
        self.assertEqual(8,defn.colno)
        self.assertEqual(100,defn.confidence)

    def test_worksIfFindingDefnOfRefInSlashMultiline(self):
        classsrc=trimLines("""
        class TheClass:
            def theMethod(self):
                pass
        """)
        src=trimLines("""
        from b.bah import TheClass
        c = TheClass()
        f1, f2 = c.func1 \\
               ,c.theMethod
        """)
        createSourceNodeAt(src,"a.foo")
        createSourceNodeAt(classsrc,"a.b.bah")
        defn = findDefinitionByCoords(pkgstructureFile1,4,10,[])
        self.assertEqual(pkgstructureFile2,defn.filename)
        self.assertEqual(2,defn.lineno)
        self.assertEqual(8,defn.colno)
        self.assertEqual(100,defn.confidence)

    def test_findsDefnInSameNonPackageDirectory(self):
        try:
            classsrc = trimLines("""
            def testFunction():
                print 'hello'
            """)
            src = trimLines("""
            from baz import testFunction
            """)
            writeTmpTestFile(src)
            newtmpfile = os.path.join(tmproot,"baz.py")
            writeFile(newtmpfile, classsrc)
            defn = findDefinitionByCoords(tmpfile,1,16,[])
            assert defn.filename == newtmpfile
            assert defn.lineno == 1
        finally:
            os.remove(newtmpfile)
            deleteTmpTestFile()
            

    def test_findsDefnInPackageSubDirectoryAndRootNotInPath(self):
        src=trimLines("""
        from b.bah import TheClass
        """)
        classsrc=trimLines("""
        class TheClass:
            def theMethod(self):
                pass
        """)
        createSourceNodeAt(src,"a.foo")
        createSourceNodeAt(classsrc,"a.b.bah")
        defn = findDefinitionByCoords(pkgstructureFile1,1,18,[])
        assert defn.filename == pkgstructureFile2
        assert defn.lineno == 1
        assert defn.colno == 6
        assert defn.confidence == 100

    def test_findsDefnInSamePackageHierarchyAndRootNotInPath(self):
        src=trimLines("""
        from a.b.bah import TheClass
        """)
        classsrc=trimLines("""
        class TheClass:
            def theMethod(self):
                pass
        """)
        createSourceNodeAt(src,"a.foo")
        createSourceNodeAt(classsrc,"a.b.bah")
        defn = findDefinitionByCoords(pkgstructureFile1,1,20,[])
        assert defn.filename == pkgstructureFile2
        assert defn.lineno == 1
        assert defn.colno == 6
        assert defn.confidence == 100


if __name__ == "__main__":
    unittest.main()
