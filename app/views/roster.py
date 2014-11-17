#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Roster
    ~~~~~~
    Queries the roster for a provided league and team and builds a JSON
    response object. Currently, the supported leagues are: MLB, NHL,
    NFL, NBA, MLS and EPL.

    :author: Jeff Kereakoglow
    :date: 2013-09-09
    :copyright: (c) 2013 by NESN.
    :license: BSD, see LICENSE for more details.
"""
from re import sub
from flask import Blueprint, jsonify, abort
from app.utils import prepare_json_output, cache_data, fetch_cached_data
from app.helpers import help_fetch_soup, help_parse_soup, format_height, get_team_id

mod = Blueprint("roster", __name__, url_prefix="/roster")

#-- Tokens
SPORT_TOKEN = "{{sport}}"

#-- Query String Parameters
PARAM_TEAM = "teamno"
PARAM_RESOURCE_TYPE = "type"

#-- Query String Arguments
ARG_RESOURCE_TYPE = "roster"  # Defined here for readability

#-- URL
ROSTER_URL = "http://stats.nesn.com/" + SPORT_TOKEN + "/teamstats.asp"

@mod.route("/mlb/<team>", methods=["GET"])
def mlb(team):
    """
    Queries the roster for a provided MLB team.

    :param team: The name of the team
    :type team: str

    :returns: A JSON response
    :rtype: flask.Response
    """

    return jsonify(roster_helper(sport="mlb", team=team, parser_func=parse_mlb_soup))

@mod.route("/nhl/<team>", methods=["GET"])
def nhl(team):
    """
    Queries the roster for a provided NHL team.

    :param team: The name of the team
    :type team: str

    :returns: A JSON response
    :rtype: flask.Response
    """
    return jsonify(roster_helper(sport="nhl", team=team, parser_func=parse_nhl_soup))

@mod.route("/nfl/<team>", methods=["GET"])
def nfl(team):
    """
    Queries the roster for a provided NFL team.

    :param team: The name of the team
    :type team: str

    :returns: A JSON response
    :rtype: flask.Response
    """
    return jsonify(roster_helper(sport="fb", team=team, parser_func=parse_nfl_soup))

@mod.route("/nba/<team>", methods=["GET"])
def nba(team):
    """
    Queries the roster for a provided NBA team.

    :param team: The name of the team
    :type team: str

    :returns: A JSON response
    :rtype: flask.Response
    """
    return jsonify(roster_helper(sport="nba", team=team, parser_func=parse_nba_soup))

def roster_helper(sport, team, parser_func):
    """
    Delegate function which helps query the roster for a provided team
    of a provided sport.

    :param sport: The name of the sport
    :type sport: str

    :param team: The name of the team
    :type team: str

    :param parser_func: A callback function
    :type parser_func: str

    :returns: A JSON response
    :rtype: flask.Response
    """

    team_id = get_team_id(sport, team)

    if team_id is None:
        abort(404)

    rv = fetch_cached_data(args=sport + str(team_id))

    if rv is not None:
        return rv

    soup = help_fetch_soup(
        url=ROSTER_URL.replace(SPORT_TOKEN, sport),
        request_params={
            PARAM_TEAM : team_id,
            PARAM_RESOURCE_TYPE: ARG_RESOURCE_TYPE
        }
    )
    out = prepare_json_output(help_parse_soup(soup, parser_func))

    del soup

    # Cache for 24 hours
    cache_data(data=out, args=sport + str(team_id), timeout=60 * 60 * 24)

    return out

def parse_mlb_soup(cells):
    vals = {}
    vals["number"] = int(cells[0].extract().text.strip().encode("utf-8"))
    vals["name"] = cells[1].extract().text.encode("utf-8")
    vals["position"] = cells[2].extract().text.encode("utf-8")

    # Split the string "R/R" and assign each value to a different
    # dict key. This is called unpacking. So slick
    vals["bats"], vals["throws"] = cells[3].extract().text.strip().encode("utf-8").split('/')

    vals["status"] = cells[4].extract().text.encode("utf-8")
    vals["height"] = format_height(cells[5].extract().text.encode("utf-8"))

    vals["weight"] = int(cells[6].extract().text.encode("utf-8"))
    vals["born"] = cells[7].extract().text.encode("utf-8")
    vals["birthplace"] = cells[8].extract().text.encode("utf-8")

    return vals

def parse_nhl_soup(cells):
    vals = {}
    vals["number"] = int(cells[0].extract().text.strip().encode("utf-8"))
    vals["name"] = cells[1].extract().text.encode("utf-8")
    vals["position"] = cells[2].extract().text.encode("utf-8")
    vals["height"] = format_height(cells[3].extract().text.encode("utf-8"))
    vals["weight"] = int(cells[4].extract().text.encode("utf-8"))
    vals["born"] = cells[5].extract().text.encode("utf-8")
    vals["birthplace"] = cells[6].extract().text.encode("utf-8")

    return vals

def parse_nfl_soup(cells):
    # Num   Name    Pos Exp Ht  Wt  Born    Birthplace  College
    vals = {}
    vals["number"] = int(cells[0].extract().text.strip().encode("utf-8"))
    vals["name"] = cells[1].extract().text.encode("utf-8")
    vals["position"] = cells[2].extract().text.encode("utf-8")
    vals["experience"] = cells[3].extract().text.encode("utf-8")

    vals["experience"] = 0 if 'R' == vals["experience"] else int(vals["experience"])

    vals["height"] = format_height(cells[4].extract().text.encode("utf-8"))
    vals["weight"] = int(cells[5].extract().text.encode("utf-8"))
    vals["born"] = cells[6].extract().text.encode("utf-8")
    vals["birthplace"] = cells[7].extract().text.encode("utf-8")
    vals["college"] = cells[8].extract().text.encode("utf-8")

    return vals
def parse_nba_soup(cells):
    # No.   Name    Pos Exp College Ht  Wt  Inj

    vals = {}
    vals["number"] = int(cells[0].extract().text.strip().encode("utf-8"))
    vals["name"] = cells[1].extract().text.encode("utf-8")
    vals["position"] = cells[2].extract().text.encode("utf-8")
    vals["experience"] = cells[3].extract().text.encode("utf-8")

    vals["experience"] = 0 if 'R' == vals["experience"] else int(vals["experience"])

    vals["college"] = cells[4].extract().text.encode("utf-8")

    vals["height"] = format_height(cells[5].extract().text.encode("utf-8"))
    vals["weight"] = int(cells[6].extract().text.encode("utf-8"))
    vals["injuries"] = cells[7].extract().text.strip().encode("utf-8")

    vals["injuries"] = None if not vals["injuries"] else vals["injuries"]

    return vals
