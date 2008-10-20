#!/usr/bin/env python
from __future__ import with_statement
import time
import sys
import os, os.path


BASEDIR = os.path.expanduser('~/.donemanager')
if not os.path.exists(BASEDIR):
   os.mkdir(BASEDIR)


def log(message, fn):
    with open(fn, 'a') as sink:
        sink.write('%s %s\n'%(time.ctime(), message))


def parze(fn):
    with open(fn) as source:
        for l in source:
            last = time.strptime(l[:24])
            print l.strip()
    age = int(time.time() - time.mktime(last))/60
    print "Time since last action %2i hours %2i minutes"%(age/60, age%60)
    

if __name__ == '__main__':
    todaysfile = time.strftime(BASEDIR+'/%Y%m%d.txt')
    if len(sys.argv) < 2:
        parze(todaysfile)
    else:
        log(sys.argv[1], todaysfile)
