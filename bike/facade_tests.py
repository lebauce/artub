# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.



from protest.assertions import *
from protest.test import TestPackageStructure
from textwrap import dedent
import bike
from testutils import trimLines

class FacadeTests:
    """
    Provides the client interface for the bicyclerepairman functionality.
    Returned by bike.init()
    """

    def __init__(self):
        self.packagestructure = TestPackageStructure()

    def __teardown__(self):
        self.packagestructure.remove()


    def provides_a_callback_mechanism_for_prompting_the_user_if_it_cant_work_out_whether_to_rename_a_variable(self):

        def mycallback(filename, line, colstart, colend):
            return True

        srcBefore=dedent("""
        class TheClass:
            def theMethod(self): pass
        dontKnowTheTypeOfThisVariable =  someMagicFunction()
        dontKnowTheTypeOfThisVariable.theMethod()
        """)
        srcAfter=dedent("""
        class TheClass:
            def newName(self): pass
        dontKnowTheTypeOfThisVariable =  someMagicFunction()
        dontKnowTheTypeOfThisVariable.newName()
        """)
        fname = self.packagestructure.create_module("foo",srcBefore)
        ctx = bike.init()
        ctx.setRenameMethodPromptCallback(mycallback)
        ctx.rename(fname,3,8,"newName")
        ctx.save()
        assert_equal(srcAfter,file(fname).read())


    def can_perform_the_extract_method_refactoring(self):
        srcBefore=trimLines("""
        class MyClass:
            def myMethod(self):
                pass
        """)

        srcAfter=trimLines("""
        class MyClass:
            def myMethod(self):
                self.newMethod()

            def newMethod(self):
                pass
        """)

        fname = self.packagestructure.create_module("foo",srcBefore)
        ctx = bike.init()
        ctx.extractMethod(fname,3,8,3,12,"newMethod")
        ctx.save()
        assert_equal(srcAfter,file(fname).read())
        #ctx.undo()
        #ctx.save()
        #self.assertEqual(readTmpTestFile(),srcBefore)
