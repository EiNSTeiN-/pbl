
import re
import time
import requests

import pbl.pollers
from pbl.pollers.baseentry import BaseEntry
from pbl.pollers.recentitemspoller import RecentItemsDownloader
from pbl.pollers.recentitemspoller import RecentItemsPoller


class SlexyEntry(BaseEntry):

    def __init__(self, data, metadata):
        BaseEntry.__init__(self, 'slexy', data, metadata)
        return


class SlexyDownloadQueue(RecentItemsDownloader):
    """ Downloader thread. """

    def __init__(self, name, interval):
        RecentItemsDownloader.__init__(self, name, interval)

        self.download_url = 'http://slexy.org/raw/{id}'
        self.details_url = 'http://slexy.org/view/{id}'

        self.details_regexp = dict(
            user=r'Author: <b>(?!Anonymous)([^<]+)</b>',
            syntax=r'Language: <b>([^<]+)</b>',
            title=r'Description: <b>(?!No description)([^<]+)</b>',
            posted_on=r'Timestamp: <b>([^<]+)</b>',
        )

        self.session = requests.session()

        return

    def process_id(self, id):
        """ From the ID of a paste, fetch the content and the metadata.
        Determine if the paste is worth keeping. """

        self.echo('processing %s [%u left]' % (id, len(self.queue)))

        # First, download the raw content here

        url = self.download_url.format(id=id)
        r = self.session.get(url, **pbl.pollers.requestoptions)
        if not r.ok:
            self.echo('Problem downloading page %s, status=%s, error=%s' % (url, repr(r.status_code), repr(r.error)))
            return False

        data = r.content

        time.sleep(0.2)

        # Second, download the details of the entry (metadata)

        url = self.details_url.format(id=id)
        r = self.session.get(url, **pbl.pollers.requestoptions)
        details = r.content

        metadata = {}
        metadata['uid'] = id
        metadata['url'] = url

        for rname in self.details_regexp:
            m = re.search(self.details_regexp[rname], details, re.DOTALL)
            if m:
                metadata[rname] = m.group(1)

        entry = SlexyEntry(data, metadata)

        if entry.match():
            entry.keep()

        return True


class Slexy(RecentItemsPoller):
    """ Basically just set a custom downloader here. """

    def __init__(self, name, interval, poll_url, regexp):

        RecentItemsPoller.__init__(self, name, interval, poll_url, regexp)

        self.downloader = SlexyDownloadQueue(name='%s/downloader' % (self.name, ), interval=0.2)

        return
