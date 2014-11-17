#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Utils
    ~~~~~~

    This is a small library of generic functions in which each serve a specific
    purpose to this application. This is not a library in development,
    instead, it is a lean file with functions. So, if a function is no
    longer used and it be safely removed without breaking code, do so.

    The goal is to keep this file as lean as possible.

    :author: Jeff Kereakoglow
    :date: 2013-09-09
    :copyright: (c) 2013 by NESN.
    :license: BSD, see LICENSE for more details.
"""
# from HTMLParser import HTMLParser
import re
import logging
from hashlib import sha224
from datetime import date, datetime
from dateutil.parser import parse
from unicodedata import normalize
from flask import request
from app import app, cache
# try:
#     import html.entities as compat_html_entities
# except ImportError: # Python 2
#     import htmlentitydefs as compat_html_entities

try:
    compat_chr = unichr # Python 2
except NameError:
    compat_chr = chr

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def logcat(message):
    """
    Helper function which logs messages to the terminal.

    Without this helper, the developer would have to write:

    import logging
    from app import app

    app.logger.debug(message)

    Whereas, with this helper, it has been reduced to:

    from app.utils import logcat

    logcat(message)

    Coming from Android development, it is a lot easier to remember
    logcat than it is to remember app.logger.debug

    :param message: The log message
    :type message: str
    """
    app.logger.debug(message)

def query_string_arg_to_bool(arg):
    param = request.args.get(arg)

    if param is None:
        return False

    elif param.lower() in ("yes", 'y', "true", "t", "1"):
        return True

    return False

def prepare_query_string(args):
    """
    Creates a simple query string.

    This is an alternative to Requests's parameter feature. Requests
    strips stuff out and coverts everything. This does a simple join,
    preserving everything.

    :param args: The data which is to be prepared
    :type args: dict

    :returns: A formatted query string
    :rtype: string
    """
    return '?' + '&'.join(["%s=%s" % (key, value) for (key, value) in args.items()])


def prepare_json_output(data):
    """Wraps the data object in a dictionary which contains meta
    information in regards to when the object was created.

    :param data: The data which is to be prepared
    :type data: anything

    :returns: A dictionary formatted for a JSON response
    :rtype: dict
    """
    return {"data" : data, "meta" : {"created_at": int(current_time()), "loaded_from_cache": False}}

def fetch_cached_data(args=None):
    """
    Retrieves a cache object when given an optional cache key.

    Because most cache keys within this app are URL dependent, the
    code which retrieves the cache has been refactored here to maximize
    consistency.

    :param cache_key: The identifier for the cache object. This must be unique
    :type cache_key: str

    :returns: A dictionary of JSON data
    :rtype: dict
    """
    cache_key = request.base_url

    if args:
        cache_key += args

    cache_key = sha224(cache_key).hexdigest()

    rv = cache.get(cache_key)

    # logcat(str(rv))

    if rv is not None:
        rv["meta"]["loaded_from_cache"] = True
    return rv

def cache_data(data, args=None, timeout=None):
    """
    Stores data in the application cache using the base URL as the main
    cache key.

    To prevent all URLs from being cached, such as
    /teams/nba?this_is_not_a_real_param=2

    The base URL along with optional arguments are used. This ensures
    that URLS passed with arbitrary query string arguments will not
    break the cache.

    Because most cache keys within this app are URL dependent, the
    code which stores the cache has been refactored here to maximize
    consistency.

    :param data: The data object to cache
    :type data: dict

    :param cache_key: The identifier for the cache object. This must be unique
    :type cache_key: str

    :param timeout: The expiry for the cache
    :type timeout: int

    :returns: None
    :rtype: None
    """
    cache_key = request.base_url

    if args:
        cache_key += args

    cache_key = sha224(cache_key).hexdigest()

    timeout = app.config["CACHE_TIMEOUT"] if timeout is None else timeout

    cache.set(cache_key, data, timeout)

# http://flask.pocoo.org/snippets/5/
def slugify(text, delimiter=u'-'):
    """Generates an slightly worse ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize("NFKD",word).encode("ascii", "ignore")
        if word:
            result.append(word)
    return unicode(delimiter.join(result))

def current_time():
    """
    Returns a UNIX timestamp for the current time.

    :returns: The current timestamp as a string
    :rtype: str
    """
    return datetime.now().strftime("%s")

def timestamp_from_string(date_string):
    """
    Returns a UNIX timestamp for a provided date string.

    This function was created with PHP's strtotime in mind. This may be
    removed if it discovered that Python supports this natively. I'm
    certain it does.

    :returns: The current timestamp as a string
    :rtype: str
    """
    return parse(date_string).strftime("%s")

# def format_datetime(dt):
#     return dt.strftime("%Y-%m-%d @ %H:%M")

# def unescape_html(s):
#     """
#     @param s a string
#     """
#     assert type(s) == type(u'')

#     result = re.sub(u'(?u)&(.+?);', htmlentity_transform, s)
#     return result

# def htmlentity_transform(matchobj):
#     """Transforms an HTML entity to a character.

#     This function receives a match object and is intended to be used with
#     the re.sub() function.
#     """
#     entity = matchobj.group(1)

#     # Known non-numeric HTML entity
#     if entity in compat_html_entities.name2codepoint:
#         return compat_chr(compat_html_entities.name2codepoint[entity])

#     mobj = re.match(u'(?u)#(x?\\d+)', entity)
#     if mobj is not None:
#         numstr = mobj.group(1)
#         if numstr.startswith(u'x'):
#             base = 16
#             numstr = u'0%s' % numstr
#         else:
#             base = 10
#         return compat_chr(int(numstr, base))

#     # Unknown entity in name, return its literal representation
#     return (u'&%s;' % entity)

# class HTMLStripper(HTMLParser):
#     def __init__(self):
#         self.reset()
#         self.fed = []
#     def handle_data(self, d):
#         self.fed.append(d)
#     def get_text(self):
#         return ''.join(self.fed)
#     # def __init__(self):
#     #     HTMLParser.__init__(self)
#     #     self.result = [ ]

#     # def handle_data(self, d):
#     #     self.result.append(d)

#     # def handle_charref(self, number):
#     #     codepoint = int(number[1:], 16) if number[0] in (u'x', u'X') else int(number)
#     #     self.result.append(unichr(codepoint))

#     # def handle_entityref(self, name):
#     #     codepoint = htmlentitydefs.name2codepoint[name]
#     #     self.result.append(unichr(codepoint))

#     # def get_text(self):
#     #     return u''.join(self.result)
