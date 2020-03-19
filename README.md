<p align="center">
	<a href="https://Clinical-Genomics.github.io/scout/">
		<img height="165" width="637" src="artwork/logo-display.png">
	</a>
	<h3 align="center">Analyze VCFs and collaborate on solving rare diseases quicker</h3>
</p>

[![Build Status][travis-img]][travis-url]
![Build Status - GitHub](https://github.com/Clinical-Genomics/scout/workflows/Scout%20tests/badge.svg)
[![PyPI Version][pypi-img]][pypi-url]
[![Coverage Status](https://coveralls.io/repos/github/Clinical-Genomics/scout/badge.svg?branch=master)](https://coveralls.io/github/Clinical-Genomics/scout?branch=master)
[![GitHub issues-closed][closed-issues-img]][closed-issues-url]
[![Average time to resolve an issue][ismaintained-resolve-img]][ismaintained-resolve-url]
[![Percentage of issues still open][ismaintained-open-rate-img]][ismaintained-open-rate-url]
[![GitHub commits](https://img.shields.io/github/commits-since/Clinical-Genomics/scout/v4.8.0.svg)](https://GitHub.com/Clinical-Genomics/scout/commit/)
[![CodeFactor](https://www.codefactor.io/repository/github/clinical-genomics/scout/badge)](https://www.codefactor.io/repository/github/clinical-genomics/scout)

## What is Scout?

- **Simple** - Analyze variants in a simple to use web interface.
- **Aggregation** - Combine results from multiple analyses and VCFs into a centralized database.
- **Collaboration** - Write comments and share cases between users and institutes.

## Documentation

This README only gives a brief overview of Scout, for a more complete reference, please check out our docs: [www.clinicalgenomics.se/scout](http://www.clinicalgenomics.se/scout/).

## Installation

<!-- You can install the latest release of Scout using `pip`:

```bash
pip install scout-browser

# ... to include optional coverage tools you would use:
pip install scout-browser[coverage]
```

If you would like to install Scout for local development: -->

```bash
git clone https://github.com/Clinical-Genomics/scout
cd scout
pip install --requirement requirements.txt --editable .
```

Scout PDF reports are created using [Flask-WeasyPrint](https://pythonhosted.org/Flask-WeasyPrint/). This library requires external dependencies which need be installed separately (namely Cairo and Pango). See platform-specific instructions for Linux, macOS and Windows available on the WeasyPrint installation [pages](https://weasyprint.readthedocs.io/en/stable/install.html#).

You also need to have an instance of MongoDB running. I've found that it's easiest to do using the official Docker image:

```bash
docker run --name mongo -p 27017:27017 mongo
```

## Usage

### Demo

Once installed, you can setup Scout by running a few commands using the included command line interface. Given you have a MongoDB server listening on the default port (27017), this is how you would setup a fully working Scout demo:

```bash
scout setup demo
```

This will setup an instance of scout with a database called `scout-demo`. Now run

```bash
scout --demo serve
```
And play around with the interface. A user has been created with email clark.kent@mail.com so use that adress to get access

### Initialize scout

To initialize a working instance with all genes, diseases etc run

```bash
scout setup database
```

for more info, run `scout --help`

> If you intent to use authentication, make sure you are using a Google email!

The previous command setup the database with a curated collection of gene definitions with links to OMIM along with HPO phenotype terms. Now we will load some example data. Scout expects the analysis to be accomplished using various gene panels so let's load one and then our first analysis case:

```bash
scout load panel scout/demo/panel_1.txt
scout load case scout/demo/643594.config.yaml
```

## Integration with chanjo for coverage report visualization

Scout may be configured to visualize coverage reports produced by [Chanjo][chanjo]. Instructions on
how to enable this feature can be found in the document [chanjo_coverage_integration][chanjo-scout].

## Integration with loqusdb for integrating local variant frequencies

Scout may be configured to visualize local variant frequencies monitored by [Loqusdb][loqusdb].
Instructions on how to enable this feature can be found in the document
[loqusdb integration][loqusdb-scout].

## Server setup

Scout needs a server config to know which databases to connect to etc. Depending on which
information you provide you activate different parts of the interface automatically,
including user authentication, coverage, and local observations.

This is an example of the config file:

```python
# scoutconfig.py

# list of email addresses to send errors to in production
ADMINS = ['paul.anderson@magnolia.com']

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DBNAME = 'scoutTest'
MONGO_USERNAME = 'testUser'
MONGO_PASSWORD = 'testPass'

# enable user authentication using Google OAuth
GOOGLE = dict(
		consumer_key='CLIENT_ID',
		consumer_secret='CLIENT_SECRET',
		base_url='https://www.googleapis.com/oauth2/v1/',
		authorize_url='https://accounts.google.com/o/oauth2/auth',
		request_token_url=None,
		request_token_params={
				'scope': ("https://www.googleapis.com/auth/userinfo.profile "
						  "https://www.googleapis.com/auth/userinfo.email"),
		},
		access_token_url='https://accounts.google.com/o/oauth2/token',
		access_token_method='POST'
)

# enable Phenomizer gene predictions from phenotype terms
PHENOMIZER_USERNAME = '???'
PHENOMIZER_PASSWORD = '???'

# enable Chanjo coverage integration
SQLALCHEMY_DATABASE_URI = '???'
REPORT_LANGUAGE = 'en'  # or 'sv'

# other interesting settings
SQLALCHEMY_TRACK_MODIFICATIONS = False  # this is essential in production
TEMPLATES_AUTO_RELOAD = False  			# consider turning off in production
SECRET_KEY = 'secret key'               # override in production!
```

Starting the server in now really easy, for the demo and local development we will use the CLI:

```bash
scout --flask-config config.py serve
```

![Scout Interface demo](artwork/scout-variant-demo.png)

### Hosting a production server

When running the server in production you will likely want to use a proper Python server solution
such as Gunicorn.
This is also how we can multiprocess the server and use encrypted HTTPS connections.

```bash
SCOUT_CONFIG=./config.py gunicorn --workers 4 --bind 0.0.0.0:8080 --access-logfile - --error-logfile
 - --keyfile /tmp/myserver.key --certfile /tmp/server.crt wsgi_gunicorn:app
```

> The `wsgi_gunicorn.py` file is included in the repo and configures Flask to work with Gunicorn.


### Integration with MatchMaker Exchange

Starting from release 4.4, Scout offers integration for patient data sharing via MatchMaker
Exchange.
General info about MatchMaker and patient matching could be found in [this paper][matchmaker-pub].
For a technical guideline of our implementation of MatchMaker Exchange at Clinical Genomics and its
integration with Scout check scouts [matchmaker docs][matchmaker-scout].
A user-oriented guide describing how to share case and variant data to MatchMaker using Scout can
be found [here][matchmaker-scout-sharing].


## Example of analysis config

TODO.


### Contributing to Scout

If you want to contribute and make Scout better, you help is very appreciated! Bug reports or
feature requests are really helpful and can be submitted via github issues.
Feel free to open a pull request to add a new functionality or fixing a bug, we welcome any help,
regardless of the amount of code provided or your skills as a programmer.
More info on how to contribute to the project and a description of the Scout branching workflow can
be found in [CONTRIBUTING](CONTRIBUTING.md).



[chanjo]: https://github.com/Clinical-Genomics/chanjo
[chanjo-scout]: docs/admin-guide/chanjo_coverage_integration.md
[loqusdb]: https://github.com/moonso/loqusdb
[loqusdb-scout]: docs/admin-guide/loqusdb_integration.md
[matchmaker-pub]: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6016856/
[matchmaker-scout]: docs/admin-guide/matchmaker_exchange_integration.md
[matchmaker-scout-sharing]: docs/user-guide/cases.md#matchmaker-exchange-integration
[travis-img]: https://img.shields.io/travis/Clinical-Genomics/scout/develop.svg?style=flat-square
[travis-url]: https://travis-ci.org/Clinical-Genomics/scout
[pypi-img]: https://img.shields.io/pypi/v/scout-browser.svg?style=flat-square
[pypi-url]: https://pypi.python.org/pypi/scout-browser/
[ismaintained-resolve-img]: http://isitmaintained.com/badge/resolution/Clinical-Genomics/scout.svg
[ismaintained-resolve-url]: http://isitmaintained.com/project/Clinical-Genomics/scout
[ismaintained-open-rate-img]: http://isitmaintained.com/badge/open/Clinical-Genomics/scout.svg
[ismaintained-open-rate-url]: http://isitmaintained.com/project/Clinical-Genomics/scout
[closed-issues-img]: https://img.shields.io/github/issues-closed/Clinical-Genomics/scout.svg
[closed-issues-url]: https://GitHub.com/Clinical-Genomics/scout/issues?q=is%3Aissue+is%3Aclosed
