#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Stats
    ~~~~~~
    Queries the statistics for a provided league and team and builds a JSON
    response object. Currently, the supported leagues are: MLB, NHL,
    NFL, NBA, MLS and EPL.

    :author: Jeff Kereakoglow
    :date: 2013-09-09
    :copyright: (c) 2013 by NESN.
    :license: BSD, see LICENSE for more details.
"""
from flask import Blueprint, jsonify
from app.utils import prepare_json_output, cache_data, fetch_cached_data, logcat
from app.helpers import help_fetch_soup, help_parse_soup, format_height

mod = Blueprint("stats", __name__, url_prefix="/stats")

#-- Tokens
SPORT_TOKEN = "{{sport}}"

#-- Query String Parameters
PARAM_TEAM = "teamno"
PARAM_RESOURCE_TYPE = "type"

#-- Query String Arguments
ARG_RESOURCE_TYPE = "stats"  # Defined here for readability

#-- URL
STATS_URL = "http://stats.nesn.com/" + SPORT_TOKEN + "/teamstats.asp"

@mod.route("/mlb/<team>", methods=["GET"])
def mlb(team):
    return jsonify(stats_helper(sport="mlb", team=2, parser_func=parse_mlb_soup))

@mod.route("/nhl/<team>", methods=["GET"])
def nhl(team):
    return jsonify(stats_helper(sport="nhl", team=1, parser_func=parse_nhl_soup))

@mod.route("/nfl/<team>", methods=["GET"])
def nfl(team):
    return jsonify(stats_helper(sport="fb", team=2, parser_func=parse_nfl_soup))

@mod.route("/nba/<team>", methods=["GET"])
def nba(team):
    return jsonify(stats_helper(sport="nba", team=2, parser_func=parse_nba_soup))

def stats_helper(sport, team, parser_func):

    rv = fetch_cached_data()

    if rv is not None:
        return rv

    soup = help_fetch_soup(
        url=STATS_URL.replace(SPORT_TOKEN, sport),
        request_params={
            PARAM_TEAM : team, # debugging for now
            PARAM_RESOURCE_TYPE: ARG_RESOURCE_TYPE
        },
        class_attrs="sortable shsTable shsBorderTable"
    )

    out = prepare_json_output(help_parse_soup(soup, parser_func))

    del soup

    # Cache for 24 hours
    cache_data(data=out, timeout=60 * 60 * 24)

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
    # Player | G | Min | FGM | FGA | FTM | FTA | 3PM | 3PA | TR | A | Stl | Blk | TO | +/-
    vals = {}
    vals["player"] = cells[0].extract().text.strip().encode("utf-8")
    vals["games"] = int(cells[1].extract().text.strip().encode("utf-8"))
    vals["minutes"] = int(cells[2].extract().text.strip().encode("utf-8"))
    vals["steals"] = int(cells[11].extract().text.strip().encode("utf-8"))
    vals["blocks"] = int(cells[12].extract().text.strip().encode("utf-8"))
    vals["plus_minus"] = int(cells[14].extract().text.strip().encode("utf-8"))

    return vals
