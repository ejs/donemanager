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
    

def timedisplay(fn):
    for t, m in parze(fn):
        yield "%s\t%s"%(time.ctime(time.mktime(t)), m)


def groupeddisplay(fn):
    totals = {}
    last = None
    for t, m in parze(fn):
        if last:
            totals[m] = totals.get(m, 0) + time.mktime(t) - time.mktime(last)
        last = t
    for task in sorted(totals, key=(lambda k:totals[k])):
        tt = int(totals[task]/60)
        yield task, "%2i:%02i"%(tt/60, tt%60)
    age = int(time.time() - time.mktime(t))/60
    yield "Time since last action %2i hours %2i minutes"%(age/60, age%60)


if __name__ == '__main__':
    BASEDIR = os.path.expanduser('~/.donemanager')
    if not os.path.exists(BASEDIR):
       os.mkdir(BASEDIR)
    todaysfile = time.strftime(BASEDIR+'/%Y%m%d.txt')
    if len(sys.argv) < 2:
        for line in timedisplay(todaysfile):
            print line
        for line in groupeddisplay(todaysfile):
            print line
    else:
        log(sys.argv[1], todaysfile)
