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
from bike import testdata
from bike.testutils import *
from bike.query.getTypeOf import getTypeOf, \
     attemptToConvertGetattrToFqn
from bike.parsing.fastparserast import Class, Function, Instance
from bike.parsing.newstuff import getModuleUsingFQN
from compiler.ast import Getattr,CallFunc,Name

class TestGetTypeOf(BRMTestCase):
    def test_getsTypeOfSimpleClassInstanceReference(self):
        src = trimLines("""
        from b.bah import TheClass
        a = TheClass()
        a.theMethod()
        """)
        root = createSourceNodeAt(src,"a.foo")
        root = createSourceNodeAt(testdata.TheClass, "a.b.bah")
        module = getModuleUsingFQN("a.foo",[pkgstructureRootDir])
        res =  getTypeOf(module,"a",[pkgstructureRootDir])
        assert isinstance(res,Instance)
        assert isinstance(res.getType(),Class)
        assert res.getType().name == "TheClass"

    def test_getsTypeOfImportedClassReference(self):
        src = trimLines("""
        import b.bah
        a = b.bah.TheClass()
        """)
        root = createSourceNodeAt(src,"a.foo")
        root = createSourceNodeAt(testdata.TheClass, "a.b.bah")
        module = getModuleUsingFQN("a.foo",[pkgstructureRootDir])
        res =  getTypeOf(module,"a",[pkgstructureRootDir])
        assert isinstance(res,Instance)
        assert isinstance(res.getType(),Class)
        assert res.getType().name == "TheClass"

    def test_getsTypeOfClassReferenceFromImportedPackage(self):
        src = trimLines("""
        import b.bah
        a = b.bah.TheClass()
        """)
        root = createSourceNodeAt(src,"a.foo")
        root = createSourceNodeAt(testdata.TheClass, "a.b.bah")
        module = getModuleUsingFQN("a.foo",[pkgstructureRootDir])
        res =  getTypeOf(module,"a",[pkgstructureRootDir])
        assert isinstance(res,Instance)
        assert isinstance(res.getType(),Class)
        assert res.getType().name == "TheClass"

    def test_getsTypeOfInstanceThatIsAnAttributeOfSelf(self):
        src = trimLines("""
        class TheClass:
            def theMethod(self):
                pass
        
        class AnotherClass:
            def __init__(self):
                self.a = TheClass()
            def anotherFn(self):
                self.a.theMethod()
        """)
        root = createSourceNodeAt(src,"a.foo")
        module = getModuleUsingFQN('a.foo',[pkgstructureRootDir])
        theclass = getTypeOf(module,"TheClass",[pkgstructureRootDir])
        fn = getTypeOf(module,"AnotherClass.anotherFn",[pkgstructureRootDir])
        self.assertEqual("TheClass",getTypeOf(fn,"self.a",[pkgstructureRootDir]).getType().name)
        #self.assertEqual(getTypeOf(fn,"self.a").getType(), theclass)
        
        

    def test_doesntGetTypeDefinedInChildFunction(self):
        src = trimLines("""
        from b.bah import TheClass
        a = AnotherClass()
        def foo():
            a = TheClass()
        a.theMethod()
        """)
        root = createSourceNodeAt(src,"a.foo")
        root = createSourceNodeAt(testdata.TheClass, "a.b.bah")
        
        themodule = getModuleUsingFQN("a.foo",[pkgstructureRootDir])
        assert getTypeOf(themodule,"a",[pkgstructureRootDir]) is None
    

    def test_getsTypeOfClassReferencedViaAlias(self):
        src = trimLines("""
        from b.bah import TheClass as FooBah
        FooBah()
        """)
        root = createSourceNodeAt(src,"a.foo")
        root = createSourceNodeAt(testdata.TheClass, "a.b.bah")
        themodule = getModuleUsingFQN("a.foo",[pkgstructureRootDir])
        self.assertEqual(getTypeOf(themodule,"FooBah",[pkgstructureRootDir]).name,"TheClass")
        self.assertEqual(getTypeOf(themodule,"FooBah",[pkgstructureRootDir]).filename,
                         os.path.abspath(os.path.join("a","b","bah.py")))
        

    def test_getsTypeOfClassImportedFromPackageInitFile(self):
        initfile = trimLines("""
        from bah import TheClass
        """)
        src = trimLines("""
        from a import b
        b.TheClass()
        """)
        createSourceNodeAt(src,"a.foo")
        createSourceNodeAt(testdata.TheClass, "a.b.bah")
        createSourceNodeAt(initfile,"a.b.__init__")
        themodule = getModuleUsingFQN("a.foo",[pkgstructureRootDir])
        self.assertEqual(getTypeOf(themodule,"b.TheClass",[pkgstructureRootDir]).name,"TheClass")
        self.assertEqual(getTypeOf(themodule,"b.TheClass",[pkgstructureRootDir]).filename,
                         os.path.abspath(os.path.join("a","b","bah.py")))


    def test_attemptToConvertGetattrToFqn_returnsNoneIfFails(self):
        ast = Getattr(CallFunc(Name("foo"),[],[],[]),"hello")
        assert attemptToConvertGetattrToFqn(ast) is None

    def test_attemptToConvertGetattrToFqn_works(self):
        ast = Getattr(Getattr(Name("foo"),"bah"),"hello")
        assert attemptToConvertGetattrToFqn(ast) == "foo.bah.hello"

    
    def test_handlesRecursionProblem(self):
        src = trimLines("""
        def fn(root):
            node = root
            node = node.getPackage('something')
        """)
        root = createSourceNodeAt(src,"a.foo")
        m = getModuleUsingFQN("a.foo",[pkgstructureRootDir])
        fn = getTypeOf(m,"fn",[pkgstructureRootDir])
        getTypeOf(fn,"node",[pkgstructureRootDir])   # stack overflow!


    def test_doesntGotIntoRecursiveLoopWhenEvaluatingARecursiveFunction(self):
        src = trimLines("""
        def fn(v):
            if v < 45:
                return fn(root+1)
        val = fn(3)
        """)
        root = createSourceNodeAt(src,"a.foo")
        mod = getModuleUsingFQN("a.foo",[pkgstructureRootDir])
        getTypeOf(mod,"val",[pkgstructureRootDir])   # stack overflow!

    def test_getsModuleImportedWithFrom(self):
        importsrc=trimLines("""
        from a.b import bah
        """)
        src=trimLines("""
        mytext = 'hello'
        """)        
        type = self.helper(importsrc,src,'bah')
        self.assertEqual(pkgstructureFile2,type.filename)

    def helper(self,importsrc,src,name):
        try:
            createPackageStructure(importsrc,src)
            from bike.parsing.newstuff import getModule
            scope = getModule(pkgstructureFile1)
            return getTypeOf(scope,name,[pkgstructureRootDir])
        finally:
            removePackageStructure()
    

    def test_getsTypeOfClassImportedAsAlias(self):
        importsrc = trimLines("""
        from b.bah import TheClass as MyTheClass
        
        def foo():
            a = MyTheClass()
            a.theMethod()
        """)
        src=trimLines("""
        class TheClass:
            def theMethod(self):
                pass
        """)
        type = self.helper(importsrc,src,'MyTheClass')
        self.assertEqual("TheClass",type.name)


        
if __name__ == "__main__":
    unittest.main()
