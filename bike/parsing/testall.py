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

#import all the tests
from test_load import *
from test_newstuff import *
from test_parserutils import *
from test_fastparser import *
from test_fastparserast import *

if __name__ == "__main__":
    from bike import logging
    logging.init()
    log = logging.getLogger("bike")
    log.setLevel(logging.WARN)
    unittest.main()

