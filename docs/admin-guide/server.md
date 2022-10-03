# Running the server

This document will explain how we like to run Scout in both development and production settings.

## Config

In order to run the web server, it is usually necessary to provide a number of parameters. All available parameters should be specified in a python-formatted configuration file. This config file is passed as a parameter when the application is launched. The following example of a config file is is used for running the development server (read further down):

```python
# -*- coding: utf-8 -*-
SECRET_KEY = "this is not secret..."
REMEMBER_COOKIE_NAME = "scout_remember_me"  # Prevent session timeout when user closes browser
# SESSION_TIMEOUT_MINUTES = 60  # Minutes of inactivity before session times out

# MONGO_URI = "mongodb://127.0.0.1:27011,127.0.0.1:27012,127.0.0.1:27013/?replicaSet=rs0&readPreference=primary"
MONGO_DBNAME = "scout"

BOOTSTRAP_SERVE_LOCAL = True
TEMPLATES_AUTO_RELOAD = True

DEBUG_TB_INTERCEPT_REDIRECTS = False

# Flask-mail: http://pythonhosted.org/flask-mail/
# see: https://bitbucket.org/danjac/flask-mail/issue/3
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False

# Filename of accrediation bagde image in server/bluprints/public/static
# If null no badge is displayed in scout
ACCREDITATION_BADGE = "swedac-1926-iso17025.png"

# LDAP login Settings
# Complete list of accepted parameters available here: https://github.com/rroemhild/flask-ldapconn
# LDAP_HOST = "localhost" # Can also be named LDAP_SERVER
# LDAP_PORT = 389
# LDAP_BASE_DN = 'cn=admin,dc=example,dc=com # Can also be named LDAP_BINDDN
# LDAP_USER_LOGIN_ATTR = "mail" # Can also be named LDAP_SEARCH_ATTR
# LDAP_USE_SSL = False
# LDAP_USE_TLS = True

# Parameters required for Google Oauth 2.0 login
# GOOGLE = dict(
#    client_id="client.apps.googleusercontent.com",
#    client_secret="secret",
#    discovery_url="https://accounts.google.com/.well-known/openid-configuration",
# )

# Chanjo database connection string - used by chanjo report to create coverage reports
# SQLALCHEMY_DATABASE_URI = "mysql+pymysql://test_user:test_passwordw@127.0.0.1:3306/chanjo"

# Configure gens service
# GENS_HOST = "127.0.0.1"
# GENS_PORT = 5000

# Connection details for communicating with a rerunner service
# RERUNNER_API_ENTRYPOINT = "http://rerunner:5001/v1.0/rerun"
# RERUNNER_TIMEOUT = 10
# RERUNNER_API_KEY = "I am the Keymaster of Gozer"

# Matchmaker connection parameters
# - Tested with PatientMatcher (https://github.com/Clinical-Genomics/patientMatcher) -
# MME_ACCEPTS = "application/vnd.ga4gh.matchmaker.v1.0+json"
# MME_URL = "http://localhost:9020"
# MME_TOKEN = "DEMO"

# Beacon connection settings
# - Tested with cgbeacon2 (https://github.com/Clinical-Genomics/cgbeacon2) -
# BEACON_URL = "http://localhost:6000/apiv1.0"
# BEACON_TOKEN = "DEMO"

# connection details for LoqusDB MongoDB database
# Example with 2 instances of LoqusDB, one using a binary file and one instance connected via REST API
# When multiple instances are available, admin users can modify which one is in use for a given institute from the admin settings page
# LOQUSDB_SETTINGS = {
#    "default" : {"binary_path": "/miniconda3/envs/loqus2.5/bin/loqusdb", "config_path": "/home/user/settings/loqus_default.yaml"},
#    "loqus_api" : {"api_url": "http://127.0.0.1:9000"},
# }

# Connection details for Scout REViewer service
# URL
# SCOUT_REVIEWER_URL = "http://127.0.0.1:8000/reviewer"

#
# Cloud IGV tracks can be configured here to allow users to enable them on their IGV views.
# CLOUD_IGV_TRACKS = [
#    {
#        "name": "custom_public_bucket",
#        "access": "public",
#        "tracks": [
#            {
#                "name": "dbVar Pathogenic or Likely Pathogenic",
#                "type": "variant",
#                "format": "vcf",
#                "build": "37",
#                "url": "https://s3-eu-west-1.amazonaws.com/pfigshare-u-files/25777457/GRCh37.variant_call.clinical.pathogenic_or_likely_pathogenic.vcf.gz",
#                "indexURL": "https://s3-eu-west-1.amazonaws.com/pfigshare-u-files/25777460/GRCh37.variant_call.clinical.pathogenic_or_likely_pathogenic.vcf.gz.tbi",
#            }
#        ],
#    },
# ]

# Chanjo-Report
REPORT_LANGUAGE = "en"
ACCEPT_LANGUAGES = ["en", "sv"]

# FEATURE FLAGS
SHOW_CAUSATIVES = True
SHOW_OBSERVED_VARIANT_ARCHIVE = True
HIDE_ALAMUT_LINK = True

# URL of a general web page where users can place orders for analyses or reruns
# RERUN_URL = "https://clinical.scilifelab.se/"
# Display case rerun monitoring toggle
RERUN_MONITOR = True

# OMIM API KEY: Required for downloading definitions from OMIM (https://www.omim.org/api)
# OMIM_API_KEY = 'valid_omim_api_key'

# Parameters for enabling Phenomizer queries
# PHENOMIZER_USERNAME = "test_user"
# PHENOMIZER_PASSWORD = "test_password"

# Rank model link
RANK_MODEL_LINK_PREFIX = "https://raw.githubusercontent.com/Clinical-Genomics/reference-files/master/rare-disease/rank_model/rank_model_-v"
RANK_MODEL_LINK_POSTFIX = "-.ini"
SV_RANK_MODEL_LINK_PREFIX = "https://raw.githubusercontent.com/Clinical-Genomics/reference-files/master/rare-disease/rank_model/svrank_model_-v"
SV_RANK_MODEL_LINK_POSTFIX = "-.ini"
```
### Minimal config

