#!/usr/bin/env python
from __future__ import with_statement
import rpyc
import time
import sys
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
    def on_connect(self):
        self.exposed_basedir = os.path.expanduser('~/.donemanager')
        self.exposed_settings = Settings(self.exposed_basedir+'/config.yaml')
        if not self.exposed_settings:
            self.exposed_settings['days_per_week'] = 5
            self.exposed_settings['hours_per_day'] = 7
            self.exposed_settings.save_settings()

    def exposed_log(self, message):
        with open(self._get_file(), 'a') as sink:
            sink.write('%s %s\n'%(time.ctime(), message))

    def exposed_history(self, age):
        fn = self._get_file(age)
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

    def _get_file(self, age=0):
        if not os.path.exists(self.exposed_basedir):
           os.mkdir(self.exposed_basedir)
        date = datetime.datetime.now()-datetime.timedelta(days=age, hours=6)
        return date.strftime(self.exposed_basedir+'/%Y%m%d.txt')

    def exposed_now(self):
        return time.time()


if __name__ == '__main__':
    from rpyc.utils.server import ThreadedServer
    ts = ThreadedServer(ListenerService, port=18861)
    ts.start()
