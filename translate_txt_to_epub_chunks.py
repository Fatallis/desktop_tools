#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys, subprocess, uuid, gi
gi.require_version('Notify', '0.7')
from joblib import Parallel, delayed
from gi.repository import GObject
from gi.repository import Notify
from desktop_tools import *


paths=sys.argv[1:]
my = MyNotification()

my.send_notification("Desktop Tools", "Translating "+str(len(paths))+" files!")

myJob=DesktopJob(paths,'en')
myJob.copy_to_tmp()
myJob.translate()
myJob.clean_null()
myJob.improve_translation()
myJob.txt2epub(myJob.tmp_txt_trans_files)
myJob.word_count()
myJob.create_chunks()
myJob.clean_dir()

my.send_notification("Desktop Tools", str(len(paths))+" files have been translated!")