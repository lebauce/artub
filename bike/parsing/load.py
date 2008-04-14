# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

import os, re
from bike.parsing.fastparser import fastparser
from bike.parsing.fastparserast import FunctionArg,ModuleName
from bike.parsing.parserutils import generateLogicalLinesAndLineNumbers, makeLineParseable
import compiler
from compiler.ast import Name, Getattr

class CantLocateSourceFileException(Exception):
    pass

class CouldNotLocateNodeException(Exception):
    pass


def getSourceNode(filename_path):
    from bike.parsing.pathutils import filenameToModulePath
    filepathtoload = resolveAutoloadFilename(filename_path)
    sourcenode = SourceFile.createFromFile(filepathtoload,
                                           filenameToModulePath(filename_path),
                                           filename_path)
    if sourcenode is None:
        raise CantLocateSourceFileException(filename_path)

    return sourcenode

# decides whether to load an auto saved file rather than the
# buffer filename.
def resolveAutoloadFilename(filename_path):
    dir,name = os.path.split(filename_path)
    autosave_filename = os.path.join(dir,"#"+name+"#")
    filepathtoload = filename_path                      
    if os.path.exists(os.path.join(dir,"#"+name+"#")):
        autosave_date = os.stat(autosave_filename).st_mtime
        file_date = os.stat(filename_path).st_mtime    
        if autosave_date > file_date:
            filepathtoload = autosave_filename
    return filepathtoload

class SourceFile:

    def createFromString(filename, modulename, src):
        return SourceFile(filename,modulename,src)
    createFromString = staticmethod(createFromString)

    def createFromFile(filename,modulename,name=None):
        if name is None:
            name = filename
        try:
            f = file(filename)
            src = f.read()
            f.close()
        except IOError:
            return None
        else:
            return SourceFile(name,modulename,src)
                
    createFromFile = staticmethod(createFromFile)
    
    def __init__(self, filename, modulename, src):

        if os.path.isabs(filename):
            self.filename = filename
        else:
            self.filename = os.path.abspath(filename)
        self.modulename = modulename

        self.resetWithSource(src)

    def resetWithSource(self, source):
        # fastparser ast
        self.fastparseroot = fastparser(source,self.modulename,self.filename)
        self.fastparseroot.setSourceNode(self)
        self._lines = source.splitlines(1)
        self.sourcenode = self

    def __repr__(self):
        return "Source(%s,%s)"%('source', self.filename)

    def getSource(self):
        return  "".join(self.getLines())

    def getLine(self,linenum):
        return self.getLines()[linenum-1]

    # TODO: rename me!
    def getFlattenedListOfScopes(self):
        return self.fastparseroot.getFlattenedListOfChildNodes()
        
    def getLines(self):
        return self._lines

    def getModule(self):
        return self.fastparseroot


    def getWordCoordsMatchingString(self,word):
        wordRE = re.compile(word)
        for line,linenum in zip(self.getLines(),xrange(1,100000)):
            if line.find(word) != -1:
                for match in wordRE.finditer(line):
                    if (match.start() != 0 and re.match("\w",line[match.start()-1]))\
                           or (match.end() < len(line) and (re.match("\w",line[match.end()]))):
                        continue  # i.e. is a substring of a bigger word

                    col = match.start()
                    # check word isn't part of comment or string
                    if line[col] == \
                           self.getModule().getMaskedModuleLines()[linenum-1][col] != '*':
                        yield linenum, col
                    #else: print "*",


    def getScopeForLine(self, lineno):
        scope = None
        childnodes = self.getFlattenedListOfScopes()
        if childnodes == []:
            return self.fastparseroot #module node

        scope = self.fastparseroot

        for node in childnodes:
            if node.linenum > lineno: break
            scope = node

        if scope.getStartLine() != scope.getEndLine(): # is inline
            while scope.getEndLine() <= lineno:
                scope = scope.getParent()
        return scope

    def translateCoordsToASTNode(self,lineno,col):
        module = self.getModule()
        maskedlines = module.getMaskedModuleLines()
        lline,backtrackchars = getLogicalLine(module, lineno)
        doctoredline = makeLineParseable(lline)
        ast = compiler.parse(doctoredline)
        idx = backtrackchars+col
        nodefinder = ASTNodeFinder(lline,idx)
        node = compiler.walk(ast, nodefinder).node
        if node is None:
            raise CouldNotLocateNodeException("Could not translate editor coordinates into source node")
        return node



wordRE = re.compile("\w+")



