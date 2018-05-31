#!/bin/bash

rm -f *.png

for i in {8..17} ; do
	python render.py --config config/config.json --width 800 --height 600 48.375884 10.889796 $i
	mv out.png $(printf %02d $(( $i - 8 )) ).png
done

cp 09.png 10.png
cp 09.png 11.png
convert -delay 50 *.png series.gif
