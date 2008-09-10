# Glumol - An adventure game creator
# Copyright (C) 1998-2008  Sylvain Baubeau & Alexis Contour

# This file is part of Glumol.

# Glumol is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# Glumol is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Glumol.  If not, see <http://www.gnu.org/licenses/>.

import pdb
from debugbar import DebugBar
import wx
from script import CScript
import os
from os.path import join
from stackless import schedule
import time
import sys
import wx.aui as PyAUI
from log import log
import signal
import threading
import linecache
import socket
import rpc
import RemoteDebugger
from code import InteractiveInterpreter
LOCALHOST = "127.0.0.1"

class MyRPCClient(rpc.RPCClient):
    def handle_EOF(self):
        "Override the base class - just re-raise EOFError"
        raise EOFError

class ModifiedInterpreter(InteractiveInterpreter):
    def __init__(self):
        locals = sys.modules['__main__'].__dict__
        InteractiveInterpreter.__init__(self, locals=locals)
        self.save_warnings_filters = None
        self.restarting = False
        self.subprocess_arglist = self.build_subprocess_arglist()

    port = 8833
    rpcclt = None
    rpcpid = None

    def spawn_subprocess(self):
        args = self.subprocess_arglist
        if wx.Platform == '__WXMAC__':
            if sys.executable.startswith("/Library"):
                exc = os.environ.get("ARTUB_PYTHON_EXECUTABLE", sys.executable)
            else:
                exc = sys.executable + "w"
        else:
            exc = sys.executable
        print 'Running', exc
        self.rpcpid = os.spawnv(os.P_NOWAIT, exc, args)

    def build_subprocess_arglist(self):
        w = ['-W' + s for s in sys.warnoptions]
        if 1/2 > 0: # account for new division
            w.append('-Qnew')
        command = "__import__('debugger.run').run.main()"
        if sys.platform[:3] == 'win' and ' ' in sys.executable:
            # handle embedded space in path by quoting the argument
            decorated_exec = '"%s"' % sys.executable
        else:
            decorated_exec = sys.executable
        return [decorated_exec] + w + ["-c", command, str(self.port)]

    def start_subprocess(self):
        # spawning first avoids passing a listening socket to the subprocess
        self.spawn_subprocess()
        # test to simulate GUI not accepting connection
        addr = (LOCALHOST, self.port)
        # starts listening for connection on localhost
        for i in range(3):
            time.sleep(i)
            try:
                self.rpcclt = MyRPCClient(addr)
                break
            except socket.error, err:
                pass
        else:
            self.display_port_binding_error()
            return None
        # Accept the connection from the Python execution server
        self.rpcclt.listening_sock.settimeout(10)
        try:
            self.rpcclt.accept()
        except socket.timeout, err:
            self.display_no_subprocess_error()
            return None
        self.rpcclt.register("stdin", sys.stdin)
        self.rpcclt.register("stdout", sys.stdout)
        self.rpcclt.register("stderr", sys.stderr)
        self.rpcclt.register("linecache", linecache)
        self.rpcclt.register("interp", self)
        self.transfer_path()
        self.poll_subprocess()
        return self.rpcclt

    def restart_subprocess(self):
        if self.restarting:
            return self.rpcclt
        self.restarting = True
        # close only the subprocess debugger
        debug = self.getdebugger()
        if debug:
            try:
                # Only close subprocess debugger, don't unregister gui_adap!
                RemoteDebugger.close_subprocess_debugger(self.rpcclt)
            except:
                pass
        # Kill subprocess, spawn a new one, accept connection.
        self.rpcclt.close()
        self.unix_terminate()
        self.spawn_subprocess()
        try:
            self.rpcclt.accept()
        except socket.timeout, err:
            self.display_no_subprocess_error()
            return None
        self.transfer_path()
        # restart subprocess debugger
        if debug:
            # Restarted debugger connects to current instance of debug GUI
            gui = RemoteDebugger.restart_subprocess_debugger(self.rpcclt)
            # reload remote debugger breakpoints for all PyShellEditWindows
        self.restarting = False
        return self.rpcclt

    def __request_interrupt(self):
        self.rpcclt.remotecall("exec", "interrupt_the_server", (), {})

    def interrupt_subprocess(self):
        threading.Thread(target=self.__request_interrupt).start()

    def kill_subprocess(self):
        try:
            self.rpcclt.close()
        except AttributeError:  # no socket
            pass
        self.unix_terminate()
        self.rpcclt = None

    def unix_terminate(self):
        "UNIX: make sure subprocess is terminated and collect status"
        if hasattr(os, 'kill'):
            try:
                os.kill(self.rpcpid, signal.SIGTERM)
            except OSError:
                # process already terminated:
                return
            else:
                try:
                    os.waitpid(self.rpcpid, 0)
                except OSError:
                    return

    def transfer_path(self):
        self.runcommand("""if 1:
        import sys as _sys
        _sys.path = %r
        del _sys
        \n""" % (sys.path,))

    active_seq = None

    def poll_subprocess(self):
        clt = self.rpcclt
        if clt is None:
            return
        try:
            response = clt.pollresponse(self.active_seq, wait=0.05)
        except (EOFError, IOError, KeyboardInterrupt):
            # lost connection or subprocess terminated itself, restart
            # [the KBI is from rpc.SocketIO.handle_EOF()]
            response = None
            self.restart_subprocess()
        if response:
            self.active_seq = None
            how, what = response
            if how == "OK":
                if what is not None:
                    print >>console, repr(what)
            elif how == "EXCEPTION":
                pass
            elif how == "ERROR":
                errmsg = "PyShell.ModifiedInterpreter: Subprocess ERROR:\n"
                print >>sys.__stderr__, errmsg, what
                print >>console, errmsg, what
            # we received a response to the currently active seq number:

    debugger = None

    def setdebugger(self, debugger):
        self.debugger = debugger

    def getdebugger(self):
        return self.debugger

    def execsource(self, source):
        "Like runsource() but assumes complete exec source"
        filename = self.stuffsource(source)
        self.execfile(filename, source)

    def execfile(self, filename, source=None):
        "Execute an existing file"
        if source is None:
            source = open(filename, "r").read()
        try:
            code = compile(source, filename, "exec")
        except (OverflowError, SyntaxError):
            #self.tkconsole.resetoutput()
            tkerr = sys.stderr
            print>>tkerr, '*** Error in script or command!\n'
            print>>tkerr, 'Traceback (most recent call last):'
            InteractiveInterpreter.showsyntaxerror(self, filename)
        else:
            self.runcode(code)

    def runsource(self, source):
        "Extend base class method: Stuff the source in the line cache first"
        filename = self.stuffsource(source)
        self.more = 0
        self.save_warnings_filters = warnings.filters[:]
        warnings.filterwarnings(action="error", category=SyntaxWarning)
        if isinstance(source, types.UnicodeType):
            import IOBinding
            try:
                source = source.encode(IOBinding.encoding)
            except UnicodeError:
                self.write("Unsupported characters in input\n")
                return
        try:
            # InteractiveInterpreter.runsource() calls its runcode() method,
            # which is overridden (see below)
            return InteractiveInterpreter.runsource(self, source, filename)
        finally:
            if self.save_warnings_filters is not None:
                warnings.filters[:] = self.save_warnings_filters
                self.save_warnings_filters = None

    gid = 0

    def stuffsource(self, source):
        "Stuff source in the filename cache"
        filename = "<pyshell#%d>" % self.gid
        self.gid = self.gid + 1
        lines = source.split("\n")
        linecache.cache[filename] = len(source)+1, 0, lines, filename
        return filename

    def prepend_syspath(self, filename):
        "Prepend sys.path with file's directory if not already included"
        self.runcommand("""if 1:
            _filename = %r
            import sys as _sys
            from os.path import dirname as _dirname
            _dir = _dirname(_filename)
            if not _dir in _sys.path:
                _sys.path.insert(0, _dir)
            del _filename, _sys, _dirname, _dir
            \n""" % (filename,))

    def showsyntaxerror(self, filename=None):
        """Extend base class method: Add Colorizing

        Color the offending position instead of printing it and pointing at it
        with a caret.

        """
        stuff = self.unpackerror()
        if stuff:
            msg, lineno, offset, line = stuff
            if lineno == 1:
                pos = "iomark + %d chars" % (offset-1)
            else:
                pos = "iomark linestart + %d lines + %d chars" % \
                      (lineno-1, offset-1)
            text.tag_add("ERROR", pos)
            text.see(pos)
            char = text.get(pos)
            if char and char in IDENTCHARS:
                text.tag_add("ERROR", pos + " wordstart", pos)
            self.write("SyntaxError: %s\n" % str(msg))
        else:
            InteractiveInterpreter.showsyntaxerror(self, filename)

    def unpackerror(self):
        type, value, tb = sys.exc_info()
        ok = type is SyntaxError
        if ok:
            try:
                msg, (dummy_filename, lineno, offset, line) = value
                if not offset:
                    offset = 0
            except:
                ok = 0
        if ok:
            return msg, lineno, offset, line
        else:
            return None

    def showtraceback(self):
        "Extend base class method to reset output properly"
        self.checklinecache()
        InteractiveInterpreter.showtraceback(self)

    def checklinecache(self):
        c = linecache.cache
        for key in c.keys():
            if key[:1] + key[-1:] != "<>":
                del c[key]

    def runcommand(self, code):
        "Run the code without invoking the debugger"
        if self.rpcclt:
            self.rpcclt.remotequeue("exec", "runcode", (code,), {})
        else:
            exec code in self.locals
        return 1

    def runcode(self, code):
        "Override base class method"
        self.checklinecache()
        if self.save_warnings_filters is not None:
            warnings.filters[:] = self.save_warnings_filters
            self.save_warnings_filters = None
        debugger = self.debugger
        try:
            try:
                if not debugger and self.rpcclt is not None:
                    self.active_seq = self.rpcclt.asyncqueue("exec", "runcode",
                                                            (code,), {})
                elif debugger:
                    debugger.run(code, self.locals)
                else:
                    exec code in self.locals
            except SystemExit:
                raose
            except:
                #if use_subprocess:
                print >> sys.stderr, "IDLE internal error in runcode()"
                self.showtraceback()
                raise
        finally:
            pass
            
    def write(self, s):
        "Override base class method"
        sys.stderr.write(s)

    def display_port_binding_error(self):
        sys.stderr.write(
            "Port Binding Error"
            "Glumol can't bind TCP/IP port 8833, which is necessary to "
            "communicate with its Python execution server.  Either "
            "no networking is installed on this computer or another "
            "process (another Glumol?) is using the port.")

    def display_no_subprocess_error(self):
        sys.stderr.write(
            "Subprocess Startup Error"
            "Glumol's subprocess didn't make connection.  Either Glumol can't "
            "start a subprocess or personal firewall software is blocking "
            "the connection. ")

    def display_executing_dialog(self):
        sys.stderr.write(
            "Already executing"
            "The Python Shell window is already executing a command; "
            "please wait until it is finished. ")

