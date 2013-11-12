# -*- coding: utf-8 *-*


class Match:

    def __init__(self, name, matches):
        self.name = name
        self.matches = matches
        return

    def __repr__(self):
        return 'Match(%s, %s)' % (repr(self.name), repr(self.matches))
