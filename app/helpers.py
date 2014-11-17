#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Helpers
    ~~~~~~~

    This is a dumping ground for refactored code. This file grows as old
    code is revisited, reassessed and then, refactored.

    In the context of this application, helper functions differ from
    Util functions in that Helper functions contain hard-coded stuff
    particular to certain cases. The functions in Utils are strictly
    generic, no hard-coded values.

    :author: Jeff Kereakoglow
    :date: 2013-09-09
    :copyright: (c) 2013 by NESN.
    :license: BSD, see LICENSE for more details.
"""
from re import sub
import requests
from flask.json import dumps, loads
from ast import literal_eval
from random import randint
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup, SoupStrainer
from app import app, redis
from app.utils import logcat, slugify, query_string_arg_to_bool, fetch_cached_data, cache_data, prepare_json_output

#-- Tokens
URL_TOKEN = "{{team}}"

TEAMS_URL = "http://stats.nesn.com/" + URL_TOKEN + "/teams.asp"

#-- Query String Parameters
PARAM_FLAT_LIST = "flat_list"

def scoreboard_display_rules():
    """
    Defines display rules for NESN's main scoreboard.

    There are 2 parts to the display rules, rank and time shown.Each
    league is ranked in order of which it ought to appear. For example,
    MLB games will always have the top-most position when displaying a
    scoreboard which consists of multiple sports. Also, the last MLB
    game will only be shown for 1 day, while future games will be shown
    15 hours in advance. Mike Hall came up with the time boundaries.
    """
    now = datetime.now()
    display_rules = {
        "mlb" : {
            "rank" : 0,
            "past" : now - timedelta(days=1),
            "future" : now + timedelta(hours=15)
        },
        "nhl" : {
            "rank" : 1,
            "past" : now - timedelta(days=6),
            "future" : now + timedelta(hours=18)
        },

        "nfl" : {
            "rank" : 2,
            "past" : now - timedelta(days=4),
            "future" : now + timedelta(days=1)
        },
        "nba" : {
            "rank" : 3,
            "past" : now - timedelta(days=2),
            "future" : now + timedelta(hours=18)
        },

        "mls" : {
            "rank" : 4,
            "past" : now - timedelta(hours=1),
            "future" : now + timedelta(hours=4)
        },

        "epl" : {
            "rank" : 5,
            "past" : now - timedelta(days=1),
            "future" : now + timedelta(hours=18)
        },
    }

    return display_rules

def teams_helper(sport=None):
    """
    Generic helper function to scrape scoring data from STATS's
    JavaScript file.
    """

    flat_list = query_string_arg_to_bool(PARAM_FLAT_LIST)

    rv = fetch_cached_data(args=PARAM_FLAT_LIST if flat_list else None)

    if rv is not None:
        return rv

    # STATs does not order NFL teams
    nfl_teams = [
        "Atlanta Falcons",
        "Buffalo Bills",
        "Chicago Bears",
        "Cincinnati Bengals",
        "Cleveland Browns",
        "Dallas Cowboys",
        "Denver Broncos",
        "Detroit Lions",
        "Green Bay Packers",
        "Tennessee Titans",
        "Indianapolis Colts",
        "Kansas City Chiefs",
        "Oakland Raiders",
        "St. Louis Rams",
        "Miami Dolphins",
        "Minnesota Vikings",
        "New England Patriots",
        "New Orleans Saints",
        "New York Giants",
        "New York Jets",
        "Philadelphia Eagles",
        "Arizona Cardinals",
        "Pittsburgh Steelers",
        "San Diego Chargers",
        "San Francisco 49ers",
        "Seattle Seahawks",
        "Tampa Bay Buccaneers",
        "Washington Redskins",
        "Carolina Panthers",
        "Jacksonville Jaguars",
        '',
        '',
        "Baltimore Ravens",
        "Houston Texans"
    ]

    soup = help_fetch_soup(url=TEAMS_URL.replace(URL_TOKEN, sport))

    stack = []
    redis_stack = []
    league_stack = []
    division_stack = []
    league = None
    division = None

    # Iterate over each conference
    for table in soup("table"):

        for row in table("tr"):
            if row.get("class") is None:
                continue

            cells = row("td")

            # Conference Row
            if "shsTableTtlRow" in row.get("class"):
                if flat_list:
                    continue

                if division_stack and division:
                    league_stack.append({ division : division_stack })

                    division_stack = []

                if league_stack and league:
                    stack.append({ league : league_stack })

                    league_stack = []

                league = format_division(row)

            # Division Row
            elif "shsTableSubttlRow" in row.get("class"):
                if flat_list:
                    continue

                if division_stack and division:
                    league_stack.append({ division : division_stack })

                    division_stack = []

                division = format_division(row)

            # Team Row
            else:
                team = cells[0].extract().text.strip().encode("utf-8")

                # Save the team as a flat list for persistent storage
                redis_stack.append(team)

                if flat_list:
                    stack.append(team)
                else:
                    division_stack.append(team)
        else:
            if division_stack and division:
                league_stack.append({ division : division_stack })

                division_stack = []

            if league_stack and league:
                stack.append({ league : league_stack })

                league_stack = []

    out = prepare_json_output(stack)
    del soup, division_stack, league_stack, stack

    redis_key = app.config["REDIS_KEY_TEAMS"].replace(
        app.config["REDIS_KEY_TOKEN_SPORT"],
        "nfl" if "fb" == sport else sport
    )

    if not redis.exists(redis_key):
        if "fb" == sport:
            redis_stack = nfl_teams

        # Convert the object to a JSON string
        redis.set(
            name=redis_key,
            value=dumps(prepare_json_output(redis_stack))
        )

    del redis_key, redis_stack

    cache_data(
        data=out,
        args=PARAM_FLAT_LIST if flat_list else None,
        timeout=60 * 60 * 24 * 300    # Cache for 300 days
    )

    return out

def get_team_id(sport, team):
    redis_key = app.config["REDIS_KEY_TEAMS"].replace(
        app.config["REDIS_KEY_TOKEN_SPORT"],
        "nfl" if "fb" == sport else sport
    )

    # First, check if the redis key exists and if it doesn't, recreate
    #
    if not redis.exists(redis_key):
        teams_helper(sport)

    # If we can't find it now, then something is definitely wrong.
    teams = redis.get(redis_key)

    if not teams:
        return None

    teams = loads(teams)

    # Replace usual tokens which represent whitespace with an actual
    # space.
    team = sub(r"(\+|_|-)", ' ', team)

    # Search for the requested team ID
    rv = [idx for idx, val in enumerate(teams["data"]) if val.lower().startswith(team)]

    # If there is more than 1 result or if there are no results
    if len(rv) > 1 or not rv:
        return None

    # Add 1 to fix the off-by-one error. Internally, the team with the
    # ID #1 is actually 0.
    return 1 + int(rv.pop())

def format_height(height):
    """
    Converts feet and inches into inches.

    http://stackoverflow.com/questions/672172/how-to-use-python-map-and-other-functional-tools
    http://stackoverflow.com/questions/4406389/if-else-in-a-list-comprehension

    1) Split the string "6-3" into a list of strings ['6','3']
    2) Convert the first element to an int and multiply it by 12
    3) Convert the second element to int
    4) Add both elements together and return and int
    """
    try:
        return sum(map(lambda x: int(x[1]) * 12 if x[0] == 0 else int(x[1]), enumerate(height.split('-'))))
    except Exception:
        pass

    return None

def format_division(nav_str):
    division = nav_str.extract().text.strip().lower().encode("utf-8")
    division = sub(r"(conference|divisi?on|league|football)\s?", '', division)
    division = slugify(text=unicode(division, "utf-8"), delimiter=u'_')

    return division

def format_int_for_stats(number):
    """STATS requires the numbers 1 through 9 to be padded with a zero.

    :returns: A formatted string
    :rtype: str
    """
    return str(number).zfill(2)

def format_month_number_for_stats(month, pad_with_zero=False):
    """STATS requires the numbers 1 through 9 to be padded with a zero.

    :returns: A formatted string
    :rtype: str
    """
    new_month = month % 12

    # new_month will be zero if month is December (12)
    new_month = 12 if new_month is 0 else new_month

    # Pad with a zero if we have a single digit
    return format_int_for_stats(new_month) if pad_with_zero else new_month

def help_fetch_soup(url, source_file_type="html", request_params=None, element=None, class_attrs=None):
    """
    Fetches the common markup shared among several things.

    :returns: A soup
    :rtype: bs4.BeautifulSoup
    """
    r = requests.get(url, params=request_params)

    # logcat(r.url)

    # Strip unnecessary whitespace from the string before passing it to
    # BeautifulSoup. I don't know if this makes things easier, but we're
    # doing it anyway.
    raw_string = sub(r"\s+", ' ', r.text)

    element = "table" if element is None else element
    class_attrs = "shsTable shsBorderTable" if class_attrs is None else class_attrs
    # class_attrs = "shsTable" if class_attrs is None else class_attrs

    # Some date from STATS are stored in a malformed JavaScript file and
    # which contain docWrites(). The best method is to call this file
    # and parse the HTML
    if source_file_type.lower() == "javascript":
        # Remove the JavaScript function call
        raw_string = raw_string.replace("document.write('", '')
        raw_string = raw_string.replace("');", '')

    # logcat(raw_string)

    soup = BeautifulSoup(
        raw_string,
        from_encoding="utf-8",
        parse_only=SoupStrainer(name=element, attrs={"class" : class_attrs})
    )

    del r, raw_string
    return soup

# http://stackoverflow.com/questions/803616/passing-functions-with-arguments-to-another-function-in-python#803632
def help_parse_soup(soup, parser_func, *args):
    """
    Generic function which iterates through all rows of a table and skips
    title rows.

    This function must only be called once. The callback function passed via
    the parameter "func" will be called once for each row in the table.

    :param url: URL of the ranking
    :type url: str
    :param parser_func: A callback function. Must accept a list of cells
    :type parser_func: str
    :returns: A list of parsed rows from a table
    :rtype: list
    """
    stack = []

    for row in soup("tr"):
        # Prevent raising an exception for trying to iterate over None
        if  row.get("class") is None:
            pass

        # Skip the table's title, subtitle and the column titles
        elif any(css_class in "shsTableTtlRow shsTableSubttlRow shsColTtlRow" for css_class in row.get("class")):
            continue

        cells = row("td")
        stack.append(parser_func(cells, *args))
    return stack

def help_get_list_from_dropdown(url, attr_name):
    """Helper function which fetches a list of golf tours or tennis
    series. Returns a list of strings.
    """
    r = requests.get(url)
    raw_string = sub(r"\s+", ' ', r.text)

    soup = BeautifulSoup(
        raw_string,
        from_encoding="utf-8",
        parse_only=SoupStrainer(name="select", attrs={"name" : attr_name})
    )

    del r, raw_string
    stack = []
    for option in soup("option"):
        if option["value"]:
            stack.append(option["value"].strip().encode("utf-8"))

    del soup
    return stack


def stats_date_string(d=None):
    """
    Returns a string that is parseable by STATS.

    This function was created with PHP's strtotime in mind. This may be
    removed if it discovered that Python supports this natively. I'm
    certain it does.

    :returns: The current timestamp as a string
    :rtype: str
    """
    d = date.today() if d is None else d
    return d.strftime("%Y%m%d")

def ics_datetime_format(dt):
    """
    Returns a string that is parseable by STATS.

    This function was created with PHP's strtotime in mind. This may be
    removed if it discovered that Python supports this natively. I'm
    certain it does.

    :returns: The current timestamp as a string
    :rtype: str
    """
    return dt.strftime("%Y%m%dT%H%M%S")

def ics_uid_format(a_date, domain=None):
    """
    Returns a string that is parseable by STATS.

    This function was created with PHP's strtotime in mind. This may be
    removed if it discovered that Python supports this natively. I'm
    certain it does.

    :returns: The current timestamp as a string
    :rtype: str
    """
    rv= a_date.strftime("%Y%m%d") + str(randint(1, 100))

    return rv if domain is None else rv + domain
