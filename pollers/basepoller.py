import sys
import threading
import re


class BasePoller(threading.Thread):

    def __init__(self, name, interval):
        threading.Thread.__init__(self)

        self.name = name
        self.interval = interval

        return

    def echo(self, s):
        print '[%s] %s' % (self.name, s)
        sys.stdout.flush()

    def run(self):
        """ Override this. """
        raise RuntimeError('This Poller does Nothing!')

