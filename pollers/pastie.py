
import requests

import pbl.pollers
from pbl.pollers.baseentry import BaseEntry
from pbl.pollers.recentitemspoller import RecentItemsDownloader
from pbl.pollers.recentitemspoller import RecentItemsPoller


class PastieEntry(BaseEntry):

    def __init__(self, data, metadata):
        BaseEntry.__init__(self, 'pastie', data, metadata)
        return


class PastieDownloadQueue(RecentItemsDownloader):
    """ Downloader thread. """

    def __init__(self, name, interval):
        RecentItemsDownloader.__init__(self, name, interval)

        self.download_url = 'http://pastie.org/pastes/{id}/download'
        self.session = requests.session()

        return

    def process_id(self, id):
        """ From the ID of a paste, fetch the content and the metadata.
        Determine if the paste is worth keeping. """

        self.echo('processing %s [%u left]' % (id, len(self.queue)))

        url = self.download_url.format(id=id)
        r = self.session.get(url, **pbl.pollers.requestoptions)

        if not r.ok:
            self.echo('Problem downloading page %s, status=%s, error=%s' % (url, repr(r.status_code), repr(r.error)))
            return False

        data = r.content

        if 'Sorry, there is no pastie' in data:
            # paste id not found...
            self.echo('paste id was removed %s' % (id, ))
            return True

        metadata = {}
        metadata['uid'] = id
        metadata['url'] = url

        entry = PastieEntry(data, metadata)

        if entry.match():
            entry.keep()

        return True


class Pastie(RecentItemsPoller):
    """ Basically just set a custom downloader here. """

    def __init__(self, name, interval, poll_url, regexp):

        RecentItemsPoller.__init__(self, name, interval, poll_url, regexp)

        self.downloader = PastieDownloadQueue(name='%s/downloader' % (self.name, ), interval=0.2)

        return