from pdb import Pdb
class Gdb(Pdb):
    """ The Glumol Debugger """

    def __init__(self, owner):
        self.first = True
        self.stepping = True
        self.command = ''
        self.lineno = 666
        self.calls = []
        self.owner = owner
        Pdb.__init__(self)
        
    def user_call(self, frame, args):
        Pdb.user_call(self, frame, args)
        name = frame.f_code.co_name
                
    def user_line(self, frame):
        self.calls = []
        for i in self.get_stack(frame, None)[0]:
           name = i[0].f_code.co_name
           if name != '?' and name != 'run':
              self.calls.append([i[0].f_code.co_filename, i[0].f_lineno, name])
        Pdb.user_line(self, frame)
        
    def user_return(self, frame, return_value):
        name = frame.f_code.co_name
        Pdb.user_return(self, frame, return_value)

    def user_exception(self, frame, (exc_type, exc_value, exc_traceback)):
        """This function is called if an exception occurs,
        but only if we are to stop at or just below this level."""
        Pdb.user_exception(self, frame, (exc_type, exc_value, exc_traceback))

    def cmdloop(self):
        if self.first:
           self.first = False
           self.set_continue()
           return
        self.command = ''
        try:
           frame, lineno = self.stack[self.curindex]
           self.owner.user_line(frame)
           self.lineno = lineno
        except:
           raise
        gns = wx.GetApp().gns
        loc = frame.f_locals
        to_remove = []
        for i, j in loc.items():
          if not gns.globals.has_key(i):
            to_remove.append(i)
            self.owner.debugframe.crust.filling.tree.Destroy()
            self.owner.debugframe.crust.filling.tree = wx.py.filling.FillingTree(parent=self.owner.debugframe.crust.filling, rootObject=loc, rootLabel=None, rootIsNamespace=False, static=False)
            self.owner.debugframe.crust.filling.tree.setText =self.owner.debugframe.crust.filling.text.SetText
        while not self.command:
            time.sleep(0.2)
            schedule()
        for i in to_remove:
            pass # del gns.globals[i]
        if self.command == 'continue':
           self.set_continue()
        elif self.command == 'step':
           self.set_step()
        elif self.command == 'return':
           self.set_return(self.curframe)
        elif self.command == 'next':
           self.set_next(self.curframe)
        elif self.command == 'quit':
           self.set_quit()
           self.quit = True
    
    def redirect_outputs(self):
       return
       self.oldout = sys.stdout
       self.olderr = sys.stderr
       self.out = redirected_output()
       sys.stderr = self.out
       sys.stdout = self.out
       
    def restore_outputs(self):
       return
       sys.stderr = self.olderr
       sys.stdout = self.oldout
       self.out.close()
       
    def print_stack_entry(self, arg):
        pass
        
    def interaction(self, frame, traceback):
        self.setup(frame, traceback)
        self.print_stack_entry(self.stack[self.curindex])
        self.cmdloop()
        self.forget()

