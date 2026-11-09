# Running the server

This document explains how to run Scout in development and production.

## App configuration

Server and CLI app settings, including database connections, authentication, and extensions, are
configured in TOML. Scout loads the defaults from `scout/server/config.toml` and optionally merges
one installation-specific TOML file. Select that file with `SCOUT_CONFIG` or the CLI `--config`
option. The `-f` and `--flask-config` options remain aliases for `--config`.

This is a minimal installation-specific configuration:

```toml
SECRET_KEY = "make-this-non-guessable"
MONGO_DBNAME = "scout"
MONGO_PORT = 27017

# Configure Google OpenID Connect authentication
[GOOGLE]
client_id = "client.apps.googleusercontent.com"
client_secret = "replace-me"
discovery_url = "https://accounts.google.com/.well-known/openid-configuration"

# Configure Chanjo2 coverage reports
# CHANJO2_URL = "http://chanjo2.example.org"
```

TOML keys for Scout settings use the uppercase Flask configuration names. Nested tables are used
for dictionary settings such as `[GOOGLE]`, `[KEYCLOAK]`, and
`[LOQUSDB_SETTINGS.default]`. The package TOML file documents additional optional settings.

The CLI options take priority over the TOML file. The Mongo connection settings can also be
overridden with the `MONGO_HOST`, `MONGO_DBNAME`, `MONGO_PORT`, `MONGO_USERNAME`,
`MONGO_PASSWORD`, and `MONGO_URI` environment variables.

### Case load configuration

Case load files are separate YAML files and are not affected by the TOML app configuration. For
example, use `scout load case my_case.yaml` to load a case.

## Development

Flask's development server can be used after installing Scout:

```bash
SCOUT_CONFIG="/full/path/to/config.toml" \
FLASK_APP=scout.server.auto \
FLASK_DEBUG=1 \
flask run
```

You can also start the server through Scout's CLI:

```bash
scout --config /full/path/to/config.toml serve
```

When no file is selected, Scout uses the packaged defaults from
`scout/server/config.toml`.

## Production

For production, run Scout with a WSGI server such as Gunicorn:

```bash
SCOUT_CONFIG="/full/path/to/config.toml" \
gunicorn \
    --workers=4 \
    --bind="HOST:PORT" \
    --keyfile="/path/to/myserver.key" \
    --certfile="/path/to/server.crt" \
    scout.server.auto:app
```

For larger deployments, use a reverse proxy such as [NGINX](https://nginx.org/) in front of
Gunicorn to handle secure communication.

## Setting up a user login system

Scout supports Google authentication via OpenID Connect, LDAP, and simple authentication using
user ID and password. Google and LDAP authentication are suitable for production. See the
[login system guide](login-system.md) for setup instructions.

[gunicorn]: http://gunicorn.org/
