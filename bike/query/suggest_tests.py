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
from suggest import *


class suggestTests:

    def __teardown__(self):
        self.t.remove()
    
    def generates_a_list_of_options_for_foo(self):
        self.t = TestPackageStructure()        
        src=dedent("""
        class TheClass:
            def bah(self):pass
            def baz(self):pass
        f = TheClass()
        f.
        """)
        fname = self.t.create_module("foo",src)
        l = [l for l in suggest(fname,6,2,[])]
        assert_equal(('bah','def bah(self):pass'),l[0])
        assert_equal(('baz','def baz(self):pass'),l[1])
