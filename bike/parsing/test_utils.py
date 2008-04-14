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
from utils import *

class Test_CarCdrEtc(unittest.TestCase):
    def test_carReturnsTheFirstElementOfTheFqn(self):
        fqn = "apple.pear.foo"
        assert fqn_car(fqn) == "apple"
        
    def test_carReturnsElementInOneElementFqn(self):
        fqn = "apple"
        assert fqn_car(fqn) == "apple"

    def test_cdrReturnsTheAllElementsOfTheFqnExceptFirst(self):
        fqn = "apple.pear.foo"
        assert fqn_cdr(fqn) == "pear.foo"
        
    def test_cdrReturnsEmptyStringForOneElementFqn(self):
        fqn = "apple"
        assert fqn_cdr(fqn) == ""

    def test_rcarReturnsTheLastElementOfTheFqn(self):
        fqn = "apple.pear.foo"
        assert fqn_rcar(fqn) == "foo"
        
    def test_rcarReturnsElementInOneElementFqn(self):
        fqn = "apple"
        assert fqn_rcar(fqn) == "apple"

    def test_rdrReturnsTheAllElementsOfTheFqnExceptLast(self):
        fqn = "apple.pear.foo"
        assert fqn_rcdr(fqn) == "apple.pear"
        
    def test_rdrReturnsEmptyStringForOneElementFqn(self):
        fqn = "apple"
        assert fqn_rcdr(fqn) == ""


if __name__ == "__main__":
    unittest.main()
