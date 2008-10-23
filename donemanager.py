#!/usr/bin/env python
from __future__ import with_statement
import time
import sys
import os, os.path


def logmessage(message, fn):
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


def basicdisplay(log, aim=7):
    """aim is the number of hours that should be worked over this time period."""
    for t, m in log:
        yield "%40s %s"%(time.ctime(time.mktime(t)), m)
    yield ''
    for task, tm in groupeddisplay(log):
        yield "% 40s %2i:%02i"%(task, tm/60, tm%60)
    yield ''
    for line in summerydisplay(log, aim):
        yield line


def summerydisplay(log, aim=7):
    """aim is the number of hours that should be worked over this time period."""
    validtime = sum(tm for task, tm in groupeddisplay(log) if not task.endswith('**'))
    mostrecent = max(i[0] for i in log)
    age = int(time.time() - time.mktime(mostrecent))/60
    togo = aim*60 - validtime
    yield "Time since last action %2i hours %2i minutes"%(age/60, age%60)
    yield "Usefull time today     %2i hours %2i minutes"%(validtime/60, validtime%60)
    if togo > 0:
        yield "You should still work  %2i hours %2i minutes"%(togo/60, togo%60)
    else:
        yield "Congratulations. have a rest."


def weeklysummery():
    valid = [todaysfile]
    actions = {}
    for day in valid:
        for ta, tm in groupeddisplay(parze(day)):
           actions[ta] = actions.get(ta, 0) + tm 
    validtime = sum(actions[task] for task in actions if not task.endswith('**'))
    wasted  = sum(actions[task] for task in actions if task.endswith('**'))
    togo = len(valid)*7*60 - validtime
    yield "Over the %i days you worked in the last week you."%len(valid)
    yield "Used   time     %2i hours %2i minutes"%(validtime/60, validtime%60)
    yield "Wasted time     %2i hours %2i minutes"%(wasted/60, wasted%60)
    yield "You should have worked %i hours."%(7*len(valid), )
    if togo > 0:
        yield "To still do this you would have to work a further %i hours  %i today"%(togo/60, togo%60)
    else:
        yield "Congratulations. have a rest."


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
            log = [(t, m) for t, m in parze(todaysfile)]
            for line in summerydisplay(log):
                print line
        if sys.argv[1] == '-w':
            for line in weeklysummery():
                print line
    else:
        logmessage(sys.argv[1], todaysfile)
