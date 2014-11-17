#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Standings
    ~~~~~~~~~

    Deemed complete as of 2013-11-22. Supports MLB, NHL, NBA, NFL, EPL
    and MLS

    Queries the standings for a provided league and builds a JSON
    response object. Currently, the supported leagues are: MLB, NHL,
    NFL, NBA, MLS and EPL.

    The URLs along with the table layouts within which the standings
    data lies, differs among leagues. For these reasons, some of the
    code could not be abstracted out into delegate functions and had to be
    handled within this file.

    Also, the returned data for each league is not identical. For
    example, the NHL uses a points system while the MLB and NFL use a
    ratio of wins to losses.

    :author: Jeff Kereakoglow
    :date: 2013-09-09
    :copyright: (c) 2013 by NESN.
    :license: BSD, see LICENSE for more details.
"""
from flask import Blueprint, jsonify
from app.utils import prepare_json_output, cache_data, fetch_cached_data, slugify, logcat
from app.helpers import help_fetch_soup

mod = Blueprint("standings", __name__, url_prefix="/standings")

# Pretty much useless, but the deviation between URLs is retarded
STANDINGS_URL = "http://stats.nesn.com/"

@mod.route("/mlb/", methods=["GET"])
def mlb():
    """
    Returns the MLB standings as JSON.

    :returns: A JSON response
    :rtype: flask.Response
    """
    url = STANDINGS_URL + "mlb/standings.asp"
    return jsonify(standings_helper(url, league="mlb"))

@mod.route("/nhl/", methods=["GET"])
def nhl():
    """
    Returns the NHL standings as JSON.

    :returns: A JSON response
    :rtype: flask.Response
    """
    url = STANDINGS_URL + "nhl/standings.asp"
    return jsonify(standings_helper(url, league="nhl"))

@mod.route("/nfl/", methods=["GET"])
def nfl():
    """
    Returns the NFL standings as JSON.

    :returns: A JSON response
    :rtype: flask.Response
    """
    # Remeber! STATS calls the NFL FB. 'Cause why the fuck not?!
    url = STANDINGS_URL + "fb/totalstandings.asp"
    return jsonify(standings_helper(url, league="nfl"))


@mod.route("/nba/", methods=["GET"])
def nba():
    """
    Returns the NBA standings as JSON.

    :returns: A JSON response
    :rtype: flask.Response
    """
    url = STANDINGS_URL + "nba/standings.asp"
    return jsonify(standings_helper(url, league="nba"))

@mod.route("/epl/", methods=["GET"])
def epl():
    """
    Returns the EPL standings as JSON.

    :returns: A JSON response
    :rtype: flask.Response
    """
    url = STANDINGS_URL + "epl/standings.asp"
    return jsonify(
        standings_helper(
            url,
            league="epl",
            skip_conference_row=True
        )
    )

@mod.route("/mls/", methods=["GET"])
def mls():
    """
    Returns the MLS standings as JSON.

    :returns: A JSON response
    :rtype: flask.Response
    """
    url = STANDINGS_URL + "mls/standings.asp"
    return jsonify(
        standings_helper(
            url,
            league="mls",
            skip_conference_row=True
        )
    )

def standings_helper(url, league, skip_conference_row=False):
    """
    Fetches and parses data.

    Supports layouts with multiple tables or with single tables. At the
    time of writing this, the MLB standings is split into 2 tables,
    while the NHL is 1.

    :param league: The league of the desired scoreboard
    :type league: str

    :returns: A formatted dictionary ready for display
    :rtype: dict
    """

    rv = fetch_cached_data()
    if rv is not None:
        return rv

    soup = help_fetch_soup(url)

    column_list = []
    row_list = []
    stack = {}

    # Iterate over each conference/league
    for table in soup("table"):
        conference = None
        division = None

        # Iterate over each division
        for row in table("tr"):

            if row.get("class") is None:
                continue

            elif "shsTableTtlRow" in row.get("class"):
                if skip_conference_row:
                    continue

                # Single table layout support.
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # If the string conference evaluates to true, then we've
                # encountered a new conference. Save the data that
                # exists in the lists column_list and row_list
                if conference:

                    # Does the list colum_stack have any data?
                    if column_list:
                        # Is this layout split into divisions?
                        if division:
                            row_list.append( { division : column_list } )
                        else:
                            row_list = column_list

                        column_list = []

                    stack[conference] = row_list
                    row_list = []

                conference = row.extract().text.strip().lower().encode("utf-8")
                conference = slugify(text=unicode(conference, "utf-8"), delimiter=u'_')

            elif "shsTableSubttlRow" in row.get("class"):
                # If the string division evaluates to true, then we've
                # encountered a new division. Save the data that
                # exists in the lists column_list and row_list
                if division:
                    # Does the list colum_stack have any data?
                    if column_list:
                        # Is this layout split into divisions?
                        if division:
                            row_list.append( { division : column_list } )
                        else:
                            row_list.append(column_list)

                        column_list = []

                division = row.extract().text.strip().lower().encode("utf-8")
                division = division.replace("division", '')
                division = slugify(text=unicode(division, "utf-8"), delimiter=u'_')

            elif any(css_class.startswith("shsRow") for css_class in row.get("class")):
                cells = row("td")
                value_dict = None

                if "mlb" == league:
                    value_dict = help_parse_mlb_soup(cells)

                elif "nhl" == league:
                    value_dict = help_parse_nhl_soup(cells)

                elif "nfl" == league:
                    value_dict = help_parse_nfl_soup(cells)

                elif "nba" == league:
                    value_dict = help_parse_nba_soup(cells)

                elif "mls" == league:
                    value_dict = help_parse_mls_soup(cells)

                elif "epl" == league:
                    value_dict = help_parse_epl_soup(cells)

                if value_dict is not None:
                    column_list.append(value_dict)

        #end for row in table("tr")

        # Get the last division in the table
        if division:
            row_list.append( { division : column_list } )

        # If there is no division, then make the columns close to the
        # conference
        else:
            row_list = column_list

        column_list = []

        # We must evaluate conference because EPL and MLS do not have
        # conferences
        if conference:
            stack[conference] = row_list

        # If a conference is nonexistent, then check for division's
        # existence. If a division exists, then treat as if it was a
        # conference (i.e. place the division at the highest level).
        # Currently, this only occurs with MLS.
        elif division:
            if row_list[0][division]:
                stack[division] = row_list[0][division]

        # Otherwise, both conference and division are nonexistent.
        # Convert stack into a list so the teams are ordered
        # accordingly.
        # Currently, this only occurs with EPL.
        else:
            # stack is a Dictionary, change it to a list
            del stack
            stack = row_list

        row_list = []

    #end for table in soup("table")
    out = prepare_json_output(stack)
    del row_list, stack

    # Cache for 2 hours
    cache_data(data=out, timeout=60 * 60 * 2)

    return out

def help_parse_mlb_soup(cells):
    """
    Helps parse data for MLB.

    :param cells: A collection of table cells from a single row.
    :type cells: dict

    :returns: A formatted dictionary
    :rtype: dict
    """

    value_dict = {}
    # Convert all NavigableStrings to Python str
    # http://bugs.python.org/issue1757057
    value_dict["team"] = str(cells[0].find('a').extract().text.strip().encode("utf-8"))   # team
    value_dict["wins"] = int(cells[1].extract().text.encode("utf-8"))   # Wins
    value_dict["losses"] = int(cells[2].extract().text.encode("utf-8"))   # Losses
    value_dict["percentage"] = float(cells[3].extract().text.encode("utf-8"))   # Win Percentage

    try:
        value_dict["games_behind"] = float(cells[4].extract().text.encode("utf-8"))   # Games behind
    except Exception:
        value_dict["games_behind"] = 0

    return value_dict

def help_parse_nhl_soup(cells):
    value_dict = {}
    #GP W   L   OTL Pts GF  GA  Home    Road    L10

    # Convert all NavigableStrings to Python str
    # http://bugs.python.org/issue1757057
    value_dict["team"] = str(cells[0].find('a').extract().text.strip().encode("utf-8"))   # team

    value_dict["games_played"] = int(cells[1].extract().text.encode("utf-8"))
    value_dict["wins"] = int(cells[2].extract().text.encode("utf-8"))
    value_dict["losses"] = int(cells[3].extract().text.encode("utf-8"))
    value_dict["overtime_losses"] = int(cells[4].extract().text.encode("utf-8"))
    value_dict["points"] = int(cells[5].extract().text.encode("utf-8"))
    value_dict["goals_for"] = int(cells[6].extract().text.encode("utf-8"))
    value_dict["goals_against"] = int(cells[7].extract().text.encode("utf-8"))

    return value_dict

def help_parse_nfl_soup(cells):
    value_dict = {}
    # Convert all NavigableStrings to Python str
    # http://bugs.python.org/issue1757057
    value_dict["team"] = str(cells[0].find('a').extract().text.strip().encode("utf-8"))
    value_dict["wins"] = int(cells[1].extract().text.encode("utf-8"))
    value_dict["losses"] = int(cells[2].extract().text.encode("utf-8"))
    value_dict["ties"] = int(cells[3].extract().text.encode("utf-8"))
    value_dict["percentage"] = float(cells[4].extract().text.encode("utf-8"))

    try:
        value_dict["games_behind"] = float(cells[5].extract().text.encode("utf-8"))
    except Exception:
        value_dict["games_behind"] = 0

    return value_dict

def help_parse_mls_soup(cells):
    value_dict = {}
    # Convert all NavigableStrings to Python str
    # http://bugs.python.org/issue1757057

    value_dict["team"] = str(cells[0].find('a').extract().text.strip().encode("utf-8"))
    value_dict["games_played"] = int(cells[1].extract().text.encode("utf-8"))
    value_dict["wins"] = int(cells[2].extract().text.encode("utf-8"))
    value_dict["draws"] = int(cells[3].extract().text.encode("utf-8"))
    value_dict["losses"] = int(cells[4].extract().text.encode("utf-8"))
    value_dict["goals_for"] = int(cells[5].extract().text.encode("utf-8"))
    value_dict["goals_against"] = int(cells[6].extract().text.encode("utf-8"))
    value_dict["points"] = int(cells[10].extract().text.encode("utf-8"))

    return value_dict

#-- Function Aliases
# Assign the aliases where functions are identical. Added here for
# completeness
help_parse_nba_soup = help_parse_mlb_soup
help_parse_epl_soup = help_parse_mls_soup
