import re

from pbl.matcher.matcher import Matcher


MATCHERS = (
    Matcher('listing of http passwords', r'((?:http|https|pop|ftp)://[^:\n]+:[^@\n]+@)', flags=re.IGNORECASE),
    Matcher('Mysql user/password', r'(mysql_connect\([^\)]*\))', flags=re.IGNORECASE),
    Matcher('SQL injection', r'((?:http|https)://[^ \n]+(?:\+union\+|\+select\+))', flags=re.IGNORECASE),
    Matcher('SQL injection', r'((?:[^\'"])(?:http|https)://[^ \n]+(?:\'))$', flags=re.IGNORECASE),
    Matcher('SQL injection', r'(sql injection)', flags=re.IGNORECASE),
    Matcher('SQL injection', r'(SQLi)(?!te)', flags=0),
    Matcher('Massive mail/pass leak', r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4})', threshold=10,
        flags=re.IGNORECASE),
    Matcher('Hack attribution', r'(hacked by .*)', flags=re.IGNORECASE),
    Matcher('File inclusion', r'((?:http|https):\/\/[^ \n]+\/[^ \n]+(?:\.\.\/))', flags=re.IGNORECASE),
    Matcher('Cisco configuration with enable password', r'^(enable secret .*)$'),
    Matcher('Cisco configuration with enable password', r'^(enable password .*)$'),
    Matcher('Juniper configuration with password', r'^(encrypted-password ".*")$'),
    Matcher('CouchDB password', r'(couchdb.createClient\([^\)]*\))'),
)
