#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Config
    ~~~~~~

    Contains all the configurations for Flask

    See http://flask.pocoo.org/docs/config/

    :author: Jeff Kereakoglow
    :date: 2013-09-09
    :copyright: (c) 2013 by NESN.
    :license: BSD, see LICENSE for more details.
"""
import os

_basedir = os.path.abspath(os.path.dirname(__file__))

# LOGGING_FORMAT = "%(asctime)-15s %(clientip)s %(user)-8s %(message)s"
# logging.basicConfig(format=FORMAT)
DEBUG = True
SECRET_KEY = "development_key"
CACHE_TIMEOUT = 60 * 60 * 15         # Default is 15 minutes

#-- Redis settings
# REDIS_CLASS = 'redis.Redis' if IS_24 else 'redis.StrictRedis'
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

REDIS_BACKUP_HOST = "localhost"
REDIS_BACKUP_PORT = 6380
REDIS_BACKUP_DB = 0

REDIS_SLAVE_HOST = "localhost"
REDIS_SLAVE_PORT = 6381
REDIS_SLAVE_DB = 0

#-- Redis Key Tokens
REDIS_KEY_TOKEN_SPORT = "{{sport}}"

#-- Redis Keys
REDIS_KEY_TEAMS = REDIS_KEY_TOKEN_SPORT + "_teams"

# DICT_KEY_DATA = "data"
# DICT_KEY_META = "meta"

# LIST_NAME = 'flask'
# RSYNC_PATH = 'librelist.com::json/%s'
# SUBJECT_PREFIX = '[flask]'
# WHOOSH_INDEX = os.path.join(_basedir, 'flask-website.whoosh')
# DOCUMENTATION_PATH = os.path.join(_basedir, '../flask/docs/_build/dirhtml')

del os
