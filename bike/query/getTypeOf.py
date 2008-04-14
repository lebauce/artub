# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

# getTypeOf(scope,fqn) and getTypeOfExpr(scope,ast)

from bike.parsing.fastparserast import Class, Function, Module, Instance
from bike.query.common import scopeIsAMethod
from bike import log
from bike.parsing.newstuff import getModuleUsingFQN
from bike.parsing.pathutils import getPackageBaseDirectory
import os
import re
import compiler
from bike.parsing.fastparserast import ElementHasNoParentException

getTypeOfStack = []

def _getTypeFromCoordinates(filepath,lineno,col,pythonpath=[]):
    from bike.query.common import getScopeForLine, translateSourceCoordsIntoASTNode, convertScopeToMatchObject
    from bike.parsing.load import getSourceNode
    node = translateSourceCoordsIntoASTNode(filepath,lineno,col)
    scope = getScopeForLine(getSourceNode(filepath),lineno)
    scope = getTypeOfExpr(scope,node,pythonpath)
    if scope is not None:
        if isinstance(scope,Instance):
            scope = scope.getType()
        return convertScopeToMatchObject(scope)
    else:
        return None


# name is the fqn of the reference, scope is the scope ast object from
# which the question is being asked.
# returns an fastparser-ast object representing the type
# or None if type not found
def getTypeOf(scope, fqn, pythonpath):
    # wraps the getTypeOf_impl method, caching results and protecting from
    # stack overflow
    
    if (fqn,scope) in getTypeOfStack:   # loop protection
        return None
    try:
        getTypeOfStack.append((fqn,scope))
        #try:
        #    hashcode = str(scope)+fqn  # this is crap!
        #    type = Cache.instance.typecache[hashcode]
        #except KeyError:
        #    type = getTypeOf_impl(scope, fqn, pythonpath)
        #    Cache.instance.typecache[hashcode] = type
        type = getTypeOf_impl(scope, fqn, pythonpath)
        return type
    finally:
        del getTypeOfStack[-1]


def getTypeOf_impl(scope, fqn, pythonpath):
    if fqn == "None":
        return None

    if "."in fqn:
        rcdr = ".".join(fqn.split(".")[:-1])
        rcar = fqn.split(".")[-1]
        newscope = getTypeOf(scope,rcdr,pythonpath)
        if newscope is not None:
            return getTypeOf(newscope, rcar,pythonpath)
        else: 
            pass

    assert scope is not None
    
    if isinstance(scope,Instance):
        return handleClassInstanceAttribute(scope, fqn, pythonpath)
    else:
        return handleModuleClassOrFunctionScope(scope,fqn, pythonpath)
        


def handleModuleClassOrFunctionScope(scope,fqn,pythonpath):
    assert isinstance(scope,Function) or isinstance(scope,Class) or isinstance(scope,Module), "this function cant take a scope of type"+str(scope.__class__)
    
    if fqn == "self" and scopeIsAMethod(scope):
        return Instance(scope.getParent())

    child = scope.getChild(fqn)
    if child: return child
    
    type = scanScopeSourceForType(scope, fqn)
    if type is not None: return type
    
    type = getImportedType(scope, fqn, pythonpath)   # try imported types
    if type is not None: return type

    if isinstance(scope,Module) and scope.getSourceNode().filename.endswith("__init__.py"):
        # try searching the package for a module
        packagedir = os.path.dirname(scope.getSourceNode().filename)
        node = getModuleUsingFQN(fqn,[packagedir]+pythonpath)
        if node is not None: return node
    
    try:
        parentScope = scope.getParent()
    except ElementHasNoParentException:
        return None  # scope is a module
    
    while isinstance(parentScope,Class):
        # don't search class scope, since this is not accessible except
        # through self   (is this true?)
        parentScope = parentScope.getParent()


    return getTypeOf(parentScope, fqn, pythonpath)


def handleClassInstanceAttribute(instance, attrname,pythonpath):
    theClass = instance.getType()

    # search methods and inner classes
    child = theClass.getChild(attrname)
    if child: return child

    #search methods for assignments with self.foo getattrs
    for child in theClass.getChildNodes():
        if not isinstance(child,Function):
            continue
        for assignnode in child._generateASTNodesMatchingKeyword(attrname,['Assign']):
            for assnode in assignnode.nodes:
                if isinstance(assnode,compiler.ast.AssAttr) and \
                       isinstance(assnode.expr,compiler.ast.Name) and \
                       assnode.expr.name == "self" and \
                       assnode.attrname == attrname:
                    # the match is the type of the assignment expression
                    res = getTypeOfExpr(child,assignnode.expr, pythonpath)
                    if res is not None:
                        return res
            

def handlePackageScope(package, fqn, pythonpath):
    child = package.getChild(fqn)
    if child:
        return child
    
    # try searching the fs
    node = getModuleUsingFQN(fqn,[package.path]+pythonpath)
    if node:
        return node
    
    # try the package init module
    initmod = package.getChild("__init__")
    if initmod is not None:
        type = getImportedType(initmod, fqn, pythonpath)
        if type:
            return type

    raise "Shouldn't get to here"



