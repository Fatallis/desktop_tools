#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys, subprocess, uuid, shutil, fileinput, gi
gi.require_version('Notify', '0.7')
from joblib import Parallel, delayed
from gi.repository import GObject
from gi.repository import Notify



def run_parallel(commands_file, remove=True):
	command=['parallel', '-k', '-a', commands_file]
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


class MyNotification(GObject.Object):

    def __init__(self):

        super(MyNotification, self).__init__()
        # lets initialise with the application name
        Notify.init("myapp_name")

    def send_notification(self, title, text, file_path_to_icon=""):

        n = Notify.Notification.new(title, text, file_path_to_icon)
        n.show()


class Epub:

	def __init__(self, filename,lang):
		self.filename=filename
		self.lang=lang
		self.tmp_dir='.'+uuid.uuid4().hex
		self.sizes=dict()


	def get_lines(self):
		command=['calibre-debug', '-r', 'EpubSplit', self.filename]
		p=subprocess.Popen(command, stdout=subprocess.PIPE)
		output = p.stdout.read()
		output=output.split('\n')

		for line in output:
			if 'Line Number: ' in line:
				max_line=line.replace('Line Number: ','')

		return max_line


	def split(self):
		if not os.path.exists(self.tmp_dir):
			os.makedirs(self.tmp_dir)

		chapter_lines=self.get_lines()
		digit_size=len(chapter_lines)

		if int(chapter_lines)<1:
			shutil.copyfile(self.filename, self.tmp_dir+'/'+self.filename)

		else:
			split_commands='.'+uuid.uuid4().hex+'.txt'
			with open(split_commands,'w') as commands:
				for i in range(int(chapter_lines)):
					number=str(i+1).rjust(digit_size, '0')
					new_name=self.filename[:-5]+'_'+number

					commands.write('calibre-debug --run-plugin EpubSplit -- -l '+self.lang+' -o "'+self.tmp_dir+'/'+new_name+'" "'+self.filename+'" '+str(i+1)+'\n')

			run_parallel(split_commands)	


	def epub2txt(self):
		epub2txt_commands='.'+uuid.uuid4().hex+'.txt'
		with open(epub2txt_commands, 'w') as commands:
			for epub in sorted(os.listdir(self.tmp_dir)):
				if epub.endswith(".epub"):
					txt_name=epub[:-5]+'.txt'
					commands.write('ebook-convert "'+self.tmp_dir+'/'+epub+'" "'+self.tmp_dir+'/'+txt_name+'"\n')

		run_parallel(epub2txt_commands)


	def word_count(self):
		wc_commands='.'+uuid.uuid4().hex+'.txt'
		with open(wc_commands, 'w') as commands:
			for txt in sorted(os.listdir(self.tmp_dir)):
				if txt.endswith(".txt") and not txt.endswith("_es.txt"):
					commands.write('wc -w "'+self.tmp_dir+'/'+txt+'"\n')

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
			filename=s.replace('.txt','.epub')

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
		basename=self.filename[:-5]
		with open(chunks_commands, 'w') as commands:
			for i, c in enumerate(chunks):
				number=str(i+1).rjust(digit_size, '0')
				new_name=basename+'_chunk_'+number+'.epub'

				commands.write('calibre-debug --run-plugin EpubMerge -- -l es -n -t "'+basename+'" -o "'+new_name+'" ')

				if isinstance(c, str):
					commands.write('"'+c+'"\n')

				else:
					for n, e in enumerate(c):
						if n == len(c)-1:
							commands.write('"'+e+'"\n')
						else:
							commands.write('"'+e+'" ')

		run_parallel(chunks_commands)


	def clean_dir(self):
		shutil.rmtree(self.tmp_dir)


	def translate(self):
		trans_commands='.'+uuid.uuid4().hex+'.txt'
		with open(trans_commands, 'w') as commands:
			for txt in sorted(os.listdir(self.tmp_dir)):
				if txt.endswith(".txt"):
					es_name=txt[:-4]+'_es.txt'
					commands.write('trans :es -no-auto -b -i "'+self.tmp_dir+'/'+txt+'" -o  "'+self.tmp_dir+'/'+es_name+'"\n')

		run_parallel(trans_commands)


	def clean_null(self):
		clean_commands='.'+uuid.uuid4().hex+'.txt'
		with open(clean_commands, 'w') as commands:
			for txt in sorted(os.listdir(self.tmp_dir)):
				if txt.endswith("_es.txt"):
					commands.write('sed -i -e "s/null//g" "'+self.tmp_dir+'/'+txt+'"\n')

		run_parallel(clean_commands)


	def txt2epub(self):
		txt2epub_commands='.'+uuid.uuid4().hex+'.txt'
		with open(txt2epub_commands, 'w') as commands:
			for txt in sorted(os.listdir(self.tmp_dir)):
				if txt.endswith("_es.txt"):
					epub_name=txt.replace('_es.txt','.epub')
					commands.write('ebook-convert "'+self.tmp_dir+'/'+txt+'" "'+self.tmp_dir+'/'+epub_name+'" --no-default-epub-cover --input-encoding=UTF-8\n')

		run_parallel(txt2epub_commands)


if __name__ == "__main__":

	paths=sys.argv[1:]
	translation=False
	if translation:
		lang='en'
	else:
		lang='es'

	my = MyNotification()
	my.send_notification("Epub tools", "Creating chunks process in progress...")

	for p in sorted(paths):
		ebook=Epub(p,lang)
		ebook.split()
		ebook.epub2txt()
		ebook.word_count()
		ebook.create_chunks()
		ebook.clean_dir()
	

	my.send_notification("Epub tools", str(len(paths))+" files have been splitted in chunks!")




