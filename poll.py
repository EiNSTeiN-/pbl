#!/usr/bin/python

import time
import threading

from pbl.config import getcfg
from pbl.database import Database

from pbl import pollers
from pbl.pollers import POLLERS

from pbl.parser.parserthread import ParserThread


def main():

    proxy = getcfg('http_proxy')
    if proxy:
        print 'Using http proxy %s' % (proxy, )
        pollers.requestoptions['proxies'] = {'http': proxy, 'https': proxy}

    try:
        threading.stack_size(512 * 1024)
    except BaseException as e:
        print 'Error changing stack size:', repr(e)

    # Connect to the database...
    Database.get()

    parser = ParserThread()
    parser.start()

    for poller in POLLERS.values():
        poller.start()

    # wait for them to finish!
    for poller in POLLERS.values():
        while poller.is_alive():
            time.sleep(1)

    while parser.is_alive():
        time.sleep(1)

    return

if __name__ == '__main__':
    main()
