#!/bin/bash

for f in *.tex
do
	echo "Processing $f"
	pdflatex $f
done

for f in *.pdf
do
	echo "Processing $f"
	convert -density 300 -background white -alpha remove "$f" "${f%.pdf}.png"
done