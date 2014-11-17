#! #!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    NESN API
    ~~~~~~~~

    The purpose of this application is to normalize data coming from
    NESN's sports statistic's provider, STATS, LLC.

    The need for structured data arose when developing mobile
    applications and when adding new functionality to NESN.

    Prior to this application, data from STATS had to be embedded on
    NESN's website using JavaScript. The trouble is that STATS uses an
    antiquated method, specifically, the document.write() function. It
    has been known for some time that document.write() can cause trouble,
    and so, we have done what we can do avoid it. We decided the best
    solution is to scrape data from STATS's website and serve it as a
    JSON API for NESN's use

    :author: Jeff Kereakoglow
    :date: 2013-09-09
    :copyright: (c) 2013 by NESN.
    :license: BSD, see LICENSE for more details.
"""
from flask import Flask, jsonify, abort
from werkzeug.contrib.cache import SimpleCache
from redis import Redis
from redis.exceptions import ConnectionError

app = Flask(__name__)
app.config.from_object("config")

# The cache object
cache = SimpleCache(__name__)

#-- Redis
redis = Redis(
    host=app.config["REDIS_HOST"],
    port=app.config["REDIS_PORT"],
    db=app.config["REDIS_DB"]
)

# Before running the app, test if the Redis server is running. If it's
# not raise an informative exception.
try:
    redis.get("initial_server_test")
except ConnectionError:
    raise ConnectionError(" The Redis server is inactive. Activate it with the command `redis-server`.")

@app.errorhandler(404)
def not_found(error):
    response = jsonify(status=404, message="No interface defined for URL.")
    response.status_code = 404
    return response

@app.route('/help', methods = ['GET'])
def help():
    """
    Returns a list of available URLs.

    :returns: A JSON response object
    :rtype: flask.Response
    """
    # func_list = {}
    func_list = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list.append(rule.rule)
            # func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(data=func_list, meta={"description" : "List of URL endpoints."})

# @app.before_request
# def return_cached():
#     # if GET and POST not empty
#     if not request.values:
#         response = cache.get(request.path)
#         if response:
#             return response

# @app.after_request
# def cache_response(response):
#     if not request.values:
#         cache.set(request.path, response, CACHE_TIMEOUT)
#     return response

from app.views import injuries
from app.views import posts
from app.views import rankings
from app.views import roster
from app.views import schedule
from app.views import scores
from app.views import standings
from app.views import stats
from app.views import teams
app.register_blueprint(injuries.mod)
app.register_blueprint(posts.mod)
app.register_blueprint(rankings.mod)
app.register_blueprint(roster.mod)
app.register_blueprint(schedule.mod)
app.register_blueprint(scores.mod)
app.register_blueprint(standings.mod)
app.register_blueprint(stats.mod)
app.register_blueprint(teams.mod)
