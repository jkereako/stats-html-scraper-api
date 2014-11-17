#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Rankings
    ~~~~~~~~
    Handles the parsing and display of tournament-style sports which are
    played by individuals, not teams. In this case, those sports are
    golf and tennis

    :author: Jeff Kereakoglow
    :date: 2013-09-09
    :copyright: (c) 2013 by NESN.
    :license: BSD, see LICENSE for more details.
"""
from flask import Blueprint, jsonify
import re
from app.utils import prepare_json_output, cache_data, fetch_cached_data, logcat
from app.helpers import help_fetch_soup, help_parse_soup, help_get_list_from_dropdown

mod = Blueprint("rankings", __name__, url_prefix="/rankings")

RANKINGS_URL = "http://stats.nesn.com/"

#-- Query String Parameters
PARAM_TOUR = "tour"

@mod.route("/golf/", methods=["GET"])
def golf():
    # http://stackoverflow.com/questions/5334531/python-documentation-standard-for-docstring#5339352
    """
    Queries all rankings for all golf tournaments.

    :returns: A JSON response
    :rtype: flask.Response
    """
    out = rankings_helper(
        url=RANKINGS_URL + "golf/final.asp",
        parser_func=parse_golf_soup
    )

    return jsonify(out)

@mod.route("/tennis/", methods=["GET"])
def tennis():
    """
    Queries all rankings for all tennis matches.

    :returns: A JSON response
    :rtype: flask.Response
    """
    out = rankings_helper(
        url=RANKINGS_URL + "tennis/rankings.asp",
        parser_func=parse_tennis_soup
    )

    return jsonify(out)

#-- Helpers
def rankings_helper(url, parser_func):
    """
    Returns all rankings for all matches

    :param url: URL of the ranking
    :type url: str
    :param parser_func: The parsing function to be applied to the scraped
    :type parser_func: str
    :returns: A formatted dictionary ready for display
    :rtype: dict
    """

    rv = fetch_cached_data()

    if rv is not None:
        return rv

    tour = help_get_list_from_dropdown(url, attr_name="tour")

    stack = {}

    for the_round in tour:
        soup = help_fetch_soup(
            url=url,
            request_params={PARAM_TOUR : the_round}
        )

        stack[the_round] = help_parse_soup(soup, parser_func)

    return stack

    out = prepare_json_output(stack)
    del stack

    # Cache for 12 hours
    cache_data(data=out, timeout=60 * 60 * 12)

    return out

def parse_tennis_soup(cells):
    """Returns all rankings for all matches

    :param cells: A list of HTML <td>
    :type url: list
    :returns: A formatted dictionary representing 1 record
    :rtype: dict
    """
    value_dict = {}
    value_dict["player"] = cells[1].extract().text.strip().encode("utf-8")
    value_dict["country"] = cells[2].extract().text.strip().encode("utf-8")
    value_dict["points"] = re.sub(r"\D", '', cells[3].extract().text.encode("utf-8") )
    value_dict["earnings_usd"] = re.sub(r"\D", '', cells[4].extract().text.encode("utf-8") )

    value_dict["earnings_usd"] = 0 if not value_dict["earnings_usd"] else value_dict["earnings_usd"]
    value_dict["points"] = 0 if not value_dict["points"] else value_dict["points"]

    try:
        value_dict["points"] = int(value_dict["points"])
        value_dict["earnings_usd"] = int(value_dict["earnings_usd"])
    except Exception:
        pass

    return value_dict

def parse_golf_soup(cells):
    """
    Converts the cells into a structured dictionary object which is
    Converts the cells into a structured dictionary object which is
    to be converted into JSON

    :param cells: A list of HTML <td>
    :type url: list
    :returns: A formatted dictionary representing 1 record
    :rtype: dict
    """
    value_dict = {}

    score_total_index = (len(cells) - 1) - 1
    logcat(score_total_index)

    #
    # position = re.sub(r"\D", '', cells[0].extract().text.encode("utf-8") )

    value_dict["player"] = cells[1].extract().text.strip().encode("utf-8")
    value_dict["to_par"] = cells[2].extract().text.strip().encode("utf-8")
    value_dict["score"] = { "total" : 0, "round" : [] }

    # The range is pre-defined.
    for i in xrange(3,7):
        # Replace '-' so only integers are left
        round_score = re.sub(r"\D", '', cells[i].extract().text.encode("utf-8") )
        round_score = 0 if not round_score else round_score
        value_dict["score"]["round"].append(int(round_score))

    # if 10 == len(cells):
    #     # If we have a row of 10 cells, then the row structure is...
    #     # Pos | Name | To Par | 1 | 2 | 3 | 4 | P | Total  Earnings
    #     score_total_index = 8

    # elif 9 == len(cells):
    #     # Else, if we have a row of 9 cells, then the row structure is...
    #     # Pos | Name | To Par | 1 | 2 | 3 | 4 | Total  Earnings
    #     score_total_index = 7

    value_dict["score"]["total"] = int(cells[score_total_index].extract().text)

    # Earnings for both golf and tennis is the last row
    value_dict["earnings_usd"] = re.sub(r"\D", '', cells[-1].extract().text.encode("utf-8") )

    value_dict["earnings_usd"] = 0 if not value_dict["earnings_usd"] else value_dict["earnings_usd"]
    value_dict["earnings_usd"] = int(value_dict["earnings_usd"])

    return value_dict

