'''Twisted server for jfsite.
To run the server type:
python txstart.py -ny'''
from twisted.scripts.twistd import run
import sys

sys.argv.append('txserver.py')

run()