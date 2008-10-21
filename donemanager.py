#!/usr/bin/env python
from __future__ import with_statement
import time
import sys
import os, os.path


def log(message, fn):
    with open(fn, 'a') as sink:
        sink.write('%s %s\n'%(time.ctime(), message))


def parze(fn):
    with open(fn) as source:
        for l in source:
            t, d = l[:24].strip(), l[24:].strip()
            yield time.strptime(t), d
    

if __name__ == '__main__':
    BASEDIR = os.path.expanduser('~/.donemanager')
    if not os.path.exists(BASEDIR):
       os.mkdir(BASEDIR)
    todaysfile = time.strftime(BASEDIR+'/%Y%m%d.txt')
    if len(sys.argv) < 2:
        for t, m in parze(todaysfile):
            print t, m
        age = int(time.time() - time.mktime(t))/60
        print "Time since last action %2i hours %2i minutes"%(age/60, age%60)
    else:
        log(sys.argv[1], todaysfile)
