# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from __future__ import generators
from bike.globals import *
from bike.parsing.fastparserast import Module, Class, Function, Instance
from bike.query.common import Match, \
     getScopeForLine, translateSourceCoordsIntoASTNode, \
     exprIsAMethod, convertScopeToMatchObject, createMatchObject, \
     CouldNotLocateNodeException, scopeIsAMethod
from compiler.ast import AssName,Name,Getattr,AssAttr
import compiler
from findDefinition import findDefinitionFromASTNode, findDefinitionOfName, \
                           findDefinitionByCoords
from bike.query.getTypeOf import getTypeOfExpr
from bike.query.relationships import getRootClassesOfHierarchy
from bike import log
from bike.parsing.load import getSourceNode
from bike.parsing.newstuff import getSourceNodesContainingRegex

class CouldntFindDefinitionException(Exception):
    pass

def findReferencesIncludingDefn(filename,lineno,col):
    return findReferences(filename,lineno,col,1)


def findReferences(filename,lineno,col,includeDefn=0,pythonpath=[]):
    sourcenode = getSourceNode(filename)
    node = translateSourceCoordsIntoASTNode(filename,lineno,col)
    assert node is not None
    scope,defnmatch = getDefinitionAndScope(sourcenode,lineno,node,pythonpath)
    try:
        for match in findReferencesIncludingDefn_impl(sourcenode,node,
                                                      scope,defnmatch,pythonpath):

            if not includeDefn and match == defnmatch:
                continue        # don't return definition
            else:
                yield match
    except CouldntFindDefinitionException:
        raise CouldntFindDefinitionException("Could not find definition. Please locate manually (maybe using find definition) and find references from that")

def findReferencesIncludingDefn_impl(sourcenode,node,scope,defnmatch,pythonpath):    
    if isinstance(node,Name) or isinstance(node,AssName):
        return generateRefsToName(node.name,scope,sourcenode,defnmatch,pythonpath)
    elif isinstance(node,Getattr) or isinstance(node,AssAttr):        
        exprtype = getTypeOfExpr(scope,node.expr,pythonpath)
        if exprtype is None:
            raise CouldntFindDefinitionException()

        if isinstance(exprtype,Instance):
            exprtype = exprtype.getType()
            return generateRefsToAttribute(exprtype,node.attrname,pythonpath)
        
        else:
            targetname = node.attrname
            return globalScanForNameReferences(targetname, sourcenode.filename, defnmatch, pythonpath)

    elif isinstance(node,compiler.ast.Function) or \
                             isinstance(node,compiler.ast.Class):
        return handleClassOrFunctionRefs(scope, node, defnmatch,pythonpath)
    else:
        assert 0,"Seed to references must be Name,Getattr,Function or Class"

def handleClassOrFunctionRefs(scope, node, defnmatch,pythonpath):
    if exprIsAMethod(scope,node):
        return generateRefsToAttribute(scope,node.name,pythonpath)
    else:
        return generateRefsToName(node.name,scope, scope.module.getSourceNode(),defnmatch,pythonpath)

def getDefinitionAndScope(sourcenode,lineno,node,pythonpath):
    scope = getScopeForLine(sourcenode,lineno)
    if scope.getStartLine() == lineno and \
           scope.matchesCompilerNode(node):  # scope is the node
        return scope.getParent(), convertScopeToMatchObject(scope,100)
    defnmatch = findDefinitionFromASTNode(scope,node,pythonpath)
    if defnmatch is None:
        raise CouldntFindDefinitionException("Couldn't find definition")
    scope = getScopeForLine(sourcenode,defnmatch.lineno)
    return scope,defnmatch


def generateRefsToName(name,scope,sourcenode,defnmatch,pythonpath):
    assert scope is not None
    if isinstance(scope,Function): # can do a local search
        for linenum,col in scope.getWordCoordsMatchingString(name):
            potentualMatch = findDefinitionByCoords(sourcenode.filename,
                                                    linenum, col, pythonpath)
            if  potentualMatch is not None and \
                   potentualMatch == defnmatch:
                yield createMatchObject(scope,linenum,col,name,100)
            
    else:
        for match in  globalScanForNameReferences(name, sourcenode.filename, defnmatch, pythonpath):
            yield match

def globalScanForNameReferences(name, filename, defnmatch, pythonpath):
    for sourcenode, linenum, col in _generateCoordsMatchingString(name,filename,pythonpath):
        try:
            potentualMatch = findDefinitionByCoords(sourcenode.filename,
                                                    linenum, col, pythonpath)    
            if  potentualMatch is not None and \
                potentualMatch == defnmatch:
                scope = getScopeForLine(sourcenode,linenum)
                yield createMatchObject(scope,linenum,col,name,100)
        except CouldNotLocateNodeException:
            continue

# Works by getting the class instance behind the attribute (or class
# of the method), and then looking to see if it's in the same class
# hierarchy as the thing we're finding references of
def generateRefsToAttribute(classobj,attrname,pythonpath):
    rootClasses = getRootClassesOfHierarchy(classobj,pythonpath)
    for sourcenode, linenum, col in _generateCoordsMatchingString(attrname,classobj.filename,pythonpath):
        scope = getScopeForLine(sourcenode, linenum)
        if col != 0 and sourcenode.getLines()[linenum-1][col-1] == '.':  # possible attribute
            expr = translateSourceCoordsIntoASTNode(sourcenode.filename,linenum,col)
            assert isinstance(expr,Getattr) or isinstance(expr,AssAttr)
            exprtype = getTypeOfExpr(scope,expr.expr,pythonpath)
            if isinstance(exprtype,Instance) and \
                   _isAClassInTheSameHierarchy(exprtype.getType(),rootClasses,pythonpath):
                yield createMatchObject(scope,linenum,col,attrname,100)
            elif exprtype is None:
                # can't deduce type of expression - still could be a match
                yield createMatchObject(scope,linenum,col,attrname,50)
        elif scopeIsAMethod(scope) and scope.name == attrname:  # possible method 
            if _isAClassInTheSameHierarchy(scope.getParent(),rootClasses,pythonpath):
                yield convertScopeToMatchObject(scope,100)
                
def _isAClassInTheSameHierarchy(classobj,rootclasses,pythonpath):
    targetRootClasses = getRootClassesOfHierarchy(classobj,pythonpath)
    for rootclass in rootclasses:
        if rootclass in targetRootClasses:
            return True
    return False


def _generateCoordsMatchingString(word,filenameToStartSearchFrom,pythonpath):
    for sourcenode in getSourceNodesContainingRegex(word, filenameToStartSearchFrom, pythonpath):
        for linenum,col in sourcenode.getWordCoordsMatchingString(word):
            yield sourcenode,linenum,col

