# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

# queries to do with module/class/function relationships
from bike.globals import *
from getTypeOf import getTypeOf, getTypeOfExpr
from bike.parsing.newstuff import generateModuleFilenamesInPythonPath, generateModuleFilenamesInPackage
from bike.parsing.pathutils import getPackageBaseDirectory
from bike.query.common import walkLinesContainingStrings, getScopeForLine
from bike import log
from bike.parsing.fastparserast import Module
import re

def getRootClassesOfHierarchy(klass,pythonpath):
    if klass is None:  # i.e. dont have base class in our ast
        return None
    if klass.getBaseClassNames() == []:  # i.e. is a root class
        return [klass]
    else:
        rootclasses = []
        for base in klass.getBaseClassNames():
            baseclass = getTypeOf(klass,base,pythonpath)
            rootclass = getRootClassesOfHierarchy(baseclass,pythonpath)
            if rootclass is None:  # base class not in our ast
                rootclass = [klass]
            rootclasses+=rootclass
        return rootclasses

