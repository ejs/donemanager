import rpyc
import donemanager
import os.path

class ListenerService(rpyc.Service):
    def on_connect(self):
        self.basedir = os.path.expanduser('~/.donemanager')

    def exposed_log(self, message):
        print message
        donemanager.clean_log(message, self.basedir)


if __name__ == '__main__':
    from rpyc.utils.server import ThreadedServer
    ts = ThreadedServer(ListenerService, port=18861)
    ts.start()

