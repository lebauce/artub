# "F:\Program Files\Dev\Python 2.4\Tools\i18n\pygettext.py" .
# del locale\en\LC_MESSAGES\artub.po
# del locale\fr\LC_MESSAGES\artub.po
# copy messages.pot locale\en\LC_MESSAGES\artub.po
# copy messages.pot locale\fr\LC_MESSAGES\artub.po
cd locale
cd en
cd LC_MESSAGES
msgfmt.py artub.po
cd ..
cd ..
cd fr
cd LC_MESSAGES
msgfmt.py artub.po
cd ..
cd ..
cd ..

