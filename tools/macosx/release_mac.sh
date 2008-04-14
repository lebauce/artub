stackless setup.py py2app --includes xml.sax.drivers2.drv_pyexpat
source tools/macosx/dyld_library_path.sh
stackless gendocs.py
mkdir -p dist/artub.app/Contents/Resources/include/python2.5
mkdir -p dist/artub.app/Contents/Frameworks/Python.framework/Versions/2.5

cp /Library/Frameworks/Python.framework/Versions/2.5/include/python2.5/pyconfig.h dist/artub.app/Contents/Resources/include/python2.5/

cp -Rv plugins/ dist/artub.app/Contents/Resources/plugins
cp *py dist/artub.app/Contents/Resources
cp -Rv images dist/artub.app/Contents/Resources
mv dist/artub.app/Contents/Resources/images/Artub.icns dist/artub.app/Contents/Resources
cp -Rv docs dist/artub.app/Contents/Resources
cp -Rv startup dist/artub.app/Contents/Resources
cp -Rv debugger dist/artub.app/Contents/Resources
cp -Rv gouzi dist/artub.app/Contents/Resources
cp -Rv depplatform dist/artub.app/Contents/Resources
cp -Rv poujol dist/artub.app/Contents/Resources
cp -Rv pypoujol dist/artub.app/Contents/Resources
cp -Rv xmlmarshall dist/artub.app/Contents/Resources
cp -Rv bike dist/artub.app/Contents/Resources
cp -Rv propertiesbar dist/artub.app/Contents/Resources
cp -Rv /Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/Clan* dist/artub.app/Contents/Frameworks
cp -Rv /Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/libpng.framework/ dist/artub.app/Contents/Frameworks/libpng.framework
cp -Rv /Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/libjpeg.framework/ dist/artub.app/Contents/Frameworks/libjpeg.framework
cp -Rv /Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/mikmod.framework/ dist/artub.app/Contents/Frameworks/mikmod.framework
cp -Rv /Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/Ogg.framework/ dist/artub.app/Contents/Frameworks/Ogg.framework
cp -Rv /Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/Vorbis.framework/ dist/artub.app/Contents/Frameworks/Vorbis.framework
cp -Rv /Users/boblebauce/dev/ClanLib-0.8.0/MacOSX/SDL.framework/ dist/artub.app/Contents/Frameworks/SDL.framework
cp libboost_python.dylib dist/artub.app/Contents/Resources/poujol/
cp -Rv /Library/Frameworks/Python.framework/Versions/2.5 dist/artub.app/Contents/Frameworks/Python.framework/Versions
ln -s 2.5 dist/artub.app/Contents/Frameworks/Python.framework/Versions/Current
install_name_tool -change /Users/boblebauce/dev/ClanLib-0.8.0/build/Development/ClanSignals.framework/Versions/A/ClanSignals @executable_path/../Frameworks/ClanSignals.framework/Versions/A/ClanSignals dist/artub.app/Contents/Resources/poujol/poujol.so
install_name_tool -change libboost_python.dylib @executable_path/../Resources/poujol/libboost_python.dylib dist/artub.app/Contents/Resources/poujol/poujol.so
mv dist/artub.app dist/Artub.app
find dist/Artub.app -name \.svn -exec rm -rf {} \;
hdiutil create -srcfolder dist/Artub.app/ Glumol.dmg
cp tools/macosx/run dist/Artub.app/Contents/MacOS/
cp tools/macosx/Info.plist dist/Artub.app/Contents
#rm -rf /Applications/Artub.app
#mv dist/artub.app /Applications/Artub.app

