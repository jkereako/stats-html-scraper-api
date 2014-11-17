#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Run
    ~~~

    This is the entry point into the application.

    It seemed to be a Flask convention to name this run.py, so, that is
    exactly what we did. Also, it makes the command line a bit more
    readable.

    To run the application manually from the command line, you first
    need to activate the virtual environment in which this application
    was developed. Before that, you should cd into the root directory
    of this application. Below are the bash commands to follow

    $ cd ~/path/to/nesn-aws
    $ . app/venv/bin activate
    $ (venv) python run.py
     * Running on http://127.0.0.1:5000/
     * Restarting with reloader

    If everything went well, you ought to see the 2 lines starting with
    "* Running on http://127.0.0.1:5000/". Navigate to that URL in your
    browser and you'll see NESN's API run.

    Tip: if you need to know what URLs are valid in the application,
    navigate to /help in your browser. A list of valid endpoints will be
    returned.


    :author: Jeff Kereakoglow
    :date: 2013-09-09
    :copyright: (c) 2013 by NESN.
    :license: BSD, see LICENSE for more details.
"""
from app import app
app.run(debug=True, host="localhost", port=5000)
