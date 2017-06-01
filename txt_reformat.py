#!/usr/bin/env python
# Reformat the text output from pdftotext in order to make it easer to be readed by gTTS. There are several things to do.


import re, sys, time, os

def something(text):
	chars=['!','?',')',':']
	for char in chars:
		text=text.replace(char+'\n\n',char+'. ')
		text=text.replace(char+'\n',char+'. ')
	return text

infile=sys.argv[1]
head, tail = os.path.split(infile)
new_tail='OK_'+tail
outfile=os.path.join(head,new_tail)


with open(infile) as raw, open(outfile,'w') as out:
	text=''.join(raw.readlines())
	text=re.sub('(?<=[a-z])\n(?=[A-Z])','\n',text)
	text=re.sub('(?<=[a-z])''(?=[A-Z])',' ',text)
	text=something(text)
	text=text.replace('\n',' ')
	text=text.replace('\f','')
	text=re.sub('[ ]+',' ',text)
	text=text.replace('. ','.\n')
	text=text.replace('} ','}\n')
	text=text.replace('? ','?\n')
	text=text.replace('! ','!\n')
	text=text.replace('" ','"\n')	
	text=text.replace('.\n.\n','.\n')
	text=text.replace('- ','')
	out.write(text)

### To do ###
# Rename something function
# Make a better and simpler replacement code
# Implement argparse



