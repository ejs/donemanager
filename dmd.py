#!/usr/bin/env python
from __future__ import with_statement
import rpyc
import time
import sys
import os, os.path
import datetime


def clean(s):
    return ''.join(c for c in s.lower() if c.isalnum())


class ListenerService(rpyc.Service):
    def on_connect(self):
        self.exposed_basedir = os.path.expanduser('~/.donemanager')

    def exposed_log(self, message):
        print message
        with open(self._get_file(), 'a') as sink:
            sink.write('%s %s\n'%(time.ctime(), message))

    def exposed_history(self, age):
        print 'loading from ', age, 'ago'
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


if __name__ == '__main__':
    from rpyc.utils.server import ThreadedServer
    ts = ThreadedServer(ListenerService, port=18861)
    ts.start()
