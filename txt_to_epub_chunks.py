#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys, subprocess, uuid, gi
gi.require_version('Notify', '0.7')
from joblib import Parallel, delayed
from gi.repository import GObject
from gi.repository import Notify
from desktop_tools import *
from langdetect import detect


paths=sys.argv[1:]
my = MyNotification()

my.send_notification("Desktop tools", "Merging "+str(len(paths))+" files to epub chunks!")

lang=detect_lang(paths)

myJob=DesktopJob(paths, lang)
myJob.copy_to_tmp()
myJob.txt2epub(myJob.tmp_txt_files)
myJob.word_count()
myJob.create_chunks()
myJob.clean_dir()

my.send_notification("Desktop tools", str(len(paths))+" files have been converted to epub chunks!")
