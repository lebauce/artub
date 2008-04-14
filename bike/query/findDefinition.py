# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from bike.query.common import Match, getScopeForLine, indexToCoordinates, \
     translateSourceCoordsIntoASTNode, scanScopeForMatches, \
     exprIsAMethod, convertScopeToMatchObject, walkLinesContainingStrings, \
     scopeIsAMethod, createMatchObject
from bike.parsing.fastparserast import FunctionArg, ModuleName
from bike.parsing.parserutils import generateLogicalLines,\
     generateLogicalLinesAndLineNumbers, \
     splitLogicalLines, makeLineParseable, isWordInLine
import compiler
from compiler.ast import Getattr, Name, AssName, AssAttr
from bike.parsing.fastparserast import Class, \
                                       Module, Function, Instance
import re
from bike.query.getTypeOf import getTypeOfExpr, \
     resolveImportedModuleOrPackage

from bike.parsing.parserutils import makeLineParseable,splitLogicalLines
from bike.parsing.newstuff import getSourceNodesContainingRegex
from bike.parsing.load import getSourceNode
from bike import log

def findAllPossibleDefinitionsByCoords(filepath,lineno,col,pythonpath=[]):
    match = findDefinitionByCoords(filepath, lineno, col, pythonpath)
    if match is not None:
        yield match

    if match is None or match.confidence != 100:
        node = translateSourceCoordsIntoASTNode(filepath,lineno,col)
        if isinstance(node,Getattr):
            #print "SCANNING PYTHONPATH ---------------"
            name = node.attrname
            for match in scanPythonPathForMatchingMethodNames(name,filepath,pythonpath):
                yield match
        print >>log.progress,"done"


def findDefinitionByCoords(filepath, lineno, col, pythonpath):
    node = translateSourceCoordsIntoASTNode(filepath,lineno,col)
    if node is None:
        raise "selected node type not supported"
    scope = getScopeForLine(getSourceNode(filepath),lineno)
    if isinstance(node,compiler.ast.Function) or \
             isinstance(node,compiler.ast.Class) or isinstance(node,compiler.ast.Keyword) \
             or isinstance(node,FunctionArg):
        return createMatchObject(scope,lineno,col,node.name,100)
    if isinstance(node,ModuleName):
        module = resolveImportedModuleOrPackage(scope,node.modname,pythonpath)
        return createMatchObject(module,0,0,"")

    if not isinstance(scope, Module) and lineno == scope.linenum:  # looking for defn in fn line
        scope = scope.getParent()
    
    match = findDefinitionFromASTNode(scope,node,pythonpath)
    return match


def findDefinitionFromASTNode(scope,node, pythonpath):
    assert node is not None
    if isinstance(node,Name) or isinstance(node,AssName):
        match = findDefinitionOfName(scope, node.name, pythonpath)
    elif isinstance(node,Getattr) or isinstance(node,AssAttr):
        match = findDefinitionOfAttributeExpression(scope, node, pythonpath)
    else: assert False,"Shouldn't get to here"
    if match is not None:
        return match


def findDefinitionOfName(scope, targetname, pythonpath):
    while 1:
        # try scope children
        childscope = scope.getChild(targetname)
        if childscope is not None:
            return convertScopeToMatchObject(childscope,100)

        # check variables created in this scope
        for name,line,col, node in scope.getVariablesAssignedInScope(keyword=targetname):
            return createMatchObject(scope,line,col,name)

        # try imports
        match = searchImportedModulesForDefinition(scope,targetname,pythonpath)
        if match is not None:
            return match
    
        if not isinstance(scope,Module):
            if scopeIsAMethod(scope):
                # can't access class scope from a method,
                scope = scope.getParent().getParent()
            else:
                # try parent scope
                scope = scope.getParent()
        else: 
            break 
    return None # couldn't find it

def findDefinitionOfAttributeExpression(scope, node, pythonpath):
    assert isinstance(node,Getattr) or isinstance(node,AssAttr)
    exprtype = getTypeOfExpr(scope,node.expr, pythonpath)
    if not (exprtype is None):
        if isinstance(exprtype,Instance):
            klass = exprtype.getType()
            return findDefinitionOfClassAttributeGivenClass(klass,node.attrname,
                                                            pythonpath)
        else:
            return findDefinitionOfName(exprtype,node.attrname,pythonpath)
    else: # try a getTypeOfExpr on the expression itself
        exprtype = getTypeOfExpr(scope,node, pythonpath)
        if exprtype:
            return convertScopeToMatchObject(exprtype)

    return None

def findDefinitionOfClassAttributeGivenClass(klass,attrname,pythonpath):
    assert isinstance(klass,Class)

    # first scan the method names:
    for child in klass.getChildNodes():
        if child.name == attrname:
            return convertScopeToMatchObject(child,100)
    # then scan the method source for attribues
    for child in klass.getChildNodes():        
        if isinstance(child,Function):
            for attr,linenum,col in child.getAssignmentAttributesMatchingKeyword(attrname):
                exprtype = getTypeOfExpr(child,attr.expr,pythonpath)                    
                if isinstance(exprtype,Instance) and exprtype.getType() == klass:
                    return createMatchObject(child,linenum,col,attrname)
    # try the class scope
    for name,line,col, node in klass.getVariablesAssignedInScope(keyword=attrname):
        return createMatchObject(klass,line,col,name)

    # try base classes
    for baseclassname in klass.getBaseClassNames():
        match = findDefinitionOfName(klass.getParent(),baseclassname,pythonpath)
        baseclass = getScopeForLine(match.sourcenode,match.lineno)
        return findDefinitionOfClassAttributeGivenClass(baseclass,attrname,pythonpath)        


def searchImportedModulesForDefinition(scope,targetname,pythonpath):
    for modname, name, alias in scope.getImports():
        if name == '*' or targetname in (name,alias):
            module = resolveImportedModuleOrPackage(scope,modname,pythonpath)
            if module is None: # couldn't find module
                continue
            elif name == '*': # e.g. from foo import *
                match = findDefinitionOfName(module,targetname,pythonpath)
                if match is not None:
                    return match
            elif name == targetname: 
                match = findDefinitionOfName(module,targetname,pythonpath)
                if match is not None:
                    return match
        else:
            if modname == targetname:
                module = resolveImportedModuleOrPackage(scope,modname,
                                                        pythonpath)
                match =  createMatchObject(module,0,0,"")
                return match




def scanPythonPathForMatchingMethodNames(name, contextFilename, pythonpath):
    for srcnode in getSourceNodesContainingRegex(name,contextFilename,pythonpath):
        for scope in srcnode.getFlattenedListOfScopes():
            if scope.name == name and scopeIsAMethod(scope):
                yield convertScopeToMatchObject(scope,50)
