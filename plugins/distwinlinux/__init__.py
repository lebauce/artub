from script import CScript
import os, sys, os.path
from string import join, replace
from wx import LogMessage, GetApp
import log
import pypoujol.animation as animation
from resourceeditor import CRedistributablePlugin

class Builder(CRedistributablePlugin):
    dist_platform = "Linux / Windows"
    
    def run(self, script, args, options = {}, runpath=os.path.join('builder', 'Installer')):
        path = os.getcwd()
        os.chdir(runpath)
        largs = ""
        for opt in options.keys():
            opt = opt
            if options[opt]:
                if type(options[opt]) == bool:
                    largs += " --" + opt
                    sys.argv.append('--' + opt)
                else:
                    largs += " --" + opt
                    if not opt.endswith("="):
                        largs += " "
                    largs += options[opt]
        largs += " " + join(args, " ")
        if script.endswith(".py"):
            if os.name == "posix":
                print "cmd", "python " + script + largs
                os.system("stackless " + script + largs)
            else:
                os.system(script + largs)
        else:
            os.system(script + largs)
        os.chdir(path)
        
    def get_temp_directory(self):
        return self.project.project_path + os.sep + 'build'
        
    def check_temp_directory(self):
        try: os.mkdir(self.get_temp_directory())
        except: pass
        
    def build_resource_file(self):
        for i in animation.anim_classes:
            i.filename
        
    def generate_version_file(self, filename):
        version = ( int(self.project.product_version * 100) / 100, int(self.project.product_version * 100) % 100, 0, 0)
        
        f = open(filename, 'w')
        # version = str(self.project.version[0]) + "." + str(self.project.version[1])
        f.write("""
VSVersionInfo(
  ffi=FixedFileInfo(""")
        f.write("filevers=" + str(version) + ",\n")
        f.write("prodvers=" + str(version) + ",\n")
        f.write("""mask=0x3f,
    flags=0x20,
    OS=0x4,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904E4', 
        [StringStruct('CompanyName', '''""")
        f.write(self.project.company_name + "'''),\n")
        f.write("        StringStruct('License', '''" + self.project.license + "'''),\n")
        f.write("        StringStruct('FileDescription', '''" + self.project.description + "'''),\n")
        f.write("        StringStruct('FileVersion', '''" + str(self.project.product_version) + "'''),\n")
        f.write("        StringStruct('InternalName', '''" + self.project.name + "'''),\n")
        f.write("        StringStruct('Copyright', '''" + self.project.copyrights + "'''),\n")
        f.write("        StringStruct('LegalCopyright', '" + self.project.copyrights + "'),")
        f.write("        StringStruct('LegalTrademarks', '''" + self.project.copyrights + "'''),\n")
        f.write("        StringStruct('OriginalFilename', '''" + self.project.name + ".exe'''),\n")
        f.write("        StringStruct('ProductName', '''" + str(self.project.name) + "'''),\n")
        f.write("        StringStruct('ProductVersion', '''" + str(self.project.product_version) + "'''),\n")
        #f.write("        StringStruct('SpecialBuild', '''" + str(self.project.product_version) + "'''),\n")
        #f.write("        StringStruct('WWW', '''" + str(self.project.product_version) + "''')\n")
        f.write("""])
      ]), 
    VarFileInfo([VarStruct('Translation', [1036, 1200])])
  ]
)
""")

    def generate_makespec(self):
        project = self.project
        self.check_temp_directory()
        paths = os.getcwd() # os.path.join(os.getcwd(), "poujol")
        build_path = os.path.join(self.project.project_path, "build")
        if os.name == 'nt':
            version_file = os.path.join(build_path, str(self.project.name) + '.cfg')
            self.generate_version_file(version_file)
        else:
            version_file = ""
            
        makespec_options = { 'onefile' : not project.no_single_file, \
                             'onedir' : project.no_single_file, \
                             'tk' : project.use_tk, \
                             'ascii' : False, \
                             'debug' : project.debug, \
                             'noconsole' : not project.use_console, \
                             'strip' : False, \
                             'out' : build_path, \
                             'icon' : project.icon, \
                             'version' : version_file, \
                             'paths=' : paths, \
                             'name' : replace(project.name, ' ', '') }

        specpath = os.path.join(build_path, str(self.project.name) + '.spec')

        args = []
        listing = []
        def is_script(resource):
            return isinstance(resource, CScript)
        def add_to_args(resource):
            listing.append(resource.listing)
            if resource.filename.endswith('.py'):
                args.append('"' + str(resource.filename) + '"')
        p = os.path.join(build_path, self.project.name + ".py")
        self.project.filter_apply(add_to_args, is_script)
        import string
        listing = string.join(listing, '')
        scriptfile = open(p, 'wt')
        scriptfile.write('import sys\n')
        scriptfile.write(open(os.path.join('builder', 'prelude.py')).read())
        scriptfile.write(listing)
        scriptfile.write(open(os.path.join('builder', 'prologue_release.py')).read())
        args.append(str(p))
        print "Running Makespec.py"
        self.run('Makespec.py', args, makespec_options)
        return specpath
        
    def make_resource_file(self):
        pass
        
    def build(self, project):
        self.project = project
        path = os.path.join(GetApp().artub_path, "builder", "Installer")
        if not os.path.exists(os.path.join(path, "config.dat")):
            self.run('Configure.py', [ ], { })
        makespec = self.generate_makespec()
        print "Running Build.py"
        self.run('Build.py', [ makespec ], { })
        build_path = os.path.join(self.project.project_path, "build")
        import shutil
        if os.name == 'nt':
            folder = "windows"
            project_name = project.name + ".exe"
        elif os.name == "posix":
            project_name = project.name
            folder = "linux"
        else:
            project_name = project.name
            folder = os.name
        exe_path = os.path.join(project.project_path, "dist", folder)
        try: os.makedirs(exe_path)
        except: pass
        shutil.copyfile(os.path.join(build_path, project_name),
                        os.path.join(exe_path, project_name))
        self.project = None
        
    def get_options_page(self, parent):
        from optionspage import BuilderOptionsPage
        return BuilderOptionsPage(parent, self)
        
plugin = Builder       