class CallStackFrame(wx.ListCtrl):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize, style = wx.LC_REPORT)
        self.InsertColumn(0, _("Filename"), format=wx.LIST_FORMAT_LEFT, width=-1)
        self.InsertColumn(1, _("Line"), format=wx.LIST_FORMAT_LEFT, width=-1)
        self.InsertColumn(2, _("Name"), format=wx.LIST_FORMAT_LEFT, width=-1)
        
    def set_calls(self, calls):
        self.DeleteAllItems()
        n = 0
        for filename, line, name in calls:
            self.InsertStringItem(n, filename)
            self.SetStringItem(n, 1, str(line))
            self.SetStringItem(n, 2, name)
            n = n + 1
            
class DebuggerFrame(wx.Frame):
    def __init__(self, parent, debugger):
        wx.Frame.__init__(self, parent, -1, title = _("Debug"))
        self.nb = wx.Notebook(self, -1)
        self.debugger = debugger
        self.populate()
    
    def populate(self):
        self.callstack = CallStackFrame(self.nb)
        self.nb.AddPage(self.callstack, _("Call stack"))
        self.crust = wx.py.crust.Crust(self.nb)
        self.crust.shell.debugger = self.debugger
        self.nb.AddPage(self.crust, _("Shell")) 

class ProjectDebugger:
    def __init__(self, parent, artub):
        self.project = artub.project
        self.artub = artub
        self.debugbar = artub.toolbar_manager.create_toolbar(DebugBar,
                           infos = PyAUI.AuiPaneInfo().Name(_("Debug bar")).
                           Caption(_("Debug bar")).
                           ToolbarPane().Top())
        self.debugbar.artub = artub
        self.debugframe = DebuggerFrame(self.artub, self)
        self.first_interact = True
        self.sub_running = False
        self.end_mainloop = False
        self.interp = ModifiedInterpreter()
        self.exception = False
            
    def is_script(self, resource):
        return isinstance(resource, CScript)
                    
    def collect_breakpoints(self, resource):
        for k, v in resource.breakpoints.items():
            self.set_break(resource, v.line)

    def get_error_infos(self):
        tb = sys.exc_info()[2]
        while tb.tb_next:
            tb = tb.tb_next
        resource, line = self.get_resource_from_line(tb.tb_lineno)
        s = _("An uncaught exception ") + str(sys.exc_info()[0]) + _(" was raised") + ".\n"
        s += _("Message: ") + str(sys.exc_info()[1]) + "\n"
        s += _("Resource: ") + resource.name + "\n"        
        s += _("Line ") + str(tb.tb_lineno)
        return (s, resource, line)

    def show_error(self):
        s, resource, line = self.infos
        dlg = wx.MessageDialog(self.artub, s,
                               _("An error has occured"),
                               wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        self.artub.edit_resource(resource, self.artub.get_editor('akiki')) # Must be done in main thread
        self.artub.active_editor.go_to_line(line) 
        del self.infos
        import gc
        gc.collect()
        
    def kill(self):
        try:
            self.end_mainloop = True
            self.close_debugger()
        except: pass
        try: self.interp.kill_subprocess()
        except: pass
        
    def open_debugger(self):
        if self.interp.rpcclt:
            dbg_gui = RemoteDebugger.start_remote_debugger(self.interp.rpcclt,
                                                           self)
        self.interp.setdebugger(dbg_gui)
        self.idb = dbg_gui.idb
        self.dbg_gui = dbg_gui
    
    def close_debugger(self):
        if hasattr(self, "debugframe"):
            self.debugframe.Destroy()
            del self.debugframe
        os.chdir(self.artub.path)
        debug = self.interp.getdebugger()
        if debug:
            try:
                # Only close subprocess debugger, don't unregister gui_adap!
                import threading
                def foo():
                    log("Closing debugger")
                    #try: RemoteDebugger.close_subprocess_debugger(self.interp.rpcclt)
                    #except: pass
                    self.idb = None
                    self.dbg_gui = None
                    self.end_mainloop = True
                    try: self.interp.rpcclt.close()
                    except: pass
                    try: self.interp.unix_terminate()
                    except: pass
                    log("Debugger closed")
                threading.Thread(target=foo,
                                 args = ()).start()
            except:
                raise
        
    def interaction(self, stack, frame, info):
        if self.first_interact:
            self.first_interact = False
            self.idb.set_continue()
            return
        if stack: lineno = stack[-1][0].f_lineno
        os.chdir(self.artub.path)
        self.artub.Iconize(False)
        self.artub.Raise()
        if stack: resource, line = self.get_resource_from_line(lineno)
        else: line = 1
        if line != 1:
            if self.go_to_cursor == (resource, line):
                self.remove_break(resource, line)
            def foo():
                self.artub.edit_resource(resource, self.artub.get_editor('akiki')) # Doit etre fait dans le thread principal
                self.current_resource = resource
                self.set_debug_cursor(line) 
            self.artub.todos.append(foo)
        
        self.calls = []
        if info: s = info[0].__name__ + ": " + str(info[1]) + "\n\n"
        else: s = ''
        stack.reverse()
        for i in stack:
            name = i[0].f_code.co_name
            s = 'File "' + i[0].f_code.co_filename + '", line ' + str(i[0].f_lineno) + ', in ' + name + '\n' + s
            if name != '?' and name != 'run':
               self.calls.append([i[0].f_code.co_filename, i[0].f_lineno, name])
        self.debugframe.callstack.set_calls(self.calls)
        self.command = ''
        if info and Exception in info[0].__mro__:
            self.debugbar.set_debug_running()
            self.exception = True
            dlg = wx.MessageDialog(None, s, "An exception occurred", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            
        """
        loc = frame.f_locals
        to_remove = []
        for i, j in loc.items():
          if not gns.globals.has_key(i):
            to_remove.append(i)
            self.owner.debugframe.crust.filling.tree.Destroy()
            self.owner.debugframe.crust.filling.tree = wx.py.filling.FillingTree(parent=self.owner.debugframe.crust.filling, rootObject=loc, rootLabel=None, rootIsNamespace=False, static=False)
            self.owner.debugframe.crust.filling.tree.setText =self.owner.debugframe.crust.filling.text.SetText
        """
        
        while not self.command:
            if self.end_mainloop:
                return
            time.sleep(0.01)
            schedule()

    def run(self):
        self.exception = False
        if sys.platform == 'linux2':
            self.interp.start_subprocess()
            self.sub_running = True
            self.first_interact = True
            self.open_debugger()
            ModifiedInterpreter.port += 1
            self.interp.subprocess_arglist = self.interp.build_subprocess_arglist()
        else:
            if self.sub_running:
                self.on_stop()
                self.interp.restart_subprocess()
            else:
                self.interp.start_subprocess()
                self.sub_running = True
            self.first_interact = True
            self.open_debugger()

        self.debugframe = DebuggerFrame(self.artub, self)
        
        import string

        listing = []
        file_lines = {}
        file_lines_list = []
        
        listing += [
          "import os, sys", \
          # "from stackless import *", \
          "debug = True", \
          "sys.path.insert(0, '" + os.getcwd().replace('\\', '\\\\') + "')",
          "sys.path.insert(0, '" + join(os.getcwd(), "poujol").replace('\\', '\\\\') + "')",
          "import _poujol", # This is needed for Windows because of DLL dependencies
          "os.chdir(" + repr(self.project.project_path) + ")"]
          
        l = open(join("poujol", "__init__.py")).readlines()
        n = 0
        for i in l:
            l[n] = l[n].rstrip()
            n = n + 1
        listing += l

        def is_script_and_template(resource):
            return resource.template and isinstance(resource, CScript)
            
        def is_script_and_not_template(resource):
            return not resource.template and isinstance(resource, CScript)
            
        def add_to_args(resource):
            file_lines_list.append((resource, len(listing) + 1))
            file_lines[resource.name] = len(listing) + 1 + 2
            listing.extend(string.split(resource.listing, '\n'))
        
        p = join(self.project.project_path, "temp", self.project.name + ".py")
        self.project.filter_apply(add_to_args, is_script_and_template)
        self.project.filter_apply(add_to_args, is_script_and_not_template)
        
        self.file_lines = file_lines
        self.file_lines_list = file_lines_list
        
        self.debugframe.Show()

        listing = string.join(listing, '\n')
        idb = self.dbg_gui.idb
        listing += "\ng = GameClass(); g.run(); g.quit()\n"
        self.debugbar.set_debugging(True)
        self.project.filter_apply(self.collect_breakpoints, self.is_script)
        def mainloop(self):
            while not self.end_mainloop:
                schedule()
                clt = self.interp.rpcclt
                if clt is None:
                    return
                try:
                    response = clt.pollresponse(self.interp.active_seq, wait=0.1)
                except:
                    pass
                    self.on_stop()
                    return
                    #self.end_mainloop = True
                    #self.close_debugger();

        self.go_to_cursor = None
        self.debug_cursor = None
        self.end_mainloop = False
        self.mainloop_thread = threading.Thread(target=mainloop, args=(self,))
        self.mainloop_thread.start()
        
        os.chdir(self.project.project_path)
        filename = join(self.project.project_path, self.project.name.strip() + ".py")
        open(filename, "wt").write(listing)
        idb.run("execfile(" + repr(filename) + "); global exit_now; global quitting; exit_now = quitting = True", None)
            
        """
        self.debugframe.crust.shell.interp.locals = {}
        self.debugframe.crust.shell.gdb = None
        sys.exc_clear()
        import gc
        self.artub.debugging = False
        """

    def set_break(self, resource, line):
        self.dbg_gui.idb.set_break(join(self.project.project_path, self.project.normname + ".py"), line + self.file_lines[resource.name])
        
    def remove_break(self, resource, line):
        pass # self.clear_break(join(self.project.project_path, self.project.normname + ".py"), line + self.file_lines[resource.name])
        
    def get_resource_from_line(self, line):
        items = self.file_lines_list
        n = 0
        m = len(items)
        while line > items[n][1] and (n + 1) < m:
            n = n + 1
        n = n - 1
        line -= items[n][1]
        return (items[n][0], line - 2)
        
    def remove_debug_cursor(self):
        if self.debug_cursor:
            for i in self.artub.alive_editors:
                if i is self.debug_cursor[0]:
                    i.remove_debug_cursor(self.debug_cursor[1])
        self.debug_cursor = None
        
    def set_debug_cursor(self, line):
        self.debug_cursor = (self.artub.active_editor, line)
        self.artub.active_editor.set_debug_cursor(line)
        
    def on_continue(self):
        self.artub.Iconize(True)
        os.chdir(self.project.project_path)
        self.dbg_gui.idb.set_continue()
        self.command = "continue"
        self.remove_debug_cursor()
        self.debugbar.set_debug_running()
                    
    def on_next(self):
        os.chdir(self.project.project_path)
        self.artub.Iconize(True)
        self.dbg_gui.idb.set_next(self.dbg_gui.frame)
        self.command = "next"
        self.remove_debug_cursor()
        self.debugbar.set_debug_running()
                    
    def on_step(self):
        os.chdir(self.project.project_path)
        self.artub.Iconize(True)
        self.dbg_gui.idb.set_step()
        self.command = "step"
        self.remove_debug_cursor()
        self.debugbar.set_debug_running()
                    
    def on_return(self):
        os.chdir(self.project.project_path)
        self.artub.Iconize(True)
        self.dbg_gui.idb.set_step()
        self.command = "return"
        self.remove_debug_cursor()
        self.debugbar.set_debug_running()
                    
    def on_stop(self):
        self.command = "stop"
        self.artub.Iconize(False)
        self.remove_debug_cursor()
        self.close_debugger()
        self.debugbar.set_debugging(False)
        
    def on_go_to_cursor(self):
        if self.exception: self.on_stop(); return
        self.on_continue()
        line = self.artub.active_editor.get_current_line()
        self.set_break(self.artub.active_editor.active_resource, line)
        self.go_to_cursor = (self.artub.active_editor.active_resource, line)
                    
    def attach(self, project):
        self.project = project
        self.debugbar.enable_go(True)
