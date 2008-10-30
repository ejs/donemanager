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


def aim(basedir, period):
    pass
    # load from file formated task name\tdaylow-high\tweeklow-high\tmonthlow-high
    # chose period to check over depending on number of days 'active'
    # return dict of clean -> (low, high)

if __name__ == '__main__':
    basedir = os.path.expanduser('~/.donemanager')
    if len(sys.argv) > 1 and sys.argv[1].startswith('-'):
        if sys.argv[1] == '-s':
            log = summery(basedir, 1)
        elif sys.argv[1] == '-w':
            log = summery(basedir, 7)
        elif sys.argv[1] == '-m':
            log = summery(basedir, 7*4)
        else:
            print "Defaulting to single day check, use flags for other periods."
            print
            log = summery(basedir, 1)
        for l in log:
            print l, log[l]