# interface for MatchFinder classes
# implement the visit methods
class MatchFinder:
    def setScope(self, scope):
        self.scope = scope

    def reset(self, line):
        self.matches = []
        self.words = re.split("(\w+)", line) # every other one is a non word
        self.positions = []
        i = 0
        for word in self.words:
            self.positions.append(i)
            #if '\n' in word:  # handle newlines
            #    i = len(word[word.index('\n')+1:])
            #else:
            i+=len(word)
        self.index = 0

    def getMatches(self):
        return self.matches

    # need to visit childnodes in same order as they appear
    def visitPrintnl(self,node):
        if node.dest:
            self.visit(node.dest)
        for n in node.nodes:
            self.visit(n)
    
    def visitName(self, node):
        self.popWordsUpTo(node.name)

    def visitClass(self, node):
        self.popWordsUpTo(node.name)
        for base in node.bases:
            self.visit(base)

    def zipArgs(self, argnames, defaults):
        """Takes a list of argument names and (possibly a shorter) list of
        default values and zips them into a list of pairs (argname, default).
        Defaults are aligned so that the last len(defaults) arguments have
        them, and the first len(argnames) - len(defaults) pairs have None as a
        default.
        """
        fixed_args = len(argnames) - len(defaults)
        defaults = [None] * fixed_args + list(defaults)
        return zip(argnames, defaults)

    def visitFunction(self, node):
        self.popWordsUpTo(node.name)
        for arg, default in self.zipArgs(node.argnames, node.defaults):
            self.popWordsUpTo(arg)
            if default is not None:
                self.visit(default)
        self.visit(node.code)

    def visitGetattr(self,node):
        self.visit(node.expr)
        self.popWordsUpTo(node.attrname)

    def visitAssName(self, node):
        self.popWordsUpTo(node.name)

    def visitAssAttr(self, node):
        self.visit(node.expr)
        self.popWordsUpTo(node.attrname)

    def visitImport(self, node):
        for name, alias in node.names:
            for nameelem in name.split("."):
                self.popWordsUpTo(nameelem)
            if alias is not None:
                self.popWordsUpTo(alias)

    def visitFrom(self, node):
        for elem in node.modname.split("."):
            self.popWordsUpTo(elem)
        for name, alias in node.names:
            self.popWordsUpTo(name)
            if alias is not None:
                self.popWordsUpTo(alias)

    def visitLambda(self, node):
        for arg, default in self.zipArgs(node.argnames, node.defaults):
            self.popWordsUpTo(arg)
            if default is not None:
                self.visit(default)
        self.visit(node.code)

    def visitGlobal(self, node):
        for name in node.names:
            self.popWordsUpTo(name)

    def popWordsUpTo(self, word):
        if word == "*":
            return        # won't be able to find this
        posInWords = self.words.index(word)
        idx = self.positions[posInWords]
        self.words = self.words[posInWords+1:]
        self.positions = self.positions[posInWords+1:]

    def appendMatch(self,name,confidence=100):
        idx = self.getNextIndexOfWord(name)
        self.matches.append((idx, confidence))

    def getNextIndexOfWord(self,name):
        return self.positions[self.words.index(name)]



class ASTNodeFinder(MatchFinder):
    # line is a masked line of text
    # lineno and col are coords
    def __init__(self,line,col):
        self.line = line
        self.col = col
        self.reset(line)
        self.node = None

    def visitName(self,node):
        if self.checkIfNameMatchesColumn(node.name):
            self.node = node
        self.popWordsUpTo(node.name)

    def visitGetattr(self,node):
        self.visit(node.expr)
        if self.checkIfNameMatchesColumn(node.attrname):
            self.node = node
        self.popWordsUpTo(node.attrname)

    def visitKeyword(self,node):
        if self.checkIfNameMatchesColumn(node.name):
            self.node=node
        self.popWordsUpTo(node.name)
        self.visit(node.expr)

    def visitFunction(self, node):
        if self.checkIfNameMatchesColumn(node.name):
            self.node = node
        self.popWordsUpTo(node.name)

        for arg, default in self.zipArgs(node.argnames, node.defaults):
            if self.checkIfNameMatchesColumn(arg):
                self.node = FunctionArg(arg)
            self.popWordsUpTo(arg)
            if default is not None:
                self.visit(default)
        self.visit(node.code)


    visitAssName = visitName
    visitAssAttr = visitGetattr

    def visitClass(self, node):
        if self.checkIfNameMatchesColumn(node.name):
            self.node = node
        self.popWordsUpTo(node.name)
        for base in node.bases:
            self.visit(base)


    def checkIfNameMatchesColumn(self,name):
        idx = self.getNextIndexOfWord(name)
        if idx <= self.col and idx+len(name) > self.col:
            return 1
        return 0

    def visitFrom(self, node):
        if self._checkModuleName(node.modname):
            return
        for name, alias in node.names:
            if self.checkIfNameMatchesColumn(name):
                assert "." not in name
                self.node = Name(name)
                return
            self.popWordsUpTo(name)
            if alias is not None:
                self.popWordsUpTo(alias)


    def visitImport(self, node):
        for modname, alias in node.names:
            if self._checkModuleName(modname):
                return
            if alias is not None:
                self.popWordsUpTo(alias)

    def _checkModuleName(self, modname):
        parts = modname.split(".")
        for nameelem in parts[:-1]:
            self.popWordsUpTo(nameelem)
        if self.checkIfNameMatchesColumn(parts[-1]):
            #fakenode = Name(parts[0])
            #for p in parts[1:]:
            #    fakenode = Getattr(fakenode,p)
            self.node = ModuleName(modname)
            return True
        self.popWordsUpTo(parts[-1])
        return False


    #def visitImport(self,node):
    #    for name, alias in node.names:


    # gets round the fact that imports etc dont contain nested getattr
    # nodes for fqns (e.g. import a.b.bah) by converting the fqn
    # string into a getattr instance
    def _manufactureASTNodeFromFQN(self,fqn):
        if "." in fqn:
            assert 0, "getattr not supported yet"
        else:
            return Name(fqn)

        

def getLogicalLine(module, lineno):
    # we know that the scope is the start of a logical line, so
    # we search from there
    scope = module.getSourceNode().getScopeForLine(lineno)
    linegenerator = \
            module.generateLinesWithLineNumbers(scope.getStartLine())
    for lline,llinenum in \
            generateLogicalLinesAndLineNumbers(linegenerator):
        if llinenum > lineno:
            break
        prevline = lline
        prevlinenum = llinenum

    backtrackchars = 0
    for i in range(prevlinenum,lineno):
        backtrackchars += len(module.getSourceNode().getLines()[i-1])
    return prevline, backtrackchars
