import rpyc

class ListenerService(rpyc.Service):
    def exposed_message(self, message):
        print message


if __name__ == '__main__':
    from rpyc.utils.server import ThreadedServer
    ts = ThreadedServer(Listener, port=18861)
    ts.start()

