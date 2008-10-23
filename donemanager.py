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
        lt, lm = None, None
        for l in source:
            t, m = l[:24].strip(), l[24:].strip()
            if lm and m != lm:
                yield time.strptime(lt), lm
            lm = m
            lt = t
        if lm and lt:
            yield time.strptime(lt), lm


def groupeddisplay(log):
    totals = {}
    last = None
    for t, m in log:
        if last:
            totals[m] = totals.get(m, 0) + time.mktime(t) - time.mktime(last)
        last = t
    for task in sorted(totals, key=(lambda k:totals[k]), reverse=True):
        tt = int(totals[task]/60)
        yield task, tt


def basicdisplay(log):
    for t, m in log:
        yield "%40s %s"%(time.ctime(time.mktime(t)), m)
    yield ''
    for task, tm in groupeddisplay(log):
        yield "% 40s %2i:%02i"%(task, tm/60, tm%60)
    validtime = sum(tm for task, tm in groupeddisplay(log) if not task.endswith('**'))
    mostrecent = max(i[0] for i in log)
    age = int(time.time() - time.mktime(mostrecent))/60
    yield "Time since last action %2i hours %2i minutes"%(age/60, age%60)
    yield "Usefull time today     %2i hours %2i minutes"%(validtime/60, validtime%60)
    togo = 7*60 - validtime
    yield "You should still work  %2i hours %2i minutes"%(togo/60, togo%60)


def daysummerydisplay(fn):
    log = [(t, m) for t, m in parze(fn)]
    validtime = sum(tm for task, tm in groupeddisplay(log) if not task.endswith('**'))
    mostrecent = max(i[0] for i in log)
    age = int(time.time() - time.mktime(mostrecent))/60
    yield "Time since last action %2i hours %2i minutes"%(age/60, age%60)
    yield "Usefull time today     %2i hours %2i minutes"%(validtime/60, validtime%60)
    togo = 7*60 - validtime
    yield "You should still work  %2i hours %2i minutes"%(togo/60, togo%60)


if __name__ == '__main__':
    BASEDIR = os.path.expanduser('~/.donemanager')
    if not os.path.exists(BASEDIR):
       os.mkdir(BASEDIR)
    todaysfile = time.strftime(BASEDIR+'/%Y%m%d.txt')
    if len(sys.argv) < 2:
        log = [(t, m) for t, m in parze(todaysfile)]
        for line in basicdisplay(log):
            print line
    elif sys.argv[1].startswith('-'):
        if sys.argv[1] == '-s':
            for line in daysummerydisplay(todaysfile):
                print line
    else:
        log(sys.argv[1], todaysfile)
