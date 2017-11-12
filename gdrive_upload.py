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

my.send_notification("Google Drive", "Uploading "+str(len(paths))+" files to Google Drive!")

gdrive_upload(paths)

my.send_notification("Google Drive", str(len(paths))+" files have been uploaded to Google Drive!")
