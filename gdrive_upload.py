#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys, subprocess, uuid, gi
gi.require_version('Notify', '0.7')
from joblib import Parallel, delayed
from gi.repository import GObject
from gi.repository import Notify


class MyNotification(GObject.Object):
    def __init__(self):

        super(MyNotification, self).__init__()
        # lets initialise with the application name
        Notify.init("myapp_name")

    def send_notification(self, title, text, file_path_to_icon=""):

        n = Notify.Notification.new(title, text, file_path_to_icon)
        n.show()

my = MyNotification()


def save_tmp_file(paths):
	tmp_file='.'+uuid.uuid4().hex+'.txt'
	with open(tmp_file,'w') as tmp:
		for p in paths:
			tmp.write(p+'\n')

	return tmp_file


def gdrive_upload(tmp_file):
	p1=subprocess.Popen(['cat', tmp_file], stdout=subprocess.PIPE)
	p2=subprocess.Popen(['parallel', '/home/fatallis/.linuxbrew/bin/gdrive', 'upload', '{}'], stdin=p1.stdout, stdout=subprocess.PIPE)
	p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
	output = p2.communicate()[0]


paths=sys.argv[1:]

num_cores=4

my.send_notification("Google Drive", "Uploading "+str(len(paths))+" files to Google Drive!")

tmp_file=save_tmp_file(paths)
gdrive_upload(tmp_file)
os.remove(tmp_file)

my.send_notification("Google Drive", str(len(paths))+" files have been uploaded to Google Drive!")
