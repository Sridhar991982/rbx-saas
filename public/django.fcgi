#!/usr/bin/python
import os
import sys

_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_PROJECT_DIR, 'lib'))
sys.path.insert(0, os.path.join(_PROJECT_DIR, 'rbx'))
sys.path.insert(0, _PROJECT_DIR)

_PROJECT_NAME = os.path.basename(_PROJECT_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.servers.fastcgi import runfastcgi

runfastcgi(method='threaded', daemonize='false')
