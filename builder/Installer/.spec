a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), '', '', '', 'cousins.jpg', 'cousins.jpg', '', u'D:\\glumol\\salamano\\$$$Machin$$$.py', '--onefile', '--onedir'],
             pathex=['F:\\Documents and Settings\\bob\\Bureau\\eclipse\\workspace\\Glumol\\Salamano\\builder\\Installer'])
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name='build/.exe',
          debug=0,
          strip=0,
          upx=0,
          console=1 )
coll = COLLECT( exe,
               a.binaries,
               strip=0,
               upx=0,
               name='dist')
