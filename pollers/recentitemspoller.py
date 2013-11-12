import requests
import traceback
import sys
import re
import time

import pbl.pollers
from pbl.pollers.basepoller import BasePoller
from pbl.config import getcfg, setcfg


class RecentItemsDownloader(BasePoller):
    """ Downloader thread for the recent items poller. """

    def __init__(self, name, interval):
        BasePoller.__init__(self, name, interval)

        self.queue = []
        self.timeouts = {}
        self.errors = {}

        self.daemon = True

        return

    def add_queue(self, items):
        self.queue += items
        return

    def process_page(self, id):
        raise RuntimeError('override this method in subclass.')

    def mark_timeout(self, id):

        # Remove this ID from the queue, possibly re-adding it later
        self.queue.remove(id)

        if id in self.timeouts:
            self.timeouts[id] += 1
        else:
            self.timeouts[id] = 1

        if self.timeouts[id] > 4:
            self.echo('giving up on %s after %u timeouts' % (id, self.timeouts[id], ))
            del self.timeouts[id]
        else:
            # move this id to the end of the queue to try again
            self.queue.append(id)

        return

    def mark_error(self, id):

        # Remove this ID from the queue, possibly re-adding it later
        self.queue.remove(id)

        if id in self.errors:
            self.errors[id] += 1
        else:
            self.errors[id] = 1

        if self.errors[id] > 4:
            self.echo('giving up on %s after %u errors' % (id, self.errors[id], ))
            del self.errors[id]
        else:
            # move this id to the end of the queue to try again
            self.queue.append(id)

        return

    def run(self):

        self.echo('started')

        while True:

            if len(self.queue) == 0:
                time.sleep(self.interval)
                continue

            try:
                id = self.queue[0]
                ok = self.process_id(id)

                if not ok:
                    self.echo('page processing failed %s' % (id, ))
                    continue

                # Clear up this ID from any queue it might be in.
                if id in self.timeouts:
                    del self.timeouts[id]
                if id in self.errors:
                    del self.errors[id]
                self.queue.remove(id)
            except requests.Timeout as e:
                self.echo('timeout while processing %s: %s' % (id, repr(e), ))

                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)

                self.mark_timeout(id)
            except BaseException as e:
                self.echo('error while processing %s: %s' % (id, repr(e)))

                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)

                self.mark_error(id)

            time.sleep(self.interval)

        self.echo('stopped')

        return


class RecentItemsPoller(BasePoller):
    """ Poll a "recent items" page and retrieve all IDs from that page. """

    def __init__(self, name, interval, poll_url, regexp, method='get'):

        BasePoller.__init__(self, name, interval)

        self.poll_url = poll_url
        self.regexp = regexp
        self.session = requests.session()
        self.method = method

        self.last_seen = getcfg('last_seen_%s' % (self.name, ))

        self.daemon = True

        self.downloader = None

        return

    def poll(self):

        r = self.session.request(self.method, self.poll_url, **pbl.pollers.requestoptions)
        page = r.content

#        print page
        matches = re.findall(self.regexp, page, flags=re.DOTALL)

        if len(matches) == 0:
            self.echo('found no matches, error?')
            return

        if self.last_seen and self.last_seen in matches:
            index = matches.index(self.last_seen)
            matches = matches[:index]
        elif self.last_seen:
            self.echo('last seen item could not be found, not polling fast enough?')

        if len(matches) > 0:
            self.last_seen = matches[0]
            setcfg('last_seen_%s' % (self.name, ), self.last_seen)

        self.echo('new items: %s' % (repr(matches), ))

        self.downloader.add_queue(matches)

        return

    def run(self):

        self.echo('started')
        self.downloader.start()

        while True:

            try:
                self.poll()
            except BaseException as e:
                self.echo('error polling: %s' % (repr(e), ))

                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)

            time.sleep(self.interval)

        return
