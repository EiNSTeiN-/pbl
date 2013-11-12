# -*- coding: utf-8 *-*

import sys
import os

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(path)

import json
from mod_python import apache
from mod_python.Session import Session

from pbl.database import Database


def seen(req, **params):
    """ Return all leak id that this user has seen. """

    sess = Session(req)
    if sess.is_new():
        req.status = apache.HTTP_BAD_REQUEST
        return 'not logged in'

    db = Database.get()

    c = db.cursor()
    q = """
        select
            us.leak_id
        from
            user_seen us
        where
            us.user_id = {user_id}
    """.format(user_id=sess['user_id'])
    c.execute(q)
    r = c.fetchall()
    c.close()

    # reformat the list...
    r = [e[0] for e in r]

    req.content_type = 'application/json'
    return json.dumps(dict(items=r), ensure_ascii=False)


def index(req, **params):
    """ List recent leaks. Limit of 300 leaks shown.

    parameters:
        - after:
            show leaks after this timestamp
        - period:
            show leaks that occured within this period (today, week, month)
    """

    limit = ''
    if 'after' in params:
        if not params['after'].isdigit():
            req.status = apache.HTTP_BAD_REQUEST
            return '"after" param is not digits'

        leak_id = int(params['after'])
        where = 'l.leak_id >= %u' % leak_id

    elif 'before' in params:
        if not params['after'].isdigit():
            req.status = apache.HTTP_BAD_REQUEST
            return '"before" param is not digits'

        leak_id = int(params['after'])
        where = 'l.leak_id <= %u' % leak_id
        limit = 'limit 10'

    elif 'period' in params:
        if params['period'] == 'initial':
            # By default, load today's leaks, otherwise load the last 300 leaks from whenever...
            where = 'DATE(FROM_UNIXTIME(l.date)) = DATE(SYSDATE())'
        else:
            req.status = apache.HTTP_BAD_REQUEST
            return '"period" param has unknown value'
    else:
        req.status = apache.HTTP_BAD_REQUEST
        return 'bad request'

    sess = Session(req)
    if sess.is_new():
        seen = 'false'
    else:
        seen = '(select true from user_seen us where us.user_id = {user_id} and us.leak_id = l.leak_id)'.format(
            user_id=sess['user_id'], )

    db = Database.get()

    c = db.cursor()
    q = """
        select
            l.leak_id,
            ({seen}) as seen,
            l.date, l.comment, l.reason, l.source
        from
            leaks l
        where
            {where} and
            l.isparsed = 1
        order by leak_id
        {limit}
    """.format(seen=seen, where=where, limit=limit)
    c.execute(q)
    r = list(c.fetchall())

    if len(r) == 0 and 'period' in params and params['period'] == 'initial':
        # last chance to get some latest entry...
        c.execute("""
            select
                l.leak_id,
                ({seen}) as seen,
                l.date, l.comment, l.reason, l.source
            from
                leaks l
            where
                l.isparsed = 1
            order by leak_id desc
            limit 200
        """.format(seen=seen, where=where, limit=limit))
        r = list(c.fetchall())
        r.reverse()

    if len(r) > 0:
        leak_ids = [str(e[0]) for e in r]
        c.execute("""
            select
                leak_id, name, value
            from
                leak_metadata
            where
                leak_id in ({ids})
        """.format(ids=','.join(leak_ids)))
        metadata = c.fetchall()

        # append a dictionary at the end of every entry
        for i in range(len(r)):
            r[i] = list(r[i])
            r[i].append({})

        # insert metadata into dictionary
        for i in range(len(r)):
            for data in metadata:
                if data[0] != r[i][0]:
                    continue

                r[i][-1][data[1]] = data[2]

    c.close()

    req.content_type = 'application/json'
    return json.dumps(dict(items=r), ensure_ascii=False)
