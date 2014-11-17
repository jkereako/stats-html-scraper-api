#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Posts
    ~~~~~~
    Queries NESN.com's WordPress posts and builds a JSON
    response object.

    This is an interface for WordPress.com's public API. So, this is
    an interface for an interface. The reason for this is because
    WordPress.com's API lacks the ability to associate Facebook likes
    and Tweets with each URL. Additionally, WordPress.com's API is
    extremely verbose and contains information NESN, and probably most
    folks don't care about, such as data from Gravatar.

    One thing this script handles that WordPress.com cannot (or likely,
    will not) is association of each WordPress URL with the total count
    of Facebook likes and comments, as well as the total count of Tweets
    from Twitter. This information will be especially helpful in mobile
    applications where battery life is precious, so it will reduce the
    amount of calls to HTTP.

    All string values are defined as constants at the top of the file
    for readability, reliability and scalability.

    :author: Jeff Kereakoglow
    :date: 2013-09-09
    :copyright: (c) 2013 by NESN.
    :license: BSD, see LICENSE for more details.
"""
from flask import Blueprint, jsonify, request
import requests
from app.utils import timestamp_from_string, prepare_json_output, cache_data, fetch_cached_data

mod = Blueprint("posts", __name__, url_prefix="/posts")

#-- URLs
POSTS_URL = "http://public-api.wordpress.com/rest/v1/sites/nesn.com/posts"
WORDPRESSCOM_PHOTON_URL = "http://i0.wp.com/"
FACEBOOK_GRAPH_URL = "https://graph.facebook.com/fql"
TWITTER_URLS_URL = "http://urls.api.twitter.com/1/urls/count.json"

#-- Tokens
FQL_TOKEN = "{{urls_str}}"

#-- Query String Parameters
PARAM_NESN_POST_CATEGORY = "category"
PARAM_NESN_POST_COUNT = "count"
PARAM_WORDPRESS_POST_CATEGORY = "category"
PARAM_WORDPRESS_POST_COUNT = "number"
PARAM_TWITTER_URL = "url"
PARAM_FACEBOOK_QUERY = "q"

#-- Query String Arguments
ARG_FQL = "SELECT url,share_count,like_count,comment_count FROM link_stat WHERE url IN (" + FQL_TOKEN + ')'

@mod.route('/', methods=["GET"])
def posts():
    """
    Queries posts from WordPress.com's public API implementation for NESN.com.

    This does a few things. First, it simplifies WordPress.com's complex JSON
    response from their public API. It gathers the Facebook like and comment
    count along the Tweet count for each URL. It also interfaces with
    WordPress.com's Photon service to crop images for display on mobile devices.

    :returns: JSON
    :rtype: flask.Response
    """
    rv = fetch_cached_data()

    if rv is not None:
        return jsonify(rv)

    args = {
        PARAM_WORDPRESS_POST_CATEGORY : request.args.get(PARAM_NESN_POST_CATEGORY),
        PARAM_WORDPRESS_POST_COUNT : request.args.get(PARAM_NESN_POST_COUNT)
    }

    r = requests.get(url=POSTS_URL, params=args)
    posts = r.json()

    # Were any posts found?
    if 0 == posts["found"]:
        return jsonify(message="No posts found.", status=200)

    urls = []

    # Build list of URLs to pass to Facebook's Graph tool
    for post in posts["posts"]:

        urls.append(post["URL"])

    #-- Facebook Request
    urls_str = (','.join('\'' + url + '\'' for url in urls))

    url = ARG_FQL.replace(FQL_TOKEN, urls_str)
    args = {PARAM_FACEBOOK_QUERY : url}

    r = requests.get(url=FACEBOOK_GRAPH_URL, params=args)

    fb_response = r.json()

    vals = {}
    stack = []
    # stripper = HTMLStripper()

    for post in posts["posts"]:
        categories = []
        vals["id"] = post["ID"]
        vals["author"] = post["author"]["name"]
        vals["title"] = post["title"]
        vals["published"] = int(timestamp_from_string(post["date"]))
        vals["modified"] = int(timestamp_from_string(post["modified"]))
        vals["image"] = post["featured_image"]

        # stripper.feed(post["content"])

        # vals["content"] =  stripper.get_text()
        vals["content"] = post["content"]
        vals["url"] = post["URL"]

        #-- Twitter Request
        args = {PARAM_TWITTER_URL : vals["url"]}
        r = requests.get(url=TWITTER_URLS_URL, params=args)

        vals["tweets"] = int(r.json()["count"])

        # Match up Facebook data with URL
        for link_stat in fb_response["data"]:
            if link_stat["url"] == vals["url"]:
                vals["facebook"] = {"likes" : link_stat["like_count"], "comments" : link_stat["comment_count"]}

        for category in post["categories"]:
            categories.append(category)

        vals["categories"] = categories
        stack.append(vals.copy())
        vals = {}

    del args, categories, fb_response, r, vals
    out = prepare_json_output(stack)
    del stack

    # Automatically cached for 15 minutes
    cache_data(out)

    return jsonify(out)
