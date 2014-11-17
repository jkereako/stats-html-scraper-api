# STATS, LLC. scraper
Scrapes the URL [nesn.stats.com](http://nesn.stats.com) using [Beautiful Soup 4.3.2](http://www.crummy.com/software/BeautifulSoup/) and returns a JSON object using Flask's [jsonify](http://flask.pocoo.org/docs/0.10/api/#flask.json.jsonify).

I began this project while employed at [NESN](http://nesn.com) to better understand Python and to learn Flask. The intended goal was to organize STATS's data into an intelligble resource, because, as you can see from the website, it contains HTML markup carried over from 1996. It was never used for production, mainly due to the fact it scrapes HTML which is notoriously unreliable, but also because there was no immediate use for it.

# Binary requirements
First, you'll need to install [Redis server](http://redis.io/download). This is used for caching. You will have to install this from source, but, it's simple to do so:

```sh
$ make
...
$ make test
...
$ sudo make install
```
Although not required, you ought to install the Python package [`virtualenv`](http://virtualenv.readthedocs.org/en/latest/) if you want this to work smoothly.

####Clone the repository
```sh
$ git clone https://github.com/jkereako/stats-html-scraper-api.git
Cloning into 'stats-html-scraper-api'...
remote: Counting objects: 5, done.
remote: Compressing objects: 100% (5/5), done.
remote: Total 5 (delta 0), reused 0 (delta 0)
Unpacking objects: 100% (5/5), done.
Checking connectivity... done.
```
####Create the virtual environment
```sh
$ cd stats-html-scraper-api
$ virtualenv env
New python executable in env/bin/python
Installing setuptools, pip...done.
```
###Install package dependencies
`$ pip install -r requirements.txt`

####Run the webserver
```sh
$ python run.py 
 * Running on http://localhost:5000/
 * Restarting with reloader
```

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
