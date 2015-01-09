# Installation
This document provides a generic overview for installing this application. You can apply these steps to most Flask applications.

## Binary requirements
First, you'll need to install [Redis server](http://redis.io/download). This is used to build a run-time look-up table to compensate for STATS's silly resource identifier scheme (e.g. teams are identified by an integer, and not the team name). You will have to install this from source, but, it's simple to do so:

```sh
$ make
...
$ make test
...
$ sudo make install
```
Although not required, you ought to install the Python package [`virtualenv`](http://virtualenv.readthedocs.org/en/latest/) if you want this to work smoothly.

#### Clone the repository
```sh
$ git clone https://github.com/jkereako/stats-html-scraper-api.git
Cloning into 'stats-html-scraper-api'...
remote: Counting objects: 5, done.
remote: Compressing objects: 100% (5/5), done.
remote: Total 5 (delta 0), reused 0 (delta 0)
Unpacking objects: 100% (5/5), done.
Checking connectivity... done.
```
#### Create the virtual environment
```sh
$ cd stats-html-scraper-api
$ virtualenv env
New python executable in env/bin/python
Installing setuptools, pip...done.
```
#### Start the virtual environment and install package dependencies
```sh
$ source  env/bin/activate
(env) $ pip install -r requirements.txt
...
```

#### Run the webserver
```sh
(env) $ python run.py 
 * Running on http://localhost:5000/
 * Restarting with reloader
```

Now type in `http://localhost:5000/` into your web browser and start fooling around with this thing.
