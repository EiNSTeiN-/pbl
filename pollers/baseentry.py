# -*- coding: utf-8 *-*

import time

from pbl.matcher import MATCHERS
from pbl.database import Database


class BaseEntry:

    def __init__(self, source, data, metadata):

        self.source = source
        self.data = data
        self.metadata = metadata
        self.timestamp = int(time.time())

        self.matches = []

        return

    def match(self):
        """ Checks if there is anything in this data that could be interresting to keep.

        Returns the category name and a list of matching items. """

        for m in MATCHERS:
            match = m.match(self.data)
            if match is None:
                continue
            self.matches.append(match)

        return len(self.matches) > 0

    def keep(self):
        """ Insert an entry in the database. This should be overridden by the subclass, and
        the subclass should insert subclass-specific data in its own table. """

        reason = ', '.join([m.name for m in self.matches])
        print 'Keeping %s, reason: %s' % (repr(self), reason)

        db = Database.get()
        c = db.cursor()

        c.execute("""replace into leaks (date, data, nblines, isbad, reason, source)
                        values (%s, %s, %s, %s, %s, %s)""", (self.timestamp, self.data, None,
                        False, reason, self.source))
        leak_id = c.lastrowid

        metadata = []
        for name in self.metadata:
            metadata.append((leak_id, name, self.metadata[name]))

        c.executemany('replace into leak_metadata (leak_id, name, value) values (%s, %s, %s)', metadata)

        db.commit()
        c.close()

        return leak_id
