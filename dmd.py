import rpyc
import donemanager
import os.path

class ListenerService(rpyc.Service):
    def on_connect(self):
        self.basedir = os.path.expanduser('~/.donemanager')

    def exposed_log(self, message):
        print message
        donemanager.clean_log(message, self.basedir)

    def exposed_history(self, age):
        print 'loading from ', age, 'ago'
        for i in donemanager.clean_parze(self.basedir, age):
            yield i


if __name__ == '__main__':
    from rpyc.utils.server import ThreadedServer
    ts = ThreadedServer(ListenerService, port=18861)
    ts.start()

