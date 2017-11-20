#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys, subprocess, uuid, shutil, fileinput, gi, time, urllib, re
gi.require_version('Notify', '0.7')
from joblib import Parallel, delayed
from gi.repository import GObject
from gi.repository import Notify
from langdetect import detect
from bs4 import BeautifulSoup
from bs4.element import Comment
import cchardet as chardet


def run_parallel(commands_file, remove=True):
	command=['parallel', '-k', '-a', commands_file]
	p=subprocess.Popen(command,stdout=subprocess.PIPE)
	output = p.stdout.read()
	if remove:
		os.remove(commands_file)

	return output

def run_serial(commands_file, remove=True):
	command=['bash', commands_file]
	p=subprocess.Popen(command,stdout=subprocess.PIPE)
	output = p.stdout.read()
	if remove:
		os.remove(commands_file)

	return output

def gdrive_upload(paths):
	upload_file='.'+uuid.uuid4().hex+'.txt'
	with open(upload_file,'w') as commands:
		for p in paths:
			commands.write('/home/fatallis/.linuxbrew/bin/gdrive upload "'+p+'"\n')

	run_parallel(upload_file)

def detect_lang(paths):
	if paths[0].endswith('.txt'):
		with open(paths[0]) as lang_sample:
			lang_sample=unicode(lang_sample.read(), encoding='utf-8', errors='replace')
			lang=detect(lang_sample)
	elif paths[0].endswith('.epub'):
		command=['epub2txt', paths[0]]
		p=subprocess.Popen(command,stdout=subprocess.PIPE)
		output = p.stdout.read()
		output = unicode(output, encoding='utf-8', errors='replace')
		lang=detect(output)
	
	return lang

def pdftotext(paths):
	pdftotext_commands='.'+uuid.uuid4().hex+'.txt'
	with open(pdftotext_commands,'w') as commands:
		for p in paths:
			commands.write('pdftotext -raw -enc UTF-8 -nopgbrk "'+p+'"\n')

	run_parallel(pdftotext_commands)

	for p in paths:
		txt=p.replace('.pdf','.txt')
		beautify(txt)

def beautify(txt):

	chars1=['!','?',')',':']
	chars2=['.','}','?','!','"']

	outfile='.'+uuid.uuid4().hex+'.txt'
	with open(txt) as raw, open(outfile,'w') as out:
		text=''.join(raw.readlines())
		print text
		text=re.sub('(?<=[a-z])\n(?=[A-Z])','\n',text)
		text=re.sub('(?<=[a-z])''(?=[A-Z])',' ',text)

		for char in chars1:
			text=text.replace(char+'\n\n',char+'. ')
			text=text.replace(char+'\n',char+'. ')

		text=text.replace('\n',' ')
		text=text.replace('\f','')
		text=re.sub('[ ]+',' ',text)

		for char in chars2:
			text=text.replace(char+' ',char+'\n')

		text=text.replace('.\n.\n','.\n')
		text=text.replace('- ','')
		out.write(text)

	os.rename(outfile,txt)


class MyNotification(GObject.Object):

	def __init__(self):

		super(MyNotification, self).__init__()
		# lets initialise with the application name
		Notify.init("myapp_name")

	def send_notification(self, title, text, file_path_to_icon=""):

		n = Notify.Notification.new(title, text, file_path_to_icon)
		n.show()


