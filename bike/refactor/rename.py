# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from bike.transformer.WordRewriter import WordRewriter
from bike.query.findReferences import findReferencesIncludingDefn
from bike.transformer.save import save

def rename(filename,lineno,col,newname,promptcallback=None):
    strrewrite = WordRewriter()
    for match in findReferencesIncludingDefn(filename,lineno,col):
        if match.confidence == 100 or promptUser(promptcallback,match):
            strrewrite.rewriteString(match.sourcenode,
                                     match.lineno,match.colno,newname)
    strrewrite.commit()

def promptUser(promptCallback,match):
    if promptCallback is not None and \
       promptCallback(match.filename, match.lineno, match.colno, match.colend):
        return 1
    return 0
    
