#!/usr/bin/env python
from __future__ import with_statement
import time
import sys
import os, os.path


BASEDIR = os.path.expanduser('~/.donemanager')
if not os.path.exists(BASEDIR):
   os.mkdir(BASEDIR)


def log(message, at):
    print time.asctime(at), message


if __name__ == '__main__':
    if len(sys.argv) < 1:
        print "Please enter a message."
    else:
        log(sys.argv[1], time.localtime())
