'''Twisted server for jfsite.
To run the server type:
twistd -ny txserver.py'''

import settings
from unuk.core.txdjango.server import Server

server = Server(settings)
application = server.serve()




