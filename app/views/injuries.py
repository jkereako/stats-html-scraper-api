#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Injuries
    ~~~~~~~~

    Returns a list of injuries for each league.

    :author: Jeff Kereakoglow
    :date: 2013-09-09
    :copyright: (c) 2013 by NESN.
    :license: BSD, see LICENSE for more details.
"""
from flask import Blueprint, jsonify
import re

import requests
from bs4 import BeautifulSoup, SoupStrainer
from app.utils import prepare_json_output, fetch_cached_data, cache_data, timestamp_from_string

mod = Blueprint("injuries", __name__, url_prefix="/injuries")

@mod.route("/mlb/", methods=["GET"])
def mlb():
    # Because this object does not take any arguments, always cache

    rv = fetch_cached_data(cache_key="mlb_injuries")

    if rv is not None:
        return jsonify(rv)

    r = requests.get("http://stats.nesn.com/mlb/stats.asp?file=recentinj")
    raw_string = re.sub(r"\s+", ' ', r.text)

    # http://stackoverflow.com/questions/15871769/using-beautiful-soup-grabbing-stuff-between-li-and-li
    soup = BeautifulSoup(raw_string, from_encoding="UTF-8", parse_only=SoupStrainer(name="div", attrs={"id": "shsMLBrecentinj"}))
    del r, raw_string

    # for e in soup.findAll('br'):
    #     e.extract()

    team = None
    vals = {}
    stack = []
    team_stack = []

    # Remove title
    iter_soup = soup(["h2", "table"])
    iter_soup.pop(0)
    iter_soup.pop(0)

    # return str(iter_soup)

    for item in iter_soup:

        if item is None:
            continue

        # The team name
        elif "shsTableTitle" in item.get("class"):
            team = item.extract().text.encode("utf-8").lower().replace(' ', '_')

        # The important data
        else:
            for row in item("tr"):

                # The title row... Date, Player, Status
                if "shsTableTtlRow" in row.get("class"):
                    continue

                cells = row("td")
                vals["ts"] = int(timestamp_from_string(cells[0].extract().text.encode("utf-8")))
                vals["player"] = cells[1].extract().text.encode("utf-8")
                vals["status"] = cells[2].extract().text.encode("utf-8")

                team_stack.append(vals.copy())

            if team_stack:
                stack.append({ team : team_stack })
                team_stack = []

    out = prepare_json_output(stack)

    # Cache for 12 hours
    cache_data(data=out, timeout=60 * 60 * 12)

    return jsonify(out)
