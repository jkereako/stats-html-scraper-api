#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Teams
    ~~~~~~~~

    This builds a list of teams for any sport. The returned list can be
    divided by league and then subdivided by division. It can also be
    returned as a flat list.

    It ought to be noted that the order of the teams in this list
    is consistent with the numeric identifier STATS assigns to the team.
    For example, in the URL below:

    http://stats.nesn.com/mlb/teams.asp

    The Boston Red Sox are in the second position below the Baltimore
    Oriels. To retrieve the roster for the Boston Red Sox, the position
    in the table at /teams.asp must be passed as a query string argument
    to denote the team. Example:

    http://stats.nesn.com/mlb/teamstats.asp?team=2&type=roster

    The parameter "team" has the value "2", which indicates "Boston Red
    Sox" in the order of which it appears in /teams.asp.

    :author: Jeff Kereakoglow
    :date: 2013-09-09
    :copyright: (c) 2013 by NESN.
    :license: BSD, see LICENSE for more details.
"""
from flask import Blueprint, jsonify
from app.helpers import teams_helper

mod = Blueprint("teams", __name__, url_prefix="/teams")

@mod.route("/mlb/", methods=["GET"])
def mlb():
    """
    Generic helper function to scrape scoring data from STATS's
    JavaScript file.
    """
    return jsonify(teams_helper(sport="mlb"))

@mod.route("/nhl/", methods=["GET"])
def nhl():
    """
    Generic helper function to scrape scoring data from STATS's
    JavaScript file.
    """
    return jsonify(teams_helper(sport="nhl"))

@mod.route("/nfl/", methods=["GET"])
def nfl():
    """
    Generic helper function to scrape scoring data from STATS's
    JavaScript file.
    """

    return jsonify(teams_helper(sport="fb"))

@mod.route("/nba/", methods=["GET"])
def nba():
    """
    Generic helper function to scrape scoring data from STATS's
    JavaScript file.
    """
    return jsonify(teams_helper(sport="nba"))

@mod.route("/epl/", methods=["GET"])
def epl():
    """
    Generic helper function to scrape scoring data from STATS's
    JavaScript file.
    """
    return jsonify(teams_helper(sport="epl"))
