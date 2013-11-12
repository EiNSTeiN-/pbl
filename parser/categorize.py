import re


class word():

    regexps = (
        ('urlwithpass', r'^(.*\:\/\/[^\:]+\:[^@]+@.*)$'),
        ('url', r'([a-zA-Z]*:\/\/.*)$'),
        ('email', r'^(?:[eE][mM][aA][iI][lL][\:\=])?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4})$'),
        ('hex32', r'^([a-fA-F0-9]{32})$'),
        ('hex40', r'^([a-fA-F0-9]{40})$'),
        ('login', r'^(?:[lL]|[uU][sS][eE][rR]|[uU][sS][eE][rR][nN][aA][mM][eE]|[lL][oO][gG][iI][nN])[\:\=]([^\:]+)$'),
        ('password', r'^(?:[pP]|[pP][aA][sS][sS]|[pP][aA][sS][sS][wW][oO][rR][dD])[\:\=]([^\:]+)$'),
        ('ip', r'^(?:[iI][pP]:)?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})$'),
        #('userpass', r'^([^\:]+\:[^\:]+)$'),
        ('computeruser', r'^([A-Z0-9\-]+\^.+)$'),  # COMPUTER^Username style

        # we see a couple of user:pass:email dumps
        ('userpassemail', r'^([^\:]+\:[^\:]+\:none|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4})$'),
    )

    titles = dict(
        urlwithpass='Url with password',
        url='Url',
        email='email',
        hex32='16-bytes hash',
        hex40='20-bytes hash',
        login='Username',
        password='Password',
        ip='IP address',
        userpass='username:password',
        computeruser='COMPUTER^Username',
        userpassemail='username:password:email',
    )

    def __init__(self, word, type=None):
        self.word = word

        if type:
            # force the type here, and match the whole word
            self.type = type
            self.match = self.word
        else:
            self.type = None
            self.match = None

            for t in self.regexps:
                (type, regexp) = t
                match = re.match(regexp, word)
                if match:
                    self.type = type
                    self.match = match.groups()[0]
                    break

        return

    def __repr__(self):
        if self.type:
            return str(self.type) + '=' + repr(self.word)
        return repr(self.word)

    def __str__(self):
        return self.word

    def escape(self, w):
        w = w.replace('<', '&lt;')
        w = w.replace('>', '&gt;')
        return w

    def html(self):
        if self.type and self.match:
            title = self.titles.get(self.type)
            if not title:
                title = ''
            return '<span class="' + self.type + '" title="' + title + '">' + self.escape(self.match) + '</span>'
        return self.escape(self.word)


class line():
    def __init__(self, s, linefilter=None):
        self.s = s.strip()
        self.linefilter = linefilter
        self.whitespaces = []
        self.words = []
        self.is_table_header = False

        # do line matches; everything else is matched on single words
        self.matches = []
        if self.linefilter:
            self.applyfilter(self.linefilter)
        else:
            self.whitespaces = re.findall('[\t ]+', self.s)
            self.words = [word(w) for w in re.split('[\t ]*', self.s)]

        # collect all word types ...
        self.types = ['text' if w.type is None else w.type for w in self.words]
        return

    def __repr__(self):
        return repr(self.words)

    def __str__(self):
        if len(self.words) - 1 != len(self.whitespaces):
            print 'whitespace problem?'
            return ' '.join([str(w) for w in self.words])
        return ''.join([self.words[i] + self.whitespaces[i] for i in range(len(self.whitespaces))]) + self.words[-1]

    def html(self):
        if len(self.words) - 1 != len(self.whitespaces):
            print 'whitespace problem?', repr(self.words), repr(self.whitespaces)
            return ' '.join([w.html() for w in self.words])
        return ''.join([self.words[i].html() + self.whitespaces[i] for i in range(len(self.whitespaces))]) + \
            self.words[-1].html()

    def table(self):

        if self.is_table_header:
            header = ' class="table_header"'
        else:
            header = ''

        return ('<tr%s><td>' % (header, )) + '</td><td>'.join([w.html() for w in self.words]) + '</td></tr>'

    def empty(self):
        return len(self.words) == 0 or (len(self.words) == 1 and len(self.words[0].word) == 0)

    def applyfilter(self, filter):

        m = re.search(filter, self.s)
        if m:
            self.matches = m.groupdict()

            # do a little dance to get a friggin sorted dictionnary
            ordered = {}
            for k in self.matches:
                if self.matches[k] is None:
                    continue
                ordered[m.start(k)] = k
            ordered = [ordered[k] for k in sorted(ordered)]

            whitespaces = []
            parts = []
            last = None
            for k in ordered:
                if self.matches[k] is None:
                    continue

                if last is None and m.start(k) > 0:
                    last = 0
                if last is not None:
                    s = self.s[last:m.start(k)]
                    whitespaces += re.findall('[\t ]+', s)
                    s = [word(w) for w in re.split('[\t ]*', s) if w != '']
                    parts += s

                parts.append(word(self.matches[k], k))

                last = m.end(k)

            if last < len(self.s):
                whitespaces += re.findall('[\t ]+', self.s[last:])
                s = [word(w) for w in re.split('[\t ]*', self.s[last:]) if w != '']
                parts += s

            self.whitespaces = whitespaces
            self.words = parts
        else:
            self.whitespaces = re.findall('[\t ]+', self.s)
            self.words = [word(w) for w in re.split('[\t ]*', self.s)]

        return


def find_tables(lines):
    """ This code finds tables in a document. We consider a 'table' any
    number of lines which have the exact same whitespace pattern for more
    than 3 consecutive lines
    """

    l_start = None
    l_end = None
    count = 0
    ws = None
    tables = []

    for i in range(len(lines)):
        l_ws = lines[i].whitespaces
        if str(l_ws) != str(ws) and len(lines[i].s) == 0:
            count += 1
        elif str(l_ws) != str(ws):  # or len(relevant_types) == 0:
            if count > 15 and len(ws) > 0:
                l_end = i - 1
                tables.append(dict(start=l_start, end=l_end, whitespaces=ws, count=count))
            count = 1
            ws = l_ws
            l_start = i
        elif str(l_ws) == str(ws) and len(l_ws) > 0:
            count += 1

    if count > 15:
        l_end = i
        tables.append(dict(start=l_start, end=l_end, whitespaces=ws, count=count))

    return tables


def tag_tables(lines, tables):
    """ check each table for a header containing some
    keywords, like email, password, etc. """

    valid_headers = ['id', 'email', 'mail', 'pass', 'passwd', 'password']

    for table in tables:
        startline = lines[table['start']]

        is_header = False
        for word in startline.words:
            if str(word).lower() in valid_headers:
                is_header = True
                break

        if is_header:
            print 'Treating first line as header: %s' % (repr(startline), )

            lines[table['start']].is_table_header = True

            for i in range(len(startline.words)):
                if str(startline.words[i]).lower() in ('password', 'pass', 'passwd'):
                    print 'Marking column %u as PASSWORD line' % (i, )
                    for j in range(table['start'] + 1, table['end'] + 1):
                        if lines[j].empty():
                            continue
                        if re.match(r'^[0-9a-fA-F]{32}$', lines[j].words[i].word):
                            lines[j].words[i].type = 'hex32'
                        elif re.match(r'^[0-9a-fA-F]{40}$', lines[j].words[i].word):
                            lines[j].words[i].type = 'hex40'
                        else:
                            lines[j].words[i].type = 'password'
                        lines[j].words[i].match = lines[j].words[i].word

    return
