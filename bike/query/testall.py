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

from test_common import *
from test_getReferencesToClass import *
from test_getReferencesToMethod import *
#from test_getReferencesToModule import *
from test_findDefinition import *
from test_findReferences import *
from test_relationships import *
from test_getTypeOf import *

if __name__ == "__main__":
    unittest.main()
