a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 'bob.py'],
             pathex=['F:\\DOCUME~1\\bob\\Bureau\\INSTAL~1\\INSTAL~1'])
pyz = PYZ(a.pure)
exe = EXE( pyz,
          a.scripts,
          a.binaries  + [('safedisc.exe', 'D:\\safedisc.exe', 'BINARY')],
          name='bob.exe',
          debug=0,
          strip=0,
          upx=0,
          console=1 )
dist = COLLECT(exe, a.binaries + [('safedisc.exe', 'D:\\safedisc.exe', 'DATA')], name="dist")

# dist = COLLECT(exe, a.binaries, name="dist")
