# Installation
## Binary requirements
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
