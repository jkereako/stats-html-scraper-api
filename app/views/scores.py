#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Scores
    ~~~~~~

    Queries scoring data for a provided league and builds a JSON
    response object. Currently, the supported leagues are: MLB, NHL,
    NFL, NBA, MLS and EPL.

    The URL used is a JavaScript file which contains HTML content. So,
    before the HTML can be passed to BeautifulSoup, the document must be
    stripped of the call to document.write().

    :author: Jeff Kereakoglow
    :date: 2013-09-09
    :copyright: (c) 2013 by NESN.
    :license: BSD, see LICENSE for more details.
"""
from flask import Blueprint, jsonify
from app.utils import prepare_json_output, cache_data, fetch_cached_data
from datetime import date
from app.utils import slugify, logcat
from app.helpers import stats_date_string, help_fetch_soup

mod = Blueprint("scores", __name__, url_prefix="/scores")
SCORES_URL = "http://stats.nesn.com/multisport/today.js.asp"

#-- Query String Parameters
PARAM_SPORT = "sport"
PARAM_DATE = "day"
PARAM_LEAGUE = "lg"

# We cannot support the URL scores/ because STATS does a terrible job
# at distinguishing between sports. As of writing this, NHL preseason
# games were mixed in with MLB regular season games. This error only
# occurs if today's date is passed via querystring. Example:
# http://stats.nesn.com/multisport/today.js.asp?day=20130917

# @mod.route("/", methods=["GET"])
# def index():
#     """Fetches all today's scores for all active sports"""
#     return jsonify(scores_helper())

@mod.route("/mlb/", methods=["GET"])
@mod.route("/mlb/<int:year>/<int:month>/<int:day>/", methods=["GET"])
def mlb(year=None, month=None, day=None):
    """Fetches scoring information for the Major League Baseball"""
    return jsonify(scores_helper(year, month, day, "mlb"))

@mod.route("/nhl/", methods=["GET"])
@mod.route("/nhl/<int:year>/<int:month>/<int:day>/", methods=["GET"])
def nhl(year=None, month=None, day=None):
    """Fetches scoring information for the National Hockey League"""
    return jsonify(scores_helper(year, month, day, "nhl"))

@mod.route("/nfl/", methods=["GET"])
@mod.route("/nfl/<int:year>/<int:month>/<int:day>/", methods=["GET"])
def nfl(year=None, month=None, day=None):
    """Fetches scoring information for the National Football League"""
    # For some dumb-ass reason, STATS denotes the NFL as FB.
    return jsonify(scores_helper(year, month, day, "fb"))

@mod.route("/nba/", methods=["GET"])
@mod.route("/nba/<int:year>/<int:month>/<int:day>/", methods=["GET"])
def nba(year=None, month=None, day=None):
    """Fetches scoring information for the National Basketball League"""
    # For some dumb-ass reason, STATS denotes the NFL as FB.
    return jsonify(scores_helper(year, month, day, "nba"))

@mod.route("/epl/", methods=["GET"])
@mod.route("/epl/<int:year>/<int:month>/<int:day>/", methods=["GET"])
def epl(year=None, month=None, day=None):
    """Fetches scoring information for the English Premier League"""
    return jsonify(scores_helper(year, month, day, sport="ifb", league="epl"))

