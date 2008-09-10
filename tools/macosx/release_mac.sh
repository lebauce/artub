#BOOST_LIB=libboost_python-mt-1_35.dylib
BOOST_LIB=libboost_python-1_35.dylib
STACKLESS=stackless

if [ ! -f tools/macosx/pythonw ]; then
    gcc -arch ppc -arch i386 -o tools/macosx/pythonw tools/macosx/pythonw.c
fi

$STACKLESS setup.py py2app --excludes OpenGL --includes xml.sax.drivers2.drv_pyexpat,setuptools,wx.gizmos,wx.lib.ogl,ctypes,ctypes.util,poujol._poujol -f /Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/libpng.framework,/Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/libjpeg.framework,/Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/mikmod.framework,/Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/Ogg.framework,/Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/Vorbis.framework,/Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/SDL.framework,/Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/ClanSignals.framework,/Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/ClanCore.framework,/Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/ClanDisplay.framework,/Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/ClanGL.framework,/Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/ClanApp.framework,/Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/ClanSDL.framework,/Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/ClanMikMod.framework,/Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/ClanSound.framework,/Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/ClanGUI.framework,/Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/ClanGUIStyleSilver.framework,/Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/ClanNetwork.framework,/Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/ClanVorbis.framework,/Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/ClanLib.framework
source tools/macosx/dyld_library_path.sh
$STACKLESS gendocs.py

mkdir -p dist/artub.app/Contents/Resources/include/python2.5
cp /Library/Frameworks/Python.framework/Versions/2.5/include/python2.5/pyconfig.h dist/artub.app/Contents/Resources/include/python2.5/
# mkdir -p dist/artub.app/Contents/Frameworks/Python.framework/Versions/2.5
# cp -Rv /Library/Frameworks/Python.framework/Versions/2.5 dist/artub.app/Contents/Frameworks/Python.framework/Versions
ln -s 2.5 dist/artub.app/Contents/Frameworks/Python.framework/Versions/Current

cp -Rv plugins/ dist/artub.app/Contents/Resources/plugins
cp *py dist/artub.app/Contents/Resources
cp -Rv images dist/artub.app/Contents/Resources
mv dist/artub.app/Contents/Resources/images/Artub.icns dist/artub.app/Contents/Resources
cp -Rv docs dist/artub.app/Contents/Resources
cp -Rv startup dist/artub.app/Contents/Resources
cp -Rv debugger dist/artub.app/Contents/Resources
cp -Rv gouzi dist/artub.app/Contents/Resources
cp -Rv depplatform dist/artub.app/Contents/Resources
cp tools/macosx/pythonw dist/artub.app/Contents/MacOS

# cp -Rv poujol dist/artub.app/Contents/Resources
mkdir dist/Artub.app/Contents/Resources/poujol
cp poujol/__init__.py dist/Artub.app/Contents/Resources/poujol
ln -s ../lib/python2.5/lib-dynload/poujol/_poujol.so dist/Artub.app/Contents/Resources/poujol/
# mv dist/Artub.app/Contents/Resources/lib/python2.5/lib-dynload/poujol dist/Artub.app/Contents/Resources

cp -Rv pypoujol dist/artub.app/Contents/Resources
cp -Rv xmlmarshall dist/artub.app/Contents/Resources
cp -Rv bike dist/artub.app/Contents/Resources
cp -Rv propertiesbar dist/artub.app/Contents/Resources
cp -Rv /Library/Frameworks/Python.framework/Versions/Current/lib/python2.5/site-packages/OpenGL-*.egg dist/artub.app/Contents/Resources/lib/python2.5
cp -Rv tools/macosx/easy-install.pth dist/artub.app/Contents/Resources
cp -Rv /Library/Frameworks/Python.framework/Versions/Current/Resources/Python.app dist/Artub.app/Contents/Resources
ln -s ../../../Frameworks dist/Artub.app/Contents/Resources/Python.app/Contents/
install_name_tool -change /Library/Frameworks/Python.framework/Versions/2.5/Python @executable_path/../MacOS/../Frameworks/Python.framework/Versions/2.5/Python dist/Artub.app/Contents/Resources/Python.app/Contents/MacOS/Python

# cp -Rv /Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/Clan* dist/artub.app/Contents/Frameworks
# cp -Rv /Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/libpng.framework/ dist/artub.app/Contents/Frameworks/libpng.framework
# cp -Rv /Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/libjpeg.framework/ dist/artub.app/Contents/Frameworks/libjpeg.framework
# cp -Rv /Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/mikmod.framework/ dist/artub.app/Contents/Frameworks/mikmod.framework
# cp -Rv /Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/Ogg.framework/ dist/artub.app/Contents/Frameworks/Ogg.framework
# cp -Rv /Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/Vorbis.framework/ dist/artub.app/Contents/Frameworks/Vorbis.framework
# cp -Rv /Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/SDL.framework/ dist/artub.app/Contents/Frameworks/SDL.framework
# cp libboost_python.dylib dist/artub.app/Contents/Resources/poujol/

# install_name_tool -change /Users/boblebauce/dev/ClanLib-0.8.0/build/Development/ClanSignals.framework/Versions/A/ClanSignals @executable_path/../Frameworks/ClanSignals.framework/Versions/A/ClanSignals dist/artub.app/Contents/Resources/poujol/_poujol.so
install_name_tool -change /Library/Frameworks/Python.framework/Versions/2.5/Python @executable_path/../Frameworks/Python.framework/Versions/2.5/Python dist/Artub.app/Contents/Resources/poujol/_poujol.so
install_name_tool -change /Library/Frameworks/Python.framework/Versions/2.5/Python @executable_path/../Frameworks/Python.framework/Versions/2.5/Python dist/Artub.app//Contents/Resources/poujol/$BOOST_LIB
# install_name_tool -change $BOOST_LIB @executable_path/../Resources/poujol/$BOOST_LIB dist/artub.app/Contents/Resources/poujol/_poujol.so
install_name_tool -change $BOOST_LIB @executable_path/../Frameworks/$BOOST_LIB dist/Artub.app/Contents/Resources/poujol/_poujol.so

# install_name_tool -change /usr/local/lib/libintl.8.dylib libintl.8.dylib dist/Artub.app/Contents/Resources/poujol/_poujol.so
# install_name_tool -change /usr/local/lib/libpathplan.3.dylib libpathplan.3.dylib dist/Artub.app/Contents/Resources/poujol/_poujol.so
# install_name_tool -change /usr/lib/libz.1.dylib libz.1.dylib dist/Artub.app/Contents/Resources/poujol/_poujol.so

mv dist/artub.app dist/Artub.app
find dist/Artub.app -name \.svn -exec rm -rf {} \;
# cp /Library/Frameworks/Python.framework/Versions/Current/bin/pythonw dist/Artub.app/Contents/MacOS
cp tools/macosx/run dist/Artub.app/Contents/MacOS/
# cp tools/macosx/Info.plist dist/Artub.app/Contents
rm -rf Glumol.dmg
hdiutil create -srcfolder dist/Artub.app/ Glumol.dmg
#rm -rf /Applications/Artub.app
#mv dist/artub.app /Applications/Artub.app

