#! /bin/sh

cd ../src
python2 -m compileall .
find . -type d -exec mkdir -p ../package/res_mods/0.9.13/{} \;
find . -name '*.pyc' -exec mv {} ../package/res_mods/0.9.13/{} \;

cp -rp ../configs ../package/res_mods/

cd ../package
if [ -f spotmessanger.zip ]; then rm spotmessanger.zip; fi
zip -rm spotmessanger.zip res_mods
