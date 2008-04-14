from __future__ import generators
from bike.globals import *
from bike.parsing.fastparserast import Function, Class, Module, getModule
from bike.parsing.parserutils import generateLogicalLines, makeLineParseable, generateLogicalLinesAndLineNumbers
from bike.parsing.newstuff import getSourceNodesContainingRegex
from bike.parsing import visitor
from bike.parsing.load import getSourceNode
from bike import log
import compiler
from compiler.ast import Getattr, Name
import re,sys
from bike.parsing.newstuff import CouldNotLocateNodeException



class Match:
    def __repr__(self):
        return ",".join([self.filename, str(self.lineno), str(self.colno),
                         str(self.confidence)])
    def __str__(self):
        return ",".join([self.filename, str(self.lineno), str(self.colno),
                         str(self.confidence)])
    
    def __eq__(self,other):
        if self is None or other is None:
            return False
        return self.filename == other.filename and \
               self.lineno == other.lineno and \
               self.colno == other.colno

def getScopeForLine(sourceNode, lineno):
    return sourceNode.getScopeForLine(lineno)


# global from the perspective of 'contextFilename'
def globalScanForMatches(contextFilename, matchFinder, targetname, pythonpath):
    for sourcenode in getSourceNodesContainingRegex(targetname, contextFilename, pythonpath):
        print >> log.progress, "Scanning", sourcenode.filename
        searchscope = sourcenode.fastparseroot
        for match in scanScopeForMatches(sourcenode,searchscope,
                                         matchFinder,targetname):
            yield match


def scanScopeForMatches(sourcenode,scope,matchFinder,targetname):
    lineno = scope.getStartLine()
    for line in generateLogicalLines(scope.getMaskedLines()):
        if line.find(targetname) != -1:
            doctoredline = makeLineParseable(line)
            ast = compiler.parse(doctoredline)
            scope = getScopeForLine(sourcenode, lineno)
            matchFinder.reset(line)
            matchFinder.setScope(scope)
            matches = compiler.walk(ast, matchFinder).getMatches()
            for index, confidence in matches:
                match = Match()
                match.filename = sourcenode.filename
                match.sourcenode = sourcenode
                x, y = indexToCoordinates(line, index)
                match.lineno = lineno+y
                match.colno = x
                match.colend = match.colno+len(targetname)
                match.confidence = confidence
                yield match
        lineno+=line.count("\n")
    

def walkLinesContainingStrings(scope,astWalker,targetnames):
    lineno = scope.getStartLine()
    for line in generateLogicalLines(scope.getMaskedLines()):
        if lineContainsOneOf(line,targetnames):
            doctoredline = makeLineParseable(line)
            ast = compiler.parse(doctoredline)
            astWalker.lineno = lineno
            matches = compiler.walk(ast, astWalker)
        lineno+=line.count("\n")


def lineContainsOneOf(line,targetnames):
    for name in targetnames:
        if line.find(name) != -1:
            return True
    return False


# translates an idx in a logical line into physical line coordinates
# returns x and y coords
def indexToCoordinates(src, index):
    y = src[: index].count("\n")
    startOfLineIdx = src.rfind("\n", 0, index)+1
    x = index-startOfLineIdx
    return x, y





def translateSourceCoordsIntoASTNode(filename,lineno,col):
    sourcenode = getSourceNode(filename)
    return sourcenode.translateCoordsToASTNode(lineno,col)
    


def exprIsAMethod(scope,node):
    return isinstance(node,compiler.ast.Function) and \
           isinstance(scope,Class)

def scopeIsAMethod(scope):
    return isinstance(scope,Function) and isinstance(scope.getParent(),Class)


def convertScopeToMatchObject(scope,confidence=100):
    m = Match()
    m.sourcenode = scope.module.getSourceNode()
    m.filename = scope.filename
    if isinstance(scope,Module):
        m.lineno = 0
        m.colno = 0
    elif isinstance(scope,Class) or isinstance(scope,Function):
        m.lineno = scope.getStartLine()
        m.colno = scope.getColumnOfName()
    m.confidence = confidence
    return m

def createMatchObject(scope,line,column,name,confidence=100):
    m = Match()
    m.sourcenode = scope.module.getSourceNode()
    m.filename = m.sourcenode.filename
    m.lineno = line
    m.colno = column
    m.colend = column + len(name)
    m.confidence = confidence
    return m
