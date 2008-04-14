from bike.parsing.load import getSourceNode
from bike.query.getTypeOf import getTypeOfExpr
from bike.parsing.compilerutils import parseLogicalLine

def suggest(filename,linenum,column,pythonpath):
    s = getSourceNode(filename)
    print linenum
    line = s.getLine(linenum)
    if line[column-1] == ".":
        i = column - 2
        while i < 0:
            if re.match("\w+",line[i]):
                i -=1
            else:
                continue
        expr = line[i:column-1]
        expr =  parseLogicalLine(expr,expr,1).compilernode.nodes[0].expr
        scope = s.getScopeForLine(linenum)
        klass = getTypeOfExpr(scope,expr,pythonpath).getType()
        for scope in klass.getChildNodes():
            line = scope.generateLinesNotIncludingThoseBelongingToChildScopes().next()
            yield scope.name, line.strip()
            
        

                
            
        
        # lob the rest of the line off
        #s.getLines()[linenum-1] = s.getLine(linenum)[:column-1]
        #print s.getLines()
        #print s.translateCoordsToASTNode(linenum,column-2)
        #findDefinitionFromASTNode()
