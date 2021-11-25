#!/bin/bash

installdir=$1

cd "$installdir/bioimageit-toolboxes"
git pull

cp -r "$installdir/bioimageit-toolboxes/thumbs" "$installdir/toolboxes/"
cp "$installdir/bioimageit-toolboxes/toolboxes.json" "$installdir/toolboxes/toolboxes.json"
cp "$installdir/bioimageit-toolboxes/tools.json" "$installdir/toolboxes/tools.json"
cp "$installdir/bioimageit-toolboxes/formats.json" "$installdir/formats.json"
