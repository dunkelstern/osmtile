#!/bin/bash

for i in {8..17} ; do
	python render.py --config config/config.json --width 640 --height 480 48.375884 10.889796 $i
	mv out.png $(( $i - 8 )).png
done
