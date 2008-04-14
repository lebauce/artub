# -*- coding: iso-8859-1 -*-
#
# Bicycle Repair Man - the Python Refactoring Browser
# Copyright (C) 2001-2006 Phil Dawes <phil@phildawes.net>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from parserutils import generateLogicalLines, maskStringsAndComments, maskStringsAndRemoveComments, splitLogicalLines, isWordInLine, makeLineParseable, generateLogicalLinesAndLineNumbers
import re
import os
import compiler
from bike.parsing.compilerutils import decorateCompilerNodesWithCoordinates, LogicalLineAST, parseLogicalLine, _ASTLineDecorator
from parserutils import indexToCoordinates
from bike.parsing import visitor

TABWIDTH = 4

classNameRE = re.compile("^\s*class\s+(\w+)")
fnNameRE = re.compile("^\s*def\s+(\w+)")

def getModule(filename_path):
    from bike.parsing.load import CantLocateSourceFileException, getSourceNode
    try:
        sourcenode = getSourceNode(filename_path)
        return sourcenode.fastparseroot
    except CantLocateSourceFileException:
        return None

class DirectoryNotAPackageException(Exception):
    pass

# used so that linenum can be an attribute
class Line(str):
    pass

class FunctionArg(compiler.ast.Name):
    pass


class ModuleName:
    def __init__(self,modname):
        self.modname = modname

class StructuralNode:
    def __init__(self, filename, srclines, maskedmodulesrc):
        self.childNodes = []
        self.filename = filename
        self._parent = None
        self._modulesrc = maskedmodulesrc
        self._srclines = srclines
        self._maskedLines = None

    def addChild(self, node):
        self.childNodes.append(node)
        node.setParent(self)

    def setParent(self, parent):
        self._parent = parent

    def getParent(self):
        return self._parent

    def getChildNodes(self):
        return self.childNodes

    def getChild(self,name):
        matches = [c for c in self.getChildNodes() if c.name == name]
        if matches != []:
            return matches[0]

    def getLogicalLine(self,physicalLineno):
        return generateLogicalLines(self._srclines[physicalLineno-1:]).next()

    # badly named: actually returns line numbers of import statements
    def getImportLineNumbers(self):
        try:
            return self.importlines
        except AttributeError:
            return[]

    def getLinesNotIncludingThoseBelongingToChildScopes(self):
        srclines = self.getMaskedModuleLines()
        lines = []
        lineno = self.getStartLine()
        for child in self.getChildNodes():
            lines+=srclines[lineno-1: child.getStartLine()-1]
            lineno = child.getEndLine()
        lines+=srclines[lineno-1: self.getEndLine()-1]
        return lines


    def generateLinesNotIncludingThoseBelongingToChildScopes(self):
        srclines = self.getMaskedModuleLines()
        lines = []
        lineno = self.getStartLine()
        for child in self.getChildNodes():
            for line in srclines[lineno-1: child.getStartLine()-1]:
                yield self.attachLinenum(line,lineno)
                lineno +=1
            lineno = child.getEndLine()
        for line in srclines[lineno-1: self.getEndLine()-1]:
            yield self.attachLinenum(line,lineno)
            lineno +=1

    def generateLinesWithLineNumbers(self,startline=1):
        srclines = self.getMaskedModuleLines()
        for lineno in range(startline,len(srclines)+1):
            yield self.attachLinenum(srclines[lineno-1],lineno)

    def attachLinenum(self,line,lineno):
        line = Line(line)
        line.linenum = lineno
        return line

    def getMaskedModuleLines(self):
        maskedsrc = maskStringsAndComments(self._modulesrc)
        maskedlines = maskedsrc.splitlines(1)
        return maskedlines

    def generateTreesForLinesMatchingKeyword(self,keyword=None):
        lines = self.generateLinesNotIncludingThoseBelongingToChildScopes()
        match = None
        for line,linenum in generateLogicalLinesAndLineNumbers(lines):
            if keyword is None or isWordInLine(keyword, line):
                reallogicalline = "".join(self._srclines[linenum-1:linenum-1 + len(line.splitlines(1))])
                logicallineAST = parseLogicalLine(reallogicalline,line,linenum)
                yield logicallineAST



    # nodetypes = list of names of compiler.ast classes to match
    # - e.g. ['Function','Import']
    def _generateASTNodesMatchingKeyword(self,keyword,nodetypes):
        for tree in self.generateTreesForLinesMatchingKeyword(keyword):
            decorateCompilerNodesWithCoordinates(tree)
            def findNode(node,nodetypes):
                if _nodeclassname(node) in nodetypes:
                    yield node
                else:
                    for child in node.getChildNodes():
                        for node in findNode(child,nodetypes):
                            yield node

            def _nodeclassname(node):
                return str(node.__class__).split(".")[-1]

            for node in findNode(tree,nodetypes):
                if _nodeclassname(node) in ["Name","AssName"]:
                    if node.name != keyword:
                        continue 
                x,y = indexToCoordinates(tree.maskedline,node.index)
                y += tree.linenumber
                node.linenumber = y
                node.column = x
                if _nodeclassname(node) in ["Name","AssName"]:
                    node.text = tree.line[node.index:node.index+len(keyword)]
                else:
                    node.text = tree.line[node.index:node.endindex].strip()
                if keyword not in node.text:
                    continue
                yield node


    def getImports(self):
        imports = []
        for node in self._generateASTNodesMatchingKeyword('import',["Import","From"]):
            if isinstance(node,compiler.ast.Import):
                for name, alias in node.names:
                    modname = name
                    alias = alias
                    imports.append((modname,None,alias))
            elif isinstance(node,compiler.ast.From):
                modname = node.modname
                for name, alias in node.names:
                    imports.append((modname,name,alias))
        return imports



    def getWordCoordsMatchingString(self,word):
        lines = self.generateLinesNotIncludingThoseBelongingToChildScopes()
        wordRE = re.compile(word)
        for line in lines:
            if line.find(word) != -1:
                for match in wordRE.finditer(line):
                    if (match.start() != 0 and re.match("\w",line[match.start()-1]))\
                           or (re.match("\w",line[match.end()])):
                        continue  # i.e. is a substring of a bigger word
                    yield line.linenum, match.start()

    
    def getVariablesReferencedInScope(self,**kwargs): 
        keyword = kwargs.get("keyword",None)
        class AllVariablesVisitor(VariableReferenceVisitors,AssignmentVisitors,
                                  VisitorsBase):
            pass
        
        for lineast in self.generateTreesForLinesMatchingKeyword(keyword):
            n = AllVariablesVisitor(lineast.maskedline,keyword)
            visitor.walk(lineast.compilernode,n)
            for name,index,node in n.results:
                x,y = indexToCoordinates(lineast.maskedline,index)
                y += lineast.linenumber
                yield name,y,x,node
                    


    def getVariablesAssignedInScope(self,**kwargs): 
        keyword = kwargs.get("keyword",None)
        for lineast in self.generateTreesForLinesMatchingKeyword(keyword):
            n = AssignmentVisitor(lineast.maskedline,keyword)
            visitor.walk(lineast.compilernode,n)
            for name,index,node in n.results:
                x,y = indexToCoordinates(lineast.maskedline,index)
                y += lineast.linenumber
                yield name,y,x,node

        

    def getAssignmentNamesMatchingKeyword(self,keyword):
        for name in self._generateASbTNodesMatchingKeyword(keyword,['AssName']):
            if name.name == keyword:
                yield name, name.linenumber, name.column                    

    # e.g. a.b = "foo"
    def getAssignmentAttributesMatchingKeyword(self,keyword):
        for attr in self._generateASTNodesMatchingKeyword(keyword,['AssAttr']):
            if attr.attrname == keyword:
                yield attr,attr.linenumber, attr.column


    def getAssignmentsMatchingKeyword(self,keyword):
        for node in self._generateASTNodesMatchingKeyword(keyword,[nodetype]):
           if nodetype in ['Name','AssName']:
               if node.name == keyword:
                   yield node, node.linenumber, node.column
           elif nodetype in ['AssAttr']:
               if node.attrname == keyword:
                   yield node
           


