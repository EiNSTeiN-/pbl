# -*- coding: utf-8 *-*

from MySQLdb import OperationalError

import threading
import time
import traceback
import sys
import re

from pbl.parser import categorize
from pbl.database import Database


class ParserThread(threading.Thread):

    def __init__(self):
        super(ParserThread, self).__init__()
        self.daemon = True
        return

    def parse_leak(self, c, leak_id, data):

        lines = [categorize.line(s) for s in data.split('\n')]

        values = []

        for i in range(len(lines)):
            line = lines[i]

            for word in line.words:
                if word.type and word.match:
                    values.append((leak_id, i, word.type, word.match))

        c.execute('delete from leak_content where leak_id = %s', (leak_id, ))

        c.executemany(""" insert into leak_content (leak_id, line_id, type, value)
            values (%s, %s, %s, %s) """, values)

        html = '<br />'.join([line.html() for line in lines])
        c.execute('update leaks set htmldata = %s where leak_id = %s', (html, leak_id))

        return

    def parse_mysql_connect_variable(self, data, var):
        e = r"""(?:(["'])(?:(?=\\)\{n}|(?!\{n}).)*?\{n})|(?:\$?[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)"""

        for i in range(5):
            if var.startswith('$'):
#                print data
#                print var
                vars = re.findall(re.escape(var) + r'[\t ]*=[\t ]*(?P<var>' + e.format(n=2) + ')', data)
                vars = [v[0] for v in vars]
                vars = list(set(vars))  # remove duplicates
#                print repr(var), repr(vars)
                if len(vars) == 1:
                    var = vars[0]
                    continue
                elif len(vars) > 1:
                    break
            elif var[0] in ('"', "'"):
                var = var[1:-1]
                return var

            # what syntax is this!?
            break

        return

    def parse_mysql_connect(self, c, leak_id, data):
#        print 'parsing mysql_connect', repr(leak_id)
        e = r"""(?:(["'])(?:(?=\\)\{n}|(?!\{n}).)*?\{n})|(?:\$[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*?)"""

        all = re.findall('mysql_connect\([\t ]*(?P<host>' + e.format(n=2) + ')[\t ]*,[\t ]*(?P<username>' + \
            e.format(n=4) + ')[\t ]*,[\t ]*(?P<password>' + e.format(n=6) + ')[\t ]*\)', data)

        if len(all) != 1:
            return

        host, _, username, _, password, _ = all[0]

        host = self.parse_mysql_connect_variable(data, host)
        username = self.parse_mysql_connect_variable(data, username)
        password = self.parse_mysql_connect_variable(data, password)

        if username and password:
            comment = 'mysql connect: '
            if host:
                comment += 'host=%s, ' % (repr(host), )
            comment += 'username=%s, ' % (repr(username), )
            comment += 'password=%s' % (repr(password), )
#            print repr(comment)
        else:
            comment = None

        html = data.replace('<', '&lt;')
        html = html.replace('>', '&gt;')
        html = html.replace('\n', '<br />')
        c.execute('update leaks set htmldata = %s, comment=%s where leak_id = %s', (html, comment, leak_id))

        return

    def parse_new_leaks(self):

        db = Database.get()

        c = db.cursor()
        c.execute("""
            select
                l.leak_id, l.data, l.reason
            from
                leaks l
            where
                isparsed = 0 and
                data is not null
            order by leak_id
            limit 10
        """)
        r = c.fetchall()

        for entry in r:
            leak_id, data, reason = entry

            if 'Mysql user/password' in reason:
                self.parse_mysql_connect(c, leak_id, data)
            else:
                self.parse_leak(c, leak_id, data)

        if len(r) == 0:
            return 0

        ids = ','.join([str(e[0]) for e in r])
        c.execute(""" update leaks set isparsed=1 where leak_id in (%s) """ % (ids, ))
        print 'parsed!', repr(ids)

        db.commit()
        c.close()

        return len(r)

    def run(self):

        while True:

            try:
                n = self.parse_new_leaks()

                if n == 0:
                    time.sleep(10)
                else:
                    time.sleep(0.2)

            except OperationalError as e:
                print 'mysql error while processing %s: %s' % (id, repr(e))

                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)

                if e.args[0] == 2006:
                    # MySQL server as gone away
                    Database.reconnect()

        return
