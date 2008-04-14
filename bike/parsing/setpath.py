# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

import sys,os
if not os.path.abspath("../..") in sys.path:
    from bike import log
    print >> log.warning, "Appending to the system path. This should only happen in unit tests"
    sys.path.append(os.path.abspath("../.."))
