# -*- coding: utf-8 *-*

import re

from pbl.matcher.match import Match


class Matcher:

    def __init__(self, name, regexp, threshold=1, flags=0):
        self.name = name
        self.regexp = regexp
        self.threshold = threshold
        self.flags = flags
        return

    def __repr__(self):
        return 'Matcher(%s, %s)' % (repr(self.name), repr(self.regexp))

    def match(self, data):
        m = re.findall(self.regexp, data, flags=self.flags)
        if len(m) >= self.threshold:
            return Match(self.name, m)
        return
