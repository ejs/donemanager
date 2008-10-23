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
        lm = None
        for l in source:
            t, m = l[:24].strip(), l[24:].strip()
            if m != lm:
                yield time.strptime(t), m
            lm = m


def groupeddisplay(log):
    totals = {}
    last = None
    for t, m in log:
        if last:
            totals[m] = totals.get(m, 0) + time.mktime(t) - time.mktime(last)
        last = t
    for task in sorted(totals, key=(lambda k:totals[k])):
        tt = int(totals[task]/60)
        yield task, tt


if __name__ == '__main__':
    BASEDIR = os.path.expanduser('~/.donemanager')
    if not os.path.exists(BASEDIR):
       os.mkdir(BASEDIR)
    todaysfile = time.strftime(BASEDIR+'/%Y%m%d.txt')
    if len(sys.argv) < 2:
        log = [(t, m) for t, m in parze(todaysfile)]
        validtime = 0
        for line in log:
            print "%s\t%s"%(time.ctime(time.mktime(t)), m)
        print
        for task, tm in groupeddisplay(log):
            print "%s\t%2i:%02i"%(task, tm/60, tm%60)
            if not task.endswith('**'):
                validtime += tm
        mostrecent = max(i[0] for i in log)
        age = int(time.time() - time.mktime(mostrecent))/60
        print "Time since last action %2i hours %2i minutes"%(age/60, age%60)
        print "Usefull time today     %2i hours %2i minutes"%(validtime/60, validtime%60)
        togo = 7*60 - validtime
        print "You should still work  %2i hours %2i minutes"%(togo/60, togo%60)
    else:
        log(sys.argv[1], todaysfile)
