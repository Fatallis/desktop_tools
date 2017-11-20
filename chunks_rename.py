#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys, subprocess, uuid, gi
gi.require_version('Notify', '0.7')
from joblib import Parallel, delayed
from gi.repository import GObject
from gi.repository import Notify


new_pattern=sys.argv[1]

for file in os.listdir('.'):
    if file.startswith("A_selection"):
    	newfile=file.replace('A_selection',new_pattern)
        os.rename(file,newfile)

