import rpyc

server = rpyc.connect('localhost', 18861)
print server.root.get_service_name()
server.root.message("Hi")

server = rpyc.connect_by_service('LISTENER')
server.root.message("There")