def scores_helper(year=None, month=None, day=None, sport=None, league=None):
    """
    Generic helper function to scrape scoring data from STATS's
    JavaScript file.

    :param year: The year of the desired scoreboard
    :type year: int

    :param month: The month of the desired scoreboard
    :type month: int

    :param day: The day of the desired scoreboard
    :type day: int

    :param sport: The sport of the desired scoreboard
    :type sport: str

    :param league: The league of the desired scoreboard
    :type league: str

    :returns: A formatted dictionary ready for display
    :rtype: dict
    """
    try:
        date_string = stats_date_string(date(year, month, day))
    except (ValueError, TypeError):
        date_string = stats_date_string()

    rv = fetch_cached_data()
    if rv is not None:
        return rv

    args = {
        PARAM_SPORT : sport,
        PARAM_DATE : date_string,
        PARAM_LEAGUE : league
    }

    soup = help_fetch_soup(
        SCORES_URL,
        request_params=args,
        source_file_type="JavaScript",
        class_attrs="shsTable"
    )

    # If there is 1 or 0 rows in the document, then, there are probably
    # no scores listed.
    if len(soup("tr")) <= 2:
        # del soup

        # Cache for a day to be safe
        out = {"message" : "No games scheduled for "}

        if not month and not day and not year:
            out["message"] += "today"
        else:
            out["message"] += "{month}/{day}/{year}".format(month=month, day=day, year=year)

        cache_data(data=out, timeout=60 * 60 * 24)

        return out

    stack = {}
    vals = []
    section = ''
    team = None
    has_the_status_cell = False

    # logcat(str(soup))

    for row in soup("tr"):

        # Rows which have team names do not have .
        # This test must be first.
        if row.get("class") is None:
            cells = row("td")
            has_the_status_cell = False

            # Does this row have a status row?
            if any(css_class in "shsMiniStatus" for cell in cells for css_class in cell.get("class") ):
                has_the_status_cell = True

            if len(cells) >= 2:

                team = "home" if team is "away" or None else "away"

                # If the list of values is empty, then initialize it
                if not vals:
                    vals.append({"away": None, "home":None})

                # If the list is complete, then append a new item
                # indicating a new game.
                elif vals[-1]["away"] and vals[-1]["home"]:
                    vals.append({"away": None, "home":None})

                # Add scoring information for the game.
                vals[-1][team] = {
                    "team": cells[0].find('a').extract().text.strip().encode("utf-8"),
                    "score": cells[1].extract().text.strip().encode("utf-8")
                }

                try:
                    # Try to convert the string to an int.
                    vals[-1][team]["score"] = int(vals[-1][team]["score"])
                except (ValueError, TypeError):
                    # If it fails, assign null
                    vals[-1][team]["score"] = None

                if has_the_status_cell:
                    status = cells[2].find('a')

                    # Arbitrary game information, such as "OT" for
                    # overtime
                    extra = cells[2].find('br')

                    time = cells[2].find(name="span", attrs={"class" : "shsTimezone shsGMTZone"})

                    # Set the status only if not null
                    if status:
                        vals[-1]["status"] = status.extract().text.strip().encode("utf-8")
                        if 2 == len(vals[-1]["status"].split('-')):
                            # Save the string to the right of '-' in
                            # extra
                            if not extra:
                                extra = vals[-1]["status"].split('-')[1].strip()
                            vals[-1]["status"] = vals[-1]["status"].split('-')[0].strip()

                        vals[-1]["status"] = vals[-1]["status"].lower()

                    if time:
                        vals[-1]["time"] = time.extract().text.strip().encode("utf-8")

                    if extra:
                        # Sometimes, extra contains a NavigableString
                        try:
                            vals[-1]["extra"] = extra.extract().text.strip().encode("utf-8")

                        # While other times, it's just a str
                        except:
                            vals[-1]["extra"] = extra

                        vals[-1]["extra"] = vals[-1]["extra"].lower()

        # Skip over the first line, it's the title
        elif "shsTableTtlRow" in row.get("class"):
            continue

        elif any(css_class in "shsTableSubttlRow shsSubSectionRow shsMiniRowSpacer" for css_class in row.get("class")):
            cell = row("td")
            section = cell[0].extract().text.strip().encode("utf-8")

            # Are the scores separated into sections? If so, find the
            # separator
            if section:
                section = slugify(text=unicode(section, "utf-8"), delimiter=u'_')
                if vals:
                    stack[section] = vals
                    vals = []
                # return section
                stack[section] = None

    # Save the last value
    else:
        if section:
            stack[section] = vals
        else:
            stack = vals

    del vals

    out = prepare_json_output(stack)

    # Cache for 1 minute
    cache_data(data=out, timeout=60)

    return out

def help_parse_nhl_soup(cells):
    pass
