
import re
import time

import pbl.pollers
from pbl.pollers.baseentry import BaseEntry
from pbl.pollers.recentitemspoller import RecentItemsDownloader
from pbl.pollers.recentitemspoller import RecentItemsPoller


class GistEntry(BaseEntry):

    def __init__(self, data, metadata):
        BaseEntry.__init__(self, 'gist', data, metadata)
        return


class GistDownloadQueue(RecentItemsDownloader):
    """ Downloader thread for gist.github.com. """

    def __init__(self, name, interval):
        RecentItemsDownloader.__init__(self, name, interval)

        self.details_url = 'https://gist.github.com/{id}'

        # if something is found, these are the details to be kept from the details page.
        self.details_regexp = dict(
            user='<a href="\/[^"]+">([^<]+)<\/a> <span>\(owner\)<\/span>',
            title='<span id="description" class="edit instapaper_title">([^<]+)<\/span>'
        )

        # This regexp grabs the links to each file within this gist (i.e. potential leaks).
        self.files_regexp = '<a href="\/(raw\/[^"]+)">raw<\/a>'

        # Full url to the raw leak data
        self.files_url = 'https://gist.github.com/{link}'

        return

    def process_file(self, url):

        return

    def process_id(self, id):
        """ From the ID of a paste, fetch the content and the metadata.
        Determine if the paste is worth keeping. """

        # First, download the raw content here

        url = self.details_url.format(id=id)
        r = self.session.get(url, **pbl.pollers.requestoptions)
        if r.status_code == 404:
            # paste id not found...
            self.echo('paste id was removed %s' % (id, ))
            return True

        if not r.ok:
            self.echo('Problem downloading page %s, status=%s, error=%s' % (url, repr(r.status_code), repr(r.error)))
            return False

        details = r.content

        time.sleep(0.2)

        # Second, grab the links to each file within this gist.
        files = re.findall(self.files_regexp, details)
        print repr(files)

#        entry = GistEntry(data, metadata)
#
#        if entry.match():
#            entry.keep()

        return True


class Gist(RecentItemsPoller):
    """ Basically just set a custom downloader here. """

    def __init__(self, name, interval, poll_url, regexp):

        RecentItemsPoller.__init__(self, name, interval, poll_url, regexp)

        self.downloader = GistDownloadQueue(name='%s/downloader' % (self.name, ), interval=0.2)

        return
