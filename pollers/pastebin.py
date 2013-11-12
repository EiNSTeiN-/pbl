
import re
import time
import requests

import pbl.pollers
from pbl.pollers.baseentry import BaseEntry
from pbl.pollers.recentitemspoller import RecentItemsDownloader
from pbl.pollers.recentitemspoller import RecentItemsPoller


class PastebinEntry(BaseEntry):

    def __init__(self, data, metadata):
        BaseEntry.__init__(self, 'pastebin', data, metadata)
        return


class PastebinDownloadQueue(RecentItemsDownloader):
    """ Downloader thread for pastebin. """

    def __init__(self, name, interval):
        RecentItemsDownloader.__init__(self, name, interval)

        self.download_url = 'http://pastebin.com/download.php?i={id}'
        self.details_url = 'http://pastebin.com/{id}'

        self.details_regexp = dict(
            title=r'<h1>(?!Untitled)(.*?)</h1>',
            user=r'By: <a href="\/u\/([^"]*)">[^<]*<\/a>',
            syntax=r'syntax: <a href="[^"]*">(?!None)([^<]*)</a>',
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
        if r.status_code == 404:
            # paste id not found...
            self.echo('paste id was removed %s' % (id, ))
            return True

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

        if 'Hey, it seems you are requesting a little bit too much from Pastebin. Please slow down!' in details:
            # we'll try again later...
            return False

        for rname in self.details_regexp:
            # Title
            m = re.search(self.details_regexp[rname], details, re.DOTALL)
            if m:
                metadata[rname] = m.group(1)

        entry = PastebinEntry(data, metadata)

        if entry.match():
            entry.keep()

        return True


class Pastebin(RecentItemsPoller):
    """ Basically just set a custom downloader here. """

    def __init__(self, name, interval, poll_url, regexp):

        RecentItemsPoller.__init__(self, name, interval, poll_url, regexp)

        self.downloader = PastebinDownloadQueue(name='%s/downloader' % (self.name, ), interval=0.2)

        return
