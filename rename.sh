#!/usr/bin/env bash

OIFS="$IFS"
IFS=$'\n'
for file in `find sources -maxdepth 1 -type f -name "*.ipynb"`
do
     name="$(basename $file)"
     renamed="$(basename $file | sed 's/.*/\L&/' | sed 's/ /-/g')"
     sed -i "s/$name/$renamed/g" sources/*.ipynb _toc.yml
     git mv $file "sources/$renamed"
done
IFS="$OIFS"
