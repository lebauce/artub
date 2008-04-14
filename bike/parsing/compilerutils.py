# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

"Utilities to help augument the python compiler package"
from parserutils import makeLineParseable
import compiler
import re

def decorateCompilerNodesWithCoordinates(lineast):
    from bike.parsing import visitor
    a = _ASTLineDecorator(lineast.maskedline)
    visitor.walk(lineast.compilernode,a)

# interface for MatchFinder classes
# implement the visit methods
class _ASTLineDecorator:

    def __init__(self, line):
        self.matches = []
        self.words = re.split("(\w+)", line) # every other one is a non word
        self.positions = []
        i = 0
        for word in self.words:
            self.positions.append(i)
            i+=len(word)
        self.index = 0

    def popWordsUpTo(self, word):
        if word == "*":
            return        # won't be able to find this
        posInWords = self.words.index(word)
        idx = self.positions[posInWords]
        self.words = self.words[posInWords+1:]
        self.positions = self.positions[posInWords+1:]
        if len(self.positions) > 1:
            return self.positions[1]

    def appendMatch(self,name,confidence=100):
        idx = self.getNextIndexOfWord(name)
        self.matches.append((idx, confidence))

    def getNextIndexOfWord(self,name):
        return self.positions[self.words.index(name)]

    def getMatches(self):
        return self.matches

    def default(self, node, *args):
        if len(self.positions) > 1:
            node.index = self.positions[1]   # 0 is always whitespace
            for child in node.getChildNodes():
                self.visit(child, *args)
            if len(self.positions) > 0:
                node.endindex = self.positions[0]
            
        
    # need to visit childnodes in same order as they appear
    def visitPrintnl(self,node):
        self.popWordsUpTo("print")        
        if node.dest:
            self.visit(node.dest)
        for n in node.nodes:
            self.visit(n)
    
    def visitName(self, node):
        node.index = self.positions[1]
        self.popWordsUpTo(node.name)

    def visitClass(self, node):
        node.index = self.positions[1]
        self.popWordsUpTo(node.name)
        for base in node.bases:
            self.visit(base)

    def zipArgs(self, argnames, defaults, kwargs):
        """Takes a list of argument names and (possibly a shorter) list of
        default values and zips them into a list of pairs (argname, default).
        Defaults are aligned so that the last len(defaults) arguments have
        them, and the first len(argnames) - len(defaults) pairs have None as a
        default.
        """
        if not kwargs:
            kwargs = 0
        fixed_args = len(argnames) - len(defaults) - kwargs
        defaults = [None] * fixed_args + list(defaults) + [None]*kwargs
        return zip(argnames, defaults)

    def visitFunction(self, node):
        node.index = self.positions[1]
        assert self.words[1] == "def"
        #self.popWordsUpTo("def")
        self.popWordsUpTo(node.name)
        for arg, default in self.zipArgs(node.argnames, node.defaults, node.kwargs):
            self.popWordsUpTo(arg)
            if default is not None:
                self.visit(default)
        self.visit(node.code)

    def visitGetattr(self,node):
        node.index = self.positions[1]
        self.visit(node.expr)
        node.endindex = self.popWordsUpTo(node.attrname)
        

    def visitAssName(self, node):
        node.index = self.positions[1]
        self.popWordsUpTo(node.name)

    def visitAssAttr(self, node):
        self.visit(node.expr)
        node.index = self.positions[1]
        node.endindex = self.popWordsUpTo(node.attrname)

    def visitImport(self, node):
        node.index = self.positions[1]
        for name, alias in node.names:
            for nameelem in name.split("."):
                node.endindex = self.popWordsUpTo(nameelem)
            if alias is not None:
                node.endindex = self.popWordsUpTo(alias)

    def visitFrom(self, node):
        node.index = self.positions[1]
        for elem in node.modname.split("."):
            self.popWordsUpTo(elem)
        for name, alias in node.names:
            node.endindex = self.popWordsUpTo(name)
            if alias is not None:
                node.endindex = self.popWordsUpTo(alias)

    def visitLambda(self, node):
        node.index = self.positions[1]
        for arg, default in self.zipArgs(node.argnames, node.defaults, node.kwargs):
            self.popWordsUpTo(arg)
            if default is not None:
                self.visit(default)
        self.visit(node.code)

    def visitGlobal(self, node):
        node.index = self.positions[1]
        for name in node.names:
            self.popWordsUpTo(name)



def parseLogicalLine(line,maskedline,linenumber):
    doctoredline = makeLineParseable(maskedline)
    ast = compiler.parse(doctoredline)    
    return LogicalLineAST(ast.node,line,maskedline,linenumber)

class LogicalLineAST:
    def __init__(self, node, line, maskedline,linenumber):
        self.compilernode = node
        self.line = line
        self.maskedline = maskedline
        self.linenumber = linenumber

    def getChildren(self):
        return self.compilernode,

    def getChildNodes(self):
        return self.compilernode,

    def __repr__(self):
        return "LogicalLine(%s)" % (repr(self.compilernode))
