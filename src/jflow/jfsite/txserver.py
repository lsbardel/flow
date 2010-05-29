import settings
from unuk.core.txdjango.server import Server

server = Server(settings)
application = server.serve()
    



