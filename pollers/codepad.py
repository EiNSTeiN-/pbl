
import requests

import pbl.pollers
from pbl.pollers.baseentry import BaseEntry
from pbl.pollers.recentitemspoller import RecentItemsDownloader
from pbl.pollers.recentitemspoller import RecentItemsPoller


class CodepadEntry(BaseEntry):

    def __init__(self, data, metadata):
        BaseEntry.__init__(self, 'codepad', data, metadata)
        return


class CodepadDownloadQueue(RecentItemsDownloader):
    """ Downloader thread. """

    def __init__(self, name, interval):
        RecentItemsDownloader.__init__(self, name, interval)

        self.download_url = 'http://codepad.org/{id}/raw.'
        self.session = requests.session()

        return

    def process_id(self, id):
        """ From the ID of a paste, fetch the content and the metadata.
        Determine if the paste is worth keeping. """

        self.echo('processing %s [%u left]' % (id, len(self.queue)))

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

        metadata = {}
        metadata['uid'] = id
        metadata['url'] = url

        entry = CodepadEntry(data, metadata)

        if entry.match():
            entry.keep()

        return True


class Codepad(RecentItemsPoller):
    """ Basically just set a custom downloader here. """

    def __init__(self, name, interval, poll_url, regexp):

        RecentItemsPoller.__init__(self, name, interval, poll_url, regexp)

        self.downloader = CodepadDownloadQueue(name='%s/downloader' % (self.name, ), interval=0.2)

        return
