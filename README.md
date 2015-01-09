# STATS, LLC. scraper
A [Flask](http://flask.pocoo.org/) application which scrapes data from [NESN's web site hosted at STATS.com](http://nesn.stats.com) using [Beautiful Soup 4.3.2](http://www.crummy.com/software/BeautifulSoup/) and returns a JSON object using Flask's [jsonify](http://flask.pocoo.org/docs/0.10/api/#flask.json.jsonify).

I began this project while employed at [NESN](http://nesn.com) to better understand Python and to learn the Flask framework. The intended goal was to organize STATS's data into an intelligble resource for use with client applications. Take a look at STATS's website and you'll see contains HTML markup circa 1996.

This API was never used for production, partly because scraping HTML is notoriously unreliable—but, 1 year after original development and it still works—but mostly because there was no clear way to monetize this. As such, it was a purely acedemic exercise.

I'm hoping someone can use this to build some neat client-side applications.

# Installation
See [`INSTALL.md`](https://github.com/jkereako/stats-html-scraper-api/blob/master/INSTALL.md).

# Supported endpoints
Below are all the endpoints registered with this API. Not all of them work.
 - `/standings/mlb/` 
 - `/standings/nhl/` 
 - `/standings/nfl/` 
 - `/standings/nba/` 
 - `/standings/epl/` 
 - `/standings/mls/` 
 - `/rankings/tennis/` 
 - `/rankings/golf/` 
 - `/injuries/mlb/` 
 - `/scores/mlb/` 
 - `/scores/nhl/` 
 - `/scores/nfl/` 
 - `/scores/nba/` 
 - `/scores/epl/` 
 - `/teams/mlb/` 
 - `/teams/nhl/` 
 - `/teams/nfl/` 
 - `/teams/nba/` 
 - `/teams/epl/` 
 - `/posts/` 
 - `/help` 
 - `/scores/mlb/<int:year>/<int:month>/<int:day>/` 
 - `/scores/nhl/<int:year>/<int:month>/<int:day>/` 
 - `/scores/nfl/<int:year>/<int:month>/<int:day>/` 
 - `/scores/nba/<int:year>/<int:month>/<int:day>/` 
 - `/scores/epl/<int:year>/<int:month>/<int:day>/` 
 - `/schedule/mlb/<team>` 
 - `/schedule/nhl/<team>` 
 - `/schedule/nfl/<team>` 
 - `/roster/mlb/<team>` 
 - `/roster/nhl/<team>` 
 - `/roster/nfl/<team>` 
 - `/roster/nba/<team>` 
 - `/stats/mlb/<team>` 
 - `/stats/nhl/<team>` 
 - `/stats/nfl/<team>` 
 - `/stats/nba/<team>`