class ElementHasNoParentException(Exception): pass

class Module(StructuralNode):
    def __init__(self, filename, name, srclines, maskedsrc):
        StructuralNode.__init__(self, filename, srclines, maskedsrc)
        self.name = name
        self.indent = -TABWIDTH
        self.flattenedNodes = []
        self.module = self

    def getMaskedLines(self):
        return self.getMaskedModuleLines()

    def getFlattenedListOfChildNodes(self):
        return self.flattenedNodes

    def getStartLine(self):
        return 1

    def getEndLine(self):
        return len(self.getMaskedModuleLines())+1

    def getSourceNode(self):
        return self.sourcenode

    def setSourceNode(self, sourcenode):
        self.sourcenode = sourcenode

    def matchesCompilerNode(self,node):
        return isinstance(node,compiler.ast.Module) and \
               node.name == self.name

    def getParent(self):
        raise ElementHasNoParentException()

    def __str__(self):
        return "bike:Module:"+self.filename

indentRE = re.compile("^(\s*)\S")
class _Scope:
    # module = the module node
    # linenum = starting line number
    def __init__(self, name, module, linenum, indent):
        self.name = name
        self.module = module
        self.linenum = linenum
        self.endline = None
        self.indent = indent

    def getMaskedLines(self):
        return self.getMaskedModuleLines()[self.getStartLine()-1:self.getEndLine()-1]

    def getStartLine(self):
        return self.linenum

    def getEndLine(self):
        if self.endline is None:
            physicallines = self.getMaskedModuleLines()
            lineno = self.linenum
            logicallines = generateLogicalLines(physicallines[lineno-1:])

            # skip the first line, because it's the declaration
            line = logicallines.next()
            lineno+=line.count("\n")

            # scan to the end of the fn
            for line in logicallines:
                #print lineno,":",line,
                match = indentRE.match(line)
                if match and match.end()-1 <= self.indent:
                    break
                lineno+=line.count("\n")
            self.endline = lineno
        return self.endline

    # linenum starts at 0
    def getLine(self, linenum):
        return self._srclines[(self.getStartLine()-1) + linenum]


        

