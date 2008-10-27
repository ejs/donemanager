#!/usr/bin/env python
from __future__ import with_statement
import time
import sys
import os, os.path
import datetime
import yaml


class Settings(object):
    def __init__(self, filename):
        self.filename = filename
        self.load_settings()

    def __getitem__(self, item):
        return self.settings[item]

    def __contains__(self, item):
        return item in self.settings

    def __setitem__(self, item, value):
        self.settings[item] = value

    def __len__(self):
        return len(self.settings)

    def load_settings(self):
        try:
            with open(self.filename, 'r') as source:
                self.settings = yaml.load(source)
            if not self.settings:
                self.settings = {}
        except:
            self.settings = {}

    def save_settings(self):
        with open(self.filename,'w') as sink:
            yaml.dump(self.settings, sink)


def logmessage(message, basedir):
    if not os.path.exists(basedir):
       os.mkdir(basedir)
    date = datetime.datetime.now()-datetime.timedelta(hours=6)
    fn = date.strftime(basedir+'/%Y%m%d.txt')
    with open(fn, 'a') as sink:
        sink.write('%s %s\n'%(time.ctime(), message))


def clean(s):
    return ''.join(c for c in s.lower() if c.isalnum())


def parze(basedir, age=0):
    if not os.path.exists(basedir):
       os.mkdir(basedir)
    date = datetime.datetime.now()-datetime.timedelta(days=age, hours=6)
    fn = date.strftime(basedir+'/%Y%m%d.txt')
    if os.path.exists(fn):
        with open(fn) as source:
            lt, lm = None, None
            for l in source:
                t, m = l[:24].strip(), l[24:].strip()
                if lm and clean(m) != clean(lm):
                    yield time.mktime(time.strptime(lt)), lm
                lm = m
                lt = t
            if lm and lt:
                yield time.mktime(time.strptime(lt)), lm


def groupeddisplay(log):
    totals = {}
    keys = {}
    last = None
    for t, m in log:
        if last:
            k = keys.setdefault(clean(m), m)
            totals[k] = totals.get(k, 0) + t - last
        last = t
    for task in sorted(totals, key=(lambda k:totals[k]), reverse=True):
        tt = int(totals[task]/60)
        yield task, tt


def basicdisplay(log, aim):
    """aim is the number of hours that should be worked over this time period."""
    for t, m in log:
        yield "%40s %s %s"%(time.ctime(t), '*' if m.endswith('**') else ' ', m.rstrip('* '))
    yield ''
    for task, tm in groupeddisplay(log):
        yield "% 40s %s %2i:%02i"%(task.rstrip('* '), '*' if task.endswith('**') else ' ', tm/60, tm%60)
    yield ''
    for line in daysummery(log, aim):
        yield line


def daysummery(log, aim):
    """aim is the number of hours that should be worked over this time period."""
    actions = {}
    for ta, tm in groupeddisplay(log):
       actions[ta] = actions.get(ta, 0) + tm 
    validtime = sum(actions[task] for task in actions if not task.endswith('**'))
    wasted  = sum(actions[task] for task in actions if task.endswith('**'))
    mostrecent = max(i[0] for i in log)
    age = int(time.time() - mostrecent)/60
    togo = aim*60 - validtime
    yield "Usefull time today     %2i hours %2i minutes"%(validtime/60, validtime%60)
    yield "Wasted time            %2i hours %2i minutes"%(wasted/60, wasted%60)
    if togo > 0:
        yield "You should still work  %2i hours %2i minutes"%(togo/60, togo%60)
    else:
        yield "Congratulations. have a rest."
    yield ''
    yield "Time since last action %2i hours %2i minutes"%(age/60, age%60)


def longsummery(days, workingdays, aim):
    """
        days : the number of days to search back for existing files.
        workingdays : the aimed numner of days to work in this time.
    """
    valid = 0
    actions = {}
    keys = {}
    for day in range(days):
        flag = 0
        for ta, tm in groupeddisplay(parze(basedir, day)):
            flag = 1
            k = keys.setdefault(clean(ta), ta)
            actions[k] = actions.get(k, 0) + tm 
        valid += flag
    validtime = sum(actions[task] for task in actions if not task.endswith('**'))
    wasted  = sum(actions[task] for task in actions if task.endswith('**'))
    togo = min(workingdays, valid)*aim*60 - validtime
    for task in sorted(actions, key=lambda t:actions[t], reverse=True):
        yield "% 40s %s %2i:%02i"%(task.rstrip('* '), '*' if task.endswith('**') else ' ', actions[task]/60, actions[task]%60)
    yield "Over the %i days you worked %i."%(days, valid)
    if valid >= days:
        yield "Welldone, you are aimed for %i days."%workingdays
    else:
        yield "You are aiming for %i days so you are %i short"%(workingdays, workingdays-valid)
    yield "Used   time     %2i hours %2i minutes"%(validtime/60, validtime%60)
    yield "Wasted time     %2i hours %2i minutes"%(wasted/60, wasted%60)
    yield "You should have worked %i hours."%(aim*valid, )
    if togo > 0:
        yield "To still do this you would have to work a further %i hours %i minutes today"%(togo/60, togo%60)
    else:
        yield "Congratulations. have a rest."


if __name__ == '__main__':
    basedir = os.path.expanduser('~/.donemanager')
    settings = Settings(basedir+'/config.yaml')
    if not settings:
        settings['days_per_week'] = 5
        settings['hours_per_day'] = 7
        settings.save_settings()
    if len(sys.argv) < 2:
        log = [(t, m) for t, m in parze(basedir)]
        for line in basicdisplay(log, settings['hours_per_day']):
            print line
    elif sys.argv[1].startswith('-'):
        if sys.argv[1] == '-s':
            log = [(t, m) for t, m in parze(basedir)]
            for line in daysummery(log, settings['hours_per_day']):
                print line
        if sys.argv[1] == '-w':
            for line in longsummery(7, settings['days_per_week'], settings['hours_per_day']):
                print line
        if sys.argv[1] == '-m':
            for line in longsummery(7*4, settings['days_per_week']*4, settings['hours_per_day']):
                print line
    else:
        logmessage("".join(sys.argv[1:]), basedir)
