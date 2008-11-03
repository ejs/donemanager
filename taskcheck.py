#!/usr/bin/env python
from __future__ import with_statement
import donemanager
import sys
import os, os.path
import datetime
import yaml


def summery(basedir, period):
    actions = {}
    keys = {}
    for day in range(period):
        flag = 0
        for ta, tm in donemanager.groupeddisplay(donemanager.parze(basedir, day)):
            flag = 1
            k = keys.setdefault(donemanager.clean(ta), ta)
            actions[k] = actions.get(k, 0) + tm 
    return actions
    validtime = sum(actions[task] for task in actions if not task.endswith('**'))


def agedfile(basedir, age):
    date = datetime.datetime.now()-datetime.timedelta(days=age, hours=6)
    fn = date.strftime(basedir+'/%Y%m%d.txt')
    return os.path.exists(fn)


def aim(basedir, period, high):
    def convert(s):
        if s == '-':
            return 0
        else:
            a, b = s.split(':')
            return int(a)*60+int(b)

    active = sum(1 for i in range(period) if agedfile(basedir, i))
    active = min(active, high)
    with open(basedir+'/caps.txt', 'r') as source:
        caps = ((s.strip() for s in l.split('\t')) for l in source if l[0] != '#')
        caps = dict((a, [active*convert(b), active*convert(c)]) for a, b, c in caps)
        # add check that the low point is below the high point
    return caps


if __name__ == '__main__':
    basedir = os.path.expanduser('~/.donemanager')
    if len(sys.argv) < 2  or sys.argv[1] == '-d':
        log = summery(basedir, 1)
        target = aim(basedir, 1, 1)
    elif sys.argv[1] == '-w':
        log = summery(basedir, 7)
        target = aim(basedir, 7, 5)
    elif sys.argv[1] == '-m':
        log = summery(basedir, 7*4)
        target = aim(basedir, 7*4, 5*4)
    log = dict((donemanager.clean(n), log[n]) for n in log)

    for l in target:
        cl = donemanager.clean(l)
        if cl in log:
            if target[l][0] and log[cl] < target[l][0]:
                print "To little time spent on %s (%s should be at least %s)"%(l, donemanager.long_time(log[cl]), donemanager.long_time(target[l][0]))
            elif target[l][1] and log[cl] > target[l][1]:
                print "To  much  time spent on %s (%s should be at most %s)"%(l, donemanager.long_time(log[cl]), donemanager.long_time(target[l][1]))
        elif target[l][0]:
            print "You should spend some time on %s (aiming for at least %s)"%(l, donemanager.long_time(target[l][0]))
