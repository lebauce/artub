import sys
import xml.dom
import xml.dom.minidom
import string
from os.path import dirname
from compiler import parse, walk
import types
import pprint
import pyunparse
import compiler.ast as ast
from types import ListType, TupleType

class ClassNotFound:
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return self.name
        
class MethodNotFound: pass

class Visitor:
    def __init__(self, name):
        self.name = name
        self.result = None
        
    def visitStmt(self, node, scope=None):
        self.p = node
        for i in node.nodes:
            self.visit(i, scope)

class ClassFinder(Visitor):
    def visitClass(self, node, scope=None):
        if node.name == self.name:
            if not self.result:
                self.result = node
                self.parent = self.p
        for n in node.bases:
            self.visit(n, node.name)
        self.visit(node.code, node.name)

class AllClassesFinder(Visitor):
    def __init__(self, bases):
        self.bases = bases
        self.result = []
    
    def visitClass(self, node, scope=None):
        if self.bases:
            for i in self.bases:
                if i in node.bases:
                    self.result.append(node)
        else:
            self.result.append(node)
        self.visit(node.code, node.name)

class MethodFinder(Visitor):
    def __init__(self, name, classname):
        self.name = name
        self.classname = classname
        self.result = None
        
    def visitClass(self, node, scope=None):
        if node.name == self.classname:
            self.visit(node.code, scope)
        
    def visitFunction(self, node, scope=None):
        if node.name == self.name:
            self.result = node
            self.parent = self.p
        self.visit(node.code, scope)

class PropFinder(Visitor):
    def visitAssign(self, node, scope=None):
        if isinstance(node.nodes[0], ast.Slice):
            if node.nodes[0].expr.expr.name == "self" and \
               node.nodes[0].expr.attrname == self.name:
                if not self.result:
                    self.result = node
                    self.parent = self.p
                    
        elif isinstance(node.nodes[0], ast.AssAttr):
            if node.nodes[0].attrname == self.name:
                if not self.result:
                    self.result = node
                    self.parent = self.p
        for n in node.nodes:
            self.visit(n, scope)
        self.visit(node.expr, scope)

class GlobalPropFinder(Visitor):
    def visitAssign(self, node, scope=None):
        if isinstance(node.nodes[0], ast.AssName):
            if node.nodes[0].name == self.name:
                if not self.result:
                    self.result = node
                    self.parent = self.p
        for n in node.nodes:
            self.visit(n, scope)
        self.visit(node.expr, scope)

    def visitFunction(self, node, scope=None):
        pass
                
class Canard:
    def __init__(self, ast, parent = None):
        self.ast = ast
        self.parent = parent
        
class Method(Canard):
    def get_nodes(self, ast = None):
        if ast == None: ast = self.ast
        return ast.code.nodes

    def get_prop(self, name, ast = None):
        if ast == None: ast = self.ast
        cf = PropFinder(name)
        walk(self.ast, cf)
        return Prop(cf.result)

    def add_property(self, name, valuecode, _ast = None, position = -1):
        if _ast == None: _ast = self.ast
        valuecode = "self." + name + "=" + valuecode
        ast2 = parse(valuecode)
        if len(self.get_nodes(_ast)) == 1 and isinstance(self.get_nodes()[0], ast.Pass):
            del self.get_nodes()[0]
        if position != -1:
            self.get_nodes(_ast).insert(position, ast2.node.nodes[0])        
        else:
            self.get_nodes(_ast).append(ast2.node.nodes[0])        

class Prop(Canard):
    def change_property(self, valuecode, ast = None):
        if ast == None: ast = self.ast
        ast2 = parse("a = " + valuecode)
        self.ast.expr = ast2.node.nodes[0].expr

    def get_repr(self):
        if self.ast and self.ast.expr:
            b = Manipulator.buf()
            pyunparse.ast2py(self.ast.expr, b)
            return b.listing
        else:
            return ""
            
class GlobalProp(Canard):
    def change_property(self, valuecode, ast = None):
        if ast == None: ast = self.ast
        ast2 = parse("a = " + valuecode)
        self.ast.expr = ast2.node.nodes[0].expr

    def get_repr(self):
        if self.ast and self.ast.expr:
            buf = buffer()
            b = Manipulator.buf()
            pyunparse.ast2py(self.ast.expr, b)
            return b.listing
        else:
            return ""

