#!/usr/bin/python

import sys

INSTALLATION_PATH = '/var/www/pbl'

sys.path.append(INSTALLATION_PATH)

from pbl import daemon
from pbl import poll


class PollDaemon(daemon.Daemon):
    def run(self):
        poll.main()

if __name__ == "__main__":
        daemon = PollDaemon('/tmp/poll-daemon.pid', stdout='/var/log/pbl.log', stderr='/var/log/pbl-errors.log')
        if len(sys.argv) == 2:
                if 'start' == sys.argv[1]:
                        daemon.start()
                elif 'stop' == sys.argv[1]:
                        daemon.stop()
                elif 'restart' == sys.argv[1]:
                        daemon.restart()
                else:
                        print "Unknown command"
                        sys.exit(2)
                sys.exit(0)
        else:
                print "usage: %s start|stop|restart" % sys.argv[0]
                sys.exit(2)
