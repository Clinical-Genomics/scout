# Running the server

This document will explain how we like to run Scout in both development and production settings.

## Config

The server has it's own config file, separate from the command line tool. It's written in Python for full expressivity. These are the settings you can use:

```python
# flask.conf.py

# to encrypt cookie data
SECRET_KEY = 'makeThisSomethingNonGuessable'  # required

# connection details for MongoDB
MONGO_DBNAME = 'scout'                        # required
MONGO_PORT = 27017
MONGO_USERNAME = 'mongoUser'
MONGO_PASSWORD = 'mongoUserPassword'

# connection string for Chanjo coverage database
SQLALCHEMY_DATABASE_URI = 'mysql://chanjo:CHANJO_PASSWORD@localhost:3306/chanjo'

# connection details for LoqusDB MongoDB database
LOQUSDB_SETTINGS = dict(
    database='loqusdb',
    uri=("mongodb://{}:{}@localhost:{}/loqusdb"
         .format(MONGO_USERNAME, MONGO_PASSWORD, MONGO_PORT)),
)

# default chanjo coverage report language: 'sv' or 'en'
REPORT_LANGUAGE = 'sv'

# Google email account to user for sending emails
MAIL_USERNAME = 'paul.anderson@gmail.com'
MAIL_PASSWORD = 'mySecretPassw0rd'

TICKET_SYSTEM_EMAIL = 'support@sekvens.nu'

# emails to send error log message to
ADMINS = ['robin.andeer@scilifelab.se']

# enable Google OAuth-based login
GOOGLE = dict(
    consumer_key='CLIENT_ID.apps.googleusercontent.com',
    consumer_secret='CLIENT_SECRET',
    # Prepend to all (non-absolute) request URLs
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

# enable the phenomizer service which links HPO phenotype terms to diseases/genes
PHENOMIZER_USERNAME = 'phenoUser'
PHENOMIZER_PASSWORD = 'phenoPassword'
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

[gunicorn]: http://gunicorn.org/
