# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

import re

def getLineSeperator(line):
    if line.endswith("\r\n"):
        linesep = "\r\n"          # windoze
    else:
        linesep = line[-1]   # mac or unix
    return linesep


def getTabWidthOfLine(line):
    match = re.match("\s+",line)
    if match is None:
        return 0
    else:
        return match.end(0)

def reverseCoordsIfWrongWayRound(startcoords,endcoords):
    if(startcoords.line > endcoords.line) or \
         (startcoords.line == endcoords.line and \
          startcoords.column > endcoords.column):
        return endcoords,startcoords
    else:
        return startcoords,endcoords
