import glob
import os
import subprocess

mydir = "/home/eric/Documents/franklin/narsc2018/scripts/stargazer_output/"
for name in glob.glob(mydir+'*.tex'):
	f = open(name, 'r')
	lines = f.readlines()
	f.close()
	f = open(name, 'w')
	f.write('\\documentclass{standalone}\n')
	f.write(r'\begin{document}')
	for line in lines:
		if "table" in line or "caption" in line or "label" in line:
			pass
		else:
			f.write(line)
	f.write(r'\end{document}')
	f.close()