class Module(Canard):
    def remove_class(self, name, ast = None):
        c = self.get_class(name, ast)
        self.get_nodes().remove(c.ast)
        
    def get_all_classes(self, ast = None, derived_from = []):
        if ast == None: ast = self.ast
        cf = AllClassesFinder(derived_from)
        walk(ast, cf)
        return map(Classe, cf.result)
        
    def get_class(self, name, ast = None):
        if ast == None: ast = self.ast
        names = name.split('.')
        cl = None
        try:
            for name in names:
                cf = ClassFinder(name)
                walk(ast, cf)
                ast = Classe(cf.result, cf.parent).ast
            return Classe(cf.result, cf.parent)
        except:
            raise ClassNotFound(name)

    def get_method(self, name, ast = None):
        if ast == None: ast = self.ast
        cf = MethodFinder(name, "")
        walk(self.ast.node, cf)
        if not cf.result: raise MethodNotFound()
        return Method(cf.result)

    def remove_function(self, name, ast = None):
        m = self.get_method(name, ast)
        self.ast.node.nodes.remove(m.ast)

    def get_node(self, ast = None):
        if ast == None: ast = self.ast
        return ast.node
        
    def get_nodes(self, ast = None):
        if ast == None: ast = self.ast
        return ast.node.nodes
        
    def insert(self, node, position = -1):
        if position != -1:
            self.get_nodes().insert(position, node)
        else:
            self.get_nodes().append(node)
            
    def add_function(self, funccode, ast = None, position = -1):
        if ast == None: ast = self.ast
        ast2 = parse(funccode)
        ast2.node.nodes[0].lineno = self.ast.lineno
        self.insert(ast2.node.nodes[0], position)
        return Method(ast2.node.nodes[0])
        
    def add_class(self, name, base_classes, body, ast = None, position = -1):
        if ast == None: ast = self.ast
        s = "class " + name
        if base_classes:
            s = s + "("
            n = 0
            for i in base_classes:
                if n:
                    s += ", "
                else: n = 1           
                s = s + i
            s = s + ")"
        s = s + ":\n"
        for i in body:
            s = s + " " + i + "\n"
        ast2 = parse(s)
        self.insert(ast2.node.nodes[0], position)
        return Classe(ast2.node.nodes[0])

class Classe(Module):
    def __init__(self, ast, parent = None):
        Module.__init__(self, ast, parent)
        self.name = ast.name
        self.method = '__glumolinit__'
        self.method_args = '(self)'
        
    def get_node(self, ast = None):
        if ast == None: ast = self.ast
        return ast.code
        
    def get_nodes(self, ast = None):
        if ast == None: ast = self.ast
        return ast.code.nodes
        
    def get_all_classes(self, ast = None, derived_from = []):
        if ast == None: ast = self.ast.code
        return Module.get_all_classes(self, ast, derived_from)
    
    def get_constructor(self, ast = None):
        return self.get_method(self.method, ast)
    
    def remove_child_class(self, name, ast = None):
        m = self.get_method(name, ast)
        self.ast.code.nodes.remove(m.ast)

    def get_method(self, name, ast = None):
        if ast == None: ast = self.ast
        cf = MethodFinder(name, self.ast.name)
        walk(ast, cf)
        if not cf.result: raise MethodNotFound()
        return Method(cf.result)
        
    def set_global_property(self, name, value, ast = None):
        if ast == None: ast = self.ast
        try:
            p = self.get_global_prop(name)
            p.change_property(value)
        except:
            self.add_global_property(name, value)
            
    def set_property(self, name, value, ast = None, method = None):
        if ast == None: ast = self.ast
        cons = None
        try:
            if method: cons = self.get_method(method, ast)
            else: cons = self.get_constructor(ast)
        except:
            raise
            if not method: method = self.method
            cons = self.add_function("def " + method + "(" + self.method_args + "): pass")
        try:
            i = name.find('[') # Bien crade. Pour le cas : self.prop[:] = ...
            pname = name
            if i != -1:
                pname = name[:i]
            p = cons.get_prop(pname)
            p.change_property(value)
        except:
            p = cons.add_property(name, value) # No property

    def remove_global_property(self, name):
        m = self.get_global_prop(name)
        self.get_nodes().remove(m.ast)
        
    def remove_property(self, name, ast = None):
        cons = self.get_constructor(ast)
        m = cons.get_prop(name, ast)
        cons.ast.code.nodes.remove(m.ast)
        if not cons.ast.code.nodes:
            cons.ast.code.nodes.append(parse("pass"))

    def remove_function(self, name, ast = None):
        m = self.get_method(name, ast)
        self.ast.code.nodes.remove(m.ast)

    def add_property(self, name, valuecode, ast = None, position = -1):
        cons = self.get_constructor(ast)
        return cons.add_property(name, valuecode, ast, position)      
        
    def add_global_property(self, name, valuecode, ast = None, position = -1):
        if ast == None: ast = self.ast
        valuecode = name + "=" + valuecode
        ast2 = parse(valuecode)
        if position != -1:
            self.get_nodes().insert(position, ast2.node.nodes[0])        
        else:
            self.get_nodes().append(ast2.node.nodes[0])        

    def get_global_prop(self, name, ast = None):
        if ast == None: ast = self.ast
        pf = GlobalPropFinder(name)
        walk(ast, pf)
        return Prop(pf.result)

    def get_prop(self, name, ast = None):
        if ast == None: ast = self.ast
        cons = self.get_constructor(ast)
        return cons.get_prop(name)

class Manipulator(Module):
    def __init__(self, script):
        Module.__init__(self, self.parse_script(script))
        
    def sync(self, script):
        self.ast = self.parse_script(script)
    
    def parse_script(self, script):
        return parse(script.__dict__["listing"])
        
    class buf:
        def __init__(self):
            self.listing = ""
        def write(self, s):
            self.listing = self.listing + s

    def topy(self):
        b = Manipulator.buf()
        v = pyunparse.UnparsingVisitor(stream=b)
        v.v(self.ast)
        for k, j in self.breakpoints.items():
            if v.line_map.has_key(j.line + 1):
                # print "changing breakpoint from line", j.line + 1, "to line", v.line_map[j.line + 1]
                j.line = v.line_map[j.line + 1] - 1
        return b.listing + "\n"