Unless you aim to install all subsystems that Scout can interact with, you are well advised to start by commenting out anything more than what you use. Try the default one in scout/scout/server/config.py - or start from the following:

```python
# minimal.flask.conf.py

# to encrypt cookie data
SECRET_KEY = 'makeThisSomethingNonGuessable'  # required

# connection details for MongoDB
MONGO_DBNAME = 'scout'                        # required
MONGO_PORT = 27017
```


## Development

Flask includes a decent server which works great for development. After you [install Scout](../install.md) you can start the server with some relevant settings:

```bash
# this line will help Flask find the server
FLASK_APP=scout.server.auto \
# this will enable debug mode of Flask and reload the server on code changes
FLASK_DEBUG=1 \
# this is a Scout specific variable that should point to the server config
SCOUT_CONFIG="/full/path/to/flask.conf.py" \
flask run
```
The server can also be started from the scout cli with the command `scout serve`. The default config file that will be used when no other configuration option is provided will be the one present under scout/server/config.py. To use an alternative flask config, you can use the `-f/ --flask_config` option. Example: `scout -f path/to/flask.conf.py serve`.


## Production

Now the built-in Flask server won't cut it anymore. We are a fan of using [Gunicorn][gunicorn] for running Python services. It's easy to setup and configure and handles things like multi-processing and SSL/HTTPS without problems. You can setup the server accordingly:

```bash
SCOUT_CONFIG="/full/path/to/flask.conf.py" \
gunicorn \
    --workers=4 \
    --bind="HOST:PORT" \
    --keyfile="/path/to/myserver.key" \
    --certfile="/path/to/server.crt" \
    scout.server.auto:app
```

Note that while it might still be necessary to provide a `SCOUT_CONFIG` environment variable pointing to python config file to run a full web server, some parameters like those used to connect to MongoDB (`MONGO_HOST`, `MONGO_DBNAME`, `MONGO_PORT`, `MONGO_USERNAME`, `MONGO_PASSWORD`, `MONGO_URI`) can be also be passed as environment variables. In that case they will have precedence over those provided in the config file.

If you are running a larger environment, where this is one component, we encourage a reverse proxy configuration where Scout is served by Gunicorn, and reverse proxied by [NGINX](https://nginx.org/en/). Then NGINX will handle the secure communication.

[gunicorn]: http://gunicorn.org/