def getImportedType(scope, fqn, pythonpath):
    for modname, name, alias in scope.getImports():
        if name is None: # straight import (i.e. not a 'from')
            if modname == fqn or (alias is not None and alias == fqn):
                match = resolveImportedModuleOrPackage(scope,modname,pythonpath)
                if match: return match

        elif name == "*":  # from module import *
            if not "." in fqn:
                module = resolveImportedModuleOrPackage(scope,modname,pythonpath)
                if module:
                    match = getTypeOf(module, fqn, pythonpath)
                    if match: return match


        elif alias == fqn or \
                   (alias is None and name == fqn):
            #Is the thing being imported a module from a package?
            mod = resolveImportedModuleOrPackage(scope,
                                                 modname+"."+name,
                                                 pythonpath)
            if mod: return mod

            # or a variable from a module?
            module = resolveImportedModuleOrPackage(scope,modname,
                                                       pythonpath)
            if module is not None:
                assert isinstance(module,Module)
                match = getTypeOf(module, name, pythonpath)
                if match: return match
            

class TypeNotSupportedException:
    def __init__(self,msg):
        self.msg = msg

    def __str__(self):
        return self.msg

# attempts to evaluate the type of the expression
# returns an Instance, Class or Module scope
def getTypeOfExpr(scope, ast, pythonpath):
    if isinstance(ast, compiler.ast.Name):
        return getTypeOf(scope, ast.name, pythonpath)

    elif isinstance(ast, compiler.ast.Getattr) or \
             isinstance(ast, compiler.ast.AssAttr):

        # need to do this in order to match foo.bah.baz as
        # a string in import statements
        fqn = attemptToConvertGetattrToFqn(ast)
        if fqn is not None:
            r = getTypeOf(scope,fqn,pythonpath)
            return r

        expr = getTypeOfExpr(scope, ast.expr, pythonpath)
        if expr is not None:
            attrnametype = getTypeOf(expr, ast.attrname,pythonpath)
            return attrnametype
        return None

    elif isinstance(ast, compiler.ast.CallFunc):
        node = getTypeOfExpr(scope,ast.node, pythonpath)
        if isinstance(node,Class):
            return Instance(node)
        elif isinstance(node,Function):
            return getReturnTypeOfFunction(node,pythonpath)
    else:
        #raise TypeNotSupportedException, \
        #      "Evaluation of "+str(ast)+" not supported. scope="+str(scope)
        print >> log.warning, "Evaluation of "+str(ast)+" not supported. scope="+str(scope)
        return None


def attemptToConvertGetattrToFqn(ast):
    fqn = ast.attrname
    ast = ast.expr
    while isinstance(ast,compiler.ast.Getattr):
        fqn = ast.attrname + "." + fqn
        ast = ast.expr
    if isinstance(ast,compiler.ast.Name):
        return ast.name + "." + fqn
    else:
        return None


getReturnTypeOfFunction_stack = []
def getReturnTypeOfFunction(function,pythonpath):
    if function in getReturnTypeOfFunction_stack:   # loop protection
        return None
    try:
        getReturnTypeOfFunction_stack.append(function)
        return getReturnTypeOfFunction_impl(function,pythonpath)
    finally:
        del getReturnTypeOfFunction_stack[-1]

def getReturnTypeOfFunction_impl(function,pythonpath):
    for returnnode in function._generateASTNodesMatchingKeyword("return",['Return']):
        try:
            match = getTypeOfExpr(function,returnnode.value, pythonpath)
            if match is not None:
                return match
        except TypeNotSupportedException, ex:
            pass
        

# does parse of scope sourcecode to deduce type
def scanScopeSourceForType(scope, name):
    for node in scope._generateASTNodesMatchingKeyword(name,'Assign'):
        if isinstance(node.expr,compiler.ast.CallFunc):
            for assnode in node.nodes:
                if isinstance(assnode,compiler.ast.AssName) and \
                   assnode.name == name:
                    match = getTypeOfExpr(scope,node.expr,[])
                    if match is None:
                        return None
                    else:
                        return match


def resolveImportedModuleOrPackage(scope,fqn,pythonpath):
    # try searching from directory containing scope module
    path = os.path.dirname(scope.module.filename)
    node = getModuleUsingFQN(fqn,[path]+pythonpath)
    if node is not None:
        return node

    # try searching in same package hierarchy
    basedir = getPackageBaseDirectory(scope.module.filename)
    if fqn.split('.')[0] == os.path.split(basedir)[-1]:
        # base package in fqn matches base directory
        restOfFqn = ".".join(fqn.split('.')[1:])
        node = getModuleUsingFQN(restOfFqn,[basedir]+pythonpath)
    if node is not None:
        return node

    # try searching the python path
    node = getModuleUsingFQN(fqn,pythonpath)
    if node is not None:
        return node
