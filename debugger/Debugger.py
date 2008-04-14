import os
import bdb
import types
import sys
import stackless

class Idb(bdb.Bdb):

    def __init__(self, gui):
        self.gui = gui
        bdb.Bdb.__init__(self)

    def dispatch_exception(self, frame, arg):
        if True: #self.stop_here(frame):
            self.user_exception(frame, arg)
            if self.quitting: raise BdbQuit
        return self.trace_dispatch

    def user_line(self, frame):
        if self.in_rpc_code(frame):
            self.set_step()
            return
        message = self.__frame2message(frame)
        self.gui.interaction(message, frame)
        
    def set_continue(self):
        bdb.Bdb.set_continue(self)

    def user_exception(self, frame, info):
        if self.in_rpc_code(frame):
            self.set_step()
            return
        message = self.__frame2message(frame)
        self.gui.interaction(message, frame, info)

    def in_rpc_code(self, frame):
        if frame.f_code.co_filename.count('rpc.py'):
            return True
        else:
            prev_frame = frame.f_back
            if prev_frame.f_code.co_filename.count('Debugger.py'):
                # (that test will catch both Debugger.py and RemoteDebugger.py)
                return False
            return self.in_rpc_code(prev_frame)

    def __frame2message(self, frame):
        code = frame.f_code
        filename = code.co_filename
        lineno = frame.f_lineno
        basename = os.path.basename(filename)
        message = "%s:%s" % (basename, lineno)
        if code.co_name != "?":
            message = "%s: %s()" % (message, code.co_name)
        return message


class Debugger:

    vstack = vsource = vlocals = vglobals = None

    def __init__(self, pyshell, idb=None):
        if idb is None:
            idb = Idb(self)
        self.pyshell = pyshell
        self.idb = idb
        self.frame = None
        self.make_gui()
        self.interacting = 0

    def run(self, *args):
        try:
            self.interacting = 1
            return self.idb.run(*args)
        finally:
            self.interacting = 0

    def close(self, event=None):
        if self.interacting:
            self.top.bell()
            return
        if self.stackviewer:
            self.stackviewer.close(); self.stackviewer = None
        # Clean up pyshell if user clicked debugger control close widget.
        # (Causes a harmless extra cycle through close_debugger() if user
        # toggled debugger from pyshell Debug menu)
        self.pyshell.close_debugger()
        # Now close the debugger control window....
        self.top.destroy()

    def make_gui(self):
        pyshell = self.pyshell
        
    def interaction(self, message, frame, info=None):
        self.pyshell.debugbar.set_debugging(True)
        self.frame = frame
        if info:
            type, value, tb = info
            try:
                m1 = type.__name__
            except AttributeError:
                m1 = "%s" % str(type)
            if value is not None:
                try:
                    m1 = "%s: %s" % (m1, str(value))
                except:
                    pass
        else:
            m1 = ""
            tb = None
        end = False
        def foo():
            while not end:
                stackless.schedule()
                clt = self.pyshell.interp.rpcclt
                if clt is None:
                    return
                try:
                    response = clt.pollresponse(self.pyshell.interp.active_seq, wait=0.1)
                except:
                    pass
        import threading
        threading.Thread(target=foo, args=()).start()
        stack, i = self.idb.get_stack(self.frame, tb)
        end = True
        self.pyshell.interaction(stack, tb, info)
        self.frame = None

    def sync_source_line(self):
        frame = self.frame
        if not frame:
            return
        filename, lineno = self.__frame2fileline(frame)
        if filename[:1] + filename[-1:] != "<>" and os.path.exists(filename):
            self.flist.gotofileline(filename, lineno)

    def __frame2fileline(self, frame):
        code = frame.f_code
        filename = code.co_filename
        lineno = frame.f_lineno
        return filename, lineno

    stackviewer = None
