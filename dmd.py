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
                flag = 0
                for k, g in itertools.groupby(source, key=lambda l: clean(l[24:])):
                    l = list(g)[-1]
                    when, message = l[:24].strip(), l[24:].strip()
                    yield time.mktime(time.strptime(when)), message
                    flag = time.mktime(time.strptime(when))

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

    def exposed_aim(self, period, high):
        def convert(s):
            if s == '-':
                return 0
            else:
                a, b = s.split(':')
                return int(a)*60+int(b)

        active = sum(1 for i in range(period) if self.exposed_log_exists(i))
        active = min(active, high)
        source = self.exposed_file('/caps.txt', 'r')
        caps = ((s.strip() for s in l.split('\t')) for l in source if l[0] != '#')
        caps = dict((a, [active*convert(b), active*convert(c)]) for a, b, c in caps)
        return caps

    def exposed_grouped(self, age):
        totals = {}
        keys = {}
        last = None
        for t, m in self.exposed_history(age):
            if last:
                k = keys.setdefault(clean(m), m)
                totals[k] = totals.get(k, 0) + t - last
            last = t
        for task in sorted(totals, key=(lambda k:totals[k]), reverse=True):
            tt = int(totals[task]/60)
            yield task, tt


if __name__ == '__main__':
    from rpyc.utils.server import ThreadedServer
    ts = ThreadedServer(ListenerService, port=18861)
    ts.start()
