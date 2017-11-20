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

my.send_notification("Desktop Tools", "Converting "+str(len(paths))+" pdf files to txt!")

pdftotext(paths)

my.send_notification("Desktop Tools", str(len(paths))+" files have been converted to txt!")