class DesktopJob:

	def __init__(self, filenames, lang):
		self.filenames=filenames

		if isinstance(filenames, list):
			self.paths=filenames
			self.basename='A_selection'
		else:
			self.filename=filenames
			self.basename=os.path.splitext(self.filename)[0]

		self.lang=lang
		self.tmp_dir='.'+uuid.uuid4().hex



	def create_dir(self):
		if not os.path.exists(self.tmp_dir):
			os.makedirs(self.tmp_dir)

	def copy_to_tmp(self):
		new_files=list()
		if self.paths:
			self.create_dir()
			for p in self.paths:
				shutil.copyfile(p,self.tmp_dir+'/'+p)
				new_files.append(self.tmp_dir+'/'+p)

			self.tmp_txt_files=new_files

	def copy_from_tmp(self, filelist):
		for f in filelist:
			newfile=f.split('/')[-1]
			shutil.copyfile(f,newfile)


	def get_lines(self):
		gl_commands='.'+uuid.uuid4().hex+'.txt'
		with open(gl_commands, 'w') as commands:
			commands.write('calibre-debug -r EpubSplit "'+self.filename+'"\n')

		output=run_parallel(gl_commands)
		output=output.split('\n')

		for line in output:
			if 'Line Number: ' in line:
				max_line=line.replace('Line Number: ','')

		return max_line

	def split(self):
		if self.filenames.endswith('.epub'):
			chapter_lines=self.get_lines()
			digit_size=len(chapter_lines)
			new_files=list()

			if int(chapter_lines)<1:
				shutil.copyfile(self.filename, self.tmp_dir+'/'+self.filename)
				new_files.append(self.tmp_dir+'/'+self.filename)

			else:
				split_commands='.'+uuid.uuid4().hex+'.txt'
				with open(split_commands,'w') as commands:
					for i in range(int(chapter_lines)):
						number=str(i+1).rjust(digit_size, '0')
						new_name=self.filename[:-5]+'_'+number+'.epub'
						new_files.append(self.tmp_dir+'/'+new_name)
						commands.write('calibre-debug --run-plugin EpubSplit -- -l '+self.lang+' -o "'+self.tmp_dir+'/'+new_name+'" "'+self.filename+'" '+str(i+1)+'\n')

				run_parallel(split_commands, False)
			self.tmp_epub_files=new_files


	def epub2txt(self):
		epub2txt_commands='.'+uuid.uuid4().hex+'.txt'
		new_files=list()
		with open(epub2txt_commands, 'w') as commands:
			for epub in sorted(self.tmp_epub_files):
				txt_name=epub[:-5]+'.txt'
				new_files.append(txt_name)
				#commands.write('pandoc -f epub -t markdown_github "'+epub+'" -o "'+txt_name+'"\n')
				commands.write('ebook-convert "'+epub+'" "'+txt_name+'"\n')

		run_parallel(epub2txt_commands)
		self.tmp_txt_files=new_files


	def word_count(self):
		wc_commands='.'+uuid.uuid4().hex+'.txt'
		with open(wc_commands, 'w') as commands:
			for txt in sorted(self.tmp_txt_files):
				commands.write('wc -w "'+txt+'"\n')

		wc=run_parallel(wc_commands)

		sizes=dict()
		wc=wc.splitlines()
		for line in wc:
			size,filename=line.split(' ',1)
			sizes[filename]=int(size)

		self.sizes=sizes

	def create_chunks(self):
		chunks=list()
		total_words=0
		new_chunk=list()
		chunk_words=0
		for s in sorted(self.sizes):
			words=self.sizes[s]
			filename=s.replace('_es.txt','.epub')
			filename=filename.replace('.txt','.epub')

			if int(words)>10000:
				if len(new_chunk)<1:
					chunks.append(filename)
				else:
					chunks.append(new_chunk)
					chunks.append(filename)
					new_chunk=list()
					chunk_words=0
			else:
				if len(new_chunk)<1:
					new_chunk.append(filename)
					chunk_words+=int(words)
				else:
					if chunk_words+int(words)>10000:
						chunks.append(new_chunk)
						new_chunk=list()
						new_chunk.append(filename)
						chunk_words=int(words)
					else:
						chunk_words+=int(words)
						new_chunk.append(filename)

		if new_chunk not in chunks:
			chunks.append(new_chunk)

		digit_size=len(str(len(chunks)))

		chunks_commands='.'+uuid.uuid4().hex+'.txt'
		with open(chunks_commands, 'w') as commands:
			for i, c in enumerate(chunks):
				number=str(i+1).rjust(digit_size, '0')
				new_name=self.basename+'_chunk_'+number+'.epub'

				commands.write('calibre-debug --run-plugin EpubMerge -- -l '+self.lang+' -n -t "'+self.basename+'" -o "'+new_name+'" ')

				if isinstance(c, str):
					commands.write('"'+c+'"\n')

				else:
					for n, e in enumerate(c):
						if n == len(c)-1:
							commands.write('"'+e+'"\n')
						else:
							commands.write('"'+e+'" ')

		run_parallel(chunks_commands)


	def merge(self):
		merge_commands='.'+uuid.uuid4().hex+'.txt'
		filelist=self.tmp_epub_files[1:-1]
		print len(filelist)
		with open(merge_commands, 'w') as commands:
			new_name=self.basename+'_clean.epub'
			commands.write('calibre-debug --run-plugin EpubMerge -- -l '+self.lang+' -n -t "'+self.basename+'" -o "'+new_name+'" ')

			files_string='" "'.join(filelist)
			commands.write('"'+files_string+'"\n')

		run_parallel(merge_commands)


	def clean_dir(self):
		shutil.rmtree(self.tmp_dir)


	def translate(self):
		trans_commands='.'+uuid.uuid4().hex+'.txt'
		new_files=list()
		with open(trans_commands, 'w') as commands:
			for txt in sorted(self.tmp_txt_files):
				es_name=txt[:-4]+'_es.txt'
				new_files.append(es_name)
				commands.write('trans :es -no-auto -b -i "'+txt+'" -o  "'+es_name+'"\n')

		run_parallel(trans_commands)
		self.tmp_txt_trans_files=new_files
		self.lang='es'


	def clean_null(self):
		clean_commands='.'+uuid.uuid4().hex+'.txt'
		with open(clean_commands, 'w') as commands:
			for txt in sorted(self.tmp_txt_trans_files):
				commands.write('sed -i -e "s/null//g" "'+txt+'"\n')

		run_parallel(clean_commands)


	def improve_translation(self):
		improve_commands='.'+uuid.uuid4().hex+'.txt'
		with open('/home/fatallis/Escritorio/github/translator/science.dict') as science_dict:
			science_dict=unicode(science_dict.read(), encoding='utf-8', errors='replace')
			science_dict=science_dict.splitlines()

		improve=dict()

		scape=['/','[',']']

		for s in science_dict:
			s=re.sub(r'\t+', '\t', s)
			before,after=s.split('\t')

			for c in scape:
				before=before.replace(c,'\\'+c)
				after=after.replace(c,'\\'+c)

				improve[before]=after

		sed_files=set()
		with open(improve_commands, 'w') as commands:
			for txt in self.tmp_txt_trans_files:
				sed_file='.'+uuid.uuid4().hex+'.txt'
				sed_files.add(sed_file)
				with open(sed_file,'w') as sed_commands:
					sed_commands.write('sed -i -e "s/\[/\[ /g" "'+txt+'"\n')
					sed_commands.write('sed -i -e "s/\]/ \]/g" "'+txt+'"\n')
					for k in sorted(improve, key=len, reverse=True): # Through keys sorted by length
						sed_commands.write('sed -i -e "s/'+k.encode('utf-8')+'/'+improve[k].encode('utf-8')+'/g" "'+txt+'"\n')

				commands.write('bash "'+sed_file+'"\n')

		run_parallel(improve_commands)
		for s in sed_files:
			os.remove(s)


	def txt2epub(self, filelist):
		txt2epub_commands='.'+uuid.uuid4().hex+'.txt'
		new_files=list()
		with open(txt2epub_commands, 'w') as commands:
			for txt in sorted(filelist):
				epub_name=txt.replace('_es.txt','.epub')
				epub_name=epub_name.replace('.txt','.epub')
				new_files.append(epub_name)
				title=epub_name.split('/')[-1][:-5]
				#commands.write('ebook-convert "'+txt+'" "'+epub_name+'" --language "'+self.lang+'" --no-default-epub-cover --input-encoding=UTF-8\n')
				commands.write('pandoc -M title="'+title+'" -i "'+txt+'" -o "'+epub_name+'"\n')

		run_parallel(txt2epub_commands)
		self.tmp_epub_files=new_files





