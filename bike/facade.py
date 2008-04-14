import os
import sys
import compiler
from bike.parsing.pathutils import getRootDirectory
from bike.refactor import extractMethod
from bike.refactor.rename import rename
from bike.refactor.extractMethod import coords
from bike.transformer.save import save as saveUpdates
from bike.parsing.utils import fqn_rcar, fqn_rcdr
from bike.parsing import visitor
from bike.transformer.undo import getUndoStack, UndoStackEmptyException
from bike.parsing.fastparserast import Class, Function
from bike.query.common import getScopeForLine
from bike.query.findReferences import findReferences
from bike.query.findDefinition import findAllPossibleDefinitionsByCoords
from bike.refactor import inlineVariable, extractVariable, moveToModule
from bike.query.suggest import suggest
from bike.query.getTypeOf import _getTypeFromCoordinates
from bike import log

def init():
    return Facade()

        
class NotAPythonModuleOrPackageException: pass
class CouldntLocateASTNodeFromCoordinatesException: pass

class DeprecatedInterface:
    """
    Old functions (now deprecated), included for compatibility 
    """

    def extractFunction(self, filename_path, 
                        begin_line, begin_column, 
                        end_line, end_column, 
                        methodname):
        self.extractMethod(filename_path, begin_line, begin_column,
                     end_line, end_column,methodname)

    def renameByCoordinates(self, filename_path, line, col, newname):
        self.rename(filename_path, line, col, newname)


    def findDefinitionByCoordinates(self,filename_path,line,col):
        self.findDefinition(filename_path,line,col)


class Facade(DeprecatedInterface):
    def __init__(self):
        # Used because some refactorings delegate back to the user.
        # this flag ensures that code isnt imported during those times
        self.readyToLoadNewCode = 1 
        self.paths = []
        getUndoStack(1)  # force new undo stack
        self.promptUserClientCallback = None
        
    def save(self):
        """ save the changed files out to disk """
        savedfiles = saveUpdates()
        return savedfiles

    def setRenameMethodPromptCallback(self, callback):
        """
        sets a callback to ask the user about method refs which brm
        can't deduce the type of. The callback must be callable, and
         take the following parameters:
          - filename
          - linenumber
          - begin column
          - end column
         (begin and end columns enclose the problematic method call)
        """
        self.promptUserClientCallback = callback


    def normalizeFilename(self,filename):
        filename = os.path.expanduser(filename)
        filename = os.path.normpath(os.path.abspath(filename))
        return filename


    
    def extractMethod(self, filename_path, 
                begin_line, begin_col,
                end_line, end_col, 
                name):
        filename_path = self.normalizeFilename(filename_path)
        extractMethod.extractMethod(filename_path,
                                    coords(begin_line, begin_col), 
                                    coords(end_line, end_col), name)

    def inlineLocalVariable(self,filename_path, line, col):
        filename_path = self.normalizeFilename(filename_path)
        inlineVariable.inlineLocalVariable(filename_path,line,col)

    def extractLocalVariable(self,filename_path, begin_line, begin_col,
                             end_line, end_col, variablename):
        filename_path = self.normalizeFilename(filename_path)
        extractVariable.extractLocalVariable(filename_path,
                                             coords(begin_line, begin_col),
                                             coords(end_line, end_col),
                                             variablename)

    def moveClassToNewModule(self,filename_path, line, 
                             newfilename):
        filename_path = self.normalizeFilename(filename_path)
        newfilename = self.normalizeFilename(newfilename)
        moveToModule.moveClassToNewModule(filename_path, line, 
                                       newfilename)

    def undo(self):
        getUndoStack().undo()

    def _promptUser(self, filename, lineno, colbegin, colend):
        return self.promptUserClientCallback(filename, lineno, colbegin, colend)


    # must be an object with a write method
    def setProgressLogger(self,logger):
        log.progress = logger

    # must be an object with a write method
    def setWarningLogger(self,logger):
        log.warning = logger

    # filename_path must be absolute
    def rename(self, filename_path, line, col, newname):
        """ an ide friendly method which renames a class/fn/method
        pointed to by the coords and filename"""
        filename_path = self.normalizeFilename(filename_path)
        rename(filename_path,line,col,newname,
               self.promptUserClientCallback)



    def _reverseCoordsIfWrongWayRound(self, colbegin, colend):
        if(colbegin > colend):
            colbegin,colend = colend,colbegin
        return colbegin,colend


    def findDefinition(self,filename_path,line,col):
        """ given the coordates to a reference, tries to find the
        definition of that reference """
        filename_path = self.normalizeFilename(filename_path) 
        return findAllPossibleDefinitionsByCoords(filename_path,line,col,sys.path)

        
    # filename_path must be absolute
    def findReferencesByCoordinates(self, filename_path, line, column):
        filename_path = self.normalizeFilename(filename_path) 
        path = self._removeLibdirsFromPath(sys.path)
        return findReferences(filename_path,line,column,0,path)
                
    
    def _removeLibdirsFromPath(self, pythonpath):
        import re
        libdir = os.path.join(sys.prefix,"lib").lower()
        regex = os.path.join("python.*","site-packages")
        pythonpath = [p for p in pythonpath
                      if not p.lower().startswith(libdir) and \
                         not re.search(regex,p)]
        return pythonpath

    def suggest(self,filename_path,cursorline,cursorcol):
        filename_path = self.normalizeFilename(filename_path) 
        return suggest(filename_path,cursorline,cursorcol)


    def attemptToGetTypeOfVariable(self,filename_path,cursorline,cursorcol):
        return _getTypeFromCoordinates(filename_path,cursorline,cursorcol,sys.path)





# the context object public interface
class BRMContext_old(object):

    def save(self):
        pass
    def setRenameMethodPromptCallback(self, callback):
        pass
    
    def renameByCoordinates(self, filename_path, line, col, newname):
        pass
    def extract(self, filename_path, 
                begin_line, begin_col,
                end_line, end_col, 
                name):
        """ extracts the region into the named method/function based
        on context"""

    def inlineLocalVariable(self,filename_path, line, col):
        """ Inlines the variable pointed to by
        line:col. (N.B. line:col can also point to a reference to the
        variable as well as the definition) """


    def extractLocalVariable(self,filename_path, begin_line, begin_col,
                             end_line, end_col, variablename):
        """ Extracts the region into a variable """

    def setProgressLogger(self,logger):
        """ Sets the progress logger to an object with a write method
        """
        
    def setWarningLogger(self,logger):
        """ Sets the warning logger to an object with a write method
        """

    def undo(self):
        """ undoes the last refactoring. WARNING: this is dangerous if
        the user has modified files since the last refactoring.
        Raises UndoStackEmptyException"""

    def findReferencesByCoordinates(self, filename_path, line, column):
        """ given the coords of a function, class, method or variable
        returns a generator which finds references to it.
        """

    def findDefinitionByCoordinates(self,filename_path,line,col):        
        """ given the coordates to a reference, tries to find the
        definition of that reference """

    def moveClassToNewModule(self,filename_path, line, 
                             newfilename):
        """ moves the class pointed to by (filename_path, line)
        to a new module """
