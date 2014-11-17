#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Schedule
    ~~~~~~~~

    Queries schedule data for a provided team and league and builds a
    JSON response object. Currently, the supported leagues are: MLB, NHL,
    NFL, NBA, MLS and EPL.

    :author: Jeff Kereakoglow
    :date: 2013-09-09
    :copyright: (c) 2013 by NESN.
    :license: BSD, see LICENSE for more details.
"""
from flask import Blueprint, jsonify, abort
from re import match, sub, split
from datetime import date
from calendar import month_abbr
from app import app
from app.utils import timestamp_from_string, prepare_json_output, fetch_cached_data, cache_data, logcat
from app.helpers import help_fetch_soup, help_parse_soup, format_int_for_stats, format_month_number_for_stats, get_team_id

mod = Blueprint("schedule", __name__, url_prefix="/schedule")

#-- Tokens
SPORT_TOKEN = "{{sport}}"

#-- Generic Constants
SCHEDULE_URL = "http://stats.nesn.com/" + SPORT_TOKEN + "/teamstats.asp"
CACHE_TIMEOUT = 60 * 60 * 24    # 24 hours
MONTH_ABBREVIATION_LIST = [v for k,v in enumerate(month_abbr)]

#-- Query String Parameters
PARAM_TEAM = "teamno"
PARAM_MONTH = "month"
PARAM_RESOURCE_TYPE = "type"

#-- Query String Arguments
ARG_RESOURCE_TYPE = "schedule"  # Defined here for readability

@mod.route("/mlb/<team>", methods=["GET"])
def mlb(team):
    """
    Returns the schedule for any MLB team

    :param team: The name of the team
    :type team: str

    :returns: A JSON response
    :rtype: flask.Response
    """
    out = schedule_helper(
        sport="mlb",
        team=team,
        from_month=2,
        to_month=11,
        parser_func=parse_mlb_soup
    )

    return jsonify(out)

@mod.route("/nhl/<team>", methods=["GET"])
def nhl(team):
    """
    Returns the schedule for any NHL team

    :param team: The name of the team
    :type team: str

    :returns: A JSON response
    :rtype: flask.Response
    """
    out = schedule_helper(
        sport="nhl",
        team=team,
        from_month=9,
        to_month=6,
        parser_func=parse_nhl_soup
    )

    return jsonify(out)

@mod.route("/nfl/<team>", methods=["GET"])
def nfl(team):
    """
    Returns the schedule for any NHL team

    :param team: The name of the team
    :type team: str

    :returns: A JSON response
    :rtype: flask.Response
    """

    # The argument "schedule" is an invalid argument when requesting an
    # NFL schedule from STATS. However, "schedules", is valid.
    global ARG_RESOURCE_TYPE

    ARG_RESOURCE_TYPE ="schedules"

    out = schedule_helper(
        sport="fb",
        team=team,
        parser_func=parse_nfl_soup
    )

    return jsonify(out)


#-- Helpers
def schedule_helper(sport, team, from_month=None, to_month=None, parser_func=None):
    """
    Returns all rankings for all matches

    TODO: Support filtering operations passed via query string.

    :param url: URL of the ranking
    :type url: str

    :param team: The ID of the team
    :type team: int

    :param from_month: The month number from which the schedule begins
    :type from_month:  int

    :param to_month: The month number for which the schedule terminates
    :type to_month:  int

    :param parse_func: The parsing function to be applied to the scraped
    :type parse_func: str

    :returns: A formatted dictionary ready for display
    :rtype: dict
    """

    team_id = get_team_id(sport, team)

    if team_id is None:
        abort(404)

    rv = fetch_cached_data(args=sport + str(team_id))

    if rv is not None:
        return rv

    url = SCHEDULE_URL.replace(SPORT_TOKEN, sport)

    stack = []

    # At this time, the NFL schedule is not listed by month.
    if from_month is None and to_month is None:
        args = {
            PARAM_TEAM : format_int_for_stats(team_id),
            PARAM_RESOURCE_TYPE: ARG_RESOURCE_TYPE
        }
        soup = help_fetch_soup(url, request_params=args)

        # Only use the first table
        stack = help_parse_soup(soup("table")[0], parser_func)

    # Iterate through schedules which have a separate URL for each month
    else:
        # To increase readability, we allow the caller function to define
        # from_month and to_month in a familiar format. However, if the
        # values of from_month and to_month are 9 to 6 respectively, then it
        # becomes impossible to build an xrange. To, correct this, we ensure
        # the value of to_month is always greater than the value of
        # from_month by increasing its value 12 and then taking
        # the mod base 12 later on down the river.

        to_month = to_month + 12 if to_month < from_month else to_month

        for month in xrange(from_month, to_month):
            # Build the argument list for STATS.
            args = {
                PARAM_TEAM : format_int_for_stats(team_id),
                PARAM_RESOURCE_TYPE: ARG_RESOURCE_TYPE,
                PARAM_MONTH : format_month_number_for_stats(month, pad_with_zero=True)
            }

            # http://stackoverflow.com/questions/15871769/using-beautiful-soup-grabbing-stuff-between-li-and-li
            soup = help_fetch_soup(url, request_params=args)

            # Must use += to make this a flat list
            stack += help_parse_soup(soup, parser_func, format_month_number_for_stats(month))
            # stack[month] = help_parse_soup(soup, parser_func, month)


    out = prepare_json_output(stack)
    cache_data(data=out, args=sport + str(team_id), timeout=CACHE_TIMEOUT)
    return out

def parse_nhl_soup(cells, month):
    """
    Returns all rankings for all matches. This is called once per row
    in the table. If there are 10 rows in the table, this function will
    be called 10 times.

    :param cells: A list of <td> elements
    :type cells: list
    :param month: The month of the schedule
    :type cells: int
    :returns: A formatted dictionary representing 1 record
    :rtype: dict
    """
    # Date | Opponent | Time | TV | Result

    vals = {}
    game_time = None

    opponent = cells[1].extract().text.strip().encode("utf-8")

    vals["is_home_game"] = is_home_game(opponent)
    vals["opponent"] = strip_opponent_string(opponent)

    # 5 columns for future games. At the time of writing this, this is
    # all there is.
    if 5 == len(cells):
        game_time = help_build_date_string(cells=cells, indices=[0, 2], month=month)
        vals["networks"] = help_build_tv_network_list(cells, col_idx=3)
        vals["ts"] = int(timestamp_from_string(game_time))

    return vals

def parse_mlb_soup(cells, month):
    # All Spring Training Games, Past and Future (5 columns)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Date | Opp | Time | TV | Result
    #
    #
    # Regular and Post Season Past Game (8 columns)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Date | Opp | Result | Rec | Win | Loss | Save | Att
    #
    #
    # Regular and Post Season Future Game (5 or 6 columns)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Date | Opp | Time | TV | My Team : Pitcher | Opp: Pitcher
    #
    # The columns "My Team: Pitcher" and "Opp: Pitcher" may be combined
    # together if both are unknowns, making the column count 5


    vals = {}

    game_time = help_build_date_string(cells=cells, indices=[0, 2], month=month)
    opponent = cells[1].extract().text.strip().encode("utf-8")

    vals["is_home_game"] = is_home_game(opponent)
    vals["opponent"] = strip_opponent_string(opponent)

    if len(cells) >= 5 and len(cells) < 8:

        #-- Spring Training
        if month < 4:
            vals["result"] = help_parse_result(cells, col_idx=4, find="result")
            vals["score"] = help_parse_result(cells, col_idx=4, find="score")

        #-- Regular and Post Season: Future Games
        else:
            # Do we know who is pitching? If so, there will be 6 columns
            if 6 == len(cells):
                vals["home_pitcher"] = cells[4].extract().text.strip().encode("utf-8")
                vals["opp_pitcher"] = cells[5].extract().text.strip().encode("utf-8")

        game_time = help_build_date_string(cells=cells, indices=[0, 2], month=month)
        vals["networks"] = help_build_tv_network_list(cells, col_idx=3)
        vals["ts"] = int(timestamp_from_string(game_time))

    #-- Regular and Post Season: Past Games
    elif 8 == len(cells):
        vals["result"] = help_parse_result(cells, col_idx=2, find="result")
        vals["score"] = help_parse_result(cells, col_idx=2, find="score")
        vals["winning_pitcher"] = cells[4].extract().text.strip().encode("utf-8")
        vals["losing_pitcher"] = cells[5].extract().text.strip().encode("utf-8")
        vals["save"] = cells[6].extract().text.strip().encode("utf-8")
        vals["save"] = None if not vals["save"] else vals["save"]

    return vals

def parse_nfl_soup(cells):
    """
    Returns all rankings for all matches. This is called once per row
    in the table. If there are 10 rows in the table, this function will
    be called 10 times.

    :param cells: A list of <td> elements
    :type cells: list
    :param month: The month of the schedule
    :type cells: int
    :returns: A formatted dictionary representing 1 record
    :rtype: dict
    """
    # Week | Day | Date | Opponent | Time | TV | Result
    vals = {}

    # Bye week
    if 2 == len(cells):
        vals["is_bye_week"] = True

    else:
        game_time = None
        game_time = help_build_date_string(cells=cells, indices=[1, 4])

        opponent = cells[3].extract().text.strip().encode("utf-8")

        vals["is_home_game"] = is_home_game(opponent)
        vals["opponent"] = strip_opponent_string(opponent)
        vals["networks"] = help_build_tv_network_list(cells, col_idx=5)
        vals["result"] = help_parse_result(cells, col_idx=6, find="result")

        vals["score"] = help_parse_result(cells, col_idx=6, find="score")

        # vals["score"] = {
        #     "new_england" : vals["score"][0],
        #     "opponent" : vals["score"][1]
        # }

    return vals

def help_build_date_string(cells, indices, month=None):
    """
    Returns all rankings for all matches. This is called once per row
    in the table. If there are 10 rows in the table, this function will
    be called 10 times.

    :param cells: A list of <td> elements
    :type cells: list

    :param indices: A list of indicies which denote date and time
    :type indices: list

    :param month: The month of the schedule
    :type cells: int

    :returns: A formatted dictionary representing 1 record
    :rtype: dict
    """

    # Past and future games will always have the date
    date_str = cells[indices[0]].extract().text.strip().encode("utf-8")

    if month is not None:
        date_str += ' ' + MONTH_ABBREVIATION_LIST[month]

    date_str += ' ' + str(date.today().year)

    # Only future games will have the time
    if len(indices) > 1:
        try:
            # STATS always provides multiple timezones, find the GMT one
            date_str += ' ' + cells[indices[1]].find(name="span", attrs={"class" : "shsGMTZone"}).extract().text.encode("utf-8")
        except Exception:
            pass

    return date_str

def help_parse_result(cells, col_idx, find=None):
    if "score" == find:
        vals = cells[col_idx].find('a').text.strip().encode("utf-8")
    else:
        vals = cells[col_idx].text.strip().encode("utf-8")

    # Split on whitespace and hyphens while ignoring delimiters
    # Example result: ['W', '23', '17']
    vals = split(r"\s|-", vals)

    if "result" == find:
        # This will be either a W or L
        result = vals.pop(0).strip().lower()

        # Win
        if 'w' in result:
            return "win"

        # Loss
        elif 'l' in result:
            return "loss"

        # Tie
        elif 't' in result:
            return "tie"

    elif "score" == find:
        try:
            return [int(score) for score in vals]
        except Exception:
            pass

def help_build_tv_network_list(cells, col_idx):
    """
    Returns a list of Networks, or None if none is listed
    """
    rv = cells[col_idx].extract().text.strip().encode("utf-8")

    return None if not rv else rv.split('/')

def is_home_game(opponent):
    rv = False

    # An exception will be thrown if match() returns None
    try:
        rv = False if bool(match(r"^(@|at)\s+", opponent)) else True
        pass
    except Exception:
        rv = False

    return rv

def strip_opponent_string(opponent):
    return sub(r"^(vs.?|@|at)\s+", '', opponent)
