
import requests

import pbl.pollers
from pbl.pollers.baseentry import BaseEntry
from pbl.pollers.recentitemspoller import RecentItemsDownloader
from pbl.pollers.recentitemspoller import RecentItemsPoller


class LodgeitEntry(BaseEntry):

    def __init__(self, data, metadata):
        BaseEntry.__init__(self, 'lodgeit', data, metadata)
        return


class LodgeitDownloadQueue(RecentItemsDownloader):
    """ Downloader thread for pastebin. """

    def __init__(self, name, interval):
        RecentItemsDownloader.__init__(self, name, interval)

        self.download_url = 'http://paste.pocoo.org/raw/{id}'
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

        if 'Sorry, but the page you requested was not found on this server.' in data:
            # paste id not found...
            self.echo('paste id was removed %s' % (id, ))
            return True

        metadata = {}
        metadata['uid'] = id
        metadata['url'] = url

        entry = LodgeitEntry(data, metadata)

        if entry.match():
            entry.keep()

        return True


class Lodgeit(RecentItemsPoller):
    """ Basically just set a custom downloader here. """

    def __init__(self, name, interval, poll_url, regexp):

        RecentItemsPoller.__init__(self, name, interval, poll_url, regexp)

        self.downloader = LodgeitDownloadQueue(name='%s/downloader' % (self.name, ), interval=0.2)

        return
