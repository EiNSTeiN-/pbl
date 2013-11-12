import MySQLdb
import os

from pbl.config import getcfg, setcfg


class Database:

    def __init__(self):
        return

    @classmethod
    def get(cls):

        db = MySQLdb.connect(
            host='127.0.0.1',
            db='pbl',
            user='pbl',
            passwd='',)

        db.text_factory = str
        return db
