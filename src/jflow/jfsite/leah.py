#
# Twisted RPC JSON server for jflow
#
import sys
from django.core.management import setup_environ

import settings

setup_environ(settings)

from jflow.log import setup_logging


def startserver(PORT):
    from twisted.internet import reactor
    from twisted.web import server
    from jflow.servers.dataport import jsonService
    from jflow.log import setup_logging
    logger = setup_logging('jflow')
    reactor.listenTCP(PORT, server.Site(jsonService(logger = logger)))
    logger.info("Starting on port %s" % PORT)
    reactor.run()


if __name__ == '__main__':
    argv = sys.argv
    if len(argv) == 2:
        port = int(argv[1])
    else:
        port = 8010
    startserver(port)