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

def get_globals():
    return globals()
    
from stackless import *
from thread import start_new_thread
if debug:
    import wx
    import wx.py.shell
import os

os.chdir("d:\\glumol\\demo")

# print debug_handler

if not debug:
    from pdb import Pdb
    class Gdb(Pdb):
        """ The Glumol Debugger """
    
        def __init__(self):
            self.stepping = True
            self.command = ''
            self.lineno = 666
            self.calls = []
            self.first = True
            Pdb.__init__(self)
            
        def user_call(self, frame, args):
            import random
            Pdb.user_call(self, frame, args)
            name = frame.f_code.co_name
            #if name != '?':
            #    print "USERCALL", random.random()
                    
        def user_line(self, frame):
            if not self.first:
                pass
            print "breakpoint in ", frame.f_code.co_filename, "line", frame.f_lineno
            self.calls = []
            for i in self.get_stack(frame, None)[0]:
               name = i[0].f_code.co_name 
               if name != '?' and name != 'run':
                  self.calls.append([i[0].f_code.co_filename, i[0].f_lineno, name]) 
            Pdb.user_line(self, frame)
            
        def user_return(self, frame, return_value):
            # print "RETURN"
            name = frame.f_code.co_name
            Pdb.user_return(self, frame, return_value)
            if name != '?':
               import cheney
               cheney.user_return()
    
        """
        def user_line(self, frame):
            z = open("zzz.txt", "wt")
            z.close()
            import cheney
            cheney.user_line("caca.py", 3)
            import linecache
            name = frame.f_code.co_name
            if not name: name = '???'
            fn = self.canonic(frame.f_code.co_filename)
            line = linecache.getline(fn, frame.f_lineno)
            self.wait_for_input()
           
            #if self.stepping:
            #    self.stepping = False
            #else:
                # self.wait_for_input()
                # print 'Breakpoint in', fn, 'line', frame.f_lineno, name, ':', line.strip()
                # print fn, frame.f_lineno
                # self.set_continue()
        """
        
        def user_exception(self, frame, (exc_type, exc_value, exc_traceback)):
            """This function is called if an exception occurs,
            but only if we are to stop at or just below this level."""
            frame.f_locals['__exception__'] = exc_type, exc_value
            if type(exc_type) == type(''):
                exc_type_name = exc_type
            else: exc_type_name = exc_type.__name__
            print exc_type_name + ':', repr(exc_value)
            self.interaction(frame, exc_traceback)
    
        def cmdloop(self):
            if self.first:
               self.first = None
               # print "CONTINUE"
               self.set_continue()
               return
            sdfsdfsdffds
            try:
               frame, lineno = self.stack[self.curindex]
               self.lineno = lineno
               import cheney
               # print "CHENEY.USER_LINE", frame.f_code
               cheney.user_line(frame.f_code.co_filename, lineno)
            except:
               pass
            self.command = ''
            while not self.command:
               self.command = cheney.wait_for_input()
            # print self.command
            if self.command == 'continue':
               self.set_continue()
            elif self.command == 'step':
               self.set_step()
            elif self.command == 'step_out':
               self.set_return(self.curframe)
            elif self.command == 'step_over':
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
           sys.stdout = self.out # self.r
           print "Start running game"
           
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

    class MyApp:
        def __init__(self):
            pass # wx.App.__init__(self, False)
            
        def __del__(self):
            print "DELETE MYAPP"
            
        def OnInit(self):
            def game_thread():
                gdb = Gdb()

                for i in  range(20): print "game_thread"
                for i in breakpoints:
                    print "set_break", i, __name__
                    gdb.set_break("Machin.py", i)
                dict = {"GameClass" : GameClass, "os" : os}
                os.chdir("d:\\glumol\\demo")
                try:
                    gdb.run("GameClass().run()", dict)
                except:
                    schedule()
                    import time
                    time.sleep(5)
                    print "GAME FINISHED"
                    del dict
                    del gdb
                    import gc
                    gc.collect()
                    sys.exit()
                # print dict["__builtins__"].items()
                print "end game_thread"
                # self.ExitMainLoop()
            game_thread()
            print "OnInit schedule"
            while not get_game().quitte: 
                print "project_debugger schedule"
                schedule()
            # task = tasklet(game_thread)()
            # task.insert()
            # start_new_thread(game_thread, ())
            return True
            
    myapp = MyApp() 
    myapp.OnInit()
    # myapp.MainLoop()
    
else:
    pass # GameClass().run()
    
