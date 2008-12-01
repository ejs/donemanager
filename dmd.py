#!/usr/bin/env python
from __future__ import with_statement
import itertools
import rpyc
import time
import os, os.path
import datetime
import yaml


def clean(s):
    return ''.join(c for c in s.lower() if c.isalnum())


def long_time(t):
    if t < 60:
        return '%i minutes'%t
    elif not t%60:
        return '%i hours'%(t/60)
    else:
        return '%i hours %i minutes'%(t/60, t%60)


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


class ListenerService(rpyc.Service):
    def __init__(self, con):
        rpyc.Service.__init__(self, con)
        self.exposed_basedir = os.path.expanduser('~/.donemanager')
        if not os.path.exists(self.exposed_basedir):
           os.mkdir(self.exposed_basedir)
        self.exposed_settings = Settings(self.exposed_basedir+'/config.yaml')
        if not self.exposed_settings:
            self.exposed_settings['days_per_week'] = 5
            self.exposed_settings['hours_per_day'] = 7
            self.exposed_settings.save_settings()

    def exposed_log(self, message):
        with open(self._get_file(), 'a') as sink:
            sink.write('%s %s\n'%(time.ctime(), message))

    def exposed_history(self, age=0):
        fn = self._get_file(age)
        if os.path.exists(fn):
            with open(fn) as source:
                for k, g in itertools.groupby(source, key=lambda l: clean(l[24:])):
                    l = list(g)[-1]
                    when, message = l[:24].strip(), l[24:].strip()
                    yield time.mktime(time.strptime(when)), message

    def _get_file(self, age=0):
        date = datetime.datetime.now() - datetime.timedelta(days=age, hours=6)
        return date.strftime(self.exposed_basedir+'/%Y%m%d.txt')

    def exposed_log_exists(self, age):
        date = datetime.datetime.now()-datetime.timedelta(days=age, hours=6)
        return os.path.exists(date.strftime(self.exposed_basedir+'/%Y%m%d.txt'))

    def exposed_file(self, name, mode):
        return open(self.exposed_basedir+name, mode)

    def exposed_now(self):
        return time.time()


if __name__ == '__main__':
    from rpyc.utils.server import ThreadedServer
    ts = ThreadedServer(ListenerService, port=18861)
    ts.start()