baseClassesRE = re.compile("class\s+[^(]+\(([^)]+)\):")

class Class(StructuralNode, _Scope):
    def __init__(self, name, filename, module, linenum, indent, srclines, maskedmodulesrc):
        StructuralNode.__init__(self, filename, srclines, maskedmodulesrc)
        _Scope.__init__(self, name, module, linenum, indent)
        self.type = "Class"

    
    def getBaseClassNames(self):
        #line = self.getLine(0)
        line = self.getLogicalLine(self.getStartLine())
        match = baseClassesRE.search(line)
        if match:
            return [s.strip()for s in match.group(1).split(",")]
        else:
            return []

    def getColumnOfName(self):
        match = classNameRE.match(self.getLine(0))
        return match.start(1)

    def __repr__(self):
        return "<bike:Class:%s>" % self.name

    def __str__(self):
        return "bike:Class:"+self.filename+":"+\
               str(self.getStartLine())+":"+self.name

    def matchesCompilerNode(self,node):
        return isinstance(node,compiler.ast.Class) and \
               node.name == self.name

    def __eq__(self,other):
        return isinstance(other,Class) and \
               self.filename == other.filename and \
               self.getStartLine() == other.getStartLine()

# describes an instance of a class
class Instance:
    def __init__(self, type):
        assert type is not None
        self._type = type

    def getType(self):
        return self._type

    def __str__(self):
        return "Instance(%s)"%(self.getType())


class Function(StructuralNode, _Scope):
    def __init__(self, name, filename, module, linenum, indent,
                 srclines, maskedsrc):
        StructuralNode.__init__(self, filename, srclines, maskedsrc)
        _Scope.__init__(self, name, module, linenum, indent)
        self.type = "Function"

    def getColumnOfName(self):
        match = fnNameRE.match(self.getLine(0))
        return match.start(1)

    def __repr__(self):
        return "<bike:Function:%s>" % self.name

    def __str__(self):
        return "bike:Function:"+self.filename+":"+\
               str(self.getStartLine())+":"+self.name

    def matchesCompilerNode(self,node):
        return isinstance(node,compiler.ast.Function) and \
               node.name == self.name

    def getArguments(self):
        lineast = self.generateTreesForLinesMatchingKeyword("def").next()
        args = []
        class FnVisitor(_ASTLineDecorator):
            def visitFunction(self,node):
                node.index = self.positions[1]
                assert self.words[1] == "def"
                self.popWordsUpTo(node.name)
                for arg, default in self.zipArgs(node.argnames, node.defaults, node.kwargs):
                    if self.words[0].endswith('**'):
                        args.append(("**"+arg,self.positions[1],default))
                    else:
                        args.append((arg,self.positions[1],default))
                    self.popWordsUpTo(arg)
                    if default is not None:
                        self.visit(default)

        visitor.walk(lineast.compilernode,FnVisitor(lineast.maskedline))

        for arg,index,expr in args:
            x,y = indexToCoordinates(lineast.maskedline,index)
            y += lineast.linenumber
            yield arg,y,x,expr



class VisitorsBase(_ASTLineDecorator):
    def __init__(self,line,keyword=None):
        _ASTLineDecorator.__init__(self,line)
        self.results = []
        self.keyword = keyword


#mixin class
class AssignmentVisitors:
    def visitAssName(self,node):
        if self.keyword is None or node.name == self.keyword:
            self.results.append((node.name,self.positions[1],node))
        self.popWordsUpTo(node.name)

    def visitAugAssign(self,node):
        if self.keyword is None or \
           (isinstance(node.node,compiler.ast.Name) and \
            node.node.name == self.keyword):
            self.results.append((node.node.name,self.positions[1],node))
        self.visit(node.node)  # gets popped by 'Name'

    def visitFrom(self,node):
        for elem in node.modname.split("."):
            self.popWordsUpTo(elem)
        for name, alias in node.names:
            self.popWordsUpTo(name)
            if alias is not None:
                if self.keyword is None or self.keyword == alias:
                    # positions[3] because  [' ','as',' ',alias]
                    self.results.append((alias,self.positions[3],node))
                self.popWordsUpTo(alias)

    def visitFunction(self,node):
        self.popWordsUpTo(node.name)
        for arg, default in self.zipArgs(node.argnames, node.defaults, node.kwargs):
            if self.keyword is None or self.keyword == arg:
                self.results.append((arg,self.positions[1],node))
            self.popWordsUpTo(arg)
            if default is not None:
                self.visit(default)

#mixin class
class VariableReferenceVisitors:
        
    def visitName(self,node):
        if self.keyword is None or node.name == self.keyword:
            self.results.append((node.name,self.positions[1],node))
        self.popWordsUpTo(node.name)

    def visitKeyword(self,node):
        self.popWordsUpTo(node.name)  # keyword arg renaming not supported yet
        # but keyword arg will be a name so need to pop the above to support
        # renaming of keyword arg
        self.visit(node.expr)        


class AssignmentVisitor(AssignmentVisitors,VisitorsBase):
    pass
