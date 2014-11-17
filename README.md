# STATS, LLC. scraper
Scrapes the URL [nesn.stats.com](http://nesn.stats.com) using [Beautiful Soup 4.3.2](http://www.crummy.com/software/BeautifulSoup/) and returns a JSON object using Flask's [jsonify](http://flask.pocoo.org/docs/0.10/api/#flask.json.jsonify).

I began this project while employed at [NESN](http://nesn.com) to better understand Python and to learn Flask. The intended goal was to organize STATS's data into an intelligble resource, because, as you can see from the website, it contains HTML markup carried over from 1996. It was never used for production, mainly due to the fact it scrapes HTML which is notoriously unreliable, but also because there was no immediate use for it.

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
