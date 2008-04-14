# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from __future__ import generators

class TreeWalker(object):
    VERBOSE = 0

    def __init__(self):
        self.node = None
        self._cache = {}

    def default(self, node, *args):
        for child in node.getChildNodes():
            self.dispatch(child, *args)

    def dispatch(self, node, *args):
        self.node = node
        klass = node.__class__
        meth = self._cache.get(klass, None)
        if meth is None:
            className = klass.__name__
            meth = getattr(self.visitor, 'visit' + className, self.visitor.default)
            self._cache[klass] = meth
        return meth(node, *args)

    def preorder(self, tree, visitor, *args):
        """Do preorder walk of tree using visitor"""
        self.visitor = visitor
        visitor.visit = self.dispatch
        visitor.visitChildren = self.default
        return self.dispatch(tree, *args)

class GeneratingTreeWalker(TreeWalker):

    def default(self, node, *args):
        for child in node.getChildNodes():
            for i in self.dispatch(child, *args):
                yield i


def walk(tree, visitor):
    walker = TreeWalker()
    walker.preorder(tree, visitor)
    return walker.visitor
    

def walkAndGenerate(tree,visitor):
    walker = GeneratingTreeWalker()
    return walker.preorder(tree, visitor)


