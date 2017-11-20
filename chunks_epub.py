#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys, subprocess, uuid, shutil, fileinput, gi
gi.require_version('Notify', '0.7')
from joblib import Parallel, delayed
from gi.repository import GObject
from gi.repository import Notify
from desktop_tools import *
from langdetect import detect


if __name__ == "__main__":

	paths=sys.argv[1:]

	my = MyNotification()
	my.send_notification("Desktop tools", "Creating chunks process in progress...")

	lang=detect_lang(paths)

	for p in sorted(paths):
		ebook=DesktopJob(p,lang)
		ebook.create_dir()
		ebook.split()
		ebook.epub2txt()
		ebook.word_count()
		ebook.create_chunks()
		ebook.clean_dir()
	
	my.send_notification("Desktop tools", str(len(paths))+" files have been splitted in chunks!")




