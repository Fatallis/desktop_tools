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



class MyNotification(GObject.Object):

    def __init__(self):

        super(MyNotification, self).__init__()
        # lets initialise with the application name
        Notify.init("myapp_name")

    def send_notification(self, title, text, file_path_to_icon=""):

        n = Notify.Notification.new(title, text, file_path_to_icon)
        n.show()



if __name__ == "__main__":

	paths=sys.argv[1:]

	my = MyNotification()
	my.send_notification("TXT tools", "Converting txt files to epub in progress...")

	txt2epub_commands='.'+uuid.uuid4().hex+'.txt'
	with open(txt2epub_commands, 'w') as commands:
		for p in sorted(paths):
			epub_name=p.replace('.txt','.epub')
			commands.write('ebook-convert "'+p+'" "'+epub_name+'" --no-default-epub-cover --input-encoding=UTF-8\n')

	run_parallel(txt2epub_commands)
	my.send_notification("TXT tools", str(len(paths))+" files have been converted!")




