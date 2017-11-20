#!/usr/bin/env python

import re, sys, time, os

def something(text):
	chars=['!','?',')',':']
	for char in chars:
		text=text.replace(char+'\n\n',char+'. ')
		text=text.replace(char+'\n',char+'. ')
	return text

def something_else(text):
	for title in titles_list:
		text=text.replace(title,'\n{{split}}\n\n'+title+'.\n',1)
	return text
	


infile=sys.argv[1]
head, tail = os.path.split(infile)
new_tail='OK_'+tail
outfile=os.path.join(head,new_tail)

'''
titles='/home/fatallis/Escritorio/EETitles.txt'

titles_list=list()
with open(titles) as titles:
	for line in titles:
		titles_list.append(line.strip())
'''

'''NO BORRAR
#pattern=re.search('[ ]{20,}([A-Za-z])+.+\n',line) GOT
'''

with open(infile) as raw, open(outfile,'w') as out:
	text=''.join(raw.readlines())
	#text=re.sub('\d+\n','\n\n{{split}}\n\n',text)
	#text=text.replace('\n\n\n\n\n','\n\n{{pause=10}}\n\n')
	#text=text.replace('.\n\f','.\n\n{{pause=10}}\n\n\f')
	#text=text.replace(':\n\f',':\n\n{{pause=10}}\n\n\f')
	text=re.sub('PNL(?=[a-zA-Z]+)','PNL ',text)
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
	#text=something_else(text)
	text=text.replace('.\n.\n','.\n')
	text=text.replace('- ','')
	out.write(text)



