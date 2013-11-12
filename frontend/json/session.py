# -*- coding: utf-8 *-*

import sys
import os

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(path)

import urllib
from mod_python import apache
from mod_python.Session import Session
from mod_python import Cookie
import json

from pbl.database import Database


def get(req, **params):
    """ Return logged-in username. """

    sess = Session(req)
    if sess.is_new():
        req.content_type = 'application/json'
        return 'null'

    ret = dict()
    ret['created'] = sess.created()
    ret['user_id'] = sess['user_id']
    ret['username'] = sess['username']

    req.content_type = 'application/json'
    return json.dumps(ret, ensure_ascii=False)


def clear(req, **params):
    """ Obliterate the session. """

    sess = Session(req)
    if not sess.is_new():
        sess.invalidate()

    req.content_type = 'application/json'
    return json.dumps(dict(success=True), ensure_ascii=False)


def login(req, **params):
    """ New login attempt. Clean out old session if present, and create new one. """

    sess = Session(req)
    if not sess.is_new():
        sess.delete()
        sess = Session(req)
        if not sess.is_new():
            req.status = apache.HTTP_BAD_REQUEST
            return 'failed to create new session'

    if 'u' not in params or 'p' not in params:
        req.status = apache.HTTP_BAD_REQUEST
        return 'some parameters were not provided'

    ret = dict()

    if params['u'] != 'einstein' or params['p'] != 'fuckbin':
        ret['success'] = False
        ret['error'] = 'bad username or password'

        # note: session is not saved!
    else:
        ret['success'] = True

        # keep some stuff in session...
        sess['username'] = params['u']
        sess['user_id'] = 1

        sess.set_timeout(60 * 60 * 24 * 365 * 10)  # 10 year
        sess.save()

        # grab the user's cookie, and save the seen leaks into the database
        seen_ranges = urllib.unquote(Cookie.get_cookie(req, '__CJ_seen').value)
        seen_ranges = json.loads(seen_ranges)
        values = [[sess['user_id'], i] for seen_range in seen_ranges for i in
            range(seen_range['start'], seen_range['end'] + 1)]

        db = Database.get()
        c = db.cursor()
        c.executemany(""" replace into user_seen (user_id, leak_id) values (%s, %s) """, values)
        db.commit()
        c.close()

    req.content_type = 'application/json'
    return json.dumps(ret, ensure_ascii=False)
