# -*- coding: utf-8 *-*

import sys
import os

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(path)

import json
from mod_python import apache
from mod_python.Session import Session

from pbl.database import Database


def index(req, **params):
    """ Show details of a certain leek.

    Transfers the data and related information.
    """

    db = Database.get()

    if 'id' not in params or not params['id'].isdigit():
        req.status = apache.HTTP_BAD_REQUEST
        return '"id" param is not digits'

    leak_id = int(params['id'])

    c = db.cursor()
    c.execute("""
        select
            l.data, l.htmldata
        from
            leaks l
        where
            l.leak_id = %s
    """, (leak_id, ))
    r = c.fetchall()

    sess = Session(req)
    if not sess.is_new():
        c.execute("""
            replace into user_seen (user_id, leak_id) values (%s, %s)
        """, (sess['user_id'], leak_id))

    db.commit()
    c.close()

    details = list(r[0])
#    details[0] = urllib.quote(details[0])
    details[0] = details[0].replace('&', '&amp;').replace('<', '&lt;').replace('>',
        '&gt;').replace('"', '&quot;').replace("'", '&#39;')

    req.content_type = 'application/json'
    return json.dumps(details, ensure_ascii=False)